import yaml
import logging
import argparse
from typing import Dict, Tuple, List
from pathlib import Path
from datetime import datetime
import json
from agents.debater import Debater
from agents.judge import Judge
from utils import PlaceholderManager, extract_content, format_transcript
import random
import re
import fcntl  # Add this import at the top

def load_claims(dataset: str) -> List[Dict]:
    """Load claims based on dataset type."""
    paths = {
        'covid': 'data/final-data/enriched_covid_data_15.json',
        'climate': 'data/final-data/enriched_climate_data_15.json'
    }
    path = paths.get(dataset) or dataset

    with open(path, 'r') as f:
        all_claims = json.load(f)
        return all_claims

class DebateRunner:
    """Manages the debate process between two debaters and a judge."""
    
    CONFIG_PATH = "config/config.yaml"
    TOTAL_ROUNDS = 3
    
    # Prompt paths for different debate styles
    DEBATER_PROMPT_PATHS = {
        'default': "config/prompts/debate/debater/without_personalization/default_prompts.yaml",
        'browsing': "config/prompts/debate/debater/without_personalization/browsing_prompts.yaml",
        'default-personalized': "config/prompts/debate/debater/with_personalization/default_prompts.yaml",
        'browsing-personalized': "config/prompts/debate/debater/with_personalization/browsing_prompts.yaml"
    }
    
    JUDGE_PROMPT_PATHS = {
        'default': {
            'default': "config/prompts/debate/judge/default/no_persona_prompts.yaml",
            'persona': "config/prompts/debate/judge/default/with_persona_prompts.yaml"
        },
        'browsing': {
            'default': "config/prompts/debate/judge/browsing/no_persona_prompts.yaml",
            'persona': "config/prompts/debate/judge/browsing/with_persona_prompts.yaml"
        }
    }
    
    def __init__(self, debater_type: str, judge_type: str, claim: str,
                 first_debater_config: Dict = None, second_debater_config: Dict = None,
                 judge_config: Dict = None, sources: List[Dict] = None):
        """Initialize the debate runner."""
        self.debater_type = debater_type
        self.judge_type = judge_type
        
        # Get prompt paths
        self.debater_prompt_path = self.DEBATER_PROMPT_PATHS[debater_type]
        base_type = 'browsing' if 'browsing' in debater_type else 'default'
        self.judge_prompt_path = self.JUDGE_PROMPT_PATHS[base_type][judge_type]
        
        # Use provided configs or load from file
        if first_debater_config and second_debater_config and judge_config:
            self.first_debater_config = first_debater_config
            self.second_debater_config = second_debater_config
            self.judge_config = judge_config
        else:
            self.first_debater_config, self.second_debater_config, self.judge_config = self._load_config()
        
        # Add prompt paths to configs
        self.first_debater_config['prompt_path'] = self.debater_prompt_path
        self.second_debater_config['prompt_path'] = self.debater_prompt_path
        self.judge_config['prompt_path'] = self.judge_prompt_path
        
        # Setup context and agents
        placeholder_manager = PlaceholderManager(
            self.first_debater_config,
            debater_type,
            'debate',
            claim,
            sources
        )
        self.context = placeholder_manager.get_context()
        
        # Create specific contexts for each debater
        self.first_context = {
            **self.context,
            'opponent_name': self.second_debater_config['name']
        }
        
        self.second_context = {
            **self.context,
            'ANSWER_DEFENDING': self.context['ANSWER_OPPOSING'],
            'ANSWER_OPPOSING': self.context['ANSWER_DEFENDING'],
            'opponent_name': self.first_debater_config['name']
        }
        
        # Setup judge context
        self.judge_context = {
            'CLAIM': claim,
            'NAME_A': self.first_debater_config['name'],
            'NAME_B': self.second_debater_config['name'],
            'ANSWER_A': self.context['ANSWER_DEFENDING'],
            'ANSWER_B': self.context['ANSWER_OPPOSING'],
            'PERSONA_DIR': self.context.get('PERSONA_DIR'),
            'PERSONA_DESC': self.context.get('PERSONA_DESC')
        }
        
        # Initialize agents
        self.first_debater = Debater(self.first_debater_config, self.first_context)
        self.second_debater = Debater(self.second_debater_config, self.second_context)
        self.judge = Judge(self.judge_config, self.judge_context)
        self.full_transcript = []

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        timestamp = datetime.now().strftime('%b_%d_%I_%M_%S_%p').lower()
        folder_name = f"debater_{self.debater_type}_judge_{self.judge_type}"
        save_dir = Path('saved-data/debate') / folder_name / timestamp
        save_dir.mkdir(parents=True, exist_ok=True)
        
        log_path = save_dir / 'debate.log'
        
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(log_path)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        self.save_dir = save_dir

    def _load_config(self) -> Tuple[Dict, Dict, Dict]:
        """Load and prepare configuration for all agents."""
        with open(self.CONFIG_PATH, 'r') as file:
            config = yaml.safe_load(file)
            
            first_config = {
                **config['debaters']['first'],
                'debater_settings': config['debater_settings'],
                'prompt_path': self.debater_prompt_path
            }
            
            second_config = {
                **config['debaters']['second'],
                'debater_settings': config['debater_settings'],
                'prompt_path': self.debater_prompt_path
            }
            
            judge_config = {
                **config['debate_judge'],
                'prompt_path': self.judge_prompt_path
            }
            
            return first_config, second_config, judge_config

    def run_round(self, round_num: int) -> Dict:
        """Run a single round of debate and return round data."""
        logging.info(f"\n{'='*50}\nStarting round {round_num}\n{'='*50}")
        
        # Get first debater's response
        first_response = self.first_debater.get_response(round_num)
        logging.info(f"\nDebater A Response (Round {round_num}):\n{first_response}\n")
        logging.info("--------------------------------")
        logging.info(json.dumps(self.first_debater.messages, indent=2))
        logging.info("--------------------------------")
        
        # Extract first debater data
        first_thinking = extract_content(first_response, "thinking")
        first_argument = extract_content(first_response, "argument")
        
        # Get second debater's response
        second_response = self.second_debater.get_response(round_num)
        logging.info(f"\nDebater B Response (Round {round_num}):\n{second_response}\n")
        logging.info("--------------------------------")
        logging.info(json.dumps(self.second_debater.messages, indent=2))
        logging.info("--------------------------------")
        
        # Extract second debater data
        second_thinking = extract_content(second_response, "thinking")
        second_argument = extract_content(second_response, "argument")
        
        # Format the round transcript
        round_transcript = (
            f"{self.first_debater_config['name']}'s Argument:\n{first_argument}\n\n"
            f"{self.second_debater_config['name']}'s Argument:\n{second_argument}"
        )
        
        # Add to full transcript
        self.full_transcript.append(f"Round {round_num}:\n{round_transcript}")
        
        # Update ALL contexts with the debate transcript
        transcript_text = "\n".join(self.full_transcript)
        self.first_context['previous_rounds_transcript_debate'] = transcript_text
        self.second_context['previous_rounds_transcript_debate'] = transcript_text
        self.judge_context['previous_rounds_transcript_debate'] = transcript_text
        
        # Debug print after updating contexts
        logging.info(f"Updated transcript: {transcript_text}")
        
        # Get judge's response
        judge_response = self.judge.get_response(round_num)
        logging.info(f"\nJudge Response (Round {round_num}):\n{judge_response}\n")
        logging.info("--------------------------------")
        logging.info(json.dumps(self.judge.messages, indent=2))
        logging.info("--------------------------------")
        
        # Extract judge data
        judge_thinking = extract_content(judge_response, "thinking")
        judge_questions = extract_content(judge_response, "questions")
        
        # Add judge questions to transcript if not final round
        if round_num < self.TOTAL_ROUNDS:
            self.full_transcript.append(f"Judge Questions:\n{judge_questions}\n")
            # Update contexts again with judge questions
            transcript_text = "\n".join(self.full_transcript)
            self.first_context['previous_rounds_transcript_debate'] = transcript_text
            self.second_context['previous_rounds_transcript_debate'] = transcript_text
        
        return {
            "round_number": round_num,
            "debater_a": {
                "thinking": first_thinking,
                "argument": first_argument
            },
            "debater_b": {
                "thinking": second_thinking,
                "argument": second_argument
            },
            "judge": {
                "thinking": judge_thinking,
                "questions": judge_questions
            }
        }

    def run(self) -> None:
        """Run the complete debate process."""
        try:
            round_data = []
            for round_num in range(1, self.TOTAL_ROUNDS + 1):
                try:
                    round_info = self.run_round(round_num)
                    round_data.append(round_info)
                except Exception as e:
                    logging.error(f"Error in round {round_num}", exc_info=e)
                    raise
            
            # Return round data instead of saving
            return round_data
            
        except Exception as e:
            logging.error(f"Error in debate", exc_info=e)
            raise

    @classmethod
    def _load_base_config(cls, debater_a_model: str, debater_b_model: str, judge_model: str) -> Tuple[Dict, Dict, Dict]:
        """Load base configuration for specified models."""
        with open(cls.CONFIG_PATH, 'r') as file:
            config = yaml.safe_load(file)
            
            # Map model names to config keys
            model_map = {
                'gpt4o': 'openai',
                'claude': 'anthropic',
                'qwen': 'sglang',
                'deepseek': 'azure'
            }
            
            # Get configs for each agent
            first_debater_config = config['debaters']['first'][model_map[debater_a_model]]
            second_debater_config = config['debaters']['second'][model_map[debater_b_model]]
            judge_config = config['debate_judge'][model_map[judge_model]]
            
            # Add debater settings
            first_debater_config['debater_settings'] = config['debater_settings']
            second_debater_config['debater_settings'] = config['debater_settings']
            
            return first_debater_config, second_debater_config, judge_config

