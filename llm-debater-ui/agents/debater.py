# agents/debater.py
from cmath import e
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Tuple
from agents.base_agent import BaseAgent
from utils.helper import format_message, extract_content
from utils.config import load_prompts
import random

class Debater(BaseAgent):
    def __init__(self, client, config: Dict, name: str, position: str, prompt_dir: str = "config/default-prompt", personalization: bool = False):
        super().__init__(client, config)
        self.name = name
        self.position = position
        self.context = {}
        
        # Load prompts based on whether personalization is enabled
        if personalization:
            try:
                prompt_path = Path("config/debater-prompt-personalization/debater_personalization_prompts.yaml")                
                if not prompt_path.exists():
                    prompt_path = Path(prompt_dir) / "debater_prompts_final_browsing.yaml"
                    
                if not prompt_path.exists():
                    raise FileNotFoundError(f"Neither personalization nor default prompts found")
                    
                with open(prompt_path, 'r') as f:
                    loaded_prompts = yaml.safe_load(f)
                    self.prompts = loaded_prompts["prompts"]                    
            except Exception as e:
                print(f"Error loading prompts: {str(e)}")
                raise
        else:
            # Regular non-personalized path
            prompt_path = Path(prompt_dir) / "debater_prompts_final_browsing.yaml"
            with open(prompt_path, 'r') as f:
                loaded_prompts = yaml.safe_load(f)
                self.prompts = loaded_prompts["prompts"]

    def _format_sources(self, sources_list):
        """Format a list of source dictionaries into a string."""
        if not sources_list:
            # print(f"DEBUG: sources_list is empty or None: {sources_list}")  # Add debug print
            return ""  # Return empty string instead of raising error
        
        # Check if sources_list is already a formatted string
        if isinstance(sources_list, str):
            # print(f"DEBUG: sources_list is already a string")  # Add debug print
            return sources_list
        
        # Randomize the order of sources
        randomized_sources = sources_list.copy()  # Create a copy to not modify original
        random.shuffle(randomized_sources)  # Shuffle the sources randomly
        
        formatted = []
        for source in randomized_sources:  # Use randomized sources
            if isinstance(source, dict) and all(key in source for key in ['title', 'url', 'content']):
                formatted.append(
                    f"Title: {source['title']}\n"
                    f"URL: {source['url']}\n"
                    f"Content: {source['content']}"
                )
        
        if not formatted:
            # print(f"DEBUG: No valid sources found in: {sources_list}")  # Add debug print
            return ""  # Return empty string instead of raising error
        
        return "\n\n".join(formatted)

    def setup_context(self, context: Dict):
        """Setup debate context with statement, answers, and content."""
        # Don't try to format if content is already a string
        reference_sources = context["content"] if isinstance(context["content"], str) else self._format_sources(context["content"])
        
        self.context = {
            "NAME": self.name,
            "OPPONENT_NAME": context["opponent_name"],
            "STATEMENT": context["statement"],
            "CLAIM": context["statement"],
            "ANSWER_DEFENDING": context["answer_defending"],
            "ANSWER_OPPOSING": context["answer_opposing"],
            "ANSWER_DEFENDING_LETTER": context["answer_defending_letter"],
            "ANSWER_OPPOSING_LETTER": context["answer_opposing_letter"],
            "ANSWER_A": context["answer_defending"] if self.position == "first" else context["answer_opposing"],
            "ANSWER_B": context["answer_opposing"] if self.position == "first" else context["answer_defending"],
            "CONTENT": context["content"],
            "REFERENCE_SOURCES": reference_sources,  # Use the sources directly
            "WORD_LIMIT": context["word_limit"],
            "judge_profile": context.get("profile", "")
        }

    def get_response(self, round_num: int, transcript: List[Dict] = None) -> str:
        """Get debater's response for given round."""
        if round_num == 1:
            messages = self._format_first_round()
        else:
            messages = self._format_nth_round(round_num, transcript)
            
        response = self.call_api(messages, self.config["temperature"])
        return response

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

    def _format_message_with_profile(self, template: str, context: Dict) -> str:
        """Format message with special handling for profile sections."""
        try:
            # First replace the profile section if it exists
            if "<judge_profile>" in template and "</judge_profile>" in template:
                profile_pattern = r"<judge_profile>\s*<profile>\s*</profile>\s*</judge_profile>"
                template = re.sub(profile_pattern, context.get("judge_profile", ""), template)
            
            # Then handle all other replacements
            for key, value in context.items():
                # template = template.replace(f"<{key}>", str(value))  # For <NAME> format
                template = template.replace(f"{{{key}}}", str(value))  # For {NAME} format
            
            return template
        except Exception as e:
            print(f"Error in _format_message_with_profile: {str(e)}")
            print(f"Template: {template}")
            print(f"Context: {context}")
            return template

    def _format_nth_round(self, round_num: int, transcript: List[Dict]) -> List[Dict]:
        """Format messages for subsequent rounds."""
        # Add debug prints for CLAIM and ANSWER_DEFENDING
        # print(f"\nDEBUG nth round - Context values:")
        print(f"CLAIM: {self.context.get('CLAIM')}")
        print(f"STATEMENT: {self.context.get('STATEMENT')}")
        print(f"ANSWER_DEFENDING: {self.context.get('ANSWER_DEFENDING')}")
        
        # Load thinking advice from YAML for rounds 2 and 3
        thinking_advice = ""
        try:
            # Load the full YAML file to get thinking_advice
            prompt_path = Path("config/default-prompt/debater_prompts_final_browsing.yaml")
            with open(prompt_path, 'r') as f:
                full_yaml = yaml.safe_load(f)
                if round_num == 2:
                    advice = full_yaml.get("thinking_advice", {}).get("second_round", [])
                    thinking_advice = "\n".join(f"{i+1}. {step}" for i, step in enumerate(advice))
                elif round_num == 3:
                    advice = full_yaml.get("thinking_advice", {}).get("third_round", [])
                    thinking_advice = "\n".join(f"{i+1}. {step}" for i, step in enumerate(advice))
        except Exception as e:
            print(f"DEBUG: Error loading thinking advice: {str(e)}")
        
        # Get previous round's messages from transcript
        prev_round = transcript[-1]  
        prev_response = prev_round["raw_debater_response"] if self.position == "first" else prev_round["raw_opponent_response"]
        
        # Format transcript first
        transcript_text = self._format_transcript(transcript)
        
        # Format new round prompt
        nth_round_template = self.prompts["nth_round_messages"][0]["content"]
        
        context_dict = {
            **self.context,  # This should include CLAIM and ANSWER_DEFENDING
            "previous_rounds_transcript_debate": transcript_text,
            "round_number": round_num,
            "NAME_A": self.name if self.position == "first" else self.context["OPPONENT_NAME"],
            "NAME_B": self.context["OPPONENT_NAME"] if self.position == "first" else self.name,
            "ROUND_THINKING_ADVICE": thinking_advice  # Add thinking advice to context
        }
        
        # Debug print to see EVERYTHING in context_dict
        # print("\nDEBUG: Full context_dict contents:")
        for key, value in context_dict.items():
            print(f"{key}: {value}")
        
        # Also print the type of each value
        # print("\nDEBUG: Value types in context_dict:")
        for key, value in context_dict.items():
            print(f"{key}: {type(value)}")
        
        # Debug print the final context being used for formatting
        # print(f"\nDEBUG nth round - Final context keys: {list(context_dict.keys())}")
        # print(f"DEBUG nth round - CLAIM value in context: {context_dict.get('CLAIM')}")
        # print(f"DEBUG nth round - ANSWER_DEFENDING value in context: {context_dict.get('ANSWER_DEFENDING')}")
        
        formatted_content = nth_round_template
        for key, value in context_dict.items():
            placeholder = f"{{{key}}}"
            formatted_content = formatted_content.replace(placeholder, str(value))
        # print(f"DEBUG: Direct replacement result: {formatted_content}")
        
        if round_num == 2:
            messages = [
                *self._format_first_round(),
                {"role": "assistant", "content": prev_response},
                {"role": "user", "content": formatted_content}
            ]
        else:
            # Update path to include statement directory
            statement_dir = self.message_dir.parent
            prev_messages = statement_dir / f"round_{round_num-1}_{self.name}_messages.json"
            with open(prev_messages, 'r') as f:
                prev_round_messages = json.load(f)["messages"]
                
            messages = [
                *prev_round_messages,
                {"role": "assistant", "content": prev_response},
                {"role": "user", "content": formatted_content}
            ]
        
        return messages
    
    def _format_transcript(self, rounds: List[Dict]) -> str:
        """Format debate transcript from previous rounds."""
        transcript_parts = []
        
        for round_data in rounds:
            # Format debater's response
            debater_context = {
                "STATEMENT": self.context["STATEMENT"],
                "ANSWER_DEFENDING": self.context["ANSWER_DEFENDING"],
                "ANSWER_OPPOSING": self.context["ANSWER_OPPOSING"],
                "NAME_A": self.name if self.position == "first" else self.context["OPPONENT_NAME"],
                "NAME_B": self.context["OPPONENT_NAME"] if self.position == "first" else self.name
            }
            
            # Format opponent's response with swapped answers
            opponent_context = {
                "STATEMENT": self.context["STATEMENT"],
                "ANSWER_DEFENDING": self.context["ANSWER_OPPOSING"] if self.position == "first" else self.context["ANSWER_DEFENDING"],
                "ANSWER_OPPOSING": self.context["ANSWER_DEFENDING"] if self.position == "first" else self.context["ANSWER_OPPOSING"],
                "NAME_A": self.name if self.position == "first" else self.context["OPPONENT_NAME"],
                "NAME_B": self.context["OPPONENT_NAME"] if self.position == "first" else self.name
            }
            
            # Format judge's response
            judge_context = {
                "NAME_A": self.name if self.position == "first" else self.context["OPPONENT_NAME"],
                "NAME_B": self.context["OPPONENT_NAME"] if self.position == "first" else self.name
            }
            
            # Format each response
            debater_response = format_message(
                round_data['debater_response'] if self.position == 'first' else round_data['opponent_response'],
                debater_context
            )
            
            opponent_response = format_message(
                round_data['opponent_response'] if self.position == 'first' else round_data['debater_response'],
                opponent_context
            )
            
            judge_response = format_message(
                round_data.get('judge_response', ''),
                judge_context
            )
            # Extract only the questions part from judge's response
            judges_question_response = round_data.get('judge_feedback', '')  # Simply use judge_feedback directly
        
            # Format round template
            round_text = f"""Round {round_data['round']}
    -----------------------------
    {self.name}: 
    {debater_response}

    {self.context['OPPONENT_NAME']}: 
    {opponent_response}

    Judge: 
    {judges_question_response}
    -----------------------------"""
            
            transcript_parts.append(round_text)
        
        return "\n\n".join(transcript_parts)

    def _get_round_thinking_advice(self, round_num: int) -> str:
        """Get thinking advice for specific round from prompts."""
        # print(f"\nDEBUG: Getting thinking advice for round {round_num}")
        
        # Get thinking advice from prompts
        thinking_advice = self.prompts.get("thinking_advice", {})
        # print(f"DEBUG: Full thinking_advice from prompts: {thinking_advice}")
        
        # Get round-specific advice
        if round_num == 2:
            advice = thinking_advice.get("second_round", [])
            # print(f"DEBUG: Found second round advice: {advice}")
        elif round_num == 3:
            advice = thinking_advice.get("third_round", [])
            # print(f"DEBUG: Found third round advice: {advice}")
        else:
            # print(f"DEBUG: No advice found for round {round_num}")
            return ""
        
        # Format the advice as a numbered list
        formatted_advice = "\n".join(f"{i+1}. {step}" for i, step in enumerate(advice))
        # print(f"DEBUG: Formatted advice: {formatted_advice}")
        return formatted_advice