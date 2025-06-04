import yaml
import logging
import argparse
import json
from typing import Dict, List, Tuple
from pathlib import Path
from datetime import datetime
from agents.consultant import Consultant
from agents.judge import Judge
from utils import PlaceholderManager, extract_content, format_transcript
import re
import fcntl

def load_claims(dataset: str) -> List[Dict]:
    """Load claims based on dataset type."""
    # paths = {
    #     'covid': 'data/final-data/final_covid_data.json',
    #     'climate': 'data/final-data/final_climate_data.json'
    # }
    paths = {
        'covid': 'data/final-data/enriched_covid_data_15.json',
        'climate': 'data/final-data/enriched_climate_data_15.json'
    }
    path = paths.get(dataset) or dataset

    with open(path, 'r') as f:
        all_claims = json.load(f)
        return all_claims

class ConsultancyRunner:
    """Manages the consultation process between consultant and judge."""
    
    CONFIG_PATH = "config/config.yaml"
    TOTAL_ROUNDS = 3
    
    # Prompt paths for different consultation styles
    CONSULTANT_PROMPT_PATHS = {
        'default': "config/prompts/consultancy/consultant/without_personalization/default_prompts.yaml",
        'browsing': "config/prompts/consultancy/consultant/without_personalization/browsing_prompts.yaml",
        'default-personalized': "config/prompts/consultancy/consultant/with_personalization/default_prompts.yaml",
        'browsing-personalized': "config/prompts/consultancy/consultant/with_personalization/browsing_prompts.yaml"
    }
    
    JUDGE_PROMPT_PATHS = {
        'default': {
            'default': "config/prompts/consultancy/judge/default/no_persona_prompts.yaml",
            'persona': "config/prompts/consultancy/judge/default/with_persona_prompts.yaml"
        },
        'browsing': {
            'default': "config/prompts/consultancy/judge/browsing/no_persona_prompts.yaml",
            'persona': "config/prompts/consultancy/judge/browsing/with_persona_prompts.yaml"
        }
    }
    
    def __init__(self, consultant_type: str, judge_type: str, claim: str, 
                 consultant_config: Dict = None, judge_config: Dict = None,
                 sources: List[Dict] = None):
        """Initialize the consultancy runner."""
        self.consultant_type = consultant_type
        self.judge_type = judge_type
        
        # Get prompt paths
        self.consultant_prompt_path = self.CONSULTANT_PROMPT_PATHS[consultant_type]
        base_type = 'browsing' if 'browsing' in consultant_type else 'default'
        self.judge_prompt_path = self.JUDGE_PROMPT_PATHS[base_type][judge_type]
        
        # Use provided configs or load from file
        if consultant_config and judge_config:
            self.consultant_config = consultant_config
            self.judge_config = judge_config
        else:
            self.consultant_config, self.judge_config = self._load_config()
        
        # Add prompt paths to configs
        self.consultant_config['prompt_path'] = self.consultant_prompt_path
        self.judge_config['prompt_path'] = self.judge_prompt_path
        
        # Setup context and agents
        placeholder_manager = PlaceholderManager(
            self.consultant_config, 
            consultant_type, 
            'consultancy', 
            claim,
            sources  # Pass sources to PlaceholderManager
        )
        self.context = placeholder_manager.get_context()
        self.consultant = Consultant(self.consultant_config, self.context)
        self.judge = Judge(self.judge_config, self.context)
        self.full_transcript = []

    def _load_config(self) -> Tuple[Dict, Dict]:
        """Load and prepare configuration for both agents."""
        with open(self.CONFIG_PATH, 'r') as file:
            config = yaml.safe_load(file)
            
            # Setup consultant config
            consultant_config = config['consultant']
            consultant_config['consultant_settings'] = config['consultant_settings']
            
            # Setup judge config
            judge_config = config['consultant_judge']
            judge_config['consultant_settings'] = config['consultant_settings']
            
            return consultant_config, judge_config

    def run_round(self, round_num: int) -> Dict:
        """Run a single round of consultation and return round data."""
        logging.info(f"\n{'='*50}\nStarting round {round_num}\n{'='*50}")
        
        # Get consultant's response
        consultant_response = self.consultant.get_response(round_num=round_num)
        logging.info(f"\nConsultant Response (Round {round_num}):\n{consultant_response}\n")
        logging.info("--------------------------------")
        logging.info(json.dumps(self.consultant.messages, indent=2))
        logging.info("--------------------------------")
        
        # Extract consultant data
        consultant_thinking = extract_content(consultant_response, "thinking")
        consultant_argument = extract_content(consultant_response, "argument")
        
        # Add to full transcript
        self.full_transcript.append(f"Round {round_num}:\nConsultant Argument:\n{consultant_argument}")
        
        # Update context with consultant's argument
        self.context['previous_rounds_transcript_consultant'] = format_transcript(round_num, consultant_argument)
        
        # Update judge's context for final round
        if round_num == self.TOTAL_ROUNDS:
            self.judge.context['entire_consultant_judge_transcript'] = self.full_transcript
        
        # Get judge's response
        judge_response = self.judge.get_response(round_num=round_num)
        logging.info(f"\nJudge Response (Round {round_num}):\n{judge_response}\n")
        logging.info("--------------------------------")
        logging.info(json.dumps(self.judge.messages, indent=2))
        logging.info("--------------------------------")
        
        # Extract judge data
        judge_thinking = extract_content(judge_response, "thinking")
        judge_question = extract_content(judge_response, "question")
        
        # Add judge question to transcript (except final round)
        if round_num < self.TOTAL_ROUNDS:
            self.full_transcript.append(f"Judge Question:\n{judge_question}\n")
            self.context['previous_rounds_transcript_judge'] = judge_question
            self.context['round_number'] = round_num + 1
        
        return {
            "round_number": round_num,
            "consultant": {
                "thinking": consultant_thinking,
                "argument": consultant_argument
            },
            "judge": {
                "thinking": judge_thinking,
                "question": judge_question
            }
        }

    def run(self) -> None:
        """Run the complete consultation process."""
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
            logging.error(f"Error in consultancy", exc_info=e)
            raise

    @classmethod
    def _load_base_config(cls, consultant_model: str, judge_model: str) -> Tuple[Dict, Dict]:
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
            
            # Get the right consultant config
            consultant_config = config['consultant'][model_map[consultant_model]]
            consultant_config['consultant_settings'] = config['consultant_settings']
            
            # Get the right judge config
            judge_config = config['consultant_judge'][model_map[judge_model]]
            judge_config['consultant_settings'] = config['consultant_settings']
            
            return consultant_config, judge_config

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

