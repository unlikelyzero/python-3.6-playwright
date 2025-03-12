import pytest
import subprocess
import os
import json
from typing import Dict, Optional

@pytest.fixture(scope="session")
def py36_venv_path() -> str:
    """Path to the Python 3.6 virtual environment."""
    return os.path.join(os.getcwd(), "python-3.6-venv", "bin", "python")

@pytest.fixture(scope="session")
def py36_data(py36_venv_path: str) -> Dict:
    """
    Run the Python 3.6 script and return the collected data.
    This fixture executes our Python 3.6 requests script and parses its output.
    """
    script_path = os.path.join("tests", "py36_requests_script.py")
    try:
        # Run the Python 3.6 script using subprocess
        result = subprocess.run(
            [py36_venv_path, script_path],
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

@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context with consistent viewport size."""
    return {
        "viewport": {
            "width": 1920,
            "height": 1080
        }
    }

@pytest.fixture(scope="session")
def connect_options() -> Optional[Dict]:
    """
    Configure Playwright connection options.
    Returns connection options if PLAYWRIGHT_WS_ENDPOINT is set,
    otherwise returns None to use local browser instance.
    """
    ws_endpoint = os.getenv("PLAYWRIGHT_WS_ENDPOINT")
    if ws_endpoint:
        print(f"\nConnecting to remote Playwright server at: {ws_endpoint}")
        return {
            "ws_endpoint": ws_endpoint,
        }
    print("\nUsing local browser instance")
    return None 