# agents/judge.py
import json
import re
import yaml
from typing import Dict, List, Optional
from agents.base_agent import BaseAgent
from utils.helper import format_message, extract_content
from utils.config import load_prompts

class Judge(BaseAgent):
    def __init__(self, client, config: Dict, mode: str = "debate", persona: Optional[Dict] = None):
        super().__init__(client, config)
        self.mode = mode
        self.persona = persona

        # Load prompts based on mode and persona
        if persona:
            # For persona-based judging
            if mode == "debate":
                prompt_path = "config/role-play-prompt/debate_role_play_judge_prompts.yaml"
            else:  # consultancy mode
                prompt_path = "config/role-play-prompt/consultant_role_play_judge_prompts.yaml"
        else:
            # For regular judging
            if mode == "debate":
                prompt_path = "config/default-prompt/debate_judge_prompts.yaml"
            else:  # consultancy mode
                prompt_path = "config/default-prompt/consultant_judge_prompts.yaml"
        
        try:
            with open(prompt_path, 'r') as f:
                loaded_prompts = yaml.safe_load(f)
                self.prompts = loaded_prompts
        except Exception as e:
            print(f"Error loading prompts from {prompt_path}: {str(e)}")
            raise
    
    def setup_context(self, context: Dict):
        """Setup judge context."""
        # Base context that's always needed
        self.context = {
            "STATEMENT": context["statement"],
            "ANSWER_A": context["answer_a"],
            "ANSWER_B": context["answer_b"],
            "NAME_A": context["name_a"],
            "MAX_ROUNDS": context["max_rounds"]
        }

        # Check if we're in consultancy mode
        if "mode" in context and context["mode"] == "consultancy":
            self.mode = "consultancy"
            self.context.update({
                "MODE": "consultancy",
                "NAME_B": "None",  # Not used in consultancy mode
                "ARGUING_FOR": context.get("arguing_for", "correct")
            })
        else:
            # Debate mode settings
            self.mode = "debate"
            self.context.update({
                "MODE": "debate",
                "NAME_B": context["name_b"]  # Required for debate mode
            })
    def get_response(self, round_num: int, transcript: List[Dict]) -> str:
        """Get judge's response for current round."""
        messages = self._format_judge_messages(round_num, transcript)
        response = self.call_api(messages, self.config["temperature"])
        return response

    def extract_decision(self, response: str) -> str:
        """Extract the final decision from judge's response."""
        try:
            if self.mode == "consultancy":
                # Handle consultancy mode decisions
                lines = response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith("Decision:") or line.startswith("Final decision:"):
                        last_word = line.split()[-1].upper().rstrip('.')
                        if last_word in ["TRUE", "FALSE"]:
                            return last_word
            else:  # debate mode
                # Handle debate mode decisions using the same line-by-line approach
                lines = response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith("Decision:") or line.startswith("Final decision:"):
                        last_word = line.split()[-1].upper().rstrip('.')
                        if last_word in ["TRUE", "FALSE"]:
                            return last_word
                # Second attempt: Look for decision anywhere in response
                decision_pattern = r"Decision:.*?(TRUE|FALSE)"
                match = re.search(decision_pattern, response, re.IGNORECASE | re.DOTALL)
                if match:
                    return match.group(1).upper()

            return "UNCLEAR"
                
        except Exception as e:
            print(f"Error extracting decision: {str(e)}")
            print(f"Response was: {response}")
            return "ERROR"

    def _format_judge_messages(self, round_num: int, transcript: List[Dict]) -> List[Dict]:
        """Format messages for judge using prompt template."""
        # Determine if it's final round
        is_final = round_num == self.context["MAX_ROUNDS"]
        
        # Format transcript
        transcript_text = self._format_transcript(transcript)
        
        # Create message context
        message_context = {
            **self.context,
            "previous_rounds_transcript_debater": transcript_text
        }
        # Handle different prompt structures based on whether we have a persona
        if self.persona:
            message_context.update({
                "name_judge": self.persona["name_judge"],
                "profile": self.persona["profile"]
            })
            print(f"Debug Judge Messages: Using persona {self.persona['name_judge']}")

        
        # Get appropriate prompt template
        if is_final:
            template = self.prompts["prompts"]["final"]["messages"][0]["content"]
        else:
            template = self.prompts["prompts"]["intermediate"]["messages"][0]["content"]

        # Format complete message
        formatted_content = format_message(template, message_context)

        if round_num == 1:
            # For round 1, format system message with persona
            system_content = self.prompts["prompts"]["system"]["messages"][0]["content"]
            if self.persona:
                #system_content = format_message(system_content, message_context)
                system_content = format_message(system_content, {
                    "name_judge": self.persona["name_judge"],
                    "profile": self.persona["profile"]
                })
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": format_message(template, message_context)}
            ]
        else:
            # Update path to include statement directory
            statement_dir = self.message_dir.parent
            prev_messages = statement_dir / f"round_{round_num-1}_judge_messages.json"
            with open(prev_messages, 'r') as f:
                prev_round_data = json.load(f)
                prev_messages = prev_round_data["messages"]
                
            # Get the previous round's response from transcript
            prev_round = transcript[round_num - 2]  # -2 because round_num starts at 2
            prev_response = prev_round["raw_judge_response"]
            
            messages = [
                *prev_messages,  # Include all messages from previous round
                {"role": "assistant", "content": prev_response},  # Add judge's response from previous round
                {"role": "user", "content": format_message(template, message_context)}
            ]
        
        return messages

    def _format_transcript(self, rounds: List[Dict]) -> str:
        """Format transcript for judge."""
        transcript_parts = []
        
        for i, round_data in enumerate(rounds):
            if self.mode == "consultancy":
                # Format for consultancy mode
                consultant_argument = extract_content(round_data['consultant_response'], "argument")
                round_text = f"""Round {round_data['round']}
-----------------------------
{self.context['NAME_A']}: 
{consultant_argument}"""
            else:
                # Format for debate mode
                debater_argument = extract_content(round_data['debater_response'], "argument")
                opponent_argument = extract_content(round_data['opponent_response'], "argument")
                round_text = f"""Round {round_data['round']}
-----------------------------
{self.context['NAME_A']}: 
{debater_argument}

{self.context['NAME_B']}: 
{opponent_argument}"""

            # Add judge response for completed rounds
            if i < len(rounds) - 1 and "judge_response" in round_data:
                round_text += f"\n\nJudge: \n{round_data['judge_response']}"
                
            round_text += "\n-----------------------------"
            transcript_parts.append(round_text)
                
        return "\n\n".join(transcript_parts)