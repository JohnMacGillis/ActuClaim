import os
import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import time

# Set up logging
logging.basicConfig(
    filename='tbill_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def construct_url(date):
    """
    Construct the URL to fetch T-Bill rates for a specific date.
    
    Args:
        date: The date to fetch rates for (datetime.date object)
        
    Returns:
        The constructed URL string
    """
    date_str = date.strftime('%Y-%m-%d')
    
    params = {
        'lookupPage': 'lookup_bond_yields.php',
        'startRange': '2015-03-18',  # This seems to be a fixed parameter in your URL
        'rangeType': 'dates',
        'dFrom': date_str,
        'dTo': date_str,
        'rangeValue': '1',
        'rangeWeeklyValue': '1',
        'rangeMonthlyValue': '1',
        'series[]': 'LOOKUPS_V39059',  # This is the T-Bill rate series
        'submit_button': 'Submit'
    }
    
    # Construct query string
    query_parts = []
    for key, value in params.items():
        if key == 'series[]':
            query_parts.append(f"{key}={value}")
        else:
            query_parts.append(f"{key}={value}")
    
    url = f"https://www.bankofcanada.ca/rates/interest-rates/lookup-bond-yields/?{'&'.join(query_parts)}"
    return url

def fetch_tbill_rate(date):
    """
    Fetch T-Bill rate for a specific date from the Bank of Canada website and save HTML for inspection.
    
    Args:
        date: The date to fetch the rate for (datetime.date object)
    """
    url = construct_url(date)
    print(f"Fetching T-Bill rate for {date.strftime('%Y-%m-%d')} from URL: {url}")
    logging.info(f"Fetching T-Bill rate for {date.strftime('%Y-%m-%d')} from URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Debug response information
        print(f"Response status code: {response.status_code}")
        print(f"Response content length: {len(response.content)}")
        logging.info(f"Response status code: {response.status_code}")
        logging.info(f"Response content length: {len(response.content)}")
        
        # Save the HTML content to a file
        html_filename = f"bankofcanada_{date.strftime('%Y-%m-%d')}.html"
        with open(html_filename, "wb") as f:
            f.write(response.content)
        print(f"Saved HTML content to {html_filename}")
        logging.info(f"Saved HTML content to {html_filename}")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables
        all_tables = soup.find_all('table')
        print(f"Found {len(all_tables)} tables on the page")
        logging.info(f"Found {len(all_tables)} tables on the page")
        
        # For each table, print some info
        for i, table in enumerate(all_tables):
            print(f"\nTable {i+1}:")
            logging.info(f"Table {i+1}:")
            
            # Check for caption
            caption = table.find('caption')
            if caption:
                print(f"Caption: {caption.text.strip()}")
                logging.info(f"Caption: {caption.text.strip()}")
            
            # Check for headers
            headers = []
            header_row = table.find('tr')
            if header_row:
                header_cells = header_row.find_all(['th', 'td'])
                headers = [cell.text.strip() for cell in header_cells]
                print(f"Headers: {headers}")
                logging.info(f"Headers: {headers}")
            
            # Count rows
            rows = table.find_all('tr')
            print(f"Number of rows: {len(rows)}")
            logging.info(f"Number of rows: {len(rows)}")
            
            # Sample of first data row if exists
            if len(rows) > 1:
                data_row = rows[1]
                cells = data_row.find_all('td')
                if cells:
                    cell_texts = [cell.text.strip() for cell in cells]
                    print(f"First data row: {cell_texts}")
                    logging.info(f"First data row: {cell_texts}")
        
        print("\n" + "-"*50 + "\n")
        logging.info("-"*50)
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        logging.error(f"Error fetching data: {e}")
        import traceback
        traceback.print_exc()
        logging.error(traceback.format_exc())


# Dates to check
dates_to_check = [
    datetime.date(2025, 3, 15),  # The date mentioned
    datetime.date(2025, 3, 14),  # One day before
    datetime.date(2025, 3, 1),   # Start of month
    datetime.date(2024, 10, 15), # Within knowledge cutoff
    datetime.date(2023, 12, 15), # Older date that should have data
    datetime.date(2023, 1, 15)   # Even older date
]

# Check each date
for date in dates_to_check:
    fetch_tbill_rate(date)
    time.sleep(1)  # Delay to avoid overwhelming the server

print("Debug completed. HTML files have been saved for inspection.")
logging.info("Debug completed. HTML files have been saved for inspection.")
