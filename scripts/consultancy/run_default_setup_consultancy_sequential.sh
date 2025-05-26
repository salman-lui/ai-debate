#!/bin/bash

# Exit on error
set -e

# Log file
LOG_FILE="run_consultant_default_judge_default_setup.log"

# # All combinations
# DATASETS=("covid" "climate")
# CONSULTANT_MODELS=("gpt4o" "claude" "qwen")
# JUDGE_MODELS=("gpt4o" "claude" "qwen")
# POSITIONS=("correct" "incorrect")


# Modified combinations including DeepSeek
DATASETS=("climate")
CONSULTANT_MODELS=("deepseek")  # Added deepseek
JUDGE_MODELS=("deepseek")  # Added deepseek
POSITIONS=("incorrect")


# Log start time
echo "Starting runs at $(date)" | tee -a "$LOG_FILE"

# Run all combinations for default-default setup
for dataset in "${DATASETS[@]}"; do
    for position in "${POSITIONS[@]}"; do
        for c_model in "${CONSULTANT_MODELS[@]}"; do
            for j_model in "${JUDGE_MODELS[@]}"; do
                echo "Running: dataset=$dataset consultant=$c_model judge=$j_model position=$position" | tee -a "$LOG_FILE"
                if python run_consultancy.py \
                    --dataset "$dataset" \
                    --consultant "default" \
                    --judge "default" \
                    --consultant-model "$c_model" \
                    --judge-model "$j_model" \
                    --argue-for "$position"; then
                    echo "Successfully completed run" | tee -a "$LOG_FILE"
                else
                    echo "Failed run with exit code $?" | tee -a "$LOG_FILE"
                fi
            done
        done
    done
done

echo "Completed all runs at $(date)" | tee -a "$LOG_FILE"

# Usage:
# bash scripts/run_default_setup.sh