# Consultancy System
A structured consultancy system between a LLM consultant and judge to evaluate claims through multiple rounds of discussion.

## Core Components
- `run_consultancy.py`: Main orchestrator that manages the consultation process
- `agents/consultant.py`: Consultant agent that presents and defends arguments
- `agents/judge.py`: Judge agent that evaluates arguments
- `utils.py`: Shared utility functions
- `config/`: Configuration files for agents and prompts

## Prompt Structure
The system uses different judge prompts based on both consultant and judge types:

1. For Default Consultant:
   - `judge/default/no_persona_prompts.yaml`: Default judge
   - `judge/default/with_persona_prompts.yaml`: Persona-based judge

2. For Browsing Consultant:
   - `judge/browsing/no_persona_prompts.yaml`: Default judge
   - `judge/browsing/with_persona_prompts.yaml`: Persona-based judge

This ensures the judge's prompts align with the consultant's capabilities (e.g., browsing support).

## Setup
1. Configure settings in `config/config.yaml`:
   ```yaml
   consultant:
     name: "Consultant"
     provider: "openai"  # API provider (openai, anthropic, google, ollama, sglang)
     model: "gpt-4o"
     temperature: 0
     max_retries: 3
     argue_for: "fact"
     # For SGLang:
     # provider: "sglang"
     # model: "meta-llama/Meta-Llama-3.1-8B-Instruct"
     # port: 30000

   consultant_judge:
     name: "Consultant Judge"
     provider: "openai"
     model: "gpt-4o"
     temperature: 0
     max_retries: 3

   consultant_settings:
     max_rounds: 3
     word_limit: 150
   ```

2. Prompts are organized in:
   - `config/prompts/consultant/without_personalization/`: Default and browsing prompts
   - `config/prompts/consultant/with_personalization/`: Personalized prompts
   - `config/prompts/judge/`: Default and persona-based prompts

## Running the System
```bash
# Basic run
python run_consultancy.py --consultant default --judge default

# With browsing capability
python run_consultancy.py --consultant browsing --judge default

# With judge persona
python run_consultancy.py --consultant default --judge persona
python run_consultancy.py --consultant browsing --judge persona

# With personalization
python run_consultancy.py --consultant default-personalized --judge persona
python run_consultancy.py --consultant browsing-personalized --judge persona
```

## Available Options
- Consultant types: `default`, `browsing`, `default-personalized`, `browsing-personalized`
- Judge types: `default`, `persona`
- Supported providers: `openai`, `anthropic`, `google`, `ollama`, `sglang`

## Output
Each run creates a timestamped directory under `saved-data/consultancy/<consultant_type>_<judge_type>/` containing:
- `consultancy.log`: Detailed logging of the consultation process
- `consultation.json`: Structured output with:
  - Metadata (claim, models, settings)
  - Round-by-round data (consultant arguments and judge responses)

Each consultation runs for 3 rounds where:
1. Consultant presents initial argument
2. Judge evaluates and questions the argument
3. Final round includes judge's decision

The consultation follows a structured format with:
- Clear argument presentation
- Evidence-based reasoning
- Focused questioning
- Balanced evaluation