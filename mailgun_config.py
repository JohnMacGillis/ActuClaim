# =============================================================================
# MAILGUN EMAIL CONFIGURATION
# =============================================================================
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MailGun API Config
MAILGUN_API_KEY = "496cf4937b8a736bc5f4a9c4d8d30500-3d4b3a2a-8bae7d15"
MAILGUN_DOMAIN = "actuclaim.com"
MAILGUN_FROM_EMAIL = "info@actuclaim.com"
MAILGUN_FROM_NAME = "ActuClaim"

# Export environment variables
os.environ['ACTUCLAIM_MAILGUN_API_KEY'] = MAILGUN_API_KEY
os.environ['ACTUCLAIM_MAILGUN_DOMAIN'] = MAILGUN_DOMAIN
os.environ['ACTUCLAIM_MAILGUN_FROM_EMAIL'] = MAILGUN_FROM_EMAIL
os.environ['ACTUCLAIM_MAILGUN_FROM_NAME'] = MAILGUN_FROM_NAME

# Log configuration
logger.info(f"Mailgun configuration loaded: Domain {MAILGUN_DOMAIN}")

# Test function to verify Mailgun connection
def test_mailgun_connection():
    import requests
    try:
        logger.info(f"Testing Mailgun connection...")
        
        # Enter your email as the recipient for testing
        test_recipient = "johnmacgillis@gmail.com"  # Change this to your email for testing
        
        # Build request
        url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
        auth = ("api", MAILGUN_API_KEY)
        data = {
            "from": f"{MAILGUN_FROM_NAME} <{MAILGUN_FROM_EMAIL}>",
            "to": [test_recipient],
            "subject": "Mailgun Test from ActuClaim",
            "text": "This is a test email from ActuClaim using Mailgun API."
        }
        
        # Send request
        response = requests.post(url, auth=auth, data=data)
        
        # Check response
        if response.status_code == 200:
            logger.info(f"Mailgun test successful! Response: {response.text}")
            return True
        else:
            logger.error(f"Mailgun test failed with status code {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Mailgun test failed: {str(e)}")
        return False

# Run test when this file is executed directly
if __name__ == "__main__":
    test_mailgun_connection()
