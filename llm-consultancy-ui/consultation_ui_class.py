from typing import Dict, List, Optional
import gradio as gr
from welcome_template import WELCOME_HTML, TERMS_AND_CONDITIONS_HTML
from ui_utils import create_css
from round_state_class import RoundState
from consultant_runner_class import ConsultancyRunner
from agents.consultant import Consultant
from consultation_context_class import ConsultationContext

class ConsultationUI:
    """Manages the Gradio interface for the consultation system with proper session handling."""
    
    MIN_CHARS = 50
    
    def __init__(self):
        self.round_states: List[RoundState] = []
        self.final_judgment_components = None
        self.completion_container = None
        self.start_button = None
        self.tabs = None
        self.initial_judgment_components = None
        self.llm_experience_components = None
        self.runner_state = None
        self.topic_display = None
        self.stance_display = None
        self.ui_class_prolific_data = None
        self.ui_class_prolific_id = None

    def create_completion_html(self, runner: ConsultancyRunner) -> str:
        """Creates HTML for the completion screen with initial and final confidence levels."""
        completion_data = runner.get_completion_data()
        
        # Access the initial confidence
        initial_confidence = completion_data.get("initial_confidence", "Not recorded")
        initial_confidence_display = f"{initial_confidence}/100" if isinstance(initial_confidence, (int, float)) else initial_confidence
        
        return f'''
        <div style='text-align: center; padding: 30px; background-color: #f0fdf4; border-radius: 12px; border: 2px solid #16a34a; margin: 20px 0;'>
            <h2 style='color: #15803d; margin-bottom: 15px;'>Consultation Complete! 🎉</h2>
            <div style='margin-bottom: 20px;'>
                <h3 style='color: #166534; margin-bottom: 10px;'>Initial Assessment</h3>
                <p style='font-size: 1.2em; margin-bottom: 10px;'>Choice: <strong>{completion_data["initial_choice"]}</strong></p>
                <p style='font-size: 1.1em; margin-bottom: 15px;'>Confidence Level: <strong>{initial_confidence_display}</strong></p>
            </div>
            <div style='margin-bottom: 20px;'>
                <h3 style='color: #166534; margin-bottom: 10px;'>Final Assessment</h3>
                <p style='font-size: 1.2em; margin-bottom: 10px;'>Choice: <strong>{completion_data["final_choice"]}</strong></p>
                <p style='font-size: 1.1em; margin-bottom: 15px;'>Confidence Level: <strong>{completion_data["confidence_level"]}/100</strong></p>
            </div>
            <p style='margin-bottom: 20px;'>Thank you for participating in this consultation! 🔨</p>
            <a href='https://app.prolific.com/submissions/complete?cc=C1DA3DDR' target='_blank' 
               style='display: inline-block; background-color: #16a34a; color: white; padding: 15px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 1.1em; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: background-color 0.3s ease;'>
                Return to Prolific
            </a>
        </div>
        '''

    def _create_llm_experience_modal(self) -> Dict:
        """Creates a modal to capture the user's experience level with LLMs."""
        with gr.Column(visible=False) as llm_modal:
            with gr.Column(elem_classes=["modal-overlay"]):
                with gr.Column(elem_classes=["terms-modal"]):
                    gr.Markdown("## Your Experience with AI Assistants", elem_classes=["text-center"])
                    gr.Markdown("""
                        <div style='font-size: 1.2em; margin: 1.5rem 0; line-height: 1.6;'>
                            Before we begin, please indicate your level of experience with AI assistants like ChatGPT, Claude, or Bard.
                            
                            NOTE: Your answer has no effect on your compensation or how we view your responses. We value your honest feedback, regardless of your experience level. Your compensation is guaranteed as long as you properly complete all required sessions.
                        </div>
                    """)
                    experience_slider = gr.Slider(
                        minimum=1,
                        maximum=100,
                        step=1,
                        value=None,
                        label="Experience Level",
                        interactive=True,
                        info="1 = No experience, 100 = Expert user"
                    )
                    continue_btn = gr.Button(
                        "Continue", 
                        variant="primary",
                        elem_classes=["accept-button"],
                        interactive=False
                    )
    
        return {
            "modal": llm_modal,
            "slider": experience_slider,
            "continue_btn": continue_btn
        }

    def _create_initial_judgment_modal(self) -> Dict:
        """Creates the initial judgment modal components with confidence slider."""
        with gr.Column(visible=False) as initial_modal:
            with gr.Column(elem_classes=["modal-overlay"]):
                with gr.Column(elem_classes=["terms-modal"]):
                    gr.Markdown("## Initial Judgment", elem_classes=["text-center"])
                    statement_display = gr.Markdown("Loading...", elem_id="initial-judgment-statement")
                    initial_choice = gr.Radio(
                        choices=["True", "False"],
                        label="Your Initial Judgment",
                        interactive=True
                    )
                    
                    # Add confidence container (initially hidden)
                    with gr.Column(visible=False) as confidence_container:
                        gr.Markdown("As a percentage, how confident are you in your selection?")
                        confidence_slider = gr.Slider(
                            minimum=1,
                            maximum=100,
                            step=1,
                            value=50,
                            label="Initial Confidence Percentage",
                            interactive=True,
                            info="1 = Not confident at all, 100 = Very confident"
                        )
                    
                    continue_btn = gr.Button(
                        "Continue to Consultation", 
                        variant="primary",
                        elem_classes=["accept-button"],
                        interactive=False
                    )
        
        return {
            "modal": initial_modal,
            "statement": statement_display,
            "choice": initial_choice,
            "confidence_container": confidence_container,
            "confidence_slider": confidence_slider,
            "continue_btn": continue_btn
        }

    def _create_final_judgment_modal(self) -> Dict:
        """Creates the final judgment modal components."""
        with gr.Column(visible=False) as final_modal:
            with gr.Column(elem_classes=["modal-overlay"]):
                with gr.Column(elem_classes=["terms-modal"]):
                    gr.Markdown("## Final Judgment", elem_classes=["text-center"])
                    gr.Markdown(f"""
                                <div style='margin: 1.5rem 0; font-size: 1.2em; line-height: 1.6;'>
                                    Based on the consultation, do you believe the claim is True or False?
                                </div> """)
                    judgment_choice = gr.Radio(
                        choices=["True", "False"],
                        label="Your Judgment",
                        interactive=True
                    )
                    
                    with gr.Column(visible=False) as confidence_container:
                        gr.Markdown("As a percentage, how confident are you in your selection?")
                        confidence_slider = gr.Slider(
                            minimum=1,
                            maximum=100,
                            step=1,
                            value=50,
                            label="Confidence Percentage",
                            interactive=True,
                            info="1 = Not confident at all, 100 = Very confident"
                        )
                        
                        with gr.Column(visible=False) as reasoning_container:
                            reasoning_input = gr.Textbox(
                                label="Please explain your reasoning",
                                placeholder=f"What factors influenced your decision? (minimum {self.MIN_CHARS} characters)",
                                lines=3,
                                interactive=True
                            )
                            reasoning_char_counter = gr.Markdown(
                                f"Characters remaining: {self.MIN_CHARS}",
                                elem_classes=["large-text-box"]
                            )
                    
                    submit_judgment_btn = gr.Button(
                        "Submit Final Judgment", 
                        variant="primary",
                        elem_classes=["accept-button"],
                        interactive=False
                    )
        
        return {
            "modal": final_modal,
            "choice": judgment_choice,
            "confidence_container": confidence_container,
            "confidence_slider": confidence_slider,
            "reasoning_container": reasoning_container,
            "reasoning_input": reasoning_input,
            "reasoning_char_counter": reasoning_char_counter,
            "submit_btn": submit_judgment_btn
        }

    def _create_welcome_screen(self) -> gr.Column:
        """Creates the welcome screen components."""
        with gr.Column(visible=False) as container:
            gr.HTML(WELCOME_HTML)
            self.start_button = gr.Button(
                "Start Consultation", 
                variant="primary",
                elem_id="start-debate-btn",
                elem_classes=["start-button"],
                interactive=False
            )
            return container

    def _create_debate_interface(self) -> gr.Column:
        """Creates the main debate interface with placeholder text."""
        with gr.Column(visible=False) as container:
            self.topic_display = gr.Markdown("Loading...", elem_id="debate-topic")
            self.stance_display = gr.Markdown("Loading...", elem_id="consultant-stance")
            
            with gr.Tabs(elem_id="debate_tabs") as tabs:
                for round_num in range(1, ConsultancyRunner.TOTAL_ROUNDS + 1):
                    with gr.Tab(f"Round {round_num}", id=f"round_{round_num}_tab"):
                        state = self._create_round_components(round_num)
                        self.round_states.append(state)
            
            self.tabs = tabs
            return container

    def _create_round_components(self, round_num: int) -> RoundState:
        """Creates components for a single round with larger font sizes."""
        with gr.Column():
            status = gr.Markdown(
                f"Round {round_num} Status: Waiting to start",
                elem_classes=["status-text"]
            )
            consultant_output = gr.Markdown(
                value="",
                elem_classes=["large-text-box"]
            )
            char_counter = gr.Markdown(
                f"Characters remaining: {self.MIN_CHARS}",
                elem_classes=["large-text-box"]
            )
            judge_input = gr.Textbox(
                label="Your Response (as Judge)",
                lines=5,
                placeholder=f"Enter your response/question (minimum {self.MIN_CHARS} characters)...",
                interactive=True,
                elem_classes=["large-text-box"]
            )
            submit_button = gr.Button(
                "Submit Response", 
                variant="primary",
                interactive=False,
                elem_classes=["large-button"]
            )
            
            return RoundState(status, consultant_output, judge_input, char_counter, submit_button)
        
    def save_prolific_data(self, request: Optional[gr.Request] = None) -> None:      
        if request:
            try:
                prolific_data = {
                    "PROLIFIC_PID": request.query_params.get("PROLIFIC_PID", ""),
                    "STUDY_ID": request.query_params.get("STUDY_ID", ""),
                    "SESSION_ID": request.query_params.get("SESSION_ID", ""),
                    "host": request.client.host,
                    "user_agent": request.headers.get("user-agent", ""),
                    "headers": dict(request.headers),
                    "query_params": dict(request.query_params)
                }
                self.ui_class_prolific_id = prolific_data["PROLIFIC_PID"]
                return prolific_data
            except Exception as e:
                print(f"Error capturing Prolific data: {str(e)}")
                return None

    def _setup_event_handlers(self, welcome_container: gr.Column, debate_container: gr.Column, terms_modal: gr.Row, accept_terms_btn: gr.Button):
        """Sets up all event handlers for the interface with session state support."""
        def start_debate(runner: ConsultancyRunner):
            print("Inside start_debate")
            return {
                self.start_button: gr.Button(
                    value="",
                    elem_classes=["start-button", "loading-text-start"],
                    interactive=False
                ),
                self.runner_state: runner
            }

        def initialize_round(runner: ConsultancyRunner):
            consultant_msg = runner.process_round(1)
            return {
                welcome_container: gr.Column(visible=False),
                debate_container: gr.Column(visible=True),
                self.round_states[0].consultant_output: consultant_msg,
                self.round_states[0].status: "Round 1: In Progress",
                self.round_states[0].submit_button: gr.Button("Submit Response", interactive=False)
            }

        def handle_initial_choice(choice: str):
            """Reveals confidence slider when True/False choice is made"""
            if choice:
                return {
                    self.initial_judgment_components["confidence_container"]: gr.Column(visible=True),
                    self.initial_judgment_components["continue_btn"]: gr.Button(
                        "Continue to Consultation",
                        interactive=False,
                        variant="primary",
                        elem_classes=["accept-button"]
                    )
                }
            return {
                self.initial_judgment_components["confidence_container"]: gr.Column(visible=False),
                self.initial_judgment_components["continue_btn"]: gr.Button(
                    "Continue to Consultation",
                    interactive=False,
                    variant="primary",
                    elem_classes=["accept-button"]
                )
            }

        def update_initial_continue_button(choice: str, confidence: float):
            """Enable continue button when both choice and confidence are set"""
            if choice and confidence:
                return gr.Button(
                    "Continue to Consultation",
                    interactive=True,
                    variant="primary",
                    elem_classes=["accept-button"]
                )
            return gr.Button(
                "Continue to Consultation",
                interactive=False,
                variant="primary",
                elem_classes=["accept-button"]
            )

        def start_consultation(runner: ConsultancyRunner, choice: str, confidence: float):
            """Processes initial choice with confidence and starts consultation."""
            runner.save_initial_choice(choice, confidence)
            return {
                self.initial_judgment_components["modal"]: gr.Column(visible=False),
                welcome_container: gr.Column(visible=True),
                self.start_button: gr.Button(
                    "Start Consultation",
                    variant="primary",
                    elem_classes=["start-button"],
                    interactive=True
                ),
                self.topic_display: f"""
                    <div style='margin: 0.5rem 0 2rem 0;'>
                        <h3 style='font-size: 1.4em; margin-bottom: 1rem;'>Discussion Topic:</h3>
                        <div style='
                            background-color: #f3f4f6;
                            padding: 1.5rem;
                            border-radius: 0.75rem;
                            border-left: 6px solid #2563eb;
                            margin: 0.5rem 0 1rem 0;
                            font-size: 1.2em;
                            line-height: 1.6;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        '>
                            {runner.context.statement}
                        </div>
                    </div>
                """,
                self.stance_display: f"""
                    <div style='
                        background-color: #fdf2f8;
                        padding: 1rem;
                        border-radius: 0.75rem;
                        border-left: 6px solid #db2777;
                        margin: 0.5rem 0;
                        font-size: 1.1em;
                        line-height: 1.5;
                    '> 
                        This AI consultant is arguing that this statement is <strong>{'True' if runner.context.answer_defending else 'False'}</strong>.
                    </div>
                """,
                self.runner_state: runner
            }

        def handle_llm_experience(runner: ConsultancyRunner, experience_level: float):
            runner.debate_transcript["metadata"]["llm_experience_level"] = experience_level
            return {
                self.llm_experience_components["modal"]: gr.Column(visible=False),
                self.initial_judgment_components["modal"]: gr.Column(visible=True),
                self.initial_judgment_components["statement"]: f"""
                    <div style='font-size: 1.5em; margin: 1.5rem 0; line-height: 1.6;'>
                        Before starting the consultation, do you believe the claim: <strong>"{runner.context.statement}"</strong> is True or False?
                    </div>
                """,
                self.runner_state: runner
            }
            
        # Accept terms button event handler to show LLM experience slider first
        def accept_terms(request: gr.Request):
            self.ui_class_prolific_data = self.save_prolific_data(request)
            print(f"Captured Prolific data on terms acceptance: {self.ui_class_prolific_data}")
            
            runner = ConsultancyRunner()
            runner.context = ConsultationContext(
                word_limit=runner.config['consultant_settings']['word_limit'],
                prolific_id=self.ui_class_prolific_id
            )

            runner.debate_started = True
            runner.consultant = Consultant(runner.config, runner.context.to_dict())
            runner.debate_transcript = runner._initialize_transcript()
            runner.debate_transcript["metadata"]["prolific_data"] = self.ui_class_prolific_data
            runner.debate_transcript["metadata"]["claim_data"] = runner.context.claim_data
            runner.debate_transcript["metadata"]["claim_index"] = runner.context.claim_index
            runner.debate_transcript["metadata"]["data_path"] = str(runner.context.data_path)
            runner.debate_transcript["metadata"]["tracking_path"] = str(runner.context.tracking_path)

            return {
                terms_modal: gr.Row(visible=False),
                self.llm_experience_components["modal"]: gr.Column(visible=True),
                self.runner_state: runner
            }

        # Connect accept terms button
        accept_terms_btn.click(
            fn=accept_terms,
            inputs=[],
            outputs=[
                terms_modal,
                self.llm_experience_components["modal"],
                self.runner_state
            ]
        )

        # Event handler for LLM experience slider
        self.llm_experience_components["slider"].change(
            fn=lambda experience: gr.Button(
                "Continue", 
                variant="primary",
                elem_classes=["accept-button"],
                interactive=True if experience is not None else False
            ),
            inputs=[self.llm_experience_components["slider"]],
            outputs=[self.llm_experience_components["continue_btn"]]
        )

        # Connect LLM experience continue button
        self.llm_experience_components["continue_btn"].click(
            fn=handle_llm_experience,
            inputs=[
                self.runner_state,
                self.llm_experience_components["slider"]
            ],
            outputs=[
                self.llm_experience_components["modal"],
                self.initial_judgment_components["modal"],
                self.initial_judgment_components["statement"],
                self.runner_state
            ]
        )

        # Connect initial choice handlers
        self.initial_judgment_components["choice"].change(
            fn=handle_initial_choice,
            inputs=[self.initial_judgment_components["choice"]],
            outputs=[
                self.initial_judgment_components["confidence_container"],
                self.initial_judgment_components["continue_btn"]
            ]
        )

        # Event handler for confidence slider
        self.initial_judgment_components["confidence_slider"].change(
            fn=update_initial_continue_button,
            inputs=[
                self.initial_judgment_components["choice"],
                self.initial_judgment_components["confidence_slider"]
            ],
            outputs=[self.initial_judgment_components["continue_btn"]]
        )

        # Update continue button handler to include confidence
        self.initial_judgment_components["continue_btn"].click(
            fn=start_consultation,
            inputs=[
                self.runner_state,
                self.initial_judgment_components["choice"],
                self.initial_judgment_components["confidence_slider"]
            ],
            outputs=[
                self.initial_judgment_components["modal"],
                welcome_container,
                self.start_button,
                self.topic_display,
                self.stance_display,
                self.runner_state
            ]
        )

        # Connect start button handlers
        self.start_button.click(
            fn=start_debate,
            inputs=[self.runner_state],
            outputs=[self.start_button, self.runner_state]
        ).then(
            fn=initialize_round,
            inputs=[self.runner_state],
            outputs=[
                welcome_container,
                debate_container,
                self.round_states[0].consultant_output,
                self.round_states[0].status,
                self.round_states[0].submit_button
            ]
        )

        def update_char_count(text: str):
            char_count = len(text)
            chars_remaining = max(0, self.MIN_CHARS - char_count)
            return [
                f"Characters remaining: {chars_remaining}",
                gr.Button(
                    "Submit Response",
                    interactive=(char_count >= self.MIN_CHARS)
                )
            ]
        
        def update_reasoning_char_count(text: str):
            char_count = len(text)
            chars_remaining = max(0, self.MIN_CHARS - char_count)
            return f"Characters remaining: {chars_remaining}"
        
        def show_loading_state(round_num: int, judge_response: str):
            """First function to run when submit is clicked - shows loading state"""
            if len(judge_response.strip()) < self.MIN_CHARS:
                raise gr.Error(f"Please enter at least {self.MIN_CHARS} characters.")
            
            return gr.Button(
                value="",
                elem_classes=["loading-text-submit"],
                interactive=False
            )

        def process_submission(runner: ConsultancyRunner, round_num: int, judge_response: str):
            """Processes the submission with session-specific runner."""
            runner.update_judge_response(round_num, judge_response)
            
            outputs = {
                self.round_states[round_num - 1].status: f"Round {round_num}: Complete",
                self.round_states[round_num - 1].submit_button: gr.Button(
                    value="Submitted",
                    interactive=False,
                    elem_classes=[]
                ),
                self.runner_state: runner
            }
            
            if round_num < runner.TOTAL_ROUNDS:
                consultant_msg = runner.process_round(round_num + 1)
                outputs.update({
                    self.round_states[round_num].consultant_output: consultant_msg,
                    self.round_states[round_num].status: f"Round {round_num + 1}: In Progress",
                    self.round_states[round_num].submit_button: gr.Button("Submit Response", interactive=False),
                    self.tabs: gr.Tabs(selected=f"round_{round_num + 1}_tab")
                })
            else:
                outputs.update({
                    self.final_judgment_components["modal"]: gr.Column(visible=True),
                    self.final_judgment_components["choice"]: gr.Radio(value=None),
                })
            
            return outputs

        # Set up round-specific handlers
        for round_num, state in enumerate(self.round_states, 1):
            state.judge_input.change(
                fn=update_char_count,
                inputs=[state.judge_input],
                outputs=[state.char_counter, state.submit_button]
            )

            # First show loading state immediately
            state.submit_button.click(
                fn=lambda response, r=round_num: show_loading_state(r, response),
                inputs=[state.judge_input],
                outputs=[state.submit_button]
            ).then( 
                fn=lambda runner, response, r=round_num: process_submission(runner, r, response),
                inputs=[
                    self.runner_state,
                    state.judge_input
                ],
                outputs=[
                    state.status,
                    state.submit_button,
                    self.runner_state,
                    *([
                        self.final_judgment_components["modal"],
                        self.final_judgment_components["choice"]
                    ] if round_num == ConsultancyRunner.TOTAL_ROUNDS else [
                        self.round_states[round_num].consultant_output,
                        self.round_states[round_num].status,
                        self.round_states[round_num].submit_button,
                        self.tabs
                    ])
                ]
            )

        def handle_judgment_choice(choice: str):
            if choice:
                return {
                    self.final_judgment_components["confidence_container"]: gr.Column(visible=True),
                }
            return {
                self.final_judgment_components["confidence_container"]: gr.Column(visible=False),
                self.final_judgment_components["reasoning_container"]: gr.Column(visible=False)
            }

        def handle_confidence_selection(confidence: float):
            if confidence:
                return {
                    self.final_judgment_components["reasoning_container"]: gr.Column(visible=True)
                }
            return {
                self.final_judgment_components["reasoning_container"]: gr.Column(visible=False)
            }

        def update_submit_button(choice: str, confidence: float, reasoning: str):
            has_enough_chars = len(reasoning.strip()) >= self.MIN_CHARS
            return gr.Button(
                "Submit Final Judgment",
                interactive=bool(choice and confidence and has_enough_chars),
                variant="primary",
                elem_classes=["accept-button"]
            )

        def handle_final_judgment(runner: ConsultancyRunner, choice: str, confidence: float, reasoning: str):
            if len(reasoning.strip()) < self.MIN_CHARS:
                raise gr.Error(f"Please enter at least {self.MIN_CHARS} characters in your reasoning.")
                
            runner.save_final_judgment(choice, confidence, reasoning)
            completion_html = self.create_completion_html(runner)
            
            return {
                self.final_judgment_components["modal"]: gr.Column(visible=False),
                self.completion_container: gr.HTML(value=completion_html, visible=True),
                debate_container: gr.Column(visible=False),
                self.runner_state: runner
            }

        # Connect final judgment handlers
        self.final_judgment_components["choice"].change(
            fn=handle_judgment_choice,
            inputs=[self.final_judgment_components["choice"]],
            outputs=[
                self.final_judgment_components["confidence_container"],
                self.final_judgment_components["reasoning_container"]
            ]
        )

        self.final_judgment_components["confidence_slider"].change(
            fn=handle_confidence_selection,
            inputs=[self.final_judgment_components["confidence_slider"]],
            outputs=[self.final_judgment_components["reasoning_container"]]
        )
        
        # Event handler for reasoning input char count
        self.final_judgment_components["reasoning_input"].change(
            fn=update_reasoning_char_count,
            inputs=[self.final_judgment_components["reasoning_input"]],
            outputs=[self.final_judgment_components["reasoning_char_counter"]]
        )

        for component in [
            self.final_judgment_components["choice"],
            self.final_judgment_components["confidence_slider"],
            self.final_judgment_components["reasoning_input"]
        ]:
            component.change(
                fn=update_submit_button,
                inputs=[
                    self.final_judgment_components["choice"],
                    self.final_judgment_components["confidence_slider"],
                    self.final_judgment_components["reasoning_input"]
                ],
                outputs=[self.final_judgment_components["submit_btn"]]
            )

        self.final_judgment_components["submit_btn"].click(
            fn=handle_final_judgment,
            inputs=[
                self.runner_state,
                self.final_judgment_components["choice"],
                self.final_judgment_components["confidence_slider"],
                self.final_judgment_components["reasoning_input"]
            ],
            outputs=[
                self.final_judgment_components["modal"],
                self.completion_container,
                debate_container,
                self.runner_state
            ]
        )

    def create_interface(self) -> gr.Blocks:
        """Creates and configures the complete Gradio interface with session management."""
        with gr.Blocks(css=create_css(), title="AI Consultation System") as interface:
            # Create session-specific runner state
            self.runner_state = gr.State(lambda: ConsultancyRunner())
            
            # Terms Modal
            with gr.Row(visible=True) as terms_modal:
                with gr.Column(elem_classes=["modal-overlay"]):
                    with gr.Column(elem_classes=["terms-modal"]):
                        gr.HTML(TERMS_AND_CONDITIONS_HTML)
                        accept_terms_btn = gr.Button(
                            "I Accept the Terms & Conditions", 
                            size="lg", 
                            elem_classes=["accept-button"]
                        )

            # Create completion screen
            self.completion_container = gr.HTML(visible=False)
            
            # Create LLM experience modal
            self.llm_experience_components = self._create_llm_experience_modal()
            
            # Create initial and final judgment modals
            self.initial_judgment_components = self._create_initial_judgment_modal()
            self.final_judgment_components = self._create_final_judgment_modal()
            
            # Create main containers
            welcome_container = self._create_welcome_screen()
            debate_container = self._create_debate_interface()
            
            # Initially hide containers
            welcome_container.visible = False
            debate_container.visible = False
            
            # Set up event handlers
            self._setup_event_handlers(welcome_container, debate_container, terms_modal, accept_terms_btn)
            return interface