# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from openai import OpenAI
from datetime import datetime
import json
from utils.helper import save_transcript

class BaseAgent(ABC):
    """Base class for all debate agents."""
    
    def __init__(self, client: OpenAI, config: Dict):
        """
        Initialize base agent.
        
        Args:
            client: OpenAI client
            config: Agent configuration
        """
        self.client = client
        self.config = config
        self.messages = []
        self.message_dir = None 

    def call_api(self, messages: List[Dict], temperature: float) -> str:
        """Make API call with error handling."""
        try:
            # Save messages before making API call
            if self.message_dir:
                save_transcript(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "agent_type": self.__class__.__name__,  # Add agent type
                        "messages": messages,
                        "temperature": temperature
                    },
                    self.message_dir
                )
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                temperature=temperature
            )
            # print(f'Debug Prompt Message: {messages}')
            print(json.dumps(messages, indent=2, ensure_ascii=False))
            return response.choices[0].message.content
        except Exception as e:
            print(f"API call failed: {str(e)}")
            raise
            
    @abstractmethod
    def get_response(self, *args, **kwargs):
        """Get response from agent."""
        pass