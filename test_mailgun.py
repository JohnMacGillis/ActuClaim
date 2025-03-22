import os
import sys
import requests
import traceback

# Check domain verification status
try:
    domain_check_url = f"https://api.mailgun.net/v3/domains/{MAILGUN_DOMAIN}"
    domain_auth = ("api", MAILGUN_API_KEY)
    domain_response = requests.get(domain_check_url, auth=domain_auth)
    print(f"Domain status check: {domain_response.status_code}")
    print(f"Domain details: {domain_response.text}")
except Exception as e:
    print(f"Error checking domain: {str(e)}")

# Mailgun configuration
MAILGUN_API_KEY = "496cf4937b8a736bc5f4a9c4d8d30500-3d4b3a2a-8bae7d15"
MAILGUN_DOMAIN = "actuclaim.com"
MAILGUN_FROM_EMAIL = "info@actuclaim.com"
MAILGUN_FROM_NAME = "ActuClaim Test"

def test_mailgun():
    print("Starting Mailgun test...")
    try:
        # Enter your email as the recipient for testing
        test_recipient = "john@johnmacgillis.ca"  # Replace with your actual email
        
        # Build request
        url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
        auth = ("api", MAILGUN_API_KEY)
        data = {
            "from": f"{MAILGUN_FROM_NAME} <{MAILGUN_FROM_EMAIL}>",
            "to": [test_recipient],
            "subject": "Mailgun Test from ActuClaim",
            "text": "This is a test email from ActuClaim using Mailgun API."
        }
        
        print(f"Sending test email to {test_recipient}")
        print(f"Using domain: {MAILGUN_DOMAIN}")
        print(f"API key length: {len(MAILGUN_API_KEY)}")
        
        # Send request
        response = requests.post(url, auth=auth, data=data)
        
        # Print response details
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("Test successful! Email sent.")
            return True
        else:
            print(f"Test failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Replace with your actual email
    if len(sys.argv) > 1:
        recipient = sys.argv[1]
    else:
        recipient = "john@johnmacgillis.ca"  # Default recipient
    
    test_mailgun()
