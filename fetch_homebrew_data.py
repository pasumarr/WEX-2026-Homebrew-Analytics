"""
WEX 2026 - Homebrew Analytics Project
Author: Sai Pasumarthi
Date: March 18, 2026

Description:
Fetches top Homebrew package installation data from the Homebrew Analytics API.
Displays the top 10 most installed packages from the last 30 days.

Learning Focus:
- REST API integration and HTTP requests
- JSON data parsing and manipulation
- Error handling and status code checking
- Python requests library usage
- Professional code documentation standards
"""

import requests

# Try the Homebrew JSON API endpoint
print("Fetching Homebrew data...")
url = 'https://formulae.brew.sh/api/analytics/install/30d.json'


response = requests.get(url, headers={'User-Agent': 'WEX-2026-Project'})

print(f"Status Code: {response.status_code}")
print(f"Content Type: {response.headers.get('content-type')}")

if response.status_code == 200:
    data = response.json() # parse and read the json file
    
    # Show the top 10 packages in Homebrew
    print("\n Top 10 Most Installed Homebrew Packages (Last 30 Days):\n")
    print("="*70)
    
    # The data structure - explore what keys exist and organize them neatly
    if 'items' in data:
        for i, item in enumerate(data['items'][:10], 1):
            package_name = item.get('formula', item.get('cask', 'Unknown'))
            install_count = item.get('count', 0)
            # Format separately to avoid the error 
            formatted_count = f"{install_count:}"
            print(f"{i:2d}. {package_name:<30} - {formatted_count} installs")
    else: # just in case for errors that pop so I understand
        print("Unexpected data structure. Here's what we got:") 
        print(f"Keys available: {list(data.keys())}")
        
    print("="*70)
    print("Data fetched successfully!") # so we understand that the code ran and we have the data organized
        
else:
    print(f"Error: Status {response.status_code}")
    