def main():
    """Run the debate process."""
    parser = argparse.ArgumentParser(description='Run debate with different configurations')
    parser.add_argument('--debater', 
                       choices=['default', 'browsing', 'default-personalized', 'browsing-personalized'],
                       required=True,
                       help='Choose debater type')
    parser.add_argument('--judge',
                       choices=['default', 'persona'],
                       required=True,
                       help='Choose judge type')
    parser.add_argument('--dataset',
                       choices=['covid', 'climate'],
                       required=True,
                       help='Dataset to use')
    parser.add_argument('--debater-a-model',
                       choices=['gpt4o', 'claude', 'qwen', 'deepseek'],
                       required=True,
                       help='Model for first debater')
    parser.add_argument('--debater-b-model',
                       choices=['gpt4o', 'claude', 'qwen', 'deepseek'],
                       required=True,
                       help='Model for second debater')
    parser.add_argument('--judge-model',
                       choices=['gpt4o', 'claude', 'qwen', 'deepseek'],
                       required=True,
                       help='Model for judge')
    parser.add_argument('--judge-prolific-id',
                       required=False,
                       help='Prolific ID of judge persona')   
    parser.add_argument('--argue-for-debater-a',
                       choices=['correct', 'incorrect'],
                       required=True,
                       help='Whether debater A should argue for correct or incorrect answer')
    parser.add_argument('--test-run',
                       action='store_true',
                       help='Run with only the first claim for testing purposes')
    
    args = parser.parse_args()
    
    # Load claims based on dataset
    if args.judge == 'persona':
        claims_data = load_claims(f"./debate-claim-assignment-by-participant/{args.judge_prolific_id}_{args.dataset}.json")
    else:
        claims_data = load_claims(args.dataset)

    # If test run, use only the first claim
    if args.test_run:
        claims_data = claims_data[:1]
        print(f"\n🧪 TEST RUN MODE: Processing only the first claim for testing")
    
    # Create setup directory
    setup_dir = Path('saved-data/debate') / f"debater_{args.debater}_judge_{args.judge}"
    setup_dir.mkdir(parents=True, exist_ok=True)
    
    # # Setup logging
    # log_file = setup_dir / f"{args.dataset}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            # logging.FileHandler(log_file),  # Commented out file logging
            logging.StreamHandler()
        ]
    )
    
    # Process each claim
    all_debate_data = {}
    
    print(f"\nStarting claims processing... Total claims: {len(claims_data)}")
    if len(claims_data) == 0:
        return
    
    for claim_data in claims_data:
        try:
            logging.info(f"\nProcessing claim: {claim_data['claim']}")
            
            # Combine supporting and opposing sources (limited to first 7 each)
            all_sources = []
            if 'supporting_sources' in claim_data:
                all_sources.extend(claim_data['supporting_sources'][:7])  # Take first 7 supporting sources
            if 'opposing_sources' in claim_data:
                all_sources.extend(claim_data['opposing_sources'][:7])  # Take first 7 opposing sources
            
            first_debater_config, second_debater_config, judge_config = DebateRunner._load_base_config(
                args.debater_a_model, 
                args.debater_b_model, 
                args.judge_model
            )

            if args.judge == 'persona':
                first_debater_config['judge_prolific_id'] = args.judge_prolific_id
            
            # Add claim veracity and argue_for setting
            first_debater_config['claim_veracity'] = claim_data['veracity']
            first_debater_config['argue_for_debater_a'] = args.argue_for_debater_a
            
            # Then create runner with configs
            runner = DebateRunner(
                debater_type=args.debater,
                judge_type=args.judge,
                claim=claim_data['claim'],
                first_debater_config=first_debater_config,
                second_debater_config=second_debater_config,
                judge_config=judge_config,
                sources=all_sources
            )
            
            # Get round data and store in all_debate_data
            round_data = runner.run()
            claim_key = f"claim_{len(all_debate_data) + 1}"
            all_debate_data[claim_key] = {
                'metadata': {
                    'claim': claim_data['claim'],
                    'veracity': claim_data['veracity'],
                    'label': claim_data.get('label'),
                    'evidence': claim_data.get('evidence'),
                    'evidence_label': claim_data.get('evidence_label'),
                    'article': claim_data.get('article')
                },
                'rounds': round_data,
                'supporting_sources': claim_data.get('supporting_sources', []),
                'opposing_sources': claim_data.get('opposing_sources', [])
            }
            
        except Exception as e:
            logging.error(f"Error processing claim: {claim_data['claim']}")
            logging.error(f"Error details", exc_info=e)
            continue
    
    # Save results with runner context
    save_debate_results(args, all_debate_data, runner)

def save_debate_results(args, all_debate_data, runner):
    """Save results with file locking for parallel processing."""
    base_dir = Path('saved-data/debate')
    setup_dir = base_dir / f"debater_{args.debater}_judge_{args.judge}" / args.dataset
    setup_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = setup_dir / f"results_{args.argue_for_debater_a}.json"
    
    # Process the data first
    run_id = f"run_da-{args.debater_a_model}_db-{args.debater_b_model}_j-{args.judge_model}_{datetime.now().strftime('%Y%m%d_%H%M%S.%f')}"
    
    run_data = {
        'metadata': {
            'setup': f"{args.debater}_{args.judge}",
            'prolific_id': args.judge_prolific_id if hasattr(args, 'judge_prolific_id') else None,
            'dataset': args.dataset,
            'argue_for_debater_a': args.argue_for_debater_a,
            'timestamp': datetime.now().isoformat(),
            'debater_a_model': args.debater_a_model,
            'debater_b_model': args.debater_b_model,
            'judge_model': args.judge_model,
            'word_limit': runner.first_debater_config['debater_settings']['word_limit'],
            'debater_a_temperature': runner.first_debater_config['temperature'],
            'debater_b_temperature': runner.second_debater_config['temperature'],
            'judge_temperature': runner.judge_config['temperature']
        },
        'claims': {}
    }
    
    # Process claims data
    for claim_id, claim_data in all_debate_data.items():
        # Create new PlaceholderManager for each claim
        claim_config = runner.first_debater_config.copy()
        claim_config['claim_veracity'] = claim_data['metadata']['veracity']
        claim_config['argue_for_debater_a'] = args.argue_for_debater_a
        
        placeholder_manager = PlaceholderManager(claim_config, args.debater, 'debate', claim_data['metadata']['claim'])
        claim_context = placeholder_manager.get_context()
        
        # Extract judge's final verdict from last round
        judge_questions = claim_data['rounds'][-1]['judge']['questions']
        verdict, confidence = extract_verdict(judge_questions)
        
        # Detailed claim info
        claim_info = {
            'claim': claim_data['metadata']['claim'],
            'true_label': claim_data['metadata']['veracity'],
            'debater_a_defending': claim_context['ANSWER_DEFENDING'],
            'debater_a_opposing': claim_context['ANSWER_OPPOSING'],
            'debater_b_defending': claim_context['ANSWER_OPPOSING'],  # B argues opposite of A
            'debater_b_opposing': claim_context['ANSWER_DEFENDING'],  # B argues opposite of A
            'judge_final_verdict': verdict,
            'judge_confidence_level': confidence,
            'label': claim_data['metadata'].get('label'),
            'rounds': claim_data['rounds'],
            'sources': {
                'supporting_sources': [clean_source(s) for s in claim_data.get('supporting_sources', [])[:7]],
                'opposing_sources': [clean_source(s) for s in claim_data.get('opposing_sources', [])[:7]]
            }
        }
        
        # Add optional fields for climate dataset
        for field in ['evidence', 'evidence_label', 'article']:
            if field in claim_data['metadata']:
                claim_info[field] = claim_data['metadata'][field]
        
        run_data['claims'][claim_id] = claim_info
    
    # File locking for concurrent access
    with open(results_file, 'a+') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            # Read existing data
            f.seek(0)
            content = f.read()
            existing_data = json.loads(content) if content else {'runs': {}}
            
            # Add new run
            existing_data['runs'][run_id] = run_data
            
            # Write back
            f.seek(0)
            f.truncate()
            json.dump(existing_data, f, indent=2)
            
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    logging.info(f"Saved results to {results_file}")

def extract_verdict(question_text: str) -> (str, int):
    """Extract verdict and confidence from judge's question text, case-insensitive."""
    verdict = None
    confidence = None

    # Try finding verdict first
    match = re.search(r'verdict:\s*(\w+)', question_text, re.IGNORECASE)
    if match:
        verdict = match.group(1).capitalize()

    # Try finding decision if no verdict found
    if not verdict:
        match = re.search(r'<decision>\s*(\w+)\s*</decision>', question_text, re.IGNORECASE)
        verdict = match.group(1).capitalize()

    # Find confidence
    match = re.search(r'confidence:\s*(\d{1,3})', question_text, re.IGNORECASE)
    if match:
        confidence = int(match.group(1))

    return (verdict, confidence)

def clean_source(source):
    """Clean source object to only include essential fields."""
    return {
        'title': source.get('title', ''),
        'url': source.get('url', ''),
        'content': source.get('content', '')
    }

if __name__ == "__main__":
    main()
