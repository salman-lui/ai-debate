from pathlib import Path
import random
import yaml
import re
import logging
from typing import Dict
from dotenv import load_dotenv
from datetime import datetime
from gcp_storage import CloudStorageInterface
CURRENT_DIR = Path(__file__).parent

load_dotenv()
WEB_CONFIG = CURRENT_DIR / "config/config_web.yaml"
PROMPT_PATH = CURRENT_DIR / "config/prompts/consultancy/consultant/without_personalization/browsing_prompts.yaml"

class ConsultancyRunner:
    """Manages the consultation process between AI consultant and human judge."""
    
    TOTAL_ROUNDS = 3

    def __init__(self):
        """Initialize the ConsultancyRunner with storage, logging, and state management."""
        self._init_logging()
        self.config = self._load_config()
        self.storage = CloudStorageInterface()
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S') + f"_{random.getrandbits(64)}"
        self.debate_transcript = None
        self.rounds_completed = set()
        self.debate_started = False
        self.initial_choice = None
        self.initial_confidence = None
        self.selected_choice = None
        self.selected_confidence = None
        self.context = None
        self.consultant = None
        self.prolific_id = None

    def _init_logging(self) -> None:
        """Initialize logging configuration."""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / 'consultancy.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _load_config(self) -> Dict:
        """Load and process configuration files."""
        with open(WEB_CONFIG, 'r') as file:
            config = yaml.safe_load(file)
            consultant_config = config['consultant']
            consultant_config['consultant_settings'] = config['consultant_settings']
            consultant_config['prompt_path'] = PROMPT_PATH
            return consultant_config

    def _initialize_transcript(self) -> Dict:
        """Initialize the debate transcript structure."""
        return {
            "session_id": self.session_id,
            "debate_topic": self.context.statement,
            "rounds": [],
            "initial_choice": None,
            "initial_confidence": None,
            "final_decision": None,
            "confidence_level": None,
            "reasoning": None,
            "answer_defending": str(self.context.answer_defending).capitalize(),
            "answer_opposing": str(not self.context.answer_defending).capitalize(),
            "reference_sources": self.context.formatted_sources,
            "veracity": self.context.claim_data['veracity'],
            "label": self.context.claim_data['label'],
            "metadata": {
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "prolific_data": None,
                "total_rounds": self.TOTAL_ROUNDS,
                "word_limit": self.config['consultant_settings']['word_limit'],
                "consultant_model": self.config['model'],
                "consultant_temperature": self.config['temperature']
            }
        }

    def _process_evidence_tags(self, text: str) -> str:
            """Process evidence tags in the text and format URLs and evidence."""
            # First extract and store all URLs
            url_pattern = r'<url>(.*?)</url>'
            urls = re.findall(url_pattern, text)
            
            # Replace evidence tags with colored spans
            def replace_evidence(match):
                evidence_text = match.group(1)
                return f'<span style="color: #16a34a">{evidence_text}</span>'
            
            pattern = r'<v_evidence>(.*?)</v_evidence>'
            processed_text = re.sub(pattern, replace_evidence, text, flags=re.DOTALL)
            
            # Replace URL tags with numbered citations
            for i, url in enumerate(urls, 1):
                processed_text = processed_text.replace(f'<url>{url}</url>', f'[{i}]')
                
            # Add citations list at the end if there are any URLs
            if urls:
                processed_text += '\n\nCitations:\n'
                for i, url in enumerate(urls, 1):
                    processed_text += f'\n[{i}] {url}\n'
                    
            return processed_text

    def _extract_argument(self, response: str) -> str:
        """Extract and process argument content from consultant response."""
        patterns = [
            r'<argument>(.*?)</argument>',
            r'<argument>(.*)',
            r'</thinking>(.*)'
        ]
        
        for pattern in patterns:
            if match := re.search(pattern, response, re.DOTALL | re.IGNORECASE):
                # Process the extracted text for evidence tags before returning
                extracted_text = match.group(1).strip()
                return self._process_evidence_tags(extracted_text)
        
        return self._process_evidence_tags(response.strip())


    def process_round(self, round_num: int) -> str:
        """Process a consultation round and update transcript."""
        logging.info(f"\n{'='*50}\nStarting round {round_num}\n{'='*50}")
        
        try:
            # Get consultant response
            self.consultant.context = self.context.to_dict()
            consultant_response = self.consultant.get_response(round_num=round_num)
            logging.info(f"\nConsultant Response (Round {round_num}):\n{consultant_response}\n")
            
            # Extract and process argument
            print(consultant_response)
            argument = self._extract_argument(consultant_response)
            self.context.update_transcripts(round_num, consultant_msg=argument)
            
            # Update transcript with consultant's response
            if len(self.debate_transcript["rounds"]) < round_num:
                self.debate_transcript["rounds"].append({
                    "round_number": round_num,
                    "timestamp": datetime.now().isoformat(),
                    "consultant_response": argument,
                    "judge_feedback": None,
                    "feedback_timestamp": None
                })
                
                # Save intermediate transcript
                self._save_transcript()
            
            return argument
            
        except Exception as e:
            logging.error(f"Error processing round {round_num}: {str(e)}")
            raise

    def update_judge_response(self, round_num: int, response: str) -> None:
        """Update context and transcript with judge's response."""
        try:
            # Update context
            self.context.update_transcripts(round_num, judge_msg=response)
            self.rounds_completed.add(round_num)
            
            # Update transcript with judge's response
            if 0 <= round_num - 1 < len(self.debate_transcript["rounds"]):
                self.debate_transcript["rounds"][round_num - 1]["judge_feedback"] = response
                self.debate_transcript["rounds"][round_num - 1]["feedback_timestamp"] = datetime.now().isoformat()
                self._save_transcript()
            
            logging.info(f"Judge response updated for round {round_num}")
            
        except Exception as e:
            logging.error(f"Error updating judge response for round {round_num}: {str(e)}")
            raise

    def save_initial_choice(self, choice: str, confidence: float = None):
        """Save the initial choice in the transcript."""
        try:
            self.initial_choice = choice
            self.initial_confidence = confidence
            self.debate_transcript["initial_choice"] = choice
            self.debate_transcript["initial_confidence"] = confidence
            self._save_transcript()
            logging.info(f"Initial choice saved: {choice}")
        except Exception as e:
            logging.error(f"Error saving initial choice: {str(e)}")
            raise

    def save_final_judgment(self, choice: str, confidence: float, reasoning: str) -> None:
        """Save the final judgment details and complete the transcript."""
        try:
            # Update instance variables
            self.selected_choice = choice
            self.selected_confidence = confidence
            
            # Update transcript
            self.debate_transcript.update({
                "final_decision": choice,
                "confidence_level": confidence,
                "reasoning": reasoning,
                "metadata": {
                    **self.debate_transcript["metadata"],
                    "end_time": datetime.now().isoformat()
                }
            })
            
            self._save_transcript()
            logging.info(f"Final judgment saved for session {self.session_id}")
            
        except Exception as e:
            logging.error(f"Error saving final judgment: {str(e)}")
            raise

    def _save_transcript(self) -> None:
        """Save the current transcript to storage."""
        try:
            transcript_path = f"transcripts/{self.session_id}.json"
            self.storage.save_transcript(self.debate_transcript, transcript_path)
            logging.info(f"Transcript saved: {transcript_path}")
        except Exception as e:
            logging.error(f"Error saving transcript: {str(e)}")
            raise

    def get_completion_data(self) -> Dict:
        """Get data needed for completion screen."""
        return {
            "initial_choice": self.initial_choice,
            "initial_confidence": self.initial_confidence,
            "final_choice": self.selected_choice,
            "confidence_level": self.selected_confidence,
            "session_id": self.session_id
        }

    def get_debate_progress(self) -> Dict:
        """Get current debate progress information."""
        return {
            "total_rounds": self.TOTAL_ROUNDS,
            "completed_rounds": len(self.rounds_completed),
            "current_round": len(self.debate_transcript["rounds"]),
            "debate_started": self.debate_started
        }
