import yaml
import logging
import argparse
import json
import re
import tqdm
import fcntl
from typing import Dict, List, Tuple
from pathlib import Path
from datetime import datetime
from utils import extract_content
from agents.judge import Judge


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

class InitialJudgementRunner:
    """Runs the judge to get initial claim evaluations."""
    
    CONFIG_PATH = "config/config.yaml"
    JUDGE_PROMPT_PATH = "config/prompts/initial_confidence_prompts.yaml"
    
    def __init__(self, claim: str, judge_persona: str, judge_config: Dict = None):
        # Use provided configs or load from file
        if judge_config:
            self.judge_config = judge_config
        else:
            self.judge_config = self._load_config()
        
        # Add prompt paths to configs
        self.judge_config['prompt_path'] = self.JUDGE_PROMPT_PATH
        
        self.context = {
            'CLAIM': claim,
            'PERSONA_DIR': judge_persona
        }
        self.judge = Judge(self.judge_config, self.context)

    def _load_config(self) -> Dict:
        """Load and prepare configuration for judge agent."""
        with open(self.CONFIG_PATH, 'r') as file:
            config = yaml.safe_load(file)
            
            # Setup judge config
            judge_config = config['consultant_judge']
            return judge_config

    def run(self) -> Dict:
        """Run the judgement process and return result."""
        try:
            # Get judge's response
            judge_response = self.judge.get_response(1)
            logging.info(f"\nJudge Response:\n{judge_response}\n")
            logging.info("--------------------------------")
            logging.info(json.dumps(self.judge.messages, indent=2))
            logging.info("--------------------------------")
            
            # Extract judge thinking and decision
            judge_thinking = extract_content(judge_response, "thinking")
            
            # Extract verdict and confidence
            verdict, confidence = extract_verdict(judge_response)
            
            return {
                "judge": {
                    "thinking": judge_thinking,
                    "verdict": verdict,
                    "confidence": confidence
                }
            }
            
        except Exception as e:
            logging.error(f"Error in judgement", exc_info=e)
            raise

    @classmethod
    def _load_base_config(cls, judge_model: str) -> Dict:
        """Load base configuration for specified model."""
        with open(cls.CONFIG_PATH, 'r') as file:
            config = yaml.safe_load(file)
            
            # Map model names to config keys
            model_map = {
                'gpt4o': 'azure',
                'claude': 'anthropic',
                'qwen': 'sglang',
                'deepseek': 'azure'
            }
            
            # Get the right judge config
            judge_config = config['consultant_judge'].get(model_map[judge_model], {})
            judge_config['model_type'] = model_map[judge_model]
            
            return judge_config

def extract_verdict(response_text: str) -> Tuple[str, int]:
    """Extract verdict and confidence from judge's response text, case-insensitive."""
    verdict = None
    confidence = None

    # Try finding verdict first
    match = re.search(r'<decision>\s*(\w+)\s*</decision>', response_text, re.IGNORECASE)
    if match:
        verdict = match.group(1).lower() == 'true'
    
    # Fall back to looking for "verdict:" format
    if verdict is None:
        match = re.search(r'verdict:\s*(\w+)', response_text, re.IGNORECASE)
        if match:
            verdict = match.group(1).lower() == 'true'

    # Find confidence
    match = re.search(r'confidence:\s*(\d{1,3})', response_text, re.IGNORECASE)
    if match:
        confidence = int(match.group(1))

    return (verdict, confidence)

def save_results(args, judge_prolific_id, all_judgement_data, runner):
    """Save results with file locking for parallel processing."""
    base_dir = Path('saved-data/initial')
    setup_dir = base_dir / f"judge_{datetime.now().strftime('%Y%m%d_%H%M%S')}" / args.dataset
    setup_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = setup_dir / "results.json"
    
    # Generate run ID
    run_id = f"run_judge_initial_{datetime.now().strftime('%Y%m%d_%H%M%S.%f')}"
    
    # Structure data for this run
    run_data = {
        'metadata': {
            'prolific_id': judge_prolific_id,
            'dataset': args.dataset,
            'timestamp': datetime.now().isoformat(),
            'judge_model': args.judge_model,
            'judge_temperature': runner.judge_config.get('temperature', 0.7)
        },
        'claims': {}
    }
    
    # Process claims data
    for claim_id, claim_data in all_judgement_data.items():
        claim_info = {
            'claim': claim_data['metadata']['claim'],
            'true_label': claim_data['metadata']['veracity'],
            'judge_verdict': claim_data['result']['judge']['verdict'],
            'judge_confidence_level': claim_data['result']['judge']['confidence']
        }       
        
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
    parser = argparse.ArgumentParser(description='Get initial judgements from simulated Prolific personas')
    parser.add_argument('--dataset',
                       choices=['covid', 'climate'],
                       required=True,
                       help='Dataset to use')
    parser.add_argument('--mode',
                       choices=['debate', 'consultancy'],
                       required=True,
                       help='Which folder to grab the claims from')
    parser.add_argument('--judge-model',
                       choices=['gpt4o', 'claude', 'qwen', 'deepseek'],
                       required=True,
                       help='Model for judge')
    parser.add_argument('--personas-path',
                       default='./personas/all_personas.json',
                       help='List of all Prolific personas')
    
    args = parser.parse_args()

    # Load and update configs
    judge_config = InitialJudgementRunner._load_base_config(args.judge_model)

    # Get all Prolific submissions
    with open(args.personas_path, 'r') as personas_file:
        personas = json.load(personas_file)

    for judge_prolific_id in tqdm.tqdm(personas.keys()):
        judge_persona = personas[judge_prolific_id]

        # Load claims data
        claims_path = f"./{args.mode}-claim-assignment-by-participant/{judge_prolific_id}_{args.dataset}.json"
        try:
            with open(claims_path, 'r') as f:
                claims_data = json.load(f)
        except FileNotFoundError:
            # Fall back to loading from the dataset directly
            claims_data = load_claims(args.dataset)
            
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )

        # Process each claim
        all_judgement_data = {}
        
        print(f"\nStarting claims processing... Total claims: {len(claims_data)}")
        for idx, claim_data in enumerate(claims_data):
            try:
                logging.info(f"\nProcessing claim {idx+1}/{len(claims_data)}: {claim_data['claim']}")
                
                # Create runner and get judgment
                runner = InitialJudgementRunner(
                    claim=claim_data['claim'],
                    judge_config=judge_config,
                    judge_persona=judge_persona
                )
                
                # Get judgment result
                result = runner.run()
                
                # Store result
                claim_key = f"claim_{idx + 1}"
                all_judgement_data[claim_key] = {
                    'metadata': {
                        'claim': claim_data['claim'],
                        'veracity': claim_data.get('veracity', "unknown")
                    },
                    'result': result
                }

            except Exception as e:
                logging.error(f"Error processing claim: {claim_data['claim']}")
                logging.error(f"Error details", exc_info=e)
                continue
        
        # Save results
        save_results(args, judge_prolific_id, all_judgement_data, runner)
        logging.info(f"Processed {len(all_judgement_data)} claims successfully.")

if __name__ == "__main__":
    main()