#!/bin/bash

# Exit on error
set -e

# Log directory
LOG_DIR="logs/debate"
mkdir -p "$LOG_DIR"

# Main log file
MAIN_LOG="$LOG_DIR/run_debater_browsing_judge_default_setup.log"

# All combinations
DATASETS=("climate" "covid")
DEBATER_A_MODELS=("gpt4o" "qwen")
DEBATER_B_MODELS=("gpt4o" "qwen")
JUDGE_MODELS=("gpt4o" "qwen")
POSITIONS=("correct" "incorrect")

# Log start time
echo "Starting parallel runs at $(date)" >> "$MAIN_LOG"

# Function to run a single combination
run_combination() {
    dataset=$1
    position=$2
    da_model=$3
    db_model=$4
    j_model=$5
    
    if python run_debate.py \
        --dataset "$dataset" \
        --debater "browsing" \
        --judge "default" \
        --debater-a-model "$da_model" \
        --debater-b-model "$db_model" \
        --judge-model "$j_model" \
        --argue-for-debater-a "$position"
    then
        echo "Success: dataset=$dataset position=$position debater_a=$da_model debater_b=$db_model judge=$j_model" >> "$MAIN_LOG"
    else
        echo "Failed: dataset=$dataset position=$position debater_a=$da_model debater_b=$db_model judge=$j_model (error: $?)" >> "$MAIN_LOG"
    fi
}

# Export function and log file for GNU Parallel
export -f run_combination
export MAIN_LOG

# Generate parameter combinations
parameter_combinations() {
    for dataset in "${DATASETS[@]}"; do
        for position in "${POSITIONS[@]}"; do
            for da_model in "${DEBATER_A_MODELS[@]}"; do
                for db_model in "${DEBATER_B_MODELS[@]}"; do
                    for j_model in "${JUDGE_MODELS[@]}"; do
                        echo "$dataset" "$position" "$da_model" "$db_model" "$j_model"
                    done
                done
            done
        done
    done
}

# Run combinations using GNU Parallel
parameter_combinations | parallel --progress --bar --eta \
    --jobs 16 \
    --colsep ' ' \
    run_combination {1} {2} {3} {4} {5}

# Log completion
echo "Completed all parallel runs at $(date)" >> "$MAIN_LOG"