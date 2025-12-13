#!/usr/bin/env python3
"""Test setup wizard status endpoint"""

import requests
import json

url = "http://10.0.20.111:5000/setup/status"

print(f"Testing: GET {url}")
print()

try:
    response = requests.get(url, timeout=10)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response text: {e.response.text}")