def save_setup_results(args, all_consultation_data, runner):
    """Save results with file locking for parallel processing."""
    base_dir = Path('saved-data/consultancy')
    # base_dir = Path('saved-data/consultancy-test') # change here also     setup_dir = Path('saved-data/consultancy-test') / f"consultant_{args.consultant}_judge_{args.judge}"
    setup_dir = base_dir / f"consultant_{args.consultant}_judge_{args.judge}" / args.dataset
    setup_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = setup_dir / f"results_{args.argue_for}.json"
    
    # Process the data first
    run_id = f"run_consultant_{args.consultant_model}_judge_{args.judge_model}_{datetime.now().strftime('%Y%m%d_%H%M%S.%f')}"
    
    # Structure data for this run
    run_data = {
        'metadata': {
            'setup': f"{args.consultant}_{args.judge}",
            'prolific_id': args.judge_prolific_id if hasattr(args, 'judge_prolific_id') else None,
            'dataset': args.dataset,
            'argue_for': args.argue_for,
            'timestamp': datetime.now().isoformat(),
            'consultant_model': args.consultant_model,
            'judge_model': args.judge_model,
            'word_limit': runner.consultant_config['consultant_settings']['word_limit'],
            'consultant_temperature': runner.consultant_config['temperature'],
            'judge_temperature': runner.judge_config['temperature']
        },
        'claims': {}
    }
    
    # Process claims data
    for claim_id, claim_data in all_consultation_data.items():
        # Create new PlaceholderManager for each claim
        claim_config = runner.consultant_config.copy()
        claim_config['claim_veracity'] = claim_data['metadata']['veracity']
        claim_config['argue_for'] = args.argue_for
        
        placeholder_manager = PlaceholderManager(claim_config, args.consultant, 'consultancy', claim_data['metadata']['claim'])
        claim_context = placeholder_manager.get_context()
        
        # Extract verdict
        judge_question = claim_data['rounds'][-1]['judge']['question']
        verdict, confidence = extract_verdict(judge_question)
        
        # Basic claim info
        claim_info = {
            'claim': claim_data['metadata']['claim'],
            'true_label': claim_data['metadata']['veracity'],
            'answer_defending': claim_context['ANSWER_DEFENDING'],
            'answer_opposing': claim_context['ANSWER_OPPOSING'],
            'judge_final_verdict': verdict,
            'judge_confidence_level': confidence,
            'label': claim_data['metadata'].get('label'),
            'rounds': claim_data['rounds'],
            'sources': {
                'supporting_sources': claim_data['metadata']['supporting_sources'],
                'opposing_sources': claim_data['metadata']['opposing_sources']
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

def main():
    """Run the consultancy process."""
    parser = argparse.ArgumentParser(description='Run consultancy with different configurations')
    parser.add_argument('--consultant', 
                       choices=['default', 'browsing', 'default-personalized', 'browsing-personalized'],
                       required=True,
                       help='Choose consultant type')
    parser.add_argument('--judge',
                       choices=['default', 'persona'],
                       required=True,
                       help='Choose judge type')
    parser.add_argument('--dataset',
                       choices=['covid', 'climate'],
                       required=True,
                       help='Dataset to use')
    parser.add_argument('--consultant-model',
                       choices=['gpt4o', 'claude', 'qwen', 'deepseek'],
                       required=True,
                       help='Model for consultant')
    parser.add_argument('--judge-model',
                       choices=['gpt4o', 'claude', 'qwen', 'deepseek'],
                       required=True,
                       help='Model for judge')
    parser.add_argument('--judge-prolific-id',
                       required=False,
                       help='Prolific ID of judge persona')   
    parser.add_argument('--argue-for',
                       choices=['correct', 'incorrect'],
                       required=True,
                       help='Whether to argue for correct or incorrect answer')
    
    args = parser.parse_args()

    # Load and update configs
    consultant_config, judge_config = ConsultancyRunner._load_base_config(args.consultant_model, args.judge_model)
    
    # Load claims based on dataset
    if args.judge == 'persona':
        consultant_config['judge_prolific_id'] = args.judge_prolific_id
        claims_data = load_claims(f"./consultancy-claim-assignment-by-participant/{args.judge_prolific_id}_{args.dataset}.json")
    else:
        claims_data = load_claims(args.dataset)

    # Add argue_for to consultant config right after loading
    consultant_config['argue_for'] = args.argue_for
        
    # Create setup directory and configure logging
    setup_dir = Path('saved-data/consultancy') / f"consultant_{args.consultant}_judge_{args.judge}"
    # setup_dir = Path('saved-data/consultancy-test') / f"consultant_{args.consultant}_judge_{args.judge}"
    setup_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup logging
    # log_file = setup_dir / f"{args.dataset}_{args.argue_for}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            # logging.FileHandler(log_file),  # Commented out file logging
            logging.StreamHandler()
        ]
    )

    # Process each claim
    all_consultation_data = {}
    
    print(f"\nStarting claims processing... Total claims: {len(claims_data)}")
    for claim_data in claims_data:
        try:
            consultant_config['claim_veracity'] = claim_data['veracity']
            logging.info(f"\nProcessing claim: {claim_data['claim']}")
            
            # Combine supporting and opposing sources (limited to first 7 each)
            all_sources = []
            if 'supporting_sources' in claim_data:
                all_sources.extend(claim_data['supporting_sources'][:7])  # Take first 7 supporting sources
            if 'opposing_sources' in claim_data:
                all_sources.extend(claim_data['opposing_sources'][:7])  # Take first 7 opposing sources
            
            # Debug print to see structure
            print(f"\nDEBUG - Claim data structure:")
            print(f"Keys in claim_data: {claim_data.keys()}")
            print(f"Supporting sources direct: {len(claim_data.get('supporting_sources', []))}")
            print(f"Opposing sources direct: {len(claim_data.get('opposing_sources', []))}")
            
            runner = ConsultancyRunner(
                consultant_type=args.consultant,
                judge_type=args.judge,
                claim=claim_data['claim'],
                consultant_config=consultant_config,
                judge_config=judge_config,
                sources=all_sources
            )
            
            # Get round data and store in all_consultation_data
            round_data = runner.run()
            claim_key = f"claim_{len(all_consultation_data) + 1}"
            all_consultation_data[claim_key] = {
                'metadata': {
                    'claim': claim_data['claim'],
                    'veracity': claim_data['veracity'],
                    'label': claim_data.get('label'),
                    'evidence': claim_data.get('evidence'),
                    'evidence_label': claim_data.get('evidence_label'),
                    'article': claim_data.get('article'),
                    # Clean sources before saving
                    'supporting_sources': [clean_source(s) for s in claim_data.get('supporting_sources', [])[:7]],
                    'opposing_sources': [clean_source(s) for s in claim_data.get('opposing_sources', [])[:7]]
                },
                'rounds': round_data
            }

        except Exception as e:
            logging.error(f"Error processing claim: {claim_data['claim']}")
            logging.error(f"Error details", exc_info=e)
            continue
    
    # Save results with runner context
    save_setup_results(args, all_consultation_data, runner)

if __name__ == "__main__":
    main()