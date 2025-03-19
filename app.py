from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
import datetime
import traceback
from pji_routes import pji_routes
from werkzeug.utils import secure_filename

# Import calculation functions
from income_calculations import calculate_take_home, calculate_collateral_benefits
from lost_wages_calculations import (
    calculate_past_lost_wages_with_interest,
    calculate_future_lost_wages_annuity
)
from pdf_generation import create_enhanced_pdf_report

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['APP_NAME'] = 'ActuClaim'
app.secret_key = 'your_secret_key'  # Replace with your actual secret key
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documents')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Make app name available in all templates
@app.context_processor
def inject_app_name():
    return dict(app_name=app.config['APP_NAME'])

@app.route('/')
def index():
    return render_template('index.html', title='ActuClaim - Economic Damages Calculator')

@app.route('/calculate', methods=['POST'])
def calculate():
    # Initialize variables that might be used later
    past_lost_wages_with_interest = 0
    calculation_details = {}
    present_value = 0
    try:
        # Get client information
        client_name = request.form.get('client_name', 'Client')
        province = request.form.get('province', 'nova scotia')
        dependents = int(request.form.get("dependents", "0"))
        # Get number of dependents
        dependents = int(request.form.get("dependents", 0))
        # Get number of dependents
        dependents = int(request.form.get("dependents", 0))
        
        # Helper function for safe float conversion
        def safe_float(value_str, default=0):
            if not value_str:
                return default
            try:
                return float(value_str.replace(',', ''))
            except:
                return default
        
        # Get employment information
        employment_type = request.form.get('employment_type', 'salaried')
        is_hourly = (employment_type == 'hourly')
        
        # Initialize variables with default values
        hours_per_week = 40  # Default value
        hours_per_day = 8    # Default value
        working_days = int(request.form.get('working_days', 252))
        
        if is_hourly:
            include_vacation_pay = request.form.get('include_vacation_pay') == 'yes'
            hourly_rate = safe_float(request.form.get('hourly_rate'), 0)
            hours_per_week = safe_float(request.form.get('hours_per_week'), 40)
            salary = hourly_rate * hours_per_week * 52
            if include_vacation_pay:
                salary *= 1.04
            hours_per_day = hours_per_week / 5
        else:
            salary = safe_float(request.form.get('salary'), 0)
            hours_per_day = safe_float(request.form.get('hours_per_day'), 8)
        
        # Get number of dependents
        num_dependents = int(request.form.get("num_dependents", 0))

        # Calculate take-home pay
        result = calculate_take_home(salary, province, working_days, hours_per_day, is_hourly, hours_per_week, dependents)
        
        # Get collateral benefits
        ei_benefits_to_date = safe_float(request.form.get('ei_benefits_to_date'))
        section_b_to_date = safe_float(request.form.get('section_b_to_date'))
        ltd_benefits_to_date = safe_float(request.form.get('ltd_benefits_to_date'))
        cppd_benefits_to_date = safe_float(request.form.get('cppd_benefits_to_date'))
        other_benefits_to_date = safe_float(request.form.get('other_benefits_to_date'))
        
        ei_benefits_annual = safe_float(request.form.get('ei_benefits_annual'))
        section_b_annual = safe_float(request.form.get('section_b_annual'))
        ltd_benefits_annual = safe_float(request.form.get('ltd_benefits_annual'))
        cppd_benefits_annual = safe_float(request.form.get('cppd_benefits_annual'))
        other_benefits_annual = safe_float(request.form.get('other_benefits_annual'))
        
        # Get dates with safe defaults
        today = datetime.date.today()
        
        loss_date_str = request.form.get('loss_date')
        if loss_date_str:
            try:
                loss_date = datetime.datetime.strptime(loss_date_str, '%Y-%m-%d').date()
            except:
                loss_date = today - datetime.timedelta(days=365)  # Default to 1 year ago
        else:
            loss_date = today - datetime.timedelta(days=365)  # Default to 1 year ago
        
        start_date_str = request.form.get('start_date')
        if start_date_str:
            try:
                start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except:
                start_date = today  # Default to today
        else:
            start_date = today  # Default to today
        
        # Get EI start date (use loss date if not provided)
        ei_start_date_str = request.form.get('ei_benefits_start_date')
        ei_start_date = loss_date  # Default
        if ei_start_date_str:
            try:
                ei_start_date = datetime.datetime.strptime(ei_start_date_str, '%Y-%m-%d').date()
            except:
                # Handle invalid date format if needed
                ei_start_date = loss_date
        
        # Create collateral benefits dictionary
        total_past_benefits = (ei_benefits_to_date + section_b_to_date + 
                              ltd_benefits_to_date + cppd_benefits_to_date + 
                              other_benefits_to_date)
        
        total_annual_future_benefits = (ei_benefits_annual + section_b_annual + 
                                       ltd_benefits_annual + cppd_benefits_annual + 
                                       other_benefits_annual)
        
        collateral_benefits = {
            "EI Benefits (to date)": ei_benefits_to_date,
            "Section B Benefits (to date)": section_b_to_date,
            "LTD Benefits (to date)": ltd_benefits_to_date,
            "CPPD Benefits (to date)": cppd_benefits_to_date,
            "Other Benefits (to date)": other_benefits_to_date,
            "Total Past Benefits": total_past_benefits,
            
            "EI Benefits (annual)": ei_benefits_annual,
            "Section B Benefits (annual)": section_b_annual,
            "LTD Benefits (annual)": ltd_benefits_annual,
            "CPPD Benefits (annual)": cppd_benefits_annual,
            "Other Benefits (annual)": other_benefits_annual,
            "Total Annual Future Benefits": total_annual_future_benefits
        }
        
        # Calculate Net Pay Missed based on user input
        missed_time_unit = request.form.get('missed_time_unit', 'days').lower()
        missed_time = safe_float(request.form.get('missed_time'), 0)
        
        # Match the input time unit to the correct net pay rate
        time_unit_map = {
            "days": "Daily Net Pay",
            "hours": "Hourly Net Pay",
            "weeks": "Weekly Net Pay",
            "months": "Monthly Net Pay"
        }
        
        # Calculate the fraction of year for collateral benefits calculation
        fraction_of_year = {
            "days": missed_time / working_days if working_days > 0 else 0,
            "hours": missed_time / (working_days * hours_per_day) if working_days > 0 and hours_per_day > 0 else 0,
            "weeks": missed_time / 52,
            "months": missed_time / 12
        }
        
        time_fraction = fraction_of_year.get(missed_time_unit, 0)
        
	# Add dependents to calculation details
        calculation_details = {} # Initialize empty dictionary if needed
        calculation_details["Dependents"] = str(dependents)
        
        missed_pay = missed_time * result.get(time_unit_map.get(missed_time_unit, "Daily Net Pay"), 0)
        
        # Calculate collateral benefits deduction for past lost wages
        collateral_deduction = total_annual_future_benefits * time_fraction
        net_past_lost_wages = missed_pay - collateral_deduction
        
        # Special handling for New Brunswick
        if province.lower() == "new brunswick":
            # For New Brunswick, LTD and CPPD are not deducted from future lost wages
            ltd_benefits_annual = 0
            cppd_benefits_annual = 0
            
            # Recalculate total annual future benefits
            total_annual_future_benefits = (ei_benefits_annual + section_b_annual + 
                                          ltd_benefits_annual + cppd_benefits_annual + 
                                          other_benefits_annual)
            
            # Update the collateral benefits dictionary
            collateral_benefits["LTD Benefits (annual)"] = ltd_benefits_annual
            collateral_benefits["CPPD Benefits (annual)"] = cppd_benefits_annual
            collateral_benefits["Total Annual Future Benefits"] = total_annual_future_benefits
        
            # Initialize variables with default values
            past_lost_wages_with_interest = net_past_lost_wages
            calculation_details = {}
            # Calculate past lost wages with interest using T-Bill rates
            try:
                print("Calling calculate_past_lost_wages_with_interest with:", net_past_lost_wages, loss_date.strftime('%Y-%m-%d'))
                past_lost_wages_with_interest, calculation_details = calculate_past_lost_wages_with_interest(
                    net_past_lost_wages,
                    loss_date.strftime('%Y-%m-%d'),  # Convert date object to string
                    None  # Pass None to use T-Bill rates automatically
                )
                calculation_details["Dependents"] = str(dependents)
                print("Function returned:", past_lost_wages_with_interest)
            except Exception as e:
                print(f"Error in calculate_past_lost_wages_with_interest: {e}")
                # Provide default values
                past_lost_wages_with_interest = net_past_lost_wages  # Use base amount without interest
                calculation_details = {
                "Dependents": dependents,
                    "Loss Date": loss_date.strftime('%Y-%m-%d'),
                    "Calculation Date": datetime.date.today().strftime('%Y-%m-%d'),
                    "Years Between": 0,
                    "PJI Rate": 0,
                    "Base Amount": net_past_lost_wages,
                    "Interest Amount": 0,
                    "Past Lost Wages with Interest": net_past_lost_wages
                }
            # Handle return status with safer default and validation
        return_status = request.form.get('return_status')
        if not return_status:
            return_status = 'returning to work'  # Default value
        else:
            return_status = return_status.lower()
        
        time_horizon = 0
        birthdate = None
        retirement_age = None
        
        if "return" in return_status:
            # Handle returning to work scenario
            end_date_str = request.form.get('end_date')
            if not end_date_str:
                # Default to a future date if not provided
                end_date = start_date + datetime.timedelta(days=365)  # Default to 1 year
            else:
                try:
                    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except:
                    end_date = start_date + datetime.timedelta(days=365)
            
            days_difference = (end_date - start_date).days
            time_horizon = days_difference / 365.25
        else:
            # Handle total disability scenario
            birthdate_str = request.form.get('birthdate')
            if not birthdate_str:
                # Default to an age if not provided
                birthdate = datetime.date(start_date.year - 40, start_date.month, start_date.day)  # Assume 40 years old
            else:
                try:
                    birthdate = datetime.datetime.strptime(birthdate_str, '%Y-%m-%d').date()
                except:
                    birthdate = datetime.date(start_date.year - 40, start_date.month, start_date.day)
            
            retirement_age_str = request.form.get('retirement_age')
            if not retirement_age_str:
                retirement_age = 65  # Default retirement age
            else:
                try:
                    retirement_age = int(retirement_age_str)
                except:
                    retirement_age = 65
                
            retirement_year = birthdate.year + retirement_age
            retirement_month = birthdate.month
            retirement_day = min(birthdate.day, 28)  # Avoid issues with month lengths
            retirement_date = datetime.date(retirement_year, retirement_month, retirement_day)
            
            if retirement_date <= start_date:
                time_horizon = 0
            else:
                days_difference = (retirement_date - start_date).days
                time_horizon = days_difference / 365.25
        
        # Calculate future lost wages
        annual_net_salary = result["Net Pay (Provincially specific deductions for damages)"]
        annual_collateral_benefits = total_annual_future_benefits
        net_annual_salary = annual_net_salary - annual_collateral_benefits
        
        # Get discount rate with province-specific default
        if province.lower() == "nova scotia":
            default_discount_rate = 3.5
        else:  # PEI, Newfoundland, New Brunswick all use 2.5
            default_discount_rate = 2.5
        annual_discount_rate = safe_float(request.form.get('discount_rate'), default_discount_rate) / 100

        # Calculate present value
        present_value, total_months = calculate_future_lost_wages_annuity(
            net_annual_salary, time_horizon, annual_discount_rate
        )
        
        # Store details for document
        present_value_details = {
            "annual_salary": net_annual_salary,
            "monthly_payment": net_annual_salary / 12,
            "time_horizon": time_horizon,
            "total_months": total_months,
            "discount_rate": annual_discount_rate,
            "present_value": present_value,
            "future_collateral_benefits": annual_collateral_benefits * time_horizon
        }
        
        # Calculate total damages
        total_damages = past_lost_wages_with_interest + present_value
        
        # Generate enhanced PDF report
        try:
            # Create secure filename
            base_filename = secure_filename(client_name.replace(' ', '_'))
            if not base_filename:
                base_filename = "economic_damages"  # Fallback name
            
            filename = f"{base_filename}_actuclaim_report.pdf"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Call our enhanced PDF generation function
            create_enhanced_pdf_report(
                client_name=client_name,
                province=province,
                calculation_details=calculation_details,
                present_value_details=present_value_details,
                result=result,
                collateral_benefits=collateral_benefits,
                missed_time_unit=missed_time_unit,
                missed_time=missed_time,
                output_path=file_path,
                birthdate=birthdate,
                retirement_age=retirement_age,
    loss_date=loss_date,
    current_date=today,
    ei_days_remaining=max(0, 182 - (today - ei_start_date).days)
            )
            
            print(f"Enhanced PDF report saved successfully at: {file_path}")
            flash("ActuClaim report generated successfully!", "success")
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error generating ActuClaim report: {e}")
            print(f"Detailed error traceback: {error_details}")
            file_path = None
            filename = None
            flash(f"Error generating report: {str(e)}", "danger")
        
        # Return the results template
        return render_template(
            'results.html',
            title='ActuClaim - Economic Damages Results',
            client_name=client_name,
            province=province,
            result=result,
            missed_pay=missed_pay,
            net_past_lost_wages=net_past_lost_wages,
            calculation_details=calculation_details,
            present_value_details=present_value_details,
            total_damages=total_damages,
            collateral_benefits=collateral_benefits,
            missed_time_unit=missed_time_unit,
            past_lost_wages_with_interest=past_lost_wages_with_interest,
            missed_time=missed_time,
            file_path=file_path,
            filename=filename,
            birthdate=birthdate,
            retirement_age=retirement_age,
    loss_date=loss_date,
    current_date=today,
    ei_days_remaining=max(0, 182 - (today - ei_start_date).days)
        )
    
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in calculate route: {e}")
        print(f"Detailed error traceback: {error_details}")
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        flash(f"Error downloading file: {str(e)}")
        return redirect(url_for('index'))

app.register_blueprint(pji_routes)

if __name__ == '__main__':
    app.run(debug=True)
