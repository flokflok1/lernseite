#!/usr/bin/env python3
"""Test admin creation endpoint"""

import requests
import json

url = "http://10.0.20.111:5000/setup/admin"

# Try with the data the frontend is sending
payload = {
    "email": "admin@lsx.de",
    "password": "MyAdmin123456!",
    "first_name": "Pascal",
    "last_name": "Kozlowski"
}

print(f"Testing: POST {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(url, json=payload, timeout=10)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response Status: {e.response.status_code}")
        print(f"Response Text: {e.response.text}")
except Exception as e:
    print(f"Error: {e}")
