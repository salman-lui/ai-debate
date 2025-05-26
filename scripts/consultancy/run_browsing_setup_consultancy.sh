#!/bin/bash

# Exit on error
set -e

# Setup logging
LOG_DIR="logs/consultancy"
mkdir -p "$LOG_DIR"
MAIN_LOG="$LOG_DIR/run_consultant_browsing_judge_default_setup.log"

# All combinations
DATASETS=("climate" "covid")
CONSULTANT_MODELS=("gpt4o" "qwen")
JUDGE_MODELS=("gpt4o" "qwen")
POSITIONS=( "correct" "incorrect")

# Log start time
echo "Starting parallel runs at $(date)" >> "$MAIN_LOG"

# Function to run a single combination
run_combination() {
    dataset=$1
    position=$2
    c_model=$3
    j_model=$4
    
    if python run_consultancy.py \
        --dataset "$dataset" \
        --consultant "browsing" \
        --judge "default" \
        --consultant-model "$c_model" \
        --judge-model "$j_model" \
        --argue-for "$position"
    then
        echo "Success: dataset=$dataset position=$position consultant=$c_model judge=$j_model" >> "$MAIN_LOG"
    else
        echo "Failed: dataset=$dataset position=$position consultant=$c_model judge=$j_model (error: $?)" >> "$MAIN_LOG"
    fi
}

# Export function and log file for GNU Parallel
export -f run_combination
export MAIN_LOG

# Generate parameter combinations
parameter_combinations() {
    for dataset in "${DATASETS[@]}"; do
        for position in "${POSITIONS[@]}"; do
            for c_model in "${CONSULTANT_MODELS[@]}"; do
                for j_model in "${JUDGE_MODELS[@]}"; do
                    echo "$dataset" "$position" "$c_model" "$j_model"
                done
            done
        done
    done
}

# Run combinations using GNU Parallel
parameter_combinations | parallel --progress --bar --eta \
    --jobs 16 \
    --colsep ' ' \
    run_combination {1} {2} {3} {4}

# Log completion
echo "Completed all parallel runs at $(date)" >> "$MAIN_LOG"

# Usage:
# bash scripts/consultancy/run_browsing_setup.sh 

# python run_consultancy.py --dataset climate --consultant browsing --judge default --consultant-model gpt4o --judge-model gpt4o --argue-for correct