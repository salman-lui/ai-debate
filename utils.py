from dataclasses import dataclass
from typing import Dict, Any, Callable, Optional, List
import json
import re
import random

@dataclass
class PlaceholderSource:
    """A container for defining how to get and when to use a placeholder value."""
    getter: Callable
    description: str
    condition: Optional[Callable] = None

def format_sources(sources_list):
    """Format a list of source dictionaries into a string."""
    if not sources_list:
        raise ValueError("Sources are required for browsing setup but none were provided!")
        
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
        raise ValueError("No valid sources found! Each source must have 'title', 'url', and 'content'")
        
    return "\n\n".join(formatted)

def load_persona(prolific_id: str):
    with open('./personas/all_personas.json', 'r') as file:
        personas = json.load(file)
        return personas[prolific_id]

class PlaceholderManager:
    """Manages dynamic values that get inserted into prompt templates."""
    
    SETTINGS_KEYS = {
        'debate': 'debater_settings',
        'consultancy': 'consultant_settings'
    }
    
    def __init__(self, config: Dict, agent_type: str, mode: str, claim: str = None, sources: List[Dict] = None):
        """Initialize the placeholder manager."""
        self.config = config
        self.agent_type = agent_type
        self.mode = mode
        self._judge_prolific_id = config.get('judge_prolific_id')
        self.claim = claim
        self._raw_sources = sources  # Store sources in a separate variable
        self.context = {}
        self._define_sources()

    def _define_sources(self) -> None:
        """Define placeholder sources based on mode."""
        settings_key = self.SETTINGS_KEYS[self.mode]
        
        # Base sources common to both modes
        self.placeholder_sources = {
            'WORD_LIMIT': PlaceholderSource(
                getter=lambda: self.config[settings_key]['word_limit'],
                description=f"Word limit for {self.mode} responses"
            ),
            'CLAIM': PlaceholderSource(
                getter=lambda: self.claim,
                description="Claim being evaluated"
            ),
            # 'REFERENCE_SOURCES': PlaceholderSource(
            #     getter=lambda: """
            #         Title: Ultraviolet Light Associated With Low COVID-19 Growth - Indiatimes.com
            #         URL: https://www.indiatimes.com/trending/social-relevance/ultraviolet-covid-19-growth-525230.html
            #         Content: High Levels Of Ultraviolet Light 'Most Strongly' Associated With Reduced COVID-19 Growth: Study High levels of ultraviolent light is "most strongly" associated with reduced Covid-19 growth, says a new study where scientists looked at statistical models of the link between weather and the maximum growth rate of the virus globally.
            #         Title: Global evidence for ultraviolet radiation decreasing COVID-19 growth rates
            #         URL: https://www.pnas.org/doi/10.1073/pnas.2012370118
            #         Content: We find that ultraviolet (UV) radiation has a statistically significant effect on daily COVID-19 growth rates: a SD increase in UV lowers the daily growth rate of COVID-19 cases by ∼ 1 percentage point over the subsequent 2.5 wk, relative to an average in-sample growth rate of 13.2%. The time pattern of lagged effects peaks 9 to 11 d after UV
            #         """,
            #     description="Information from browsing",
            #     condition=lambda: 'browsing' in self.agent_type
            # ),
            'ROUND_THINKING_ADVICE': PlaceholderSource(
                getter=lambda: self.config.get('thinking_advice', {}),
                description="Round-specific thinking advice",
                condition=lambda: self.mode == 'debate'
            ),
            'REFERENCE_SOURCES': PlaceholderSource(
                getter=lambda: format_sources(self._raw_sources) if self._raw_sources else "",
                description="Information from sources",
                condition=lambda: 'browsing' in self.agent_type
            ),
            'PERSONA_DESC': PlaceholderSource(
                getter=lambda: load_persona(self._judge_prolific_id)['description'],
                description="Judge's persona info, third person",
                condition=lambda: self._judge_prolific_id is not None
            ),
            'PERSONA_DIR': PlaceholderSource(
                getter=lambda: load_persona(self._judge_prolific_id)['directions'],
                description="Judge's persona info, as directions",
                condition=lambda: self._judge_prolific_id is not None
            )
        }
        
        # Add consultancy-specific sources
        if self.mode == 'consultancy':
            # Get the veracity from config (set from JSON data)
            claim_veracity = self.config.get('claim_veracity')
            argue_for_setting = self.config.get('argue_for')  # "correct" or "incorrect"
            
            # Convert to proper True/False string
            def get_position():
                should_argue = claim_veracity if argue_for_setting == "correct" else not claim_veracity
                return str(should_argue).capitalize()
            
            self.placeholder_sources.update({
                'ANSWER_DEFENDING': PlaceholderSource(
                    getter=get_position,
                    description="Position being defended"
                ),
                'ANSWER_OPPOSING': PlaceholderSource(
                    getter=lambda: "True" if get_position() == "False" else "False",
                    description="Position being opposed"
                )
            })

        # Add debate-specific sources
        if self.mode == 'debate':
            claim_veracity = self.config.get('claim_veracity')
            argue_for_setting = self.config.get('argue_for_debater_a')
            
            def get_position():
                should_argue = claim_veracity if argue_for_setting == "correct" else not claim_veracity
                return str(should_argue).capitalize()
            
            self.placeholder_sources.update({
                'ANSWER_DEFENDING': PlaceholderSource(
                    getter=get_position,
                    description="Position being defended"
                ),
                'ANSWER_OPPOSING': PlaceholderSource(
                    getter=lambda: "True" if get_position() == "False" else "False",
                    description="Position being opposed"
                )
            })

    def get_context(self) -> Dict[str, Any]:
        """Get all placeholder values that should be included in prompts."""
        context = {}
        for key, source in self.placeholder_sources.items():
            if source.condition and not source.condition():
                continue
            value = source.getter()
            if value is not None:
                context[key] = value
        return context

def extract_content(response: str, tag_name: str) -> str:
    """Extract content from response with flexible tag handling."""
    # Try exact match first
    match = re.search(f'<{tag_name}>(.*?)</{tag_name}>', response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # If no exact match, try finding content between tag and end of text
    match = re.search(f'<{tag_name}>(.*)', response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # If still no match, try finding content after thinking section
    match = re.search(r'</thinking>(.*)', response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # If all else fails, return the original response
    return response.strip()

def format_transcript(round_num: int, response: str) -> str:
    """Format response transcript with round number."""
    return f"<round_{round_num}>\n{response}\n</round_{round_num}>"
