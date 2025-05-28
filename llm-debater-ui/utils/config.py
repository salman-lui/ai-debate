# utils/config.py
import yaml
from pathlib import Path
from typing import Dict

def load_config(config_path: str = "config/config.yaml") -> Dict:
    """Load configuration from YAML file."""
    with open(config_path) as f:
        return yaml.safe_load(f)

def load_prompts(prompt_dir: str, mode: str = "debate") -> Dict:
    """Load prompts from yaml files."""
    prompts_dir = Path(prompt_dir)
    prompts = {}
    
    print(f"Loading prompts from directory: {prompts_dir}")  # Debug print
    
    # Determine which prompts file to use
    if "debater-prompt-personalization" in str(prompts_dir):
        prompt_file = "debater_personalization_prompts.yaml"
        print(f"Using personalization prompt: {prompt_file}")  # Debug print
    elif "consultant-prompt-personalization" in str(prompts_dir):
        prompt_file = "consultant_personalization_prompts.yaml"
        print(f"Using consultant prompt: {prompt_file}")  # Debug print
    else:
        # Default prompts
        if mode == "consultancy":
            prompt_file = "consultant_prompts.yaml"
        else:
            prompt_file = "debater_prompts_final_browsing.yaml"
        prompt_path = prompts_dir / prompt_file
        print(f"Using default prompt: {prompt_file}")  # Debug print
        print(f"Full prompt path: {prompt_path}")  # Debug print
    
    try:
        with open(prompts_dir / prompt_file) as f:
            prompts.update(yaml.safe_load(f))
            print(f"Successfully loaded prompts from: {prompt_file}")  # Debug print
        return prompts
    except Exception as e:
        print(f"Error loading prompts: {str(e)}")
        raise
    