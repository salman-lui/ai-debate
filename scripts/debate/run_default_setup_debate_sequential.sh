#!/bin/bash

# Exit on error
set -e

# Log file
LOG_FILE="run_debater_default_judge_default_setup.log"


# Full combinations (commented out)
# DATASETS=("covid" "climate")
# DEBATER_A_MODELS=("gpt4o" "claude" "qwen" "deepseek")
# DEBATER_B_MODELS=("gpt4o" "claude" "qwen" "deepseek")
# JUDGE_MODELS=("gpt4o" "claude" "qwen" "deepseek")
# POSITIONS=("correct" "incorrect")


# All combinations
DATASETS=("climate")
DEBATER_A_MODELS=("gpt4o")
DEBATER_B_MODELS=("qwen")
JUDGE_MODELS=("gpt4o")
POSITIONS=("correct")

# Log start time
echo "Starting runs at $(date)" >> "$LOG_FILE"

# Run all combinations for default-default setup
for dataset in "${DATASETS[@]}"
do
    for position in "${POSITIONS[@]}"
    do
        for da_model in "${DEBATER_A_MODELS[@]}"
        do
            for db_model in "${DEBATER_B_MODELS[@]}"
            do
                for j_model in "${JUDGE_MODELS[@]}"
                do
                    # Log the current run
                    echo "Running: dataset=${dataset} debater_a=${da_model} debater_b=${db_model} judge=${j_model} position=${position}" >> "$LOG_FILE"
                    
                    # Run the debate
                    if python run_debate.py \
                        --dataset "${dataset}" \
                        --debater "default" \
                        --judge "default" \
                        --debater-a-model "${da_model}" \
                        --debater-b-model "${db_model}" \
                        --judge-model "${j_model}" \
                        --argue-for-debater-a "${position}"
                    then
                        echo "Successfully completed run" >> "$LOG_FILE"
                    else
                        echo "Failed run with exit code $?" >> "$LOG_FILE"
                    fi
                done
            done
        done
    done
done

# Log completion
echo "Completed all runs at $(date)" >> "$LOG_FILE"

# Usage:
# bash scripts/debate/run_default_setup_debate_sequential.sh
