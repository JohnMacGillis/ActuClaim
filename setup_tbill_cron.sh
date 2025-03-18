#!/bin/bash

# This script sets up a cron job to run the T-Bill updater twice a month

# Define the path to the Python script and virtual environment
APP_DIR="/root/actuclaim"
SCRIPT="$APP_DIR/tbill_updater.py"
VENV="$APP_DIR/venv/bin/python"

# Create the cron job commands
# Run on the 15th of each month at 6:00 AM
CRON_15TH="0 6 15 * * $VENV $SCRIPT >> $APP_DIR/tbill_updater_cron.log 2>&1"

# Run on the 1st of each month at 6:00 AM (to catch the end of previous month)
CRON_1ST="0 6 1 * * $VENV $SCRIPT >> $APP_DIR/tbill_updater_cron.log 2>&1"

# Add the cron jobs to the current crontab
(crontab -l 2>/dev/null | grep -v "$SCRIPT") | { cat; echo "$CRON_15TH"; echo "$CRON_1ST"; } | crontab -

echo "Cron job set up to run T-Bill updater on the 15th and 1st day of each month at 6:00 AM."
echo "Cron jobs added:"
echo "$CRON_15TH"
echo "$CRON_1ST"
