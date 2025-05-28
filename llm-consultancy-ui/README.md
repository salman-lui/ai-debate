# LLM Consultation Web Interface

A web-based interface for the AI consultation system, allowing human judges to interact with an AI consultant in real-time.

## Features
- Interactive web UI for consultation sessions
- Random claim selection from COVID dataset
- Real-time character counting for responses
- Multi-round consultation (3 rounds)
- Initial and final judgment collection
- Automatic source randomization
- Session transcript saving

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Configuration
Three main configuration files:
- `config/config_web.yaml`: Web UI settings and consultant configuration
- `data/check-covid/.../with_source_final_covid_test_agreed_claims.json`: Claims dataset
- `config/prompts/.../browsing_prompts.yaml`: Consultant prompts

### 3. Running the UI
```bash
python consultancy_web/run_consultancy_gradio.py
```
The interface will be available at `http://0.0.0.0:7860`

## Usage Flow
1. Accept terms and conditions
2. Make initial judgment on the claim
3. Participate in 3 rounds of consultation:
   - Read consultant's analysis
   - Provide feedback (within word limit)
4. Make final judgment with confidence level
5. View session summary

## Data Storage
Session transcripts are saved with:
- Claim details and sources
- All consultation rounds
- Initial/final judgments
- Metadata (model, temperature, timestamps)

## Requirements
- Python 3.8+
- Gradio
- PyYAML
- Google Cloud Storage (for transcript storage)
