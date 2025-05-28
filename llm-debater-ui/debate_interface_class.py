import gradio as gr
from web_debate_manager import WebDebateManager
from gcp_storage import log_debug
from datetime import datetime
import re
from debate_state_class import DebateState

class DebateInterface:    
    def __init__(self):
        self.MIN_FEEDBACK_LENGTH = 50
        self.MIN_REASONING_LENGTH = 50
        
    def process_citations(self, text):
        """Process evidence tags in the text and format URLs and evidence."""
        # First extract and store all URLs
        url_pattern = r'<url>(.*?)</url>'
        urls = re.findall(url_pattern, text)
        
        # Replace evidence tags with colored spans
        def replace_evidence(match):
            evidence_text = match.group(1)
            return f'<span style="color: #16a34a; font-weight: 500;">{evidence_text}</span>'
        
        pattern = r'<v_evidence>(.*?)</v_evidence>'
        processed_text = re.sub(pattern, replace_evidence, text, flags=re.DOTALL)
        
        # Replace URL tags with numbered citations
        for i, url in enumerate(urls, 1):
            processed_text = processed_text.replace(f'<url>{url}</url>', f'[{i}]')
        
        # Add citations list at the end if there are any URLs
        if urls:
            processed_text += '<div class="citations-section">'
            processed_text += '<h4>Citations:</h4>'
            processed_text += '<ol class="citations-list">'
            for url in urls:
                processed_text += f'<li><a href="{url}" target="_blank">{url}</a></li>'
            processed_text += '</ol></div>'
        
        return processed_text
    
    def extract_and_process_argument(self, response, is_debater_a):
        """Extract and process argument content."""
        prefix = "<strong>Debater A:</strong> " if is_debater_a else "<strong>Debater B:</strong> "
        return prefix + self.process_citations(response)
    
    def create_completion_html(self, state: DebateState) -> str:
        """Creates HTML for the completion screen"""
        return f"""
            <div style='text-align: center; padding: 30px; background-color: #f0fdf4; border-radius: 12px; border: 2px solid #16a34a; margin: 20px 0;'>
                <h2 style='color: #15803d; margin-bottom: 15px;'>Debate Complete! 🎉</h2>
                <p style='font-size: 1.2em; margin-bottom: 15px;'>You have selected <strong>{state.selected_choice}</strong> as your answer.</p>
                <p style='font-size: 1.1em; margin-bottom: 15px;'>Confidence Level: <strong>{state.selected_confidence}/100</strong></p>
                <p style='margin-bottom: 20px;'>Thank you for participating in this debate! 🔨</p>
                <a href='https://app.prolific.com/submissions/complete?cc=C1DA3DDR' 
                target='_blank' 
                style='display: inline-block; 
                        background-color: #16a34a; 
                        color: white; 
                        padding: 15px 30px; 
                        border-radius: 8px; 
                        text-decoration: none; 
                        font-weight: bold; 
                        font-size: 1.1em;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        transition: background-color 0.3s ease;'>
                    Return to Prolific
                </a>
            </div>
            """
    
    def accept_terms(self, state: DebateState, request: gr.Request):
        """Accept terms and initialize debate manager"""
        state.terms_accepted = True
        state.debate_transcript["metadata"]["terms_accepted"] = True

        prolific_id = None
        if request and hasattr(request, 'query_params'):
            prolific_id = request.query_params.get('PROLIFIC_PID', None)
            if prolific_id:
                print(f"Found Prolific ID in request: {prolific_id}")
        
        # Initialize debate manager immediately after accepting terms
        state.debate_manager = WebDebateManager(
            config_path="config/config.yaml",
            prompt_dir="config/default-prompt",
            prolific_id=prolific_id
        )
        state.debate_manager.setup_debate()
        
        return [
            gr.update(visible=False),  # terms_modal
            gr.update(visible=True),   # llm_experience_modal
            state
        ]
    
    def update_experience_continue_btn(self, experience_level):
        """Enable continue button when experience level is selected"""
        is_valid = experience_level is not None
        return gr.update(interactive=is_valid)
    
    def handle_llm_experience(self, state: DebateState, experience_level):
        """Save LLM experience level and proceed to initial judgment"""
        state.llm_experience_level = experience_level
        state.debate_transcript["llm_experience_level"] = experience_level
        
        topic = state.debate_manager._get_debate_topic()
        state.debate_transcript["debate_topic"] = topic
        
        statement_html = f"""
        <div style='margin: 1.5rem 0; font-size: 1.2em; line-height: 1.6;'>
            Please provide your initial judgment on the statement:
            <div style='background-color: #f8fafc; padding: 15px; border-radius: 6px; margin: 15px 0; font-weight: bold;'>
                "{topic['statement']}"
            </div>
            Is this statement True or False?
        </div>
        """
        
        return [
            gr.update(visible=False),  # llm_experience_modal
            gr.update(visible=True),   # initial_judgment_modal
            gr.update(value=statement_html),  # initial_statement_display
            state  # Return updated state
        ]
    
    def handle_initial_judgment_selection(self, state: DebateState, choice):
        """Handle the selection of True/False in initial judgment modal"""
        state.initial_choice = choice
        return [gr.update(visible=True), state]
    
    def update_initial_confidence(self, state: DebateState, confidence):
        """Store the initial confidence level and enable continue button"""
        state.initial_confidence = confidence if confidence else 50
        return [gr.update(interactive=True), state]
    
    def submit_initial_judgment(self, state: DebateState):
        """Save initial judgment data and proceed to welcome screen"""
        # Store the initial judgment data in the transcript
        state.debate_transcript["initial_judgment"]["decision"] = state.initial_choice
        state.debate_transcript["initial_judgment"]["confidence_level"] = state.initial_confidence
        state.save_current_state()
        
        return [
            gr.update(visible=False),  # initial_judgment_modal
            gr.update(visible=True),   # welcome_screen
            gr.update(visible=True),   # start_button
            state  # Return updated state
        ]

    def validate_feedback(self, feedback, state: DebateState):
        """Validate feedback length and return button state"""
        is_valid = len(feedback.strip()) >= state.MIN_FEEDBACK_LENGTH
        return gr.update(interactive=is_valid)

    def initialize_debate(self, state: DebateState):
        """Initial step to show loading state"""
        return [
            gr.update(value="Loading debate...", interactive=False),
            state
        ]

    def start_debate(self, state: DebateState, request: gr.Request = None):
        """Start the debate and get opening arguments"""
        state.debate_started = True
        state.current_round = 1

        try:
            state.debate_transcript["metadata"]["access_url"] = {
                "host": request.client.host,
                "user_agent": request.headers["user-agent"],
                "headers": dict(request.headers),
                "query_params": dict(request.query_params)
            }
        except Exception as e:
            log_debug(f"Error capturing URL: {str(e)}")
            state.debate_transcript["metadata"]["access_url"] = f"Could not capture URL: {str(e)}"
        
        # Get opening arguments
        round_data = state.debate_manager._run_round(state.current_round, state.transcript)
        state.transcript.append(round_data)
        state.debate_transcript["rounds"].append({
            "round_number": state.current_round,
            "timestamp": datetime.now().isoformat(),
            "debater_a_response": round_data['debater_response'],
            "debater_b_response": round_data['opponent_response'],
            "judge_feedback": None,
            "debater_positions": round_data['debater_positions'],
            "ground_truth_veracity": round_data['ground_truth_veracity']
        })
        state.save_current_state()
        
        # Process arguments for citations
        debater_response_html = self.extract_and_process_argument(round_data['debater_response'], True)
        opponent_response_html = self.extract_and_process_argument(round_data['opponent_response'], False)
        
        return [
            debater_response_html,
            opponent_response_html,
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(interactive=False), 
            gr.update(selected="round1"),
            gr.update(value="Start New Debate", interactive=True),
            gr.update(
                visible=True,
                placeholder=f"Provide feedback and comments here to guide the debaters (minimum {state.MIN_FEEDBACK_LENGTH} characters)"
            ),
            gr.update(visible=False),
            state
        ]

    def show_topic(self, state: DebateState):
        """Get and format the debate topic and positions"""
        topic = state.debate_transcript["debate_topic"]
        debater1_position = state.debate_manager.get_first_debater_context()["ANSWER_DEFENDING"]
        debater2_position = state.debate_manager.get_second_debater_context()["ANSWER_DEFENDING"]
        
        formatted_topic = f"""
            <div style='background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 20px; font-size: 1.1em;'>
                <div style='background-color: white; padding: 15px; border-radius: 6px; margin-bottom: 15px;'>
                    <strong style='font-size: 1.25em;'>Argument Statement: </strong><span style='font-size: 1.2em;'>{topic['statement']}</span>
                </div>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                    <div style='background-color: #eff6ff; padding: 15px; border-radius: 6px;'>
                        <strong style='color: #1e40af; font-size: 1.15em;'>Debater A Position: </strong><span style='font-size: 1.2em;'>{debater1_position}</span>
                    </div>
                    <div style='background-color: #faf5ff; padding: 15px; border-radius: 6px;'>
                        <strong style='color: #5b21b6; font-size: 1.15em;'>Debater B Position: </strong><span style='font-size: 1.2em;'>{debater2_position}</span>
                    </div>
                </div>
            </div>
            """
        state._formatted_header = formatted_topic
        return [formatted_topic, state]
    
    def next_round(self, state: DebateState, judge_feedback):
        """Process next round of debate"""
        if not state.debate_started or len(judge_feedback.strip()) < state.MIN_FEEDBACK_LENGTH:
            return [gr.update()] * 14 + [state]

        if judge_feedback:
            state.transcript[-1]["judge_feedback"] = judge_feedback
            state.debate_transcript["rounds"][-1]["judge_feedback"] = judge_feedback

        state.current_round += 1
        
        # Get next round responses
        round_data = state.debate_manager._run_round(state.current_round, state.transcript)
        state.transcript.append(round_data)
        state.debate_transcript["rounds"].append({
            "round_number": state.current_round,
            "timestamp": datetime.now().isoformat(),
            "debater_a_response": round_data['debater_response'],
            "debater_b_response": round_data['opponent_response'],
            "judge_feedback": None,
            "debater_positions": round_data['debater_positions'],
            "ground_truth_veracity": round_data['ground_truth_veracity']
        })
        state.save_current_state()

        # Process arguments for citations
        debater_response_html = self.extract_and_process_argument(round_data['debater_response'], True)
        opponent_response_html = self.extract_and_process_argument(round_data['opponent_response'], False)

        def format_feedback(round_num, feedback):
            return f"""
            ### Judge's Feedback - Round {round_num}
            {feedback}
            """

        updates = {
            "topic": state._formatted_header,
            "tabs": gr.update(selected=state.round_tabs[state.current_round]),
            "final_modal": gr.update(visible=False),
            "next_button": gr.update(value="Next Round", interactive=True, elem_classes=["start-button"]),
            "next_button2": gr.update(value="Next Round", interactive=True, elem_classes=["start-button"])
        }
        
        if state.current_round == 2:
            updates.update({
                "round1_input_container": gr.update(visible=False),
                "round1_feedback": gr.update(
                    value=format_feedback(1, judge_feedback),
                    visible=True
                ),
                "round2_a": debater_response_html,
                "round2_b": opponent_response_html,
                "round2_input_container": gr.update(visible=True),
                "round2_feedback": gr.update(visible=False),
                "round3_feedback": gr.update(visible=False)
            })
            
        elif state.current_round == 3:
            updates.update({
                "round1_input_container": gr.update(visible=False),
                "round1_feedback": gr.update(
                    value=format_feedback(1, state.debate_transcript["rounds"][0]["judge_feedback"]),
                    visible=True
                ),
                "round2_input_container": gr.update(visible=False),
                "round2_feedback": gr.update(
                    value=format_feedback(2, judge_feedback),
                    visible=True
                ),
                "round3_a": debater_response_html,
                "round3_b": opponent_response_html,
                "round3_feedback": gr.update(visible=False)
            })
        
        result = [
            updates["topic"],
            updates["round1_feedback"],
            updates["round2_feedback"],
            updates["round3_feedback"],
            updates.get("round2_a", gr.update()),
            updates.get("round2_b", gr.update()),
            updates.get("round3_a", gr.update()),
            updates.get("round3_b", gr.update()),
            updates.get("round1_input_container", gr.update()),
            updates.get("round2_input_container", gr.update()),
            updates["tabs"],
            updates["next_button"],
            updates["next_button2"],
            updates["final_modal"],
            state
        ]
        
        return result
    
    def show_final_judgment_modal(self, state: DebateState):
        """Show the final judgment modal after Round 3 is complete"""
        debate_statement = state.debate_transcript["debate_topic"]["statement"]
        judgment_question = f"""
        <div style='margin: 0.5rem 0; font-size: 1.2em; line-height: 1;'>
            Based on the arguments presented by both debaters, do you believe the statement is True or False?
            <div style='background-color: #f8fafc; padding: 5px; border-radius: 6px; margin: 5px 0; font-weight: bold;'>
                "{debate_statement}"
            </div>
            
        </div>
        """
        
        return [
            gr.update(visible=True),  # final_modal
            gr.update(value=judgment_question),  # judgment_question_md
            state
        ]

    def set_loading_state(self, state: DebateState):
        """Set the next round button to loading state"""
        return [
            gr.update(value="Loading next round...", interactive=False, elem_classes=["loading-button", "start-button"]),
            gr.update(value="Loading next round...", interactive=False, elem_classes=["loading-button", "start-button"]),
            state
        ]
    
    def handle_judgment_selection(self, state: DebateState, choice):
        """Handle the selection of True/False in final judgment modal"""
        state.selected_choice = choice
        return [gr.update(visible=True), state]
    
    def update_confidence(self, state: DebateState, confidence):
        """Store the confidence level and show reasoning container"""
        state.selected_confidence = confidence if confidence else 50
        return [gr.update(visible=True), state]
    
    def update_reasoning_counter(self, reasoning, state: DebateState):
        """Update character counter for reasoning input"""
        remaining = max(0, state.MIN_REASONING_LENGTH - len(reasoning.strip()))
        btn_interactive = len(reasoning.strip()) >= state.MIN_REASONING_LENGTH
        return [
            f"Characters remaining: {remaining}",
            gr.update(interactive=btn_interactive)
        ]
    
    def submit_final_judgment(self, state: DebateState, reasoning):
        """Handle final judgment submission with all data"""
        if len(reasoning.strip()) < state.MIN_REASONING_LENGTH:
            return [gr.update()] * 4 + [state]
        
        state.debate_transcript["final_decision"] = state.selected_choice
        state.debate_transcript["confidence_level"] = state.selected_confidence
        state.debate_transcript["reasoning"] = reasoning
        state.debate_transcript["metadata"]["end_time"] = datetime.now().isoformat()
        state.save_current_state()
        
        completion_html = self.create_completion_html(state)
        
        return [
            gr.update(visible=False),      # final_modal
            gr.update(visible=False),      # debate_interface
            gr.update(visible=True),       # completion_screen
            gr.update(value=completion_html), # completion_html
            state
        ]
