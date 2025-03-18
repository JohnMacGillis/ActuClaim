# T-Bill Rate Auto-Update System

## Overview

The system automatically updates T-Bill rates from the Bank of Canada website and maintains a comprehensive record in the Excel file at `/root/actuclaim/data/TBill Rate (2022 to present).xlsx`. This data is used for pre-judgment interest (PJI) calculations in the ActuClaim application.

## Key Features

- **Bi-Weekly Updates**: The system ensures rates are available for the 1st and 15th of each month, plus the current date.
- **Automatic Scheduling**: Updates run via cron jobs on the 1st and 15th of each month at 6:00 AM.
- **Intelligent Data Collection**: Uses date ranges to efficiently collect multiple rates with fewer API calls.
- **Gap Filling**: Automatically uses nearby dates when rates aren't available for specific dates.
- **Fallback Mechanisms**: Falls back to existing data when new rates can't be fetched.
- **Detailed Logging**: All activities are logged to `/root/actuclaim/tbill_updater.log`.

## Components

### 1. T-Bill Updater Script (`tbill_updater.py`)

The main script that fetches T-Bill rates from the Bank of Canada website and updates the Excel file.

Key functions:
- `fetch_tbill_rates()`: Retrieves rates for a date range
- `update_excel_file()`: Updates the Excel file with new rates
- `fill_gaps()`: Ensures rates are available for key dates
- `run_update()`: Main function that orchestrates the update process

### 2. Cron Job Setup (`setup_tbill_cron.sh`)

Configures cron jobs to automatically run the T-Bill updater on the 1st and 15th of each month.

### 3. T-Bill Report Tool (`tbill_report.py`)

A utility script for generating reports on T-Bill rates:

```bash
# View rates for the last 90 days
python tbill_report.py

# Specify a different number of days
python tbill_report.py 30
```

## How It Works

1. **Data Collection**: The system queries the Bank of Canada website for T-Bill rates (series V39059).
2. **Data Processing**: Rates are extracted from HTML tables and organized by date.
3. **Gap Filling**: Missing dates are filled with rates from the nearest available date.
4. **Data Storage**: All rates are stored in an Excel file for easy access by the application.

## Maintenance Tasks

### Regular Checks

```bash
# Check the logs to ensure updates are running properly
tail -n 50 tbill_updater.log

# Verify the Excel file is being updated
ls -la /root/actuclaim/data/TBill\ Rate\ \(2022\ to\ present\).xlsx

# Test the updater manually
python tbill_updater.py
```

### Troubleshooting

If the updater fails to run properly:

1. Check the logs for error messages:
   ```bash
   grep "ERROR" tbill_updater.log
   ```

2. Verify the cron jobs are set up correctly:
   ```bash
   crontab -l
   ```

3. Test network connectivity to the Bank of Canada website:
   ```bash
   curl -I https://www.bankofcanada.ca/rates/interest-rates/lookup-bond-yields/
   ```

## Implementation Details

The T-Bill updater was implemented to handle various edge cases:

- **Weekend Dates**: Properly handles weekends by using the closest business day rates
- **Bank Holidays**: Recognizes bank holidays and uses appropriate nearby rates
- **Missing Data**: Uses fallback mechanisms when data can't be retrieved
- **Different Table Formats**: Handles various HTML table formats used by the Bank of Canada

## Integration with ActuClaim

The T-Bill rates are used by the `calculate_past_lost_wages_with_interest` function in `app.py` and accessed through the `get_average_tbill_rate` function in `tbill_utils.py`.

No changes to the existing application code were needed, as the auto-updater maintains the Excel file in the format expected by the application.
