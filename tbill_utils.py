import os
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to the T-Bill rates Excel file with correct filename
TBILL_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'TBill Rate (2022 to present).xlsx')

def load_tbill_rates():
    """
    Load T-Bill rates from Excel file
    Returns a pandas DataFrame with dates and rates
    """
    try:
        # Log the file path
        logger.info(f"Attempting to load T-Bill rates from: {TBILL_FILE_PATH}")
        
        # Check if file exists
        if not os.path.exists(TBILL_FILE_PATH):
            logger.error(f"T-Bill rate file not found at: {TBILL_FILE_PATH}")
            return None
            
        # Read the Excel file
        logger.info("File exists, attempting to read Excel data")
        df = pd.read_excel(TBILL_FILE_PATH)
        
        # Log the columns found
        logger.info(f"Excel file columns: {df.columns.tolist()}")
        
        # Ensure column names are as expected
        if 'Date' not in df.columns or 'T-Bill Rate' not in df.columns:
            column_names = df.columns.tolist()
            logger.warning(f"Expected columns not found. Found: {column_names}")
            # If column names don't match, try to rename them
            if len(column_names) >= 2:
                logger.info(f"Attempting to rename columns: {column_names[0]} -> Date, {column_names[1]} -> T-Bill Rate")
                df = df.rename(columns={column_names[0]: 'Date', column_names[1]: 'T-Bill Rate'})
            else:
                logger.error(f"Unexpected Excel structure. Columns: {column_names}")
                return None
        
        # Convert Date column to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        logger.info(f"Converted Date column. Sample dates: {df['Date'].head(3).tolist()}")
        
        # Convert T-Bill Rate to float, handling non-numeric values
        df['T-Bill Rate'] = pd.to_numeric(df['T-Bill Rate'], errors='coerce')
        # Log any NaN values
        nan_count = df['T-Bill Rate'].isna().sum()
        if nan_count > 0:
            logger.warning(f"Found {nan_count} non-numeric values in T-Bill Rate column")
        
        # Drop rows with NaN values (which were non-numeric)
        df = df.dropna(subset=['T-Bill Rate'])
        
        # Sort by date
        df = df.sort_values('Date')
        
        logger.info(f"Successfully loaded {len(df)} T-Bill rates")
        if not df.empty:
            logger.info(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
            logger.info(f"T-Bill rate range: {df['T-Bill Rate'].min()}% to {df['T-Bill Rate'].max()}%")
        return df
    
    except Exception as e:
        logger.error(f"Error loading T-Bill rates: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def get_average_tbill_rate(start_date, end_date=None):
    """
    Calculate the average T-Bill rate between start_date and end_date
    
    Args:
        start_date (str or datetime): Date of loss in 'YYYY-MM-DD' format or datetime object
        end_date (str or datetime, optional): Date of calculation, defaults to today
        
    Returns:
        float: Average T-Bill rate, or None if calculation fails
    """
    try:
        # Convert string dates to datetime if necessary
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            logger.info(f"Converted start_date string to datetime: {start_date}")
        
        if end_date is None:
            end_date = datetime.now()
            logger.info(f"Using current date as end_date: {end_date}")
        elif isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            logger.info(f"Converted end_date string to datetime: {end_date}")
        
        logger.info(f"Calculating average T-Bill rate between {start_date.date()} and {end_date.date()}")
        
        # Load T-Bill rates
        rates_df = load_tbill_rates()
        if rates_df is None:
            logger.error("Failed to load T-Bill rates, returning default rate of 2.5%")
            return 2.5
        
        # Filter rates between start_date and end_date
        mask = (rates_df['Date'] >= start_date) & (rates_df['Date'] <= end_date)
        filtered_df = rates_df[mask]
        
        if filtered_df.empty:
            logger.warning(f"No T-Bill rates found between {start_date} and {end_date}")
            
            # Use the closest available rate as a fallback
            if not rates_df.empty:
                if start_date < rates_df['Date'].min():
                    # If start_date is before earliest available rate, use earliest rate
                    closest_rate = rates_df.iloc[0]['T-Bill Rate']
                    logger.info(f"Using earliest available rate: {closest_rate}")
                    return closest_rate
                elif end_date > rates_df['Date'].max():
                    # If end_date is after latest available rate, use latest rate
                    closest_rate = rates_df.iloc[-1]['T-Bill Rate']
                    logger.info(f"Using latest available rate: {closest_rate}")
                    return closest_rate
            
            logger.error("Could not determine appropriate T-Bill rate, returning default rate of 2.5%")
            return 2.5
        
        # Calculate average rate
        avg_rate = filtered_df['T-Bill Rate'].mean()
        logger.info(f"Average T-Bill rate between {start_date.date()} and {end_date.date()}: {avg_rate:.2f}%")
        
        return round(avg_rate, 2)
    
    except Exception as e:
        logger.error(f"Error calculating average T-Bill rate: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        logger.error("Returning default rate of 2.5% due to error")
        return 2.5

# Example usage
if __name__ == "__main__":
    # Test the function with a sample date range
    today = datetime.now()
    six_months_ago = today - timedelta(days=180)
    avg_rate = get_average_tbill_rate(six_months_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
    print(f"Average T-Bill rate for last 6 months: {avg_rate}%")
    
    # Test with various date ranges
    test_ranges = [
        ("Last month", today - timedelta(days=30), today),
        ("Last year", today - timedelta(days=365), today),
        ("2022-2023", datetime(2022, 1, 1), datetime(2023, 12, 31)),
        ("All time", datetime(2000, 1, 1), today)
    ]
    
    for label, start, end in test_ranges:
        rate = get_average_tbill_rate(start, end)
        print(f"{label}: {rate}%")
