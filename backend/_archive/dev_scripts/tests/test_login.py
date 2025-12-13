"""Test login endpoint"""
import requests
import json

url = "http://10.0.20.111:5000/api/v1/auth/login"
payload = {
    "email": "admin@lsx.de",
    "password": "MyAdmin123456!"
}

print(f"Testing login at {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(url, json=payload, timeout=10)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response text: {e.response.text}")
