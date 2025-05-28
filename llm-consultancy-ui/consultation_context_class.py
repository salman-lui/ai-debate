import random
from typing import Dict, Optional
from helper_functions import load_claim_data, format_sources

class ConsultationContext:
    """Manages the consultation context and state."""
    def __init__(self, word_limit: int, prolific_id: str):
        self.claim_data, self.claim_index, self.data_path, self.tracking_path = load_claim_data(prolific_id)
        
        # Set claim from JSON
        self.statement = self.claim_data['claim']
        self.word_limit = word_limit
        
        # Randomly choose True or False for ANSWER_DEFENDING
        self.answer_defending = random.choice([True, False])
        
        # Combine and randomize sources
        all_sources = []
        if 'supporting_sources' in self.claim_data:
            all_sources.extend(self.claim_data['supporting_sources'])
        if 'opposing_sources' in self.claim_data:
            all_sources.extend(self.claim_data['opposing_sources'])
            
        # Randomize sources using format_sources
        self.formatted_sources = format_sources(all_sources)
        
        # Initialize transcript variables
        self.previous_rounds_transcript_consultant: Optional[str] = None
        self.previous_rounds_transcript_judge: Optional[str] = None
        self.round_number: int = 1

    def update_transcripts(self, round_num: int, consultant_msg: Optional[str] = None, judge_msg: Optional[str] = None):
        """Updates consultation transcripts with new messages."""
        if consultant_msg:
            self.previous_rounds_transcript_consultant = f"<round_{round_num}>\n{consultant_msg}\n</round_{round_num}>"
        if judge_msg:
            self.previous_rounds_transcript_judge = judge_msg
            self.round_number = round_num + 1

    def to_dict(self) -> Dict:
        """Converts context to dictionary format for the consultant."""
        return {
            "CLAIM": self.statement,
            "ANSWER_DEFENDING": str(self.answer_defending).capitalize(),
            "ANSWER_OPPOSING": str(not self.answer_defending).capitalize(),
            "REFERENCE_SOURCES": self.formatted_sources,
            "WORD_LIMIT": self.word_limit,
            "previous_rounds_transcript_consultant": self.previous_rounds_transcript_consultant,
            "previous_rounds_transcript_judge": self.previous_rounds_transcript_judge,
            "round_number": self.round_number
        }
 