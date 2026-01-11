#!/bin/bash
# toolforge-jobs run owidcat --image python3.9 --command "~/OWID-categories/owid_task.sh"

cd OWID-categories
~/local/bin/python3 src/fetch_commons_files.py
~/local/bin/python3 src/run_categorize.py
~/local/bin/python3 src/run_categorize.py --work-path continents --files-type maps
