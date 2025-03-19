#!/usr/bin/env python3

import os
import re
from datetime import datetime, timedelta

def analyze_files(directory):
    """
    Analyze files in the given directory to identify potentially unused or unnecessary files.
    """
    print(f"Analyzing files in {directory}")
    
    # Lists to categorize files
    old_files = []
    backup_files = []
    cache_files = []
    log_files = []
    temp_files = []
    
    # Patterns to identify potentially unnecessary files
    backup_patterns = [
        r'.*\.bak$',
        r'.*\.backup$',
        r'.*~$',
        r'.*\.old$',
        r'.*\.orig$'
    ]
    
    cache_patterns = [
        r'.*\.pyc$',
        r'.*\.pyo$',
        r'.*\.pyd$',
        r'__pycache__',
        r'.*\.swp$',
        r'.*\.swo$'
    ]
    
    log_patterns = [
        r'.*\.log$',
        r'.*_log$'
    ]
    
    temp_patterns = [
        r'^tmp.*',
        r'.*\.tmp$',
        r'^temp.*'
    ]
    
    # Current timestamp
    now = datetime.now()
    
    # Walk through directory
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            
            try:
                # Get file stats
                stat = os.stat(filepath)
                file_age = now - datetime.fromtimestamp(stat.st_mtime)
                file_size = stat.st_size
                
                # Check for old files (not modified in 6 months)
                if file_age > timedelta(days=180):
                    old_files.append({
                        'path': filepath,
                        'size': file_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime)
                    })
                
                # Check for backup files
                if any(re.match(pattern, filename, re.IGNORECASE) for pattern in backup_patterns):
                    backup_files.append({
                        'path': filepath,
                        'size': file_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime)
                    })
                
                # Check for cache files
                if any(re.search(pattern, filepath, re.IGNORECASE) for pattern in cache_patterns):
                    cache_files.append({
                        'path': filepath,
                        'size': file_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime)
                    })
                
                # Check for log files
                if any(re.match(pattern, filename, re.IGNORECASE) for pattern in log_patterns):
                    log_files.append({
                        'path': filepath,
                        'size': file_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime)
                    })
                
                # Check for temp files
                if any(re.match(pattern, filename, re.IGNORECASE) for pattern in temp_patterns):
                    temp_files.append({
                        'path': filepath,
                        'size': file_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime)
                    })
            
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    
    # Print results
    print("\n=== Potentially Unnecessary Files ===")
    
    def print_file_list(title, file_list):
        if file_list:
            print(f"\n{title}:")
            for file in file_list:
                print(f"- {file['path']} (Size: {file['size']} bytes, Last Modified: {file['last_modified']})")
    
    print_file_list("Old Files (Not Modified in 6+ Months)", old_files)
    print_file_list("Backup Files", backup_files)
    print_file_list("Cache Files", cache_files)
    print_file_list("Log Files", log_files)
    print_file_list("Temporary Files", temp_files)
    
    # Summary
    print("\n=== Summary ===")
    print(f"Old Files: {len(old_files)}")
    print(f"Backup Files: {len(backup_files)}")
    print(f"Cache Files: {len(cache_files)}")
    print(f"Log Files: {len(log_files)}")
    print(f"Temporary Files: {len(temp_files)}")

def main():
    # Set the directory to analyze (change this as needed)
    target_directory = '/var/www/actuclaim'
    analyze_files(target_directory)

if __name__ == '__main__':
    main()
