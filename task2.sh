#!/bin/bash

# Configuration
WARMUP="-warmup_instructions 25000000"
SIM="-simulation_instructions 25000000"
TRACES=("trace1" "trace2" "trace3" "trace4")

EXCLUSIVE_BIN="./bin/champsim-exclusive-no"
NON_INCLUSIVE_BIN="./bin/champsim-no" # Updated path for non-inclusive simulation

EXCLUSIVE_DIR="results/Task2/exclusive"
NON_INCLUSIVE_DIR="results/Task2/non-inclusive"
RESULTS_DIR="results/Task2"

# --- Setup ---

echo "--- 1. Setting up result directories ---"
mkdir -p "$EXCLUSIVE_DIR"
mkdir -p "$NON_INCLUSIVE_DIR"
mkdir -p "$RESULTS_DIR"

# --- Simulation Runs ---

# 1. Run Exclusive (./bin/champsim-exclusive-no) simulations
echo "--- 2. Running Exclusive Cache Simulations ---"
for trace_name in "${TRACES[@]}"; do
    TRACE_PATH="./traces/${trace_name}.champsimtrace.xz"
    OUTPUT_FILE="$EXCLUSIVE_DIR/${trace_name}.txt"
    
    # Check if the output file already exists before running
    if [ -f "$OUTPUT_FILE" ]; then
        echo "  -> Skipped (Exclusive): Output file already exists at $OUTPUT_FILE"
        continue
    fi
    
    echo "  -> Executing $trace_name (Exclusive) | Output: $OUTPUT_FILE"
    # Run the exclusive configuration and redirect output to the designated file
    $EXCLUSIVE_BIN $WARMUP $SIM -traces "$TRACE_PATH" > "$OUTPUT_FILE" 2>&1
done

# 2. Run Non-Inclusive (./bin/champsim-no) simulations
echo "--- 3. Running Non-Inclusive Cache Simulations ---"
for trace_name in "${TRACES[@]}"; do
    TRACE_PATH="./traces/${trace_name}.champsimtrace.xz"
    OUTPUT_FILE="$NON_INCLUSIVE_DIR/${trace_name}.txt"

    # Check if the output file already exists before running
    if [ -f "$OUTPUT_FILE" ]; then
        echo "  -> Skipped (Non-Inclusive): Output file already exists at $OUTPUT_FILE"
        continue
    fi
    
    echo "  -> Executing $trace_name (Non-Inclusive) | Output: $OUTPUT_FILE"
    # Run the non-inclusive configuration and redirect output
    $NON_INCLUSIVE_BIN $WARMUP $SIM -traces "$TRACE_PATH" > "$OUTPUT_FILE" 2>&1
done

# --- Data Processing ---

# 3. Call the Python script to process logs, generate report, and create plot
echo "--- 4. Simulations finished. Processing results with process_results.py ---"
# Note: Ensure you have 'pandas' and 'matplotlib' installed: pip install pandas matplotlib
python3 task2_process_results.py

echo "--- Script Complete ---"
echo "Results (CSV and Plot) are available in the 'results/Task2' directory."