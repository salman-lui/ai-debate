# LLM Debater UI

A web-based interface for the AI Debate system that enables human judges to evaluate debates between AI agents on controversial claims. Built with Gradio, this UI provides an interactive experience for assessing AI-generated arguments.

## Overview

This UI component is part of the larger [AI Debate Aids Assessment of Controversial Claims](https://arxiv.org/abs/2506.02175) project. It provides:

- Interactive debate viewing with 3 rounds (Opening Arguments, Rebuttals, Closing Arguments)
- Initial and final judgment collection with confidence levels
- Real-time feedback mechanism for guiding debaters
- Citation processing and display
- Integration with Prolific for human experiments
- Cloud storage for debate transcripts

## Features

- **Multi-round Debate Format**: Structured 3-round debate with distinct phases
- **Judge Feedback System**: Minimum 50-character feedback requirements per round
- **Confidence Tracking**: Captures judge confidence before and after debates
- **Citation Support**: Processes and displays evidence with source links
- **Responsive Design**: Custom CSS interface
- **Data Persistence**: Automatic saving to Google Cloud Storage

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/salman-lui/ai-debate.git
# Install dependencies
pip install -r requirements.txt
cd ai-debate/llm-debater-ui
```

### Configuration

1. Set up Google Cloud credentials:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

2. Configure debate parameters in `config/config.yaml`

3. Set up debate prompts in `config/default-prompt/`

4. Set up OPENAI_API_KEY in your environment:

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

### Running the Application

**Local Development:**

```bash
python app.py
```

**Docker Deployment:**

```bash
docker build -t llm-debater-ui .
docker run -p 7860:7860 llm-debater-ui
```

## Project Structure

```
llm-debater-ui/
├── agents/              # Debate agent implementations
├── config/              # Configuration files and prompts
├── data-web/           # Web-specific data files
├── debate-data-final/  # Finalized debate datasets
├── utils/              # Utility functions
├── app.py              # Main Gradio application
├── debate_interface_class.py    # UI logic and handlers
├── debate_state_class.py        # State management
├── web_debate_manager.py        # Debate orchestration
├── gcp_storage.py              # Cloud storage interface
├── create_css.py               # CSS styling
├── welcome_html.py             # HTML templates
└── Dockerfile                  # Container configuration
```

## User Flow

1. **Terms Acceptance**: Users accept terms and conditions
2. **Experience Assessment**: Users rate their AI assistant experience (1-100)
3. **Initial Judgment**: Users evaluate the claim before seeing arguments
4. **Debate Viewing**:
   - Round 1: Opening Arguments
   - Round 2: Rebuttals (with judge feedback)
   - Round 3: Closing Arguments (with judge feedback)
5. **Final Judgment**: Users provide final verdict with confidence and reasoning
6. **Completion**: Redirect to Prolific with completion code

## Key Components

### DebateInterface Class

Handles all UI interactions and state transitions:

- Feedback validation
- Citation processing
- Round progression
- Judgment collection

### DebateState Class

Manages session state and data persistence:

- Transcript storage
- State synchronization
- Cloud storage integration

### WebDebateManager

Orchestrates the debate between AI agents:

- Agent initialization
- Round execution
- Context management

## Data Collection

The system collects:

- Initial and final judgments
- Confidence levels (1-100 scale)
- Judge feedback per round (min 50 characters)
- Final reasoning (min 50 characters)
- LLM experience level
- Complete debate transcripts

All data is automatically saved to Google Cloud Storage with session-based organization.

## Integration with Prolific

The UI supports Prolific integration for human experiments:

- Automatic participant ID capture from URL parameters
- Completion redirect with success code
- Session tracking for participant data

## Customization

### Styling

Modify `create_css.py` to customize the interface appearance.

### Debate Format

Adjust debate structure in `web_debate_manager.py`.

### Prompts

Update agent prompts in `config/default-prompt/` directory.

## Environment Variables

```bash
GOOGLE_APPLICATION_CREDENTIALS  # Path to GCP service account key
GRADIO_SERVER_NAME             # Server binding (default: 0.0.0.0)
GRADIO_SERVER_PORT             # Server port (default: 7860)
```

## License

This project is part of the AI Debate research system. Please refer to the main repository for licensing information.

## Support

For issues or questions specific to the UI component, please open an issue in the main repository with the `[debate-UI]` tag.
