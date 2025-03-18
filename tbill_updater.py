import os
import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import time

# Set up logging
logging.basicConfig(
    filename='tbill_updater.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TBillUpdater:
    def __init__(self, output_file_path):
        """
        Initialize the T-Bill rate updater.
        
        Args:
            output_file_path: Path to the Excel file where T-Bill rates are stored
        """
        self.output_file_path = output_file_path
        self.base_url = "https://www.bankofcanada.ca/rates/interest-rates/lookup-bond-yields/"
        
    def construct_url(self, start_date, end_date=None):
        """
        Construct the URL to fetch T-Bill rates for a date range.
        
        Args:
            start_date: The start date (datetime.date object)
            end_date: The end date (datetime.date object), defaults to start_date
            
        Returns:
            The constructed URL string
        """
        start_str = start_date.strftime('%Y-%m-%d')
        
        if end_date is None:
            end_date = start_date
            
        end_str = end_date.strftime('%Y-%m-%d')
        
        params = {
            'lookupPage': 'lookup_bond_yields.php',
            'startRange': '2015-03-18',  # This seems to be a fixed parameter in your URL
            'rangeType': 'dates',
            'dFrom': start_str,
            'dTo': end_str,
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
        
        url = f"{self.base_url}?{'&'.join(query_parts)}"
        return url
    
    def fetch_tbill_rates(self, start_date, end_date=None):
        """
        Fetch T-Bill rates for a date range from the Bank of Canada website.
        
        Args:
            start_date: The start date (datetime.date object)
            end_date: The end date (datetime.date object), defaults to start_date
            
        Returns:
            Dictionary mapping dates to rates
        """
        if end_date is None:
            end_date = start_date
            
        url = self.construct_url(start_date, end_date)
        logging.info(f"Fetching T-Bill rates from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} from URL: {url}")
        
        rates = {}
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Debug response information
            logging.info(f"Response status code: {response.status_code}")
            logging.info(f"Response content length: {len(response.content)}")
            
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get all tables
            all_tables = soup.find_all('table')
            logging.info(f"Found {len(all_tables)} tables on the page")
            
            # If no tables found, return empty dict
            if not all_tables:
                logging.warning("No tables found on the page")
                return rates
            
            # Process the last table (usually the relevant data table)
            data_table = all_tables[-1]
            
            # Extract the headers to understand the table structure
            headers = []
            header_row = data_table.find('tr')
            if header_row:
                header_cells = header_row.find_all(['th', 'td'])
                headers = [cell.text.strip() for cell in header_cells]
                logging.info(f"Table headers: {headers}")
            
            # Find column index for V39059 (the T-Bill rate code)
            v39059_index = None
            for i, header in enumerate(headers):
                if header == 'V39059':
                    v39059_index = i
                    break
            
            if v39059_index is None:
                logging.warning("V39059 column not found in table")
                return rates
            
            # Process date columns
            date_columns = []
            for i, header in enumerate(headers):
                if i > v39059_index and header:  # Date columns come after V39059
                    try:
                        date = datetime.datetime.strptime(header, '%Y-%m-%d').date()
                        date_columns.append((i, date))
                    except (ValueError, TypeError):
                        pass
            
            # If no date columns found, try getting dates from first column of data rows
            if not date_columns:
                data_rows = data_table.find_all('tr')[1:]  # Skip header row
                for row in data_rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        try:
                            date_str = cells[0].text.strip()
                            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                            
                            # Try to get the rate from the appropriate column
                            if v39059_index < len(cells):
                                rate_str = cells[v39059_index].text.strip()
                                if rate_str and rate_str.lower() != 'na' and rate_str.lower() != 'bank holiday':
                                    try:
                                        rate = float(rate_str.replace('%', '').strip())
                                        rates[date] = rate
                                        logging.info(f"Found rate {rate} for date {date}")
                                    except ValueError:
                                        logging.warning(f"Could not convert '{rate_str}' to float")
                        except ValueError:
                            pass
            else:
                # Extract rates from the first data row
                data_rows = data_table.find_all('tr')[1:]  # Skip header row
                for row in data_rows:
                    cells = row.find_all('td')
                    
                    for col_index, date in date_columns:
                        if col_index < len(cells):
                            rate_str = cells[col_index - 1].text.strip()  # Adjust index
                            if rate_str and rate_str.lower() != 'na' and rate_str.lower() != 'bank holiday':
                                try:
                                    rate = float(rate_str.replace('%', '').strip())
                                    rates[date] = rate
                                    logging.info(f"Found rate {rate} for date {date}")
                                except ValueError:
                                    logging.warning(f"Could not convert '{rate_str}' to float")
            
            # For multi-table pages, also check the first table for rates
            if len(all_tables) > 1:
                alt_table = all_tables[0]
                data_rows = alt_table.find_all('tr')[1:]  # Skip header row
                
                for row in data_rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        try:
                            date_str = cells[0].text.strip()
                            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                            rate_str = cells[1].text.strip()
                            
                            if rate_str and rate_str.lower() != 'na' and rate_str.lower() != 'bank holiday':
                                try:
                                    rate = float(rate_str.replace('%', '').strip())
                                    rates[date] = rate
                                    logging.info(f"Found rate {rate} for date {date} in alternative table")
                                except ValueError:
                                    pass
                        except (ValueError, IndexError):
                            pass
            
            return rates
            
        except requests.RequestException as e:
            logging.error(f"Error fetching data: {e}")
            return rates
    
    def update_excel_file(self, rates_dict):
        """
        Update the Excel file with new T-Bill rates.
        
        Args:
            rates_dict: Dictionary mapping dates to rates
            
        Returns:
            True if update was successful, False otherwise
        """
        if not rates_dict:
            logging.warning("No rates to update in Excel file")
            return False
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)
            
            # Initialize DataFrame
            if os.path.exists(self.output_file_path):
                # Load existing data
                df = pd.read_excel(self.output_file_path)
                logging.info(f"Loaded existing Excel file with {len(df)} rows")
                
                # Ensure Date column is datetime
                df['Date'] = pd.to_datetime(df['Date'])
            else:
                # Create new DataFrame
                df = pd.DataFrame(columns=['Date', 'T-Bill Rate'])
                logging.info("Creating new Excel file")
            
            # Add new rates or update existing ones
            updated_count = 0
            new_count = 0
            
            for date, rate in rates_dict.items():
                date_str = date.strftime('%Y-%m-%d')
                
                # Check if date exists
                if 'Date' in df.columns and len(df) > 0:
                    date_exists = False
                    df_dates = df['Date'].dt.strftime('%Y-%m-%d').tolist()
                    
                    if date_str in df_dates:
                        date_exists = True
                        idx = df_dates.index(date_str)
                        old_rate = df.loc[idx, 'T-Bill Rate']
                        
                        if old_rate != rate:
                            df.loc[idx, 'T-Bill Rate'] = rate
                            logging.info(f"Updated rate for {date_str} from {old_rate} to {rate}")
                            updated_count += 1
                    
                    if not date_exists:
                        # Add new row
                        new_row = pd.DataFrame({'Date': [pd.Timestamp(date)], 'T-Bill Rate': [rate]})
                        df = pd.concat([df, new_row], ignore_index=True)
                        logging.info(f"Added new rate {rate} for date {date_str}")
                        new_count += 1
                else:
                    # Add first row
                    new_row = pd.DataFrame({'Date': [pd.Timestamp(date)], 'T-Bill Rate': [rate]})
                    df = pd.concat([df, new_row], ignore_index=True)
                    logging.info(f"Added new rate {rate} for date {date_str}")
                    new_count += 1
            
            # Sort by date (newest first)
            df = df.sort_values(by='Date', ascending=False)
            
            # Save to Excel
            df.to_excel(self.output_file_path, index=False)
            logging.info(f"Successfully saved data to {self.output_file_path} (Updated: {updated_count}, New: {new_count})")
            return True
            
        except Exception as e:
            logging.error(f"Error updating Excel file: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return False
    
    def get_date_ranges_to_check(self):
        """
        Get date ranges to check based on bi-weekly update pattern.
        
        Returns:
            List of (start_date, end_date) tuples to check
        """
        today = datetime.date.today()
        
        # Try to ensure we have the most recent dates
        # First try just today
        ranges = [(today, today)]
        
        # Then try the most recent week
        week_ago = today - datetime.timedelta(days=7)
        ranges.append((week_ago, today))
        
        # Then try the most recent month
        month_ago = today - datetime.timedelta(days=30)
        ranges.append((month_ago, today))
        
        # If we're checking near the beginning or middle of month (1st or 15th),
        # add specific coverage for these dates
        day_of_month = today.day
        
        if 1 <= day_of_month <= 5:
            # If checking near 1st, add the previous month end
            prev_month_end = (today.replace(day=1) - datetime.timedelta(days=1))
            ranges.append((prev_month_end - datetime.timedelta(days=5), prev_month_end))
        
        if 14 <= day_of_month <= 16:
            # If checking near 15th, ensure we cover mid-month
            mid_month = today.replace(day=15)
            ranges.append((mid_month - datetime.timedelta(days=2), mid_month + datetime.timedelta(days=2)))
        
        return ranges
    
    def fill_gaps(self, target_date, rates_dict):
        """
        Fills gaps for specific dates by using nearby dates if needed.
        
        Args:
            target_date: The specific date we want to ensure has a rate
            rates_dict: Dictionary of available rates by date
            
        Returns:
            Rate for the target date (or closest available)
        """
        # If we have the exact date, use it
        if target_date in rates_dict:
            return target_date, rates_dict[target_date]
        
        # Check nearby dates (up to 5 days before and after)
        for days in range(1, 6):
            # Check day before
            before_date = target_date - datetime.timedelta(days=days)
            if before_date in rates_dict:
                logging.info(f"Using rate from {before_date} for {target_date}")
                return before_date, rates_dict[before_date]
            
            # Check day after
            after_date = target_date + datetime.timedelta(days=days)
            if after_date in rates_dict:
                logging.info(f"Using rate from {after_date} for {target_date}")
                return after_date, rates_dict[after_date]
        
        # If no nearby date found, return None
        return None, None
    
    def run_update(self):
        """
        Run the update process using a bi-weekly approach.
        
        Returns:
            True if successful, False otherwise
        """
        today = datetime.date.today()
        logging.info(f"Starting bi-weekly T-Bill rate update for {today.strftime('%Y-%m-%d')}")
        
        # Get all date ranges to check
        date_ranges = self.get_date_ranges_to_check()
        
        # Combined dictionary of all rates found
        all_rates = {}
        
        # Try each date range
        for start_date, end_date in date_ranges:
            logging.info(f"Checking date range from {start_date} to {end_date}")
            rates = self.fetch_tbill_rates(start_date, end_date)
            
            if rates:
                all_rates.update(rates)
                logging.info(f"Found {len(rates)} rates in this range")
            
            # Add small delay between requests
            time.sleep(1)
        
        if all_rates:
            logging.info(f"Found a total of {len(all_rates)} T-Bill rates")
            
            # Ensure we have rates for specific target dates (1st and 15th of month)
            target_dates = []
            
            # Add target dates for current month
            current_month = today.month
            current_year = today.year
            
            # 1st and 15th of current month
            target_dates.append(datetime.date(current_year, current_month, 1))
            target_dates.append(datetime.date(current_year, current_month, 15))
            
            # Add last day of previous month if we're early in the month
            if today.day <= 15:
                prev_month_end = (datetime.date(current_year, current_month, 1) - datetime.timedelta(days=1))
                target_dates.append(prev_month_end)
            
            # If today is not already in all_rates, ensure we add it
            if today not in all_rates:
                target_dates.append(today)
            
            # Fill gaps for target dates
            filled_rates = all_rates.copy()
            
            for target_date in target_dates:
                if target_date not in all_rates:
                    filled_date, filled_rate = self.fill_gaps(target_date, all_rates)
                    if filled_date and filled_rate:
                        filled_rates[target_date] = filled_rate
                        logging.info(f"Filled gap for {target_date} using rate {filled_rate} from {filled_date}")
            
            # Update Excel file with all rates
            success = self.update_excel_file(filled_rates)
            return success
        else:
            logging.warning("No T-Bill rates found in any date range")
            
            # Try to use existing rates from Excel file
            try:
                if os.path.exists(self.output_file_path):
                    df = pd.read_excel(self.output_file_path)
                    if 'Date' in df.columns and 'T-Bill Rate' in df.columns and len(df) > 0:
                        df['Date'] = pd.to_datetime(df['Date'])
                        df = df.sort_values('Date', ascending=False)
                        
                        if len(df) > 0:
                            latest_date = df.iloc[0]['Date'].date()
                            latest_rate = float(df.iloc[0]['T-Bill Rate'])
                            
                            # Use this rate for today if needed
                            if latest_date != today:
                                new_rates = {today: latest_rate}
                                success = self.update_excel_file(new_rates)
                                logging.info(f"Used existing rate {latest_rate} from {latest_date} for today ({today})")
                                return success
                            return True  # No update needed, already have today's rate
            except Exception as e:
                logging.error(f"Error while trying to use existing rates: {e}")
            
            return False


if __name__ == "__main__":
    # Define the path to the Excel file
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    excel_file = os.path.join(data_dir, 'TBill Rate (2022 to present).xlsx')
    
    # Create and run the updater
    updater = TBillUpdater(excel_file)
    updater.run_update()
