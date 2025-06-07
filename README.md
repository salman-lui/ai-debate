<div align="center">
  <h1>AI Debate Aids Assessment of Controversial Claims</h1>
  <p>
    <a href="https://arxiv.org/abs/2506.02175" target="_blank">[Paper]</a>
  </p>
  <p>AI debate improves human judgment accuracy on controversial claims by 10% over single-advisor consultancy, with persona-based LLM judges outperforming humans—demonstrating progress on scalable oversight for supervising AI systems beyond human expertise.</p>
</div>
<br>

![](visuals/debate-overview.png)

****************************************************************

This repository provides all resources for the paper ["AI Debate Aids Assessment of Controversial Claims"](https://arxiv.org/abs/2506.02175).

- [Quick Start](#quick-start)
- [LLM Judge Experiments](#llm-judge-experiments)
  - [Debate Mode](#debate-mode)
  - [Consultancy Mode](#consultancy-mode)
- [Human Judge Experiments](#human-judge-experiments)
- [Configuration](#configuration)
- [Data](#data)
- [Citation](#citation)

### Quick Start

#### Installation
```bash
git clone https://github.com/yourusername/ai-debate-consultancy.git
cd ai-debate-consultancy
pip install -r requirements.txt
```

#### Setup Configuration
Edit `config/config.yaml` to configure your API keys and model settings.

### LLM Judge Experiments

#### Debate Mode

**Single Run:**
```bash
python run_debate.py \
    --dataset covid \
    --debater default \
    --judge default \
    --debater-a-model gpt4o \
    --debater-b-model qwen \
    --judge-model gpt4o \
    --argue-for-debater-a correct
```

**Batch Processing (All Combinations):**
```bash
# Run all dataset/model/position combinations in parallel
bash scripts/debate/run_default_setup_debate_parallel.sh

# Sequential processing (if parallel not available)
bash scripts/debate/run_default_setup_debate_sequential.sh
```

This runs experiments with:
- Datasets: `covid`, `climate`
- Models: `gpt4o`, `qwen`
- Positions: `correct`, `incorrect`
- All debater A/B and judge model combinations

#### Consultancy Mode

**Single Run:**
```bash
python run_consultancy.py \
    --dataset covid \
    --consultant default \
    --judge default \
    --consultant-model gpt4o \
    --judge-model qwen \
    --argue-for correct
```

**Batch Processing:**
```bash
# Run all combinations in parallel
bash scripts/consultancy/run_default_setup_consultancy_parallel.sh

# Sequential processing
bash scripts/consultancy/run_default_setup_consultancy_sequential.sh
```

### Human Judge Experiments

This assumes you have CSV files with human judge responses, such as those exported from Prolific.

First, run the following script to generate personas:

> **Note:** The template inside the Python script will need to be modified depending on the fields in your CSV, and what you want each persona to say. It currently is set up for our COVID dataset.

```bash
# multiple CSVs can be passed in at once by repeating the -i flag
python get_personas_from_prolific.py -i input.csv
```

Then, to run a debate or consultancy experiment, run one of the following shell scripts. These scripts do two experiments: one which incorporates the simulated personas, and a control run which has the same claims but no persona.

> **Note:** these scripts are likewise configured to run on the COVID dataset. You will need to place JSON files containing the assigned claims for every Prolific response under `consultancy-claim-assignment-by-participant/PROLIFIC_ID.json` and `debate-claim-assignment-by-participant/PROLIFIC_ID.json`.

```bash
# runs consultancy both with and without the simulated personas
./scripts/consultancy/run_browsing_setup_with_without_personas.sh

# runs debate both with and without the simulated personas
./scripts/debate/run_browsing_setup_with_without_personas.sh
```

The claim assignment files are formatted as such:

```json
[
  {
    "claim": "Ferrets pass the novel coronavirus on to one another in a different way than humans do",
    "veracity": false,
    "label": "refute",
    "supporting_sources": [
      {
        "source_id": 1,
        "title": "SARS-CoV-2 is transmitted via contact and via the air between ferrets",
        "url": "https://www.nature.com/articles/s41467-020-17367-2",
        "content": "The study published in Nature Communications..."
      },
      {
        "source_id": 2,
        "title": "Infection and Rapid Transmission of SARS-CoV-2 in Ferrets",
        "url": "https://www.sciencedirect.com/science/article/pii/S1931312820301876",
        "content": "The message from Elsevier B.V. indicates a technical issue..."
      },
      ...
    ]
  },
  ...
]
```

### Configuration

Available options:
- **Datasets**: `covid`, `climate` 
- **Models**: `gpt4o`, `claude`, `qwen`, `deepseek`
- **Agent types**: `default`, `browsing`, `default-personalized`, `browsing-personalized`
- **Judge types**: `default`, `persona`

### Data

Results are automatically saved in structured JSON format:
```
saved-data/
├── debate/
│   └── debater_default_judge_default/
│       ├── covid/results_correct.json
│       └── climate/results_incorrect.json
└── consultancy/
    └── consultant_default_judge_default/
        ├── covid/results_correct.json
        └── climate/results_incorrect.json
```

Each experiment produces:
- Judge verdicts vs ground truth accuracy
- Confidence scores and calibration
- Complete conversation transcripts
- Model performance comparisons

### Citation

```bibtex
@misc{rahman2025aidebate,
      title={AI Debate Aids Assessment of Controversial Claims}, 
      author={Salman Rahman and Sheriff Issaka and Ashima Suvarna and Genglin Liu and James Shiffer and Jaeyoung Lee and Md Rizwan Parvez and Hamid Palangi and Shi Feng and Nanyun Peng and Yejin Choi and Julian Michael and Liwei Jiang and Saadia Gabriel},
```

