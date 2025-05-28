import gradio as gr
from create_css import create_css
from welcome_html import WELCOME_HTML, TERMS_HTML, LLM_EXPERIENCE_HTML
from debate_state_class import DebateState
from debate_interface_class import DebateInterface

def create_debate_app():
    debate_ui = DebateInterface()

    with gr.Blocks(css=create_css(), title="AI Debate System") as demo:
        debate_state = gr.State(DebateState)
        
        # Completion Screen
        with gr.Column(visible=False) as completion_screen:
            completion_html = gr.HTML()
        
        # Terms Modal
        with gr.Column(visible=True, elem_classes=["modal-overlay"]) as terms_modal:
            with gr.Column(elem_classes=["terms-modal"]):
                gr.HTML(TERMS_HTML)
                accept_terms_btn = gr.Button("I Accept the Terms & Conditions", size="lg", elem_classes=["accept-button"])

        # LLM Experience Modal
        with gr.Column(visible=False, elem_classes=["modal-overlay"]) as llm_experience_modal:
            with gr.Column(elem_classes=["terms-modal"]):
                gr.Markdown("## Your Experience with AI Assistants", elem_classes=["text-center"])
                gr.Markdown(LLM_EXPERIENCE_HTML)
                experience_slider = gr.Slider(
                    minimum=1,
                    maximum=100,
                    step=1,
                    value=None,
                    label="Experience Level",
                    interactive=True,
                    info="1 = No experience, 100 = Expert user"
                )
                experience_continue_btn = gr.Button(
                    "Continue", 
                    variant="primary",
                    elem_classes=["accept-button"],
                    interactive=False
                )

        # Initial Judgment Modal
        with gr.Column(visible=False, elem_classes=["modal-overlay"]) as initial_judgment_modal:
            with gr.Column(elem_classes=["terms-modal"]):
                gr.Markdown("## Initial Judgment", elem_classes=["text-center"])
                initial_statement_display = gr.HTML("Loading...", elem_id="initial-judgment-statement")
                initial_choice = gr.Radio(
                    choices=["True", "False"],
                    label="Your Initial Judgment",
                    interactive=True
                )
                
                # Add confidence container (initially hidden)
                with gr.Column(visible=False) as initial_confidence_container:
                    gr.Markdown("As a percentage, how confident are you in your selection?")
                    initial_confidence_slider = gr.Slider(
                        minimum=1,
                        maximum=100,
                        step=1,
                        value=50,
                        label="Initial Confidence Percentage",
                        interactive=True,
                        info="1 = Not confident at all, 100 = Very confident"
                    )
                
                initial_continue_btn = gr.Button(
                    "Continue to Debate", 
                    variant="primary",
                    elem_classes=["accept-button"],
                    interactive=False
                )

        # Welcome Screen
        with gr.Column(visible=False) as welcome_screen:
            gr.HTML(WELCOME_HTML)
            start_button = gr.Button("Start Debate", size="lg", elem_classes=["loading-button", "start-button"], visible=True)

        # Final Judgment Modal
        with gr.Column(visible=False, elem_classes=["modal-overlay"]) as final_modal:
            with gr.Column(elem_classes=["terms-modal"]):
                judgment_question_md = gr.HTML(elem_id="final-judgment-statement")
                judgment_choice = gr.Radio(
                    choices=["True", "False"],
                    interactive=True
                )
                
                with gr.Column(visible=False) as confidence_container:
                    gr.Markdown("As a percentage, how confident are you in your selection?")
                    confidence_slider = gr.Slider(
                        minimum=1,
                        maximum=100,
                        step=1,
                        value=50,
                        interactive=True,
                        info="1 = Not confident at all, 100 = Very confident"
                    )
                    
                    with gr.Column(visible=False) as reasoning_container:
                        reasoning_input = gr.Textbox(
                            label="Please explain your reasoning",
                            placeholder=f"Explain why you chose this answer (minimum 50 characters)",
                            lines=2,
                            interactive=True
                        )
                        reasoning_char_counter = gr.Markdown(
                            f"Characters remaining: 50",
                            elem_classes=["character-counter"]
                        )
                
                submit_judgment_btn = gr.Button(
                    "Submit Final Judgment", 
                    variant="primary",
                    elem_classes=["accept-button"],
                    interactive=False
                )

        # Debate Interface
        with gr.Column(visible=False) as debate_interface:
            topic_display = gr.HTML()
            
            # In the UI section, update the tabs structure
            with gr.Tabs(elem_id="debate_tabs") as tabs:
                with gr.TabItem("Round 1: Opening Arguments", id="round1"):
                    with gr.Row():
                        round1_a = gr.HTML(label="Debater A Opening", elem_classes=["position-a-box"])
                        round1_b = gr.HTML(label="Debater B Opening", elem_classes=["position-b-box"])
                    round1_feedback = gr.Markdown(visible=False)
                    with gr.Column(visible=True) as round1_input_container:
                        judge_input = gr.Textbox(
                            label="Judge's Feedback",
                            placeholder=f"Provide feedback and comments here to guide the debaters (minimum 50 characters)",
                            lines=5,
                            visible=True
                        )
                        next_button = gr.Button(
                            "Next Round",
                            interactive=False,
                            size="lg",
                            elem_classes=["start-button"]
                        )

                with gr.TabItem("Round 2: Rebuttals", id="round2"):
                    with gr.Row():
                        round2_a = gr.HTML(label="Debater A Rebuttal", elem_classes=["position-a-box"])
                        round2_b = gr.HTML(label="Debater B Rebuttal", elem_classes=["position-b-box"])
                    round2_feedback = gr.Markdown(visible=False)
                    with gr.Column(visible=True) as round2_input_container:
                        judge_input2 = gr.Textbox(
                            label="Judge's Feedback",
                            placeholder=f"Provide feedback and comments here to guide the debaters (minimum 50 characters)",
                            lines=5,
                            visible=True
                        )
                        next_button2 = gr.Button(
                            "Next Round",
                            interactive=False,
                            size="lg",
                            elem_classes=["start-button"]
                        )

                with gr.TabItem("Round 3: Closing Arguments", id="round3"):
                    with gr.Row():
                        round3_a = gr.HTML(label="Debater A Closing", elem_classes=["position-a-box"])
                        round3_b = gr.HTML(label="Debater B Closing", elem_classes=["position-b-box"])
                    round3_feedback = gr.Markdown(visible=False)
                    next_button3 = gr.Button(
                        "Provide Final Judgment",
                        size="lg",
                        elem_classes=["start-button"]
                    )

        # Terms acceptance now goes to LLM experience modal
        accept_terms_btn.click(
            fn=debate_ui.accept_terms,
            inputs=[debate_state],
            outputs=[
                terms_modal,
                llm_experience_modal,
                debate_state
            ]
        )
        
        # Experience slider enables continue button when value changes
        experience_slider.change(
            fn=debate_ui.update_experience_continue_btn,
            inputs=[experience_slider],
            outputs=[experience_continue_btn]
        )
        
        # Experience continue button transitions to initial judgment
        experience_continue_btn.click(
            fn=debate_ui.handle_llm_experience,
            inputs=[debate_state, experience_slider],
            outputs=[
                llm_experience_modal,
                initial_judgment_modal,
                initial_statement_display,
                debate_state
            ]
        )
        
        # Initial judgment interactions
        initial_choice.change(
            fn=debate_ui.handle_initial_judgment_selection,
            inputs=[debate_state, initial_choice],
            outputs=[initial_confidence_container, debate_state]
        )
        
        initial_confidence_slider.change(
            fn=debate_ui.update_initial_confidence,
            inputs=[debate_state, initial_confidence_slider],
            outputs=[initial_continue_btn, debate_state]
        )
        
        initial_continue_btn.click(
            fn=debate_ui.submit_initial_judgment,
            inputs=[debate_state],
            outputs=[
                initial_judgment_modal,
                welcome_screen,
                start_button,
                debate_state
            ]
        )
        
        # Start debate flow with state
        start_button.click(
            fn=debate_ui.initialize_debate,
            inputs=[debate_state],
            outputs=[start_button, debate_state]
        ).then(
            fn=debate_ui.show_topic,
            inputs=[debate_state],
            outputs=[topic_display, debate_state]
        ).then(
            fn=debate_ui.start_debate,
            inputs=[debate_state],
            outputs=[
                round1_a,
                round1_b,
                debate_interface,
                welcome_screen,
                next_button,
                tabs,
                start_button,
                judge_input,
                final_modal,
                debate_state
            ]
        )

        # Validate feedback to enable/disable next buttons
        judge_input.change(
            fn=debate_ui.validate_feedback,
            inputs=[judge_input, debate_state],
            outputs=[next_button]
        )

        judge_input2.change(
            fn=debate_ui.validate_feedback,
            inputs=[judge_input2, debate_state],
            outputs=[next_button2]
        )

        # Next round handling with state
        next_button.click(
            fn=debate_ui.set_loading_state,
            inputs=[debate_state],
            outputs=[next_button, next_button2, debate_state]
        ).then(
            fn=debate_ui.next_round,
            inputs=[debate_state, judge_input],
            outputs=[
                topic_display,
                round1_feedback,
                round2_feedback,
                round3_feedback,
                round2_a,
                round2_b,
                round3_a,
                round3_b,
                round1_input_container,
                round2_input_container,
                tabs,
                next_button,
                next_button2,
                final_modal,
                debate_state
            ]
        )

        next_button2.click(
            fn=debate_ui.set_loading_state,
            inputs=[debate_state],
            outputs=[next_button, next_button2, debate_state]
        ).then(
            fn=debate_ui.next_round,
            inputs=[debate_state, judge_input2],
            outputs=[
                topic_display,
                round1_feedback,
                round2_feedback,
                round3_feedback,
                round2_a,
                round2_b,
                round3_a,
                round3_b,
                round1_input_container,
                round2_input_container,
                tabs,
                next_button,
                next_button2,
                final_modal,
                debate_state
            ]
        )
        
        # Show final judgment modal after Round 3
        next_button3.click(
            fn=debate_ui.show_final_judgment_modal,
            inputs=[debate_state],
            outputs=[final_modal, judgment_question_md, debate_state]
        )

        # Final judgment modal interactions
        judgment_choice.change(
            fn=debate_ui.handle_judgment_selection,
            inputs=[debate_state, judgment_choice],
            outputs=[confidence_container, debate_state]
        )
        
        confidence_slider.change(
            fn=debate_ui.update_confidence,
            inputs=[debate_state, confidence_slider],
            outputs=[reasoning_container, debate_state]
        )
        
        reasoning_input.change(
            fn=debate_ui.update_reasoning_counter,
            inputs=[reasoning_input, debate_state],
            outputs=[reasoning_char_counter, submit_judgment_btn]
        )
        
        # Submit final judgment
        submit_judgment_btn.click(
            fn=debate_ui.submit_final_judgment,
            inputs=[debate_state, reasoning_input],
            outputs=[
                final_modal,
                debate_interface,
                completion_screen,
                completion_html,
                debate_state
            ]
        )

    return demo

demo = create_debate_app()
demo.launch()