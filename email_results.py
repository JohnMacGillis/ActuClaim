# =============================================================================
# EMAIL RESULTS FUNCTIONALITY - USING MAILGUN
# =============================================================================
import logging
import traceback
import datetime
import os
import requests

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Mailgun config
try:
    from mailgun_config import MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_FROM_EMAIL, MAILGUN_FROM_NAME
    logger.info("Successfully imported Mailgun configuration")
except ImportError:
    logger.error("Failed to import mailgun_config module")
    # Provide fallback defaults
    MAILGUN_API_KEY = os.environ.get('ACTUCLAIM_MAILGUN_API_KEY', '')
    MAILGUN_DOMAIN = os.environ.get('ACTUCLAIM_MAILGUN_DOMAIN', 'actuclaim.com')
    MAILGUN_FROM_EMAIL = os.environ.get('ACTUCLAIM_MAILGUN_FROM_EMAIL', 'info@actuclaim.com')
    MAILGUN_FROM_NAME = os.environ.get('ACTUCLAIM_MAILGUN_FROM_NAME', 'ActuClaim')

def send_results_email(recipient_email, client_name, province, calculation_details, present_value_details, 
                      result, collateral_benefits, missed_time_unit, missed_time, 
                      past_lost_wages_with_interest, net_past_lost_wages, missed_pay, total_damages,
                      birthdate=None, retirement_age=None, loss_date=None, current_date=None, 
                      ei_days_remaining=0, **kwargs):
    """
    Send calculation results via email using the Mailgun API.
    """
    try:
        # Set defaults for current_date if not provided
        if current_date is None:
            current_date = datetime.date.today()
            
        # Format dates
        today_date = current_date.strftime("%B %d, %Y") if isinstance(current_date, datetime.date) else str(current_date)
        
        # Handle loss_date formatting
        loss_date_str = ""
        if loss_date:
            if isinstance(loss_date, datetime.date):
                loss_date_str = loss_date.strftime("%B %d, %Y")
            elif isinstance(loss_date, str):
                try:
                    parsed_date = datetime.datetime.strptime(loss_date, '%Y-%m-%d').date()
                    loss_date_str = parsed_date.strftime("%B %d, %Y")
                except ValueError:
                    loss_date_str = loss_date
            else:
                loss_date_str = str(loss_date)
        
        # Build HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Economic Damages Calculation Results</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f9f9f9;
                    margin: 0;
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: #fff;
                    padding: 25px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                
                h1, h2, h3, h4 {{
                    color: #2d5ca9;
                    margin-top: 20px;
                    margin-bottom: 10px;
                }}
                
                h1 {{
                    font-size: 24px;
                    text-align: center;
                    border-bottom: 2px solid #2d5ca9;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                
                h2 {{
                    font-size: 20px;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 8px;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    background-color: #fff;
                }}
                
                th, td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #ddd;
                }}
                
                th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                    text-align: left;
                }}
                
                .text-end {{
                    text-align: right;
                }}
                
                .total-row {{
                    font-weight: bold;
                    background-color: #f8f9fa;
                }}
                
                .damages-summary {{
                    background-color: #f0f7ff;
                    border: 1px solid #d0e3ff;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                }}
                
                .calculation-section {{
                    margin-bottom: 30px;
                    background: #fff;
                    border: 1px solid #eee;
                    border-radius: 8px;
                    padding: 20px;
                }}
                
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-top: 1px solid #eee;
                    padding-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Economic Damages Assessment</h1>
                <p style="text-align: center;">Results for <strong>{client_name}</strong> | Generated on {today_date}</p>
                
                <div class="damages-summary">
                    <table class="damages-summary-table">
                        <tbody>
                            <tr>
                                <td>Past Lost Wages with Interest</td>
                                <td class="text-end">${past_lost_wages_with_interest:,.2f}</td>
                            </tr>
                            <tr>
                                <td>Future Lost Wages</td>
                                <td class="text-end">${present_value_details.get('present_value', 0):,.2f}</td>
                            </tr>
                            <tr class="total-row">
                                <td>Total Economic Damages</td>
                                <td class="text-end" id="total-damages-amount">${total_damages:,.2f}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="calculation-section">
                    <div class="row">
                        <div class="income-summary">
                            <h2>Income Summary</h2>
                            <table>
                                <tbody>
                                    <tr>
                                        <td>Gross Income</td>
                                        <td class="text-end">${result.get("Gross Income", 0):,.2f}</td>
                                    </tr>
        """
        
        # Add dependent benefit if present
        if result.get('Dependent Benefit', 0) > 0:
            html_content += f"""
                                    <tr>
                                        <td>Dependent Benefit ({calculation_details.get('Dependents', '0')} dependents)</td>
                                        <td class="text-end">${result.get('Dependent Benefit', 0):,.2f}</td>
                                    </tr>
            """
        
        # Handle different provincial tax naming conventions
        provincial_tax = result.get(f"{province.title()} Tax", 
                                   result.get('Provincial Tax', 
                                             result.get(f"{province.capitalize()} Tax", 0)))
        
        html_content += f"""
                                    <tr>
                                        <td>Federal Tax</td>
                                        <td class="text-end">-${result.get('Federal Tax', 0):,.2f}</td>
                                    </tr>
                                    <tr>
                                        <td>Provincial Tax ({province.title()})</td>
                                        <td class="text-end">-${provincial_tax:,.2f}</td>
                                    </tr>
                                    <tr>
                                        <td>CPP/EI Contributions</td>
                                        <td class="text-end">-${result.get('CPP Contribution', 0) + result.get('EI Contribution', 0):,.2f}</td>
                                    </tr>
                                    <tr class="total-row">
                                        <td>Net Income</td>
                                        <td class="text-end">${result.get('Net Pay (Provincially specific deductions for damages)', 0):,.2f}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <div class="past-lost-wages">
                            <h2>Past Lost Wages</h2>
                            <table>
                                <tbody>
                                    <tr>
                                        <td>Missed Time</td>
                                        <td class="text-end">{missed_time} {missed_time_unit}</td>
                                    </tr>
                                    <tr>
                                        <td>Gross Missed Income</td>
                                        <td class="text-end">${missed_pay:,.2f}</td>
                                    </tr>
                                    <tr>
                                        <td>Collateral Benefits Deduction</td>
                                        <td class="text-end">-${collateral_benefits.get('Total Past Benefits', 0):,.2f}</td>
                                    </tr>
                                    <tr class="total-row">
                                        <td>Net Past Lost Wages</td>
                                        <td class="text-end">${net_past_lost_wages:,.2f}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="row">
                        <div class="pre-judgment-interest">
                            <h2>Pre-Judgment Interest (PJI) Calculation</h2>
                            <table>
                                <tbody>
                                    <tr>
                                        <td>Original Past Lost Wages</td>
                                        <td class="text-end">${net_past_lost_wages:,.2f}</td>
                                    </tr>
                                    <tr>
                                        <td>Loss Date</td>
                                        <td class="text-end">{loss_date_str}</td>
                                    </tr>
                                    <tr>
                                        <td>Calculation Date</td>
                                        <td class="text-end">{today_date}</td>
                                    </tr>
                                    <tr>
                                        <td>Years Between</td>
                                        <td class="text-end">{calculation_details.get('Years Between', 0):.2f}</td>
                                    </tr>
                                    <tr>
                                        <td>PJI Rate</td>
                                        <td class="text-end">{calculation_details.get('PJI Rate', 2.5):.2f}%</td>
                                    </tr>
                                    <tr>
                                        <td>Pre-Judgment Interest Amount</td>
                                        <td class="text-end">${calculation_details.get('Interest Amount', 0):,.2f}</td>
                                    </tr>
                                    <tr class="total-row highlight">
                                        <td>Past Lost Wages with Interest</td>
                                        <td class="text-end">${past_lost_wages_with_interest:,.2f}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
        """
        
        # Only include Future Lost Wages section if there are future lost wages
        if present_value_details.get('present_value', 0) > 0:
            html_content += f"""
                        <div class="future-lost-wages">
                            <h2>Future Lost Wages</h2>
                            <table>
                                <tbody>
                                    <tr>
                                        <td>Annual Net Salary</td>
                                        <td class="text-end">${present_value_details.get('annual_salary', 0):,.2f}</td>
                                    </tr>
                                    <tr>
                                        <td>Annual Collateral Benefits</td>
                                        <td class="text-end">-${collateral_benefits.get('Total Annual Future Benefits', 0):,.2f}</td>
                                    </tr>
                                    <tr>
                                        <td>Time Horizon</td>
                                        <td class="text-end">{present_value_details.get('time_horizon', 0):.2f} years</td>
                                    </tr>
                                    <tr>
                                        <td>Discount Rate</td>
                                        <td class="text-end">{present_value_details.get('discount_rate', 0) * 100:.2f}%</td>
                                    </tr>
                                    <tr class="total-row">
                                        <td>Present Value of Future Lost Wages</td>
                                        <td class="text-end">${present_value_details.get('present_value', 0):,.2f}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
            """
        else:
            html_content += """
                        <div class="future-lost-wages">
                            <h2>Future Lost Wages</h2>
                            <div class="no-future-wages-message">
                                <p>No future lost wages calculated as requested.</p>
                            </div>
                        </div>
            """
        
        # Close the remaining divs and add footer
        html_content += """
                    </div>
                </div>
                
                <div class="footer">
                    <p>This report was generated by ActuClaim Economic Damages Calculator.</p>
                    <p>The information provided is based on the inputs and assumptions specified in the calculation.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version as fallback
        text_content = f"""
ACTUCLAIM ECONOMIC DAMAGES CALCULATION
Results for {client_name} | Generated on {today_date}

ECONOMIC DAMAGES SUMMARY
Past Lost Wages with Interest: ${past_lost_wages_with_interest:,.2f}
Future Lost Wages: ${present_value_details.get('present_value', 0):,.2f}
Total Economic Damages: ${total_damages:,.2f}

This report was generated by ActuClaim Economic Damages Calculator.
        """
        
        # Send email using Mailgun API
        logger.debug(f"Sending email to {recipient_email} via Mailgun API")
        
        # Build Mailgun API request
        url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
        auth = ("api", MAILGUN_API_KEY)
        data = {
            "from": f"{MAILGUN_FROM_NAME} <{MAILGUN_FROM_EMAIL}>",
            "to": recipient_email,
            "subject": f"ActuClaim Economic Damages Report for {client_name}",
            "text": text_content,
            "html": html_content
        }
        
        # Send request
        response = requests.post(url, auth=auth, data=data)
        
        # Check response
        if response.status_code == 200:
            logger.info(f"Email sent successfully to {recipient_email}. Response: {response.text}")
            return True
        else:
            logger.error(f"Failed to send email. Status code: {response.status_code}, Response: {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        logger.error(f"Detailed error: {traceback.format_exc()}")
        return False
