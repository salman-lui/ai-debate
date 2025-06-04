#!/bin/bash

# Exit on error
set -e

# Log directory
LOG_DIR="logs/consultancy"
mkdir -p "$LOG_DIR"

# Main log file
MAIN_LOG="$LOG_DIR/run_browsing_setup_with_personas.log"

POSITIONS=("correct" "incorrect")

run_personalized() {
    filename=$1
    position=$2

    # Extract the judge-prolific-id from the filename (part before the first '_')
    judge_id=$(basename "$1" | cut -d '_' -f1)
    # Run the Python script with the extracted ID and fixed dataset 'covid'
    if python run_consultancy.py \
        --dataset covid \
        --consultant browsing-personalized \
        --judge persona \
        --consultant-model gpt4o \
        --judge-model gpt4o \
        --argue-for "$position" \
        --judge-prolific-id "$judge_id"
    then
        echo "Success: personalized, prolific_id=$judge_id position=$position" >> "$MAIN_LOG"
    else
        echo "Failed: personalized, prolific_id=$judge_id position=$position (error: $?)" >> "$MAIN_LOG"
    fi
}

run_unpersonalized() {
    filename=$1
    position=$2

    # Extract the judge-prolific-id from the filename (part before the first '_')
    judge_id=$(basename "$1" | cut -d '_' -f1)
    # Run the Python script with the extracted ID and fixed dataset 'covid'
    if python run_consultancy.py \
        --dataset covid \
        --consultant browsing \
        --judge persona \
        --consultant-model gpt4o \
        --judge-model gpt4o \
        --argue-for "$position" \
        --judge-prolific-id "$judge_id"
    then
        echo "Success: unpersonalized, position=$position" >> "$MAIN_LOG"
    else
        echo "Failed: unpersonalized, position=$position (error: $?)" >> "$MAIN_LOG"
    fi
}


# Export function and log file for GNU Parallel
export -f run_personalized
export -f run_unpersonalized
export MAIN_LOG

# Generate parameter combinations
parameter_combinations() {
    for position in "${POSITIONS[@]}"; do
        for file in ./consultancy-claim-assignment-by-participant/*.json; do
            echo "$file" "$position"
        done
    done
}

# Run combinations using GNU Parallel
parameter_combinations | parallel --progress --bar --eta \
    --jobs 16 \
    --colsep ' ' \
    run_personalized {1} {2}

parameter_combinations | parallel --progress --bar --eta \
    --jobs 16 \
    --colsep ' ' \
    run_unpersonalized {1} {2}

# Log completion
echo "Completed all parallel runs at $(date)" >> "$MAIN_LOG"

# Usage:
# bash scripts/consultancy/run_browsing_setup_with_personas.sh