# agents/consultant.py
import json
import re
from typing import Dict, List, Tuple
from .base_agent import BaseAgent
from utils.helper import format_message, extract_content
from utils.config import load_prompts

class Consultant(BaseAgent):
    """Consultant agent implementation."""
    def __init__(self, client, config: Dict, name: str, prompt_dir: str = "config/default-prompt", 
            mode: str = "consultancy", personalization: bool = False):
        super().__init__(client, config)
        self.name = name
        self.context = {}
        
        # Determine correct prompt path based on personalization flag
        if personalization:
            prompt_path = "config/consultant-prompt-personalization/consultant_personalization_prompts.yaml"
        else:
            prompt_path = "config/default-prompt/consultant_prompts.yaml"
                
        try:
            loaded_prompts = load_prompts(prompt_dir, mode="consultancy")   
            self.prompts = loaded_prompts["prompts"]
        except Exception as e:
            print(f"Error loading consultant prompts: {str(e)}")
            raise

    def setup_context(self, context: Dict):
        """Setup consultant context."""
        self.context = {
            "NAME": context["NAME"],
            "STATEMENT": context["STATEMENT"],  # Changed from lowercase
            "ANSWER_A": context["ANSWER_A"],
            "ANSWER_B": context["ANSWER_B"],
            "ANSWER_DEFENDING": context["ANSWER_DEFENDING"],
            "ANSWER_OPPOSING": context["ANSWER_OPPOSING"],
            "ANSWER_DEFENDING_LETTER": context["ANSWER_DEFENDING_LETTER"],
            "ANSWER_OPPOSING_LETTER": context["ANSWER_OPPOSING_LETTER"],
            "CONTENT": context["CONTENT"],
            "WORD_LIMIT": context["WORD_LIMIT"],
            "judge_profile": context.get("profile", "")  # Add judge profile

        }
    def get_response(self, round_num: int, transcript: List[Dict] = None) -> str:
        """Get consultant's response for given round."""
        if round_num == 1:
            messages = self._format_first_round()
        else:
            messages = self._format_nth_round(round_num, transcript)
            
        response = self.call_api(messages, self.config["temperature"])
        return response
    
    def _format_message_with_profile(self, template: str, context: Dict) -> str:
        """Format message with special handling for profile sections."""
        try:
            # First replace the profile section if it exists
            if "<judge_profile>" in template and "</judge_profile>" in template:
                # Replace the entire profile section with the actual profile
                profile_pattern = r"<judge_profile>\s*<profile>\s*</profile>\s*</judge_profile>"
                template = re.sub(profile_pattern, context.get("judge_profile", ""), template)
            
            # Then handle all other replacements
            for key, value in context.items():
                template = template.replace(f"<{key}>", str(value))
                
            return template
        except Exception as e:
            print(f"Error in _format_message_with_profile: {str(e)}")
            print(f"Template: {template}")
            print(f"Context: {context}")
            return template
    
    def _format_first_round(self) -> List[Dict]:
        """Format messages for first round using prompt template."""
        formatted_messages = []
        
        # Get first round messages template
        first_round_messages = self.prompts["first_round_messages"]
        # Format each message with special handling for profile
        for message_template in first_round_messages:
            content = self._format_message_with_profile(
                message_template["content"], 
                self.context
            )
            formatted_messages.append({
                "role": message_template["role"],
                "content": content
            })
        
        return formatted_messages

    def _format_nth_round(self, round_num: int, transcript: List[Dict]) -> List[Dict]:
        """Format messages for subsequent rounds."""
        # Format transcript first
        transcript_text = self._format_transcript(transcript)
        
        # Format new round prompt
        nth_round_template = self.prompts["nth_round_messages"][0]["content"]
        formatted_content = format_message(nth_round_template, {
            **self.context,
            "previous_rounds_transcript": transcript_text,
            "round_number": round_num
        })
        
        if round_num == 2:
            messages = [
                *self._format_first_round(),
                {"role": "assistant", "content": transcript[-1]["consultant_response"]},
                {"role": "user", "content": formatted_content}
            ]
        else:
            with open(self.message_dir.parent / f"round_{round_num-1}_{self.name}_messages.json", 'r') as f:
                prev_messages = json.load(f)["messages"]
                
            messages = [
                *prev_messages,
                {"role": "assistant", "content": transcript[-1]["consultant_response"]},
                {"role": "user", "content": formatted_content}
            ]
        
        return messages

    def _format_transcript(self, rounds: List[Dict]) -> str:
        """Format consultancy transcript from previous rounds."""
        transcript_parts = []
        
        for round_data in rounds:
            round_text = f"""Round {round_data['round']}
-----------------------------
Consultant: 
{round_data['consultant_response']}

Judge: 
{round_data.get('judge_response', '')}
-----------------------------"""
            transcript_parts.append(round_text)
            
        return "\n\n".join(transcript_parts)