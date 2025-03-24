from datetime import datetime
from tbill_utils import get_average_tbill_rate

def calculate_past_lost_wages_with_interest(net_past_lost_wages, loss_date, pji_rate=None):
    """Calculate past lost wages with interest, always using T-Bill rates."""
    # Get current date
    current_date = datetime.now()
    
    # Calculate years between loss date and current date
    loss_date_obj = datetime.strptime(loss_date, '%Y-%m-%d')
    years_between = (current_date - loss_date_obj).days / 365.25  # Using 365.25 to account for leap years
    
    # Always calculate using T-Bill rates, ignoring any pji_rate parameter
    # Get average T-Bill rate for the period
    avg_tbill_rate = get_average_tbill_rate(loss_date, current_date.strftime('%Y-%m-%d'))
    
    # Fall back to a default rate if unable to calculate
    if avg_tbill_rate is None:
        pji_rate = 0.02  # Default to 2%
    else:
        pji_rate = avg_tbill_rate / 100  # Convert percentage to decimal
    
    # Calculate past loss with interest: Past Loss × (1 + Interest Rate)^Years Between
    past_loss_with_interest = net_past_lost_wages * (1 + pji_rate) ** years_between
    
    # Prepare calculation details
    calculation_details = {
        "Loss Date": loss_date,
        "Calculation Date": current_date.strftime('%Y-%m-%d'),
        "Years Between": round(years_between, 2),
        "PJI Rate": pji_rate * 100,  # Convert to percentage for display
        "Base Amount": net_past_lost_wages,
        "Interest Amount": past_loss_with_interest - net_past_lost_wages,
        "Past Lost Wages with Interest": past_loss_with_interest
    }
    
    return round(past_loss_with_interest, 2), calculation_details

def calculate_future_lost_wages_annuity(annual_lost_wages, time_horizon, discount_rate):
    """Calculate future lost wages as an annuity."""
    # Calculate total months for the time horizon
    total_months = int(time_horizon * 12)
    
    # Calculate present value using annuity formula
    # PV = PMT × (1 - (1 + r)^-n) / r
    if discount_rate == 0:
        present_value = annual_lost_wages * time_horizon
    else:
        r = discount_rate
        n = time_horizon
        present_value = annual_lost_wages * (1 - (1 + r) ** -n) / r
    
    # Prepare calculation details (for consistency with other functions)
    calculation_details = {
        "Annual Lost Wages": annual_lost_wages,
        "Time Horizon (Years)": time_horizon,
        "Total Months": total_months,
        "Discount Rate": discount_rate * 100,  # Convert to percentage for display
        "Present Value": present_value
    }
    
    return round(present_value, 2), total_months    
