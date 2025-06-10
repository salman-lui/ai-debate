# LLM Consultancy UI

A web-based interface for the AI Consultancy system that enables human judges to evaluate claims with guidance from a single AI consultant. Built with Gradio, this UI provides an interactive consultation experience for assessing controversial claims with AI assistance.

## Overview

This UI component is part of the larger [AI Debate Aids Assessment of Controversial Claims](https://arxiv.org/abs/2506.02175) project. It provides:

- Interactive 3-round consultation with an AI advisor
- Initial and final judgment collection with confidence levels
- Real-time dialogue between human judge and AI consultant
- Evidence citation processing and display
- Integration with Prolific for human experiments
- Cloud storage for consultation transcripts

## Features

- **Multi-round Consultation**: Structured 3-round interaction with AI consultant
- **Interactive Dialogue**: Minimum 50-character responses for meaningful exchanges
- **Confidence Tracking**: Captures judge confidence before and after consultation
- **Evidence Support**: Processes and displays evidence with source citations
- **Responsive Design**: Clean interface with progress tracking
- **Data Persistence**: Automatic saving to Google Cloud Storage
- **Claim Management**: Automatic claim selection with usage tracking

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

1. Set up environment variables in `.env`:

```bash
GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

2. Configure consultation parameters in `config/config_web.yaml`

3. Set up consultant prompts in `config/prompts/consultancy/`

### Running the Application

**Local Development:**

```bash
python run_consultancy_gradio.py
```

**Docker Deployment:**

```bash
docker build -t llm-consultancy-ui .
docker run -p 7860:7860 llm-consultancy-ui
```

## Project Structure

```
llm-consultancy-ui/
├── agents/                      # AI consultant agent implementations
├── config/                      # Configuration files and prompts
│   ├── config_web.yaml         # Main configuration
│   └── prompts/                # Consultant prompt templates
├── data/                       # Claim datasets and tracking
│   └── 60-full-batch-2/       # COVID claims with usage counters
├── run_consultancy_gradio.py   # Main application entry point
├── consultation_ui_class.py    # UI logic and event handlers
├── consultant_runner_class.py  # Consultation orchestration
├── consultation_context_class.py # Context and state management
├── round_state_class.py        # Round-specific state
├── helper_functions.py         # Utility functions
├── gcp_storage.py             # Cloud storage interface
├── ui_utils.py                # UI styling utilities
├── welcome_template.py        # HTML templates
└── Dockerfile                 # Container configuration
```

## User Flow

1. **Terms Acceptance**: Users accept terms and conditions
2. **Experience Assessment**: Users rate their AI assistant experience (1-100 scale)
3. **Initial Judgment**: Users evaluate the claim before consultation
   - True/False selection
   - Confidence level (1-100)
4. **Consultation Rounds**:
   - Round 1: Initial consultation
   - Round 2: Follow-up questions and clarification
   - Round 3: Final consultation
5. **Final Judgment**: Users provide final verdict with:
   - True/False selection
   - Confidence level (1-100)
   - Written reasoning (min 50 characters)
6. **Completion**: Redirect to Prolific with completion code

## Key Components

### ConsultationUI Class

Manages the Gradio interface and user interactions:

- Modal flow control
- Character count validation
- Event handler setup
- Session state management

### ConsultancyRunner Class

Orchestrates the consultation process:

- Consultant initialization
- Round progression
- Transcript management
- Storage operations

### ConsultationContext Class

Manages consultation context and claim data:

- Claim loading with usage tracking
- Source randomization
- Transcript updates
- Context formatting for AI

### Helper Functions

Utilities for data management:

- Claim data loading from JSON
- Usage tracking to ensure even distribution
- Source formatting and randomization

## Data Collection

The system collects comprehensive consultation data:

### Claim Management

- Claims loaded from `data/60-full-batch-2/{prolific_id}_covid.json`
- Usage tracking in `{prolific_id}_claim_counter.json`
- Automatic selection of least-used claims
- Support for both supporting and opposing sources

## Integration with Prolific

The UI supports seamless Prolific integration:

- Automatic participant ID capture from URL parameters
- Claim assignment based on Prolific ID
- Usage tracking per participant
- Completion redirect with success code `C1DA3DDR`

## Customization

### Styling

Modify `ui_utils.py` to customize CSS and appearance.

## Environment Variables

```bash
GOOGLE_APPLICATION_CREDENTIALS  # Path to GCP service account key
# Additional API keys as needed for consultant models
```

## Citation

If you use this UI in your research, please cite:

```bibtex
@misc{rahman2025aidebate,
      title={AI Debate Aids Assessment of Controversial Claims},
      author={Salman Rahman and Sheriff Issaka and Ashima Suvarna and Genglin Liu and James Shiffer and Jaeyoung Lee and Md Rizwan Parvez and Hamid Palangi and Shi Feng and Nanyun Peng and Yejin Choi and Julian Michael and Liwei Jiang and Saadia Gabriel},
      year={2025}
}
```

## License

This project is part of the AI Debate research system. Please refer to the main repository for licensing information.

## Support

For issues or questions specific to the consultancy UI component, please open an issue in the main repository with the `[consultancy-UI]` tag.
