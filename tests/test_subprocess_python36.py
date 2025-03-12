from playwright.sync_api import Page, expect
import re
from typing import Dict
import subprocess
import json
import os

def run_py36_script() -> Dict:
    """
    Execute the Python 3.6 script as a subprocess and return its results.
    """
    script_path = os.path.join(os.path.dirname(__file__), "py36_requests_script.py")
    py36_path = os.path.join(os.getcwd(), "python-3.6-venv", "bin", "python")
    
    try:
        # Run the Python 3.6 script using subprocess
        result = subprocess.run(
            [py36_path, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the JSON results from the subprocess output
        output = result.stdout
        json_start = output.find("---JSON_START---") + len("---JSON_START---")
        json_end = output.find("---JSON_END---")
        json_str = output[json_start:json_end].strip()
        data = json.loads(json_str)
        
        if "error" in data:
            raise Exception(f"Error in Python 3.6 requests: {data['error']}")
        
        # Log the data we collected
        print("\nData collected from Python 3.6:")
        print(f"IP Address: {data['requests_info']['ip']}")
        print(f"Requests User-Agent: {data['requests_info']['user_agent']}")
        print(f"Website Status Code: {data['website_data']['status_code']}")
        
        return data
        
    except subprocess.CalledProcessError as e:
        print(f"Error running Python 3.6 script: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from script output: {e}")
        raise
    except FileNotFoundError:
        print(f"Script not found at {script_path}")
        raise

def test_basic_navigation(page: Page):
    """
    Basic test that only verifies navigation to CrowdStrike works.
    This test demonstrates the minimal setup needed for Playwright testing.
    """
    # Navigate to CrowdStrike and wait for the page to be fully loaded
    page.goto("https://www.crowdstrike.com/")
    
    # Wait for the title to be available and verify it
    expect(page).to_have_title(re.compile("CrowdStrike", re.IGNORECASE))
    
    # Additional verification that the page loaded correctly
    expect(page.locator("body")).to_be_visible()

def test_mixed_version_requests(page: Page):
    """
    Test that demonstrates mixed Python version testing:
    - Uses Python 3.6 to make HTTP requests and collect data
    - Uses Python 3.9 with Playwright to perform browser testing
    - Verifies data consistency between the two environments
    """
    # First collect data using Python 3.6
    py36_data = run_py36_script()
    
    # Navigate to CrowdStrike and verify basic functionality
    page.goto("https://www.crowdstrike.com/")
    expect(page).to_have_title(re.compile("CrowdStrike", re.IGNORECASE))

    # Click the accept cookies button if it exists
    try:
        page.get_by_role("button", name="Accept Cookies").click()
    except:
        print("No cookie banner found or already accepted")
    
    # Click the search button and wait for the search input
    page.get_by_role("button", name="Search Icon").click()

    # Fill and submit the search
    search_term = py36_data['website_data']['search_term']
    page.get_by_role("searchbox", name="Search field").fill(search_term)
    page.get_by_role("searchbox", name="Search field").press("Enter")
    
    # Wait for and verify search results
    # Look for the search term in search results, allowing for partial matches
    results = page.locator('#results').filter(has_text=search_term)
    expect(results).to_be_visible()
