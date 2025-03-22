import os
import sys
import traceback
import datetime
import requests

# Import your actual email function
try:
    from email_results import send_results_email
    print("Successfully imported email_results module")
except ImportError as e:
    print(f"Failed to import email_results: {e}")
    sys.exit(1)

# Import configuration
try:
    import mailgun_config
    print("Successfully imported mailgun_config")
except ImportError as e:
    print(f"Failed to import mailgun_config: {e}")

def test_integration():
    print("Starting email integration test...")
    
    try:
        # Create dummy test data similar to what your app would use
        recipient_email = "john@johnmacgillis.ca"  # Your email
        client_name = "Test Client"
        province = "Nova Scotia"
        calculation_details = {"Years Between": 2.5, "PJI Rate": 2.0, "Interest Amount": 100.00, "Dependents": "0"}
        present_value_details = {"present_value": 10000.00, "annual_salary": 50000.00, "discount_rate": 0.025}
        result = {"Gross Income": 50000.00, "Federal Tax": 5000.00, "Provincial Tax": 3000.00, "CPP Contribution": 1000.00, "EI Contribution": 500.00, "Net Pay (Provincially specific deductions for damages)": 40500.00}
        collateral_benefits = {"Total Past Benefits": 1000.00, "Total Annual Future Benefits": 500.00}
        missed_time_unit = "days"
        missed_time = 30
        past_lost_wages_with_interest = 3500.00
        net_past_lost_wages = 3400.00
        missed_pay = 4400.00
        total_damages = 13500.00
        birthdate = datetime.date(1980, 1, 1)
        retirement_age = 65
        loss_date = datetime.date(2023, 1, 1)
        current_date = datetime.date.today()
        ei_days_remaining = 30
        
        # Call the actual email function
        print("Calling send_results_email...")
        result = send_results_email(
            recipient_email=recipient_email,
            client_name=client_name,
            province=province,
            calculation_details=calculation_details,
            present_value_details=present_value_details,
            result=result,
            collateral_benefits=collateral_benefits,
            missed_time_unit=missed_time_unit,
            missed_time=missed_time,
            past_lost_wages_with_interest=past_lost_wages_with_interest,
            net_past_lost_wages=net_past_lost_wages,
            missed_pay=missed_pay,
            total_damages=total_damages,
            birthdate=birthdate,
            retirement_age=retirement_age,
            loss_date=loss_date,
            current_date=current_date,
            ei_days_remaining=ei_days_remaining
        )
        
        print(f"Email function returned: {result}")
        return result
        
    except Exception as e:
        print(f"Exception during integration test: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    test_integration()
