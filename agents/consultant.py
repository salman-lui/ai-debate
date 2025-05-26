from typing import Dict
import yaml
import json
from agents.base_agent import BaseAgent

class Consultant(BaseAgent):
    """Consultant agent that argues for a position in a structured debate."""
    
    def __init__(self, config: Dict, context: Dict):
        """Initialize consultant with config and context."""
        super().__init__(config)
        self.name = config.get('name', 'Consultant')
        self.context = context
        self.messages = []
        self._load_prompt_templates()

    def _format_prompt(self, prompt: str) -> str:
        """Format prompt with context variables."""
        return prompt.format(**self.context)

    def _load_prompt_templates(self) -> None:
        """Load prompt templates from YAML file."""
        with open(self.config['prompt_path'], 'r') as file:
            prompts = yaml.safe_load(file)['prompts']
            first_round = prompts['first_round_messages']
            
            self.prompts = {
                'first_round': {
                    'system': first_round[0]['content'],
                    'user1': first_round[1]['content'],
                    'assistant': first_round[2]['content'],
                    'user2': first_round[3]['content']
                },
                'nth_round': prompts['nth_round_messages'][0]['content']
            }

    def get_response(self, round_num: int) -> str:
        """Get consultant's response for the specified round."""
        self._prepare_messages(round_num)
        response = self.call_api(
            messages=self.messages,
            temperature=self.config['temperature']
        )
        self.messages.append({"role": "assistant", "content": response})
        return response
    
    def _prepare_messages(self, round_num: int) -> None:
        """Prepare messages for the current round."""
        if round_num == 1:
            self.messages = [
                {"role": "system", "content": self._format_prompt(self.prompts['first_round']['system'])},
                {"role": "user", "content": self._format_prompt(self.prompts['first_round']['user1'])},
                {"role": "assistant", "content": self._format_prompt(self.prompts['first_round']['assistant'])},
                {"role": "user", "content": self._format_prompt(self.prompts['first_round']['user2'])}
            ]
        else:
            self.messages.append({
                "role": "user", 
                "content": self._format_prompt(self.prompts['nth_round'])
            })

