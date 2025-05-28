from pathlib import Path
import sys
import json
import random
from typing import Dict
from dotenv import load_dotenv
load_dotenv()

# Use absolute path based on the file location
CURRENT_DIR = Path(__file__).parent

def load_claim_data(prolific_id: str):
    """Load a claim from the COVID dataset with usage tracking."""
    print(f"Prolific ID: {prolific_id}")
    if prolific_id is None or prolific_id == "":
        print("Prolific ID is None, using default claim")
        prolific_id = "default"
    
    DATA_PATH = CURRENT_DIR / f"data/60-full-batch-2/{prolific_id}_covid.json"
    print(f"Loading claim data from: {DATA_PATH}")
    try:
        with open(DATA_PATH, 'r', encoding='utf-8-sig') as f:
            claims = json.loads(f.read().strip())
    except FileNotFoundError:
        print(f"File not found: {DATA_PATH}")
        print(f"Current working directory: {Path.cwd()}")
        print(f"Files in current directory: {list(Path.cwd().iterdir())}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {DATA_PATH}")
        sys.exit(1)
    
    # Initialize or load tracking file
    tracking_path = CURRENT_DIR / f"data/60-full-batch-2/{prolific_id}_claim_counter.json"
    try:
        with open(tracking_path, 'r') as f:
            usage_data = json.load(f)
    except FileNotFoundError:
        usage_data = {str(i): 0 for i in range(len(claims))}
        with open(tracking_path, 'w') as f:
            json.dump(usage_data, f)
    
    # Find claim with minimum usage
    min_usage = min(usage_data.values())
    min_usage_indices = [i for i, count in usage_data.items() 
                        if count == min_usage]
    
    # Select random claim from those with minimum usage
    selected_idx = random.choice(min_usage_indices)
    usage_data[selected_idx] = usage_data[selected_idx] + 1
    
    # Save updated usage data
    with open(tracking_path, 'w') as f:
        json.dump(usage_data, f)
    
    return claims[int(selected_idx)], selected_idx, DATA_PATH, tracking_path

def format_sources(sources_list):
    """Format a list of source dictionaries into a string."""
    if not sources_list:
        raise ValueError("Sources are required for browsing setup but none were provided!")
        
    # Randomize the order of sources
    randomized_sources = sources_list.copy()
    random.shuffle(randomized_sources)
        
    formatted = []
    for source in randomized_sources:
        if isinstance(source, dict) and all(key in source for key in ['title', 'url', 'content']):
            formatted.append(
                f"Title: {source['title']}\n"
                f"URL: {source['url']}\n"
                f"Content: {source['content']}"
            )
    
    if not formatted:
        raise ValueError("No valid sources found! Each source must have 'title', 'url', and 'content'")
        
    return "\n\n".join(formatted)
