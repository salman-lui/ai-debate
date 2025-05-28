# core/debate_manager.py
from typing import Dict, List, Optional
from pathlib import Path
import json
import random
from datetime import datetime
import pandas as pd
from openai import OpenAI
from gcp_storage import CloudStorageInterface
import os

from agents.debater import Debater
from utils.config import load_config, load_prompts
from utils.helper import save_transcript, extract_content
from utils.utils import format_sources

def load_secret(key: str) -> str:
    """Load secret value from SECRET file"""
    try:
        with open('SECRET', 'r') as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    if k == key:
                        return v
        raise KeyError(f"Key '{key}' not found in SECRET file")
    except FileNotFoundError:
        raise FileNotFoundError("SECRET file not found. Please create a SECRET file with your API key.")
    
class WebDebateManager:
    def __init__(self, config_path: str = "config/config.yaml", prompt_dir: str = "config/default-prompt", prolific_id: Optional[str] = None):
        print("Initializing WebDebateManager...")
        print(prolific_id)
        print("-" * 20)
        # Load basic configurations
        self.config = load_config(config_path)
        print(f"DEBUG WebDebateManager - Loaded word_limit from config: {self.config['debate_settings']['word_limit']}")
        self.client = OpenAI(api_key=load_secret('OPENAI_API_KEY'))
        self.prompts_dir = prompt_dir
        self.prompts = load_prompts(self.prompts_dir)
        self.prolific_id = prolific_id if prolific_id and prolific_id != "" else "default"
        
        # Initialize directories
        try:
            # Check if running locally or in Cloud Run
            if os.environ.get('K_SERVICE'):  # Running in Cloud Run
                self.base_output_dir = Path("/app/output")
            else:  # Running locally
                self.base_output_dir = Path("./local_output")
            
            # Create output directory
            self.base_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create tracking directory for user data
            self.tracking_dir = self.base_output_dir / "tracking"
            self.tracking_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating output directory: {e}")
        
        # Create timestamp for this debate session
        self.session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create main debate directory with timestamp
        self.debate_dir = self.base_output_dir / f"web_debate_{self.session_timestamp}"
        self.message_dir = self.debate_dir / "prompts"
        self.transcript_dir = self.debate_dir / "transcript"
        
        # Create all directories
        self.debate_dir.mkdir(parents=True, exist_ok=True)
        self.message_dir.mkdir(parents=True, exist_ok=True)
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize agents
        self.first_debater = None
        self.second_debater = None
        
        # Load debate data
        self.debate_data = self._load_debate_data()
        
        # Initialize usage tracking
        self.usage_tracking = self._initialize_usage_tracking()
        self.current_debate_index = self._get_next_debate_index()

        self.storage = CloudStorageInterface()
        
    def _load_debate_data(self) -> pd.DataFrame:
        """Load debate topics from JSON, trying user-specific file first."""
        # Try to load user-specific JSON if prolific_id is provided and not default
        if self.prolific_id != "default":
            # Get the directory of the default JSON
            json_dir = Path("debate-data-final/debate-final-68")
            # Construct user-specific JSON path
            user_json_path = json_dir / f"{self.prolific_id}_covid.json"
            try:
                print(f"Attempting to load user-specific debate data: {user_json_path}")
                with open(user_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert JSON to DataFrame with required columns
                    df = pd.DataFrame([{
                        'statement': item['claim'],
                        'correct_answer': str(item['veracity']).capitalize(),
                        'incorrect_answer': str(not item['veracity']).capitalize(),
                        'full_content': format_sources(item['supporting_sources'][:15]),
                        'veracity': item['veracity']
                    } for item in data])
                    return df
            except FileNotFoundError:
                print(f"User-specific JSON not found: {user_json_path}, falling back to default.")
        
        # Fallback to default JSON
        default_json_path = Path("debate-data-final/debate-final-68/default_covid.json")
        print(f"Loading default debate data: {default_json_path}")
        with open(default_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert JSON to DataFrame with required columns
            df = pd.DataFrame([{
                'statement': item['claim'],
                'correct_answer': str(item['veracity']).capitalize(),
                'incorrect_answer': str(not item['veracity']).capitalize(),
                'full_content': format_sources(item['supporting_sources'][:15]),
                'veracity': item['veracity']
            } for item in data])
            return df
    
    def _initialize_usage_tracking(self) -> Dict:
        """Initialize or load usage tracking data."""
        tracking_path = self.tracking_dir / f"{self.prolific_id}_debate_tracking.json"
        
        try:
            with open(tracking_path, 'r') as f:
                tracking_data = json.load(f)
                
                # Check if all debate indices are tracked
                # If new debates have been added, add them to tracking
                if len(tracking_data) < len(self.debate_data):
                    for i in range(len(self.debate_data)):
                        if str(i) not in tracking_data:
                            tracking_data[str(i)] = 0
                    # Save updated tracking data
                    with open(tracking_path, 'w') as f:
                        json.dump(tracking_data, f)
                
                return tracking_data
        except (FileNotFoundError, json.JSONDecodeError):
            # Initialize tracking data for all debates
            tracking_data = {str(i): 0 for i in range(len(self.debate_data))}
            tracking_path.parent.mkdir(parents=True, exist_ok=True)
            with open(tracking_path, 'w') as f:
                json.dump(tracking_data, f)
            return tracking_data
    
    def _update_usage_tracking(self, index: int):
        """Update usage tracking after using a debate topic."""
        tracking_path = self.tracking_dir / f"{self.prolific_id}_debate_tracking.json"
        self.usage_tracking[str(index)] = self.usage_tracking.get(str(index), 0) + 1
        
        try:
            with open(tracking_path, 'w') as f:
                json.dump(self.usage_tracking, f)
        except Exception as e:
            print(f"Error updating tracking data: {e}")
    
    def _get_next_debate_index(self) -> int:
        """Get the index of the next debate topic based on usage frequency."""
        # Find the minimum usage count
        min_usage = min(self.usage_tracking.values())
        min_usage_indices = [int(i) for i, count in self.usage_tracking.items() 
                            if count == min_usage and int(i) < len(self.debate_data)]
        
        # Select a random debate from those with minimum usage
        if min_usage_indices:
            selected_index = random.choice(min_usage_indices)
            print(f"Selected debate index {selected_index} (usage count: {min_usage})")
            return selected_index
        else:
            # Fallback to first debate if no valid indices
            print("No valid debate indices found, defaulting to index 0")
            return 0

    def _get_debate_topic(self) -> Dict:
        """Get debate topic from loaded data."""
        print(f"Current debate index: {self.current_debate_index}")
        row = self.debate_data.iloc[self.current_debate_index]
        columns = self.config["data"]["columns"]
        
        return {
            "statement": row[columns["statement"]],
            "answer_a": row[columns["correct_answer"]],
            "answer_b": row[columns["incorrect_answer"]],
            "content": row[columns["content"]]
        }


    def setup_debate(self):
        """Setup debate and agents with specified or next available index."""
        self._update_usage_tracking(self.current_debate_index)
        topic = self._get_debate_topic()
        
        # Initialize only debater agents
        self.first_debater = Debater(
            client=self.client,
            config=self.config["debaters"]["first"],
            name=self.config["debaters"]["first"]["name"],
            position="first",
            prompt_dir=self.prompts_dir,
            personalization=False
        )
        
        self.second_debater = Debater(
            client=self.client,
            config=self.config["debaters"]["second"],
            name=self.config["debaters"]["second"]["name"],
            position="second",
            prompt_dir=self.prompts_dir,
            personalization=False
        )
        
        # Setup contexts for debaters
        self._setup_contexts(topic)

    def _setup_contexts(self, topic: Dict):
        """Setup contexts for debater agents."""
        # Create a list of answers and randomly shuffle them
        answers = [
            {"answer": topic["answer_a"], "letter": "A"},
            {"answer": topic["answer_b"], "letter": "B"}
        ]
        random.shuffle(answers)
        
        # Setup first debater context
        first_debater_context = {
            "opponent_name": self.second_debater.name,
            "statement": topic["statement"],
            "answer_defending": answers[0]["answer"],
            "answer_opposing": answers[1]["answer"],
            "answer_defending_letter": answers[0]["letter"],
            "answer_opposing_letter": answers[1]["letter"],
            "content": topic["content"],
            "word_limit": self.config["debate_settings"]["word_limit"]
        }
        
        # Setup second debater context
        second_debater_context = {
            "opponent_name": self.first_debater.name,
            "statement": topic["statement"],
            "answer_defending": answers[1]["answer"],
            "answer_opposing": answers[0]["answer"],
            "answer_defending_letter": answers[1]["letter"],
            "answer_opposing_letter": answers[0]["letter"],
            "content": topic["content"],
            "word_limit": self.config["debate_settings"]["word_limit"]
        }

        print(f"DEBUG WebDebateManager - Setting up context with word_limit: {first_debater_context['word_limit']}")
        self.first_debater.setup_context(first_debater_context)
        self.second_debater.setup_context(second_debater_context)
    
    def get_first_debater_context(self) -> Dict:
        return self.first_debater.context
    
    def get_second_debater_context(self) -> Dict:
        return self.second_debater.context

    def _run_round(self, round_num: int, transcript: List[Dict]) -> Dict:
        """Run a single debate round."""
        # Create statement-specific directory using debate index
        statement_dir = self.message_dir / f"statement_{self.current_debate_index + 1}"
        statement_dir.mkdir(parents=True, exist_ok=True)

        # Set message paths for this round with statement-specific directory
        first_debater_msg_path = statement_dir / f"round_{round_num}_{self.first_debater.name}_messages.json"
        second_debater_msg_path = statement_dir / f"round_{round_num}_{self.second_debater.name}_messages.json"

        # Set message paths in agents (only debaters)
        self.first_debater.message_dir = first_debater_msg_path
        self.second_debater.message_dir = second_debater_msg_path
        
        # Get first debater response
        print(f"\n{self.first_debater.name}'s turn...")
        first_response = self.first_debater.get_response(round_num, transcript)
        first_argument = extract_content(first_response, "argument")
        print(f"\n{self.first_debater.name}'s Response:")
        print("-" * 20)
        print(first_argument)
        print("-" * 20)
        
        # Get second debater response
        print(f"\n{self.second_debater.name}'s turn...")
        second_response = self.second_debater.get_response(round_num, transcript)
        second_argument = extract_content(second_response, "argument")
        print(f"\n{self.second_debater.name}'s Response:")
        print("-" * 20)
        print(second_argument)
        print("-" * 20)
        
        # Print waiting for judge feedback
        print("\nWaiting for judge feedback from web interface...")
        
        # Return round data (judge response will be filled by web interface)
        return {
            "round": round_num,
            "debater_response": first_argument,
            "opponent_response": second_argument,
            "judge_response": "",  # Will be filled by web interface
            "raw_debater_response": first_response,
            "raw_opponent_response": second_response,
            "raw_judge_response": "",
            "debater_positions": {
                "first_debater": {
                    "name": self.first_debater.name,
                    "defending": self.first_debater.context["ANSWER_DEFENDING"],
                    "opposing": self.first_debater.context["ANSWER_OPPOSING"]
                },
                "second_debater": {
                    "name": self.second_debater.name,
                    "defending": self.second_debater.context["ANSWER_DEFENDING"],
                    "opposing": self.second_debater.context["ANSWER_OPPOSING"]
                }
            },
            "ground_truth_veracity": self.debate_data.iloc[self.current_debate_index]["veracity"]
        }
