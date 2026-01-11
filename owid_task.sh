#!/bin/bash
# toolforge-jobs run owidcat --image tf-python39 --command "~/OWID-categories/owid_task.sh"

set -euo pipefail

# Configuration
PROJECT_DIR="$HOME/OWID-categories"
PYTHON_BIN="$HOME/local/bin/python3"
LOG_FILE="$PROJECT_DIR/logs/task_$(date +%Y%m%d).log"

# Setup env
mkdir -p "$PROJECT_DIR/logs"
cd "$PROJECT_DIR"

echo "[$(date)] Starting OWID processing task" | tee -a "$LOG_FILE"

# Phase 1: Fetch and classify
echo "Running Phase 1: Fetching files..." | tee -a "$LOG_FILE"
"$PYTHON_BIN" src/fetch_commons_files.py 2>&1 | tee -a "$LOG_FILE"

# Phase 2: Automated Categorization
echo "Running Phase 2: Categorizing countries..." | tee -a "$LOG_FILE"
"$PYTHON_BIN" src/run_categorize.py 2>&1 | tee -a "$LOG_FILE"

echo "Running Phase 2: Categorizing continent maps..." | tee -a "$LOG_FILE"
"$PYTHON_BIN" src/run_categorize.py --work-path continents --files-type maps 2>&1 | tee -a "$LOG_FILE"

echo "[$(date)] Task completed" | tee -a "$LOG_FILE"
