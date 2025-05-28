from gcp_storage import CloudStorageInterface
from datetime import datetime

class DebateState:
    """Encapsulates all session-specific state for a debate."""
    
    def __init__(self):
        self.current_round = 1
        self.debate_started = False
        self.transcript = []
        self._formatted_header = None
        self.round_tabs = {
            1: "round1",
            2: "round2",
            3: "round3"
        }
        self.selected_choice = None
        self.MIN_FEEDBACK_LENGTH = 50
        self.MIN_REASONING_LENGTH = 50
        self.terms_accepted = False
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.llm_experience_level = None
        self.debate_transcript = {
            "session_id": self.session_id,
            "debate_topic": None,
            "initial_judgment": {
                "decision": None,
                "confidence_level": None
            },
            "rounds": [],
            "final_decision": None,
            "confidence_level": None,
            "reasoning": None,
            "llm_experience_level": None,
            "metadata": {
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "access_url": None
            }
        }
        self.storage = CloudStorageInterface()
        self.selected_confidence = None
        self.debate_manager = None
        self.prolific_id = None
        self.initial_choice = None
        self.initial_confidence = None
    
    def save_current_state(self):
        """Save the current state of the debate transcript."""
        try:
            filename = f"debate_{self.debate_transcript['session_id']}_transcript.json"
            base_path = f"web_debate_{self.debate_transcript['session_id']}"
            self.storage.set_base_path(base_path)
            self.storage.save_transcript(self.debate_transcript, f"transcript/{filename}")
            print(f"Successfully saved transcript to GCP bucket")
        except Exception as e:
            print(f"Error saving transcript: {str(e)}")
        return self
