# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
import datetime

def check_install_libraries():
    """Check and install required libraries if not present."""
    try:
        import docx
    except ImportError:
        print("\nThe 'python-docx' library is not installed. Installing it now...")
        import sys
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
        print("Successfully installed 'python-docx' library.\n")
    
    try:
        import tabulate
    except ImportError:
        print("\nThe 'tabulate' library is not installed. Installing it now...")
        import sys
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
        print("Successfully installed 'tabulate' library.\n")

def parse_date(date_str):
    """Parse date string in various formats and return a date object."""
    try:
        # Try different date formats
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"]:
            try:
                return datetime.datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError("Invalid date format")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD or DD/MM/YYYY format.")
        return None
