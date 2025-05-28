from typing import Dict
import yaml
from agents.base_agent import BaseAgent

class Judge(BaseAgent):
    """Judge agent that evaluates arguments."""
    
    def __init__(self, config: Dict, context: Dict):
        """Initialize judge with config and context."""
        super().__init__(config)
        self.name = config.get('name', 'Judge')
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
            
            self.prompts = {
                'system': prompts['system']['messages'][0]['content'],
                'intermediate': prompts['intermediate']['messages'][0]['content'],
                'final': prompts['final']['messages'][0]['content']
            }

    def get_response(self, round_num: int) -> str:
        """Get judge's response for the specified round."""
        self._prepare_messages(round_num)
        response = self.call_api(
            messages=self.messages,
            temperature=self.config.get('temperature', 0)
        )
        self.messages.append({"role": "assistant", "content": response})
        return response
    
    def _prepare_messages(self, round_num: int) -> None:
        """Prepare messages for the current round."""
        if round_num == 1:
            self.messages = [
                {"role": "system", "content": self._format_prompt(self.prompts['system'])},
                {"role": "user", "content": self._format_prompt(self.prompts['intermediate'])}
            ]
        else:
            prompt = self.prompts['final'] if round_num == 3 else self.prompts['intermediate']
            self.messages.append({
                "role": "user", 
                "content": self._format_prompt(prompt)
            })
