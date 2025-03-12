import sys
import requests
import json

def make_requests():
    results = {
        "requests_info": {},
        "website_data": {}
    }
    
    # Get IP and user agent information
    try:
        response = requests.get("https://httpbin.org/ip")
        results["requests_info"]["ip"] = response.json()["origin"]
        
        response = requests.get("https://httpbin.org/user-agent")
        results["requests_info"]["user_agent"] = response.json()["user-agent"]
        
        # Get Crowdstrike website headers and search for a specific term
        response = requests.get("https://www.crowdstrike.com/")
        results["website_data"] = {
            "url": response.url,
            "status_code": response.status_code,
            "server": response.headers.get('server', ''),
            "content_type": response.headers.get('content-type', ''),
            "search_term": "endpoint protection"  # We'll use this in our Playwright test
        }
        
    except Exception as e:
        results["error"] = str(e)
    
    return results

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"Requests version: {requests.__version__}")
    results = make_requests()
    print("---JSON_START---")  # Marker for parsing
    print(json.dumps(results))
    print("---JSON_END---") 