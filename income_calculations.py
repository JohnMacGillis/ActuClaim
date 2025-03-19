# =============================================================================
# INCOME CALCULATION FUNCTIONS
# =============================================================================
import datetime

def calculate_take_home(income, province, working_days, hours_per_day, is_hourly=False, hours_per_week=None, dependents=0):
    """Calculate take-home pay after taxes and deductions."""
    # Import necessary functions from tax_calculations.py
    from tax_calculations import (
        calculate_federal_tax,
        calculate_provincial_tax,
        calculate_cpp_contributions,
        calculate_ei_contribution,
        calculate_dependent_benefit
    )
    
    # Calculate dependent benefit
    dependent_benefit = calculate_dependent_benefit(dependents)
    
    # Calculate taxes and deductions
    federal_tax = calculate_federal_tax(income, dependents)
    provincial_tax = calculate_provincial_tax(income, province, dependents)
    cpp_contribution, cpp2_contribution = calculate_cpp_contributions(income)
    ei_contribution = calculate_ei_contribution(income)

    # Adjust deductions based on province rules
    if province.lower() == "new brunswick":
        # In New Brunswick, CPP, CPP2, and EI are not deducted for damages calculations
        cpp_contribution, cpp2_contribution, ei_contribution = 0, 0, 0
    elif province.lower() == "prince edward island":
        federal_tax, provincial_tax, cpp_contribution, cpp2_contribution, ei_contribution = 0, 0, 0, 0, 0
    
    total_deductions = federal_tax + provincial_tax + cpp_contribution + cpp2_contribution + ei_contribution
    take_home_pay = income - total_deductions
    
    # Calculate different pay periods
    if is_hourly and hours_per_week is not None:
        weekly_net_pay = take_home_pay / 52
        days_per_week = 5
        daily_net_pay = weekly_net_pay / days_per_week
        hourly_net_pay = weekly_net_pay / hours_per_week
        monthly_net_pay = weekly_net_pay * 4.33
    else:
        daily_net_pay = take_home_pay / working_days
        hourly_net_pay = take_home_pay / (working_days * hours_per_day)
        weekly_net_pay = take_home_pay / 52
        monthly_net_pay = take_home_pay / 12

    return {
        "Gross Income": income,
        "Federal Tax": round(federal_tax, 2),
        f"{province.capitalize()} Tax": round(provincial_tax, 2),
        "CPP Contribution": cpp_contribution,
        "CPP2 Contribution": cpp2_contribution,
        "EI Contribution": ei_contribution,
        "Dependent Benefit": dependent_benefit,
        "Total Deductions": round(total_deductions, 2),
        "Net Pay (Provincially specific deductions for damages)": round(take_home_pay, 2),
        "Daily Net Pay": round(daily_net_pay, 2),
        "Hourly Net Pay": round(hourly_net_pay, 2),
        "Weekly Net Pay": round(weekly_net_pay, 2),
        "Monthly Net Pay": round(monthly_net_pay, 2),
        "Working Days": working_days
    }

