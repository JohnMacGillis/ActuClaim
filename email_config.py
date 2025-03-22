# =============================================================================
# EMAIL CONFIGURATION FOR GOOGLE WORKSPACE
# =============================================================================
import os
import logging
import socket

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# SMTP configuration for Google Workspace
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "info@actuclaim.com"
SMTP_PASSWORD = "Outlook1!"
SENDER_EMAIL = "info@actuclaim.com"

# Export environment variables
os.environ['ACTUCLAIM_SMTP_SERVER'] = SMTP_SERVER
os.environ['ACTUCLAIM_SMTP_PORT'] = str(SMTP_PORT)
os.environ['ACTUCLAIM_SMTP_USERNAME'] = SMTP_USERNAME
os.environ['ACTUCLAIM_SMTP_PASSWORD'] = SMTP_PASSWORD
os.environ['ACTUCLAIM_SENDER_EMAIL'] = SENDER_EMAIL

# Log configuration
logger.info(f"Email configuration loaded: {SMTP_SERVER}:{SMTP_PORT} with user {SMTP_USERNAME}")

# Test the connection with timeout handling
def test_connection():
    import smtplib
    try:
        # Set timeout to prevent hanging
        socket.setdefaulttimeout(10)
        
        logger.info(f"Testing connection to {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.set_debuglevel(1)
        
        logger.info("Starting TLS...")
        server.starttls()
        
        logger.info(f"Logging in with {SMTP_USERNAME}...")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        logger.info("Login successful! Closing connection...")
        server.quit()
        
        logger.info("SMTP connection test PASSED")
        return True
    except socket.timeout:
        logger.error(f"Connection timed out. Check if {SMTP_SERVER}:{SMTP_PORT} is accessible.")
        return False
    except socket.gaierror:
        logger.error(f"Address lookup error. Check if {SMTP_SERVER} is correct.")
        return False
    except smtplib.SMTPAuthenticationError:
        logger.error("Authentication failed. Check username and password.")
        return False
    except Exception as e:
        logger.error(f"SMTP connection test failed: {str(e)}")
        return False

# Run test when this file is executed directly
if __name__ == "__main__":
    test_connection()
