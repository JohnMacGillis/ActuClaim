from datetime import datetime
import logging
from tbill_utils import get_average_tbill_rate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_pji(loss_date, calculation_date=None, amount=0):
    """
    Calculate Pre-Judgment Interest based on average T-Bill rates
    
    Args:
        loss_date (str): Date of loss in 'YYYY-MM-DD' format
        calculation_date (str, optional): Date of calculation, defaults to today
        amount (float): The amount on which to calculate interest
        
    Returns:
        dict: PJI calculation results
    """
    try:
        # Convert loss_date to datetime
        loss_date_obj = datetime.strptime(loss_date, '%Y-%m-%d')
        
        # Set calculation_date to today if not provided
        if calculation_date is None:
            calculation_date_obj = datetime.now()
        else:
            calculation_date_obj = datetime.strptime(calculation_date, '%Y-%m-%d')
        
        # Calculate days between dates
        days_diff = (calculation_date_obj - loss_date_obj).days
        years_diff = days_diff / 365.25  # Using 365.25 to account for leap years
        
        # Get average T-Bill rate for the period
        avg_tbill_rate = get_average_tbill_rate(loss_date_obj, calculation_date_obj)
        
        # Fall back to a default rate if unable to calculate
        if avg_tbill_rate is None:
            logger.warning("Could not determine T-Bill rate, using default rate of 2.0%")
            avg_tbill_rate = 2.0
        
        # Calculate PJI
        interest_amount = (amount * avg_tbill_rate / 100) * years_diff
        
        return {
            'loss_date': loss_date,
            'calculation_date': calculation_date_obj.strftime('%Y-%m-%d'),
            'days_diff': days_diff,
            'years_diff': round(years_diff, 2),
            'tbill_rate': avg_tbill_rate,
            'amount': amount,
            'interest_amount': round(interest_amount, 2),
            'total_amount': round(amount + interest_amount, 2)
        }
    
    except Exception as e:
        logger.error(f"Error calculating PJI: {str(e)}")
        return {
            'error': str(e),
            'loss_date': loss_date,
            'calculation_date': calculation_date,
            'amount': amount,
            'interest_amount': 0,
            'total_amount': amount
        }

# Example usage
if __name__ == "__main__":
    result = calculate_pji('2022-04-01', amount=10000)
    print(f"PJI Calculation: {result}")
