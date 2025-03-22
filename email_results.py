# =============================================================================
# EMAIL RESULTS FUNCTIONALITY - ENHANCED ERROR HANDLING
# =============================================================================
import smtplib
import logging
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import os
import socket  # For timeout handling

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_results_email(recipient_email, client_name, province, calculation_details, present_value_details, 
                      result, collateral_benefits, missed_time_unit, missed_time, 
                      past_lost_wages_with_interest, net_past_lost_wages, missed_pay, total_damages,
                      birthdate=None, retirement_age=None, loss_date=None, current_date=None, 
                      ei_days_remaining=0, **kwargs):
    """
    Send calculation results via email with enhanced error handling and timeouts.
    """
    try:
        # Get SMTP configuration with strict checking
        smtp_server = os.environ.get('ACTUCLAIM_SMTP_SERVER')
        smtp_port = os.environ.get('ACTUCLAIM_SMTP_PORT')
        smtp_username = os.environ.get('ACTUCLAIM_SMTP_USERNAME')
        smtp_password = os.environ.get('ACTUCLAIM_SMTP_PASSWORD')
        sender_email = os.environ.get('ACTUCLAIM_SENDER_EMAIL', smtp_username)
        
        # Validate SMTP configuration
        if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
            missing = []
            if not smtp_server: missing.append("SMTP_SERVER")
            if not smtp_port: missing.append("SMTP_PORT")
            if not smtp_username: missing.append("SMTP_USERNAME")
            if not smtp_password: missing.append("SMTP_PASSWORD")
            logger.error(f"Missing SMTP configuration: {', '.join(missing)}")
            return False
        
        # Convert port to integer
        try:
            smtp_port = int(smtp_port)
        except ValueError:
            logger.error(f"Invalid SMTP port: {smtp_port}")
            return False
            
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
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"ActuClaim Economic Damages Report for {client_name}"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Build HTML content (HTML generation code remains the same)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <!-- HTML content here - same as before -->
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Set timeout for SMTP operations - critical for preventing hanging
        socket.setdefaulttimeout(30)  # 30 seconds timeout
        
        # Send email with explicit exception handling
        logger.debug(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")
        try:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        except (socket.timeout, socket.gaierror, ConnectionRefusedError) as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            return False
            
        try:
            server.set_debuglevel(1)  # Enable debug output
            logger.debug("Starting TLS")
            server.starttls()
        except Exception as e:
            logger.error(f"Failed to start TLS: {e}")
            try:
                server.quit()
            except:
                pass
            return False
            
        try:
            logger.debug(f"Logging in with username: {smtp_username}")
            server.login(smtp_username, smtp_password)
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            try:
                server.quit()
            except:
                pass
            return False
        
        try:
            logger.debug(f"Sending email to: {recipient_email}")
            server.send_message(msg)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            try:
                server.quit()
            except:
                pass
            return False
                
        try:
            server.quit()
        except:
            pass
            
        logger.info(f"Successfully sent email to: {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        logger.error(f"Detailed error: {traceback.format_exc()}")
        return False