def calculate_collateral_benefits(ei_benefits_to_date=0, section_b_to_date=0, ltd_benefits_to_date=0, 
                                 cppd_benefits_to_date=0, other_benefits_to_date=0,
                                 ei_benefits_annual=0, section_b_annual=0, ltd_benefits_annual=0,
                                 cppd_benefits_annual=0, other_benefits_annual=0,
                                 ei_start_date=None, loss_date=None, future_start_date=None):
    """Calculate collateral benefits with EI sickness benefits limitation."""
    
    # Default values if not provided from form
    if ei_benefits_to_date is None:
        ei_benefits_to_date = 0
    if section_b_to_date is None:
        section_b_to_date = 0
    if ltd_benefits_to_date is None:
        ltd_benefits_to_date = 0
    if cppd_benefits_to_date is None:
        cppd_benefits_to_date = 0
    if other_benefits_to_date is None:
        other_benefits_to_date = 0
    
    if ei_benefits_annual is None:
        ei_benefits_annual = 0
    if section_b_annual is None:
        section_b_annual = 0
    if ltd_benefits_annual is None:
        ltd_benefits_annual = 0
    if cppd_benefits_annual is None:
        cppd_benefits_annual = 0
    if other_benefits_annual is None:
        other_benefits_annual = 0
    
    # Calculate total past benefits
    total_past_benefits = (ei_benefits_to_date + section_b_to_date + 
                          ltd_benefits_to_date + cppd_benefits_to_date + 
                          other_benefits_to_date)
    
    # Initialize variables for EI calculation
    adjusted_annual_ei = ei_benefits_annual
    remaining_ei_days = None
    ei_benefits_info = {}
    
    # Calculate EI benefits considering 26-week limitation
    if ei_benefits_annual > 0 and ei_start_date and loss_date and future_start_date:
        try:
            # Convert string dates to datetime objects if needed
            if isinstance(ei_start_date, str):
                ei_start_date = datetime.datetime.strptime(ei_start_date, "%Y-%m-%d").date()
            if isinstance(loss_date, str):
                loss_date = datetime.datetime.strptime(loss_date, "%Y-%m-%d").date()
            if isinstance(future_start_date, str):
                future_start_date = datetime.datetime.strptime(future_start_date, "%Y-%m-%d").date()
            
            # Maximum EI period (26 weeks = 182 days)
            max_ei_period = 182
            
            # Calculate days from EI start to future damages start
            ei_days_used = max(0, (future_start_date - ei_start_date).days)
            
            # Calculate remaining EI days for future period
            remaining_ei_days = max(0, max_ei_period - ei_days_used)
            
            # Calculate what portion of annual EI benefits applies to future period
            future_ei_portion = min(1.0, remaining_ei_days / 365)
            
            # Adjust annual EI benefits for future period
            adjusted_annual_ei = ei_benefits_annual * future_ei_portion
            
            # Store additional EI information
            ei_benefits_info = {
                "EI Start Date": ei_start_date.strftime("%Y-%m-%d"),
                "EI Days Used": ei_days_used,
                "EI Remaining Days": remaining_ei_days,
                "EI Future Portion": future_ei_portion
            }
            
        except Exception as e:
            # If there's an error in date calculation, use the original annual amount
            print(f"Error calculating EI limitation: {e}")
            adjusted_annual_ei = ei_benefits_annual
    
    # Calculate total annual future benefits with adjusted EI
    total_annual_future_benefits = (adjusted_annual_ei + section_b_annual + 
                                   ltd_benefits_annual + cppd_benefits_annual + 
                                   other_benefits_annual)
    
    # Combine all benefit information
    result = {
        "EI Benefits (to date)": ei_benefits_to_date,
        "Section B Benefits (to date)": section_b_to_date,
        "LTD Benefits (to date)": ltd_benefits_to_date,
        "CPPD Benefits (to date)": cppd_benefits_to_date,
        "Other Benefits (to date)": other_benefits_to_date,
        "Total Past Benefits": total_past_benefits,
        
        "EI Benefits (annual)": adjusted_annual_ei,  # Adjusted for 26-week limit
        "Section B Benefits (annual)": section_b_annual,
        "LTD Benefits (annual)": ltd_benefits_annual,
        "CPPD Benefits (annual)": cppd_benefits_annual,
        "Other Benefits (annual)": other_benefits_annual,
        "Total Annual Future Benefits": total_annual_future_benefits
    }
    
    # Add EI specific information if available
    if ei_benefits_info:
        result.update(ei_benefits_info)
    
    return result

# Command-line interactive version for standalone use
def collect_collateral_benefits_interactive():
    """Collect and calculate collateral benefits information via command line."""
    print("\n--- Collateral Benefits Information ---")
    print("Please enter annual amounts for each benefit category:")
    
    ei_benefits = float(input("EI Benefits (annual amount): $").replace(',', '') or 0)
    ei_start_date_str = input("EI Benefits Start Date (YYYY-MM-DD) or leave blank: ").strip()
    ei_start_date = None
    if ei_start_date_str:
        try:
            ei_start_date = datetime.datetime.strptime(ei_start_date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Using default calculations.")
    
    section_b = float(input("Section B Benefits (annual amount): $").replace(',', '') or 0)
    ltd_benefits = float(input("LTD Benefits (annual amount): $").replace(',', '') or 0)
    cppd_benefits = float(input("CPPD Benefits (annual amount): $").replace(',', '') or 0)
    other_benefits = float(input("Other Benefits (annual amount): $").replace(',', '') or 0)
    
    # For interactive use, we'll simplify by using current date as future start date
    loss_date_str = input("Date of Loss (YYYY-MM-DD) or leave blank for today: ").strip()
    loss_date = datetime.date.today()
    if loss_date_str:
        try:
            loss_date = datetime.datetime.strptime(loss_date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Using today's date.")
    
    # Calculate benefits with EI limitation
    benefits = calculate_collateral_benefits(
        0, 0, 0, 0, 0,  # Past benefits (all zero for simplicity)
        ei_benefits, section_b, ltd_benefits, cppd_benefits, other_benefits,  # Annual benefits
        ei_start_date, loss_date, datetime.date.today()  # Dates
    )
    
    # Display results
    print("\nCalculated Collateral Benefits:")
    for key, value in benefits.items():
        print(f"{key}: ${value:,.2f}" if isinstance(value, (int, float)) else f"{key}: {value}")
    
    return benefits

if __name__ == "__main__":
    # Run interactive version if script is executed directly
    collect_collateral_benefits_interactive()
