import gradio as gr
from dataclasses import dataclass

@dataclass
class RoundState:
    """Represents the UI state for a single consultation round."""
    status: gr.Markdown
    consultant_output: gr.Textbox
    judge_input: gr.Textbox
    char_counter: gr.Markdown
    submit_button: gr.Button