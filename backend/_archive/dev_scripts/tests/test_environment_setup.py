#!/usr/bin/env python3
"""Test environment setup endpoints"""

import requests
import json

BASE_URL = "http://10.0.20.111:5000/setup"

print("=" * 80)
print("Testing Environment Setup Endpoints")
print("=" * 80)
print()

# Test 1: GET /setup/environment
print("1. GET /setup/environment - Get environment info")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/environment", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print()
print()

# Test 2: POST /setup/environment - Configure development
print("2. POST /setup/environment - Configure for development")
print("-" * 80)
try:
    payload = {
        "environment": "development",
        "overwrite": True  # Allow overwriting existing .env
    }

    response = requests.post(f"{BASE_URL}/environment", json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print()
print()

# Test 3: GET /setup/environment again to verify
print("3. GET /setup/environment - Verify .env was created")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/environment", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 80)
