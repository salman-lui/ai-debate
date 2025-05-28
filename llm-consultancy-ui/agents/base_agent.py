from abc import ABC
import json
from typing import Dict, List, Optional, Union, Tuple
from time import sleep
from random import uniform
import os
import aisuite as ai
import requests
import google.auth
import google.auth.transport.requests
from openai import OpenAI
from colorama import Fore, Style
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

class APICallError(Exception):
    """Custom exception for API call failures"""
    pass

class BaseAgent:
    """Universal base agent for handling different LLM APIs.
    
    Configuration structure:
    {
        "provider": "openai|google|anthropic|sglang|ollama",  # Required: API provider
        "model": "model-name",                                # Required: Model identifier
        "temperature": 0.7,                                   # Required: Temperature for sampling
        "max_retries": 3,                                     # Optional: Number of retries (default: 3)
        
        # Provider-specific configurations
        "project_id": "your-project",           # Required for Google
        "location": "us-central1",              # Required for Google
        "port": 30000,                          # Required for SGLang
        "base_url": "http://localhost:11434",   # Required for Ollama
        "api_key": "ollama",                    # Required for Ollama
        "response_format": {"type": "json_object"}  # Optional: For JSON responses (only for openai models) Make sure you include the word json in some form in the message
    }
    
    Usage:
        agent = BaseAgent(config)
        response = agent.call_api(messages, temperature=0.7)
        # Or with message inspection:
        response, messages = agent.call_api(messages, temperature=0.7, return_messages=True)
        # For JSON response (openai only):
        response = agent.call_api(messages, temperature=0.7, response_format={"type": "json_object"})
    """
    
    def __init__(self, config: Dict):
        """Initialize base agent with provider-specific setup."""
        self.config = config
        self.provider = config['provider']
        self.max_retries = config.get('max_retries', 3)

        # Initialize client
        try:
            if self.provider == 'openai':
                if any(f'o{i}' in config['model'] for i in range(1, 6)):  # handles o1, o2, o3, o4, o5
                    self.client = OpenAI()
                    self.model = config['model']
                else:
                    self.client = ai.Client()
                    self.model = f"{self.provider}:{config['model']}"
            elif self.provider == 'azure':
                self.client = ChatCompletionsClient(
                    endpoint=config['endpoint'],
                    credential=AzureKeyCredential(os.getenv("AZURE_INFERENCE_CREDENTIAL", ''))
                )
                self.model = config['model']
            elif self.provider == 'google':
                if 'meta' in config['model']:
                    self.project_id = config['project_id']
                    self.location = config['location']
                    self.model = config['model']
                else:
                    os.environ['GOOGLE_PROJECT_ID'] = config['project_id']
                    os.environ['GOOGLE_REGION'] = config['location']
                    self.client = ai.Client()
                    self.model = f"{self.provider}:{config['model']}"
            elif self.provider == 'sglang':
                # Initialize SGLang using OpenAI client
                self.client = OpenAI(
                    base_url=f"http://localhost:{config.get('port', 30000)}/v1",
                    api_key="None"  # SGLang doesn't require an API key
                )
                self.model = config['model']
            else:
                # For all other providers
                self.client = ai.Client()
                self.model = f"{self.provider}:{config['model']}"
                
        except Exception as e:
            raise APICallError(f"Error initializing {self.provider} client: {str(e)}")

    def call_api(self, messages: List[Dict], temperature: float, response_format: Optional[Dict] = None, return_messages: bool = False) -> Union[str, Tuple[str, List[Dict]]]:
        """Universal API call handler with retries.
        
        Args:
            messages: List of message dictionaries
            temperature: Float value for temperature
            response_format: Optional response format specifications
            return_messages: If True, returns tuple of (response, messages)
        
        Returns:
            Either string response or tuple of (response, messages) if return_messages=True
        """
        print(f'{Fore.GREEN}Model is {self.model}, temperature is {temperature}{Style.RESET_ALL}')
        
        # Provider-specific configurations
        provider_configs = {
            'google': {'base_delay': 1, 'retry_delay': 3, 'jitter': 2},
            'openai': {'base_delay': 1, 'retry_delay': 3, 'jitter': 1},
            'anthropic': {'base_delay': 1, 'retry_delay': 2, 'jitter': 1},
            'ollama': {'base_delay': 0, 'retry_delay': 0, 'jitter': 0},
            'sglang': {'base_delay': 0, 'retry_delay': 1, 'jitter': 0.5},
            'azure': {'base_delay': 1, 'retry_delay': 2, 'jitter': 1}  # Add Azure configuration
        }
        
        config = provider_configs[self.provider]

        # print(json.dumps(messages, indent=2, ensure_ascii=False))
        # breakpoint()
        
        for attempt in range(self.max_retries):
            try:
                # Add retry delay if needed
                if attempt > 0:
                    delay = config['retry_delay'] * attempt + uniform(0, config['jitter'])
                    print(f"\nRetry attempt {attempt + 1}/{self.max_retries}. Waiting {delay:.2f}s...")
                    sleep(delay)

                # Get response based on provider
                if self.provider == 'openai':
                    if any(f'o{i}' in self.model for i in range(1, 6)):  # handles o1, o2, o3, o4, o5
                        response = self._call_openai_o1_model(messages)
                    else:
                        api_params = {
                            "model": self.model,
                            "messages": messages,
                            "temperature": temperature
                        }
                        if response_format:
                            api_params["response_format"] = response_format
                        response = self.client.chat.completions.create(**api_params)
                        response = response.choices[0].message.content
                elif self.provider == 'azure':
                    payload = {
                        "messages": messages
                    }
                    response = self.client.complete(payload)
                    response = response.choices[0].message.content
                elif self.provider == 'google' and 'meta' in self.model:
                    response = self._call_google_meta_api(messages, temperature)
                elif self.provider == 'sglang':
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=2048
                    )
                    response = response.choices[0].message.content
                else:
                    api_params = {
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature
                    }
                    if response_format:
                        api_params["response_format"] = response_format
                        
                    response = self.client.chat.completions.create(**api_params)
                    response = response.choices[0].message.content

                # Return based on return_messages flag
                return (response, messages) if return_messages else response

            except Exception as e:
                error_msg = str(e)
                if hasattr(e, 'response'):
                    error_msg = f"Error code: {e.status_code} - {error_msg} - Response: {e.response}"
                
                print(f"\nAPI call failed for {self.provider} (Attempt {attempt + 1}/{self.max_retries})")
                print(f"Error: {error_msg}")
                
                if attempt == self.max_retries - 1:
                    raise APICallError(f"Failed to get response from {self.provider}: {error_msg}")
                continue

    def _call_google_meta_api(self, messages: List[Dict], temperature: float) -> str:
        """Handle Google-hosted Meta models."""
        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        
        response = requests.post(
            f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/endpoints/openapi/chat/completions",
            headers={
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
        )
        
        if response.status_code != 200:
            raise APICallError(f"Error {response.status_code}: {response.text}")
        return response.json()['choices'][0]['message']['content']

    def _call_openai_o1_model(self, messages: List[Dict]) -> str:
        """Handle OpenAI o1 models which only accept user messages."""
        # Warning about message handling
        print("\nWarning: OpenAI o1 model only accepts user messages. System messages will be ignored.")
        
        # Format message for o1 model
        formatted_messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": messages[-1]['content']  # Just take the last user message
                }
            ]
        }]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages
        )
        return response.choices[0].message.content

def main():
    """Test different model configurations."""
    test_configs = [
        # OpenAI standard config
        {
            "provider": "openai",
            "model": "gpt-4o",
            "max_retries": 3,
            "temperature": 0
            #"response_format": {"type": "json_object"}  # Correct format as a dictionary if json response is needed (only for openai models) Make sure you include the word json in some form in the message. 
        },
        # Azure DeepSeek config
        {
            "provider": "azure",
            "model": "DeepSeek-R1",
            "endpoint": "https://DeepSeek-R1-rgchv.eastus.models.ai.azure.com",
            "max_retries": 3,
            "temperature": 0
        },
        # SGLang config
        {
            "provider": "sglang",
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "port": 30000,
            "max_retries": 3,
            "temperature": 0
        },
        # OpenAI preview model config
        {
            "provider": "openai",
            "model": "o1-preview",
            "max_retries": 3,
            "temperature": 0
        },
        # Google standard config
        {
            "provider": "google",
            "model": "gemini-1.5-pro-002",
            "project_id": "mars-lab-429920",
            "location": "us-central1",
            "max_retries": 3,
            "temperature": 0
        }, 
        # Google-hosted Meta model config
        {
            "provider": "google",
            "model": "meta/llama-3.1-405b-instruct-maas",
            "project_id": "mars-lab-429920",
            "location": "us-central1",
            "max_retries": 3,
            "temperature": 0
        },
        # SGLang config
        {
            "provider": "sglang",
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "port": 30000,
            "max_retries": 3,
            "temperature": 0
        },
        # Ollama config
        {
            "provider": "ollama",
            "model": "llama3.1:latest",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
            "max_retries": 3,
            "temperature": 0
        },
        # Anthropic config
        {
            "provider": "anthropic",
            "model": "claude-3-sonnet-20240229",
            "max_retries": 3,
            "temperature": 0
        }
    ]

    # Test message for all models
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]

    for config in test_configs:
        print("\n" + "="*50)
        print(f"Testing {config['provider']} with model {config['model']}")
        print("="*50)
        
        try:
            agent = BaseAgent(config)
            # Test with message inspection
            response, messages = agent.call_api(
                messages=test_messages,
                temperature=config['temperature'],
                #response_format=config.get('response_format'),  # Pass response_format from config
                return_messages=True
            )
            print(f"\nMessages sent: {messages}")
            print(f"\nResponse: {response}")
            print("\nTest completed successfully!")
            
        except Exception as e:
            print(f"Error testing configuration: {str(e)}")
        
        print("-"*50)
    breakpoint()

if __name__ == "__main__":
    main()