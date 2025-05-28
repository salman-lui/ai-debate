# utils/helpers.py
import json
import re
from pathlib import Path
from typing import Dict, List

def save_transcript(data: Dict, filepath: Path):
    """Save debate data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def format_message(template: str, context: Dict) -> str:
    """Format message template with context variables."""
    try:
        formatted = template
        for key, value in context.items():
            # Handle both <KEY> and nested tag formats
            formatted = formatted.replace(f"<{key}>", str(value))
            
            # Special handling for persona tags
            if key == "profile":
                formatted = re.sub(
                    r"<persona_profile>\s*<profile>\s*</profile>\s*</persona_profile>",
                    str(value),
                    formatted
                )
                
        return formatted
    except Exception as e:
        print(f"Error in format_message: {str(e)}")
        print(f"Template: {template}")
        print(f"Context: {context}")
        return template


def extract_content(response: str, tag: str) -> str:
    """Extract content between XML-style tags."""
    # First try exact match with both opening and closing tags
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # If no exact match, try finding content after opening tag
    pattern = f"<{tag}>(.*)"
    match = re.search(pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # If still no match, return original response
    return response