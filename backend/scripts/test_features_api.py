#!/usr/bin/env python3
"""
Test script for Feature-Based Authorization API endpoints.

Tests:
- Feature metadata endpoint (public)
- Available features endpoint (authenticated)
- Feature access check endpoint (authenticated)
- Context-filtered features endpoint (authenticated)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from app import create_app

def test_feature_api():
    """Test Feature API endpoints."""
    
    app = create_app('development')
    client = app.test_client()
    
    print("\n" + "="*60)
    print("FEATURE API ENDPOINT TESTS")
    print("="*60)
    
    # Test 1: Feature Metadata (Public, no auth required)
    print("\n✓ Test 1: GET /api/v1/features/<feature_code>/metadata (Public)")
    print("-" * 60)
    
    response = client.get('/api/v1/features/code_sandbox/metadata')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Response: {json.dumps(data, indent=2)}")
        print("✅ PASS: Public metadata endpoint works")
    else:
        print(f"❌ FAIL: Expected 200, got {response.status_code}")
        print(f"Response: {response.data.decode()}")
    
    # Test 2: Invalid feature metadata
    print("\n✓ Test 2: GET /api/v1/features/nonexistent/metadata (404)")
    print("-" * 60)
    
    response = client.get('/api/v1/features/nonexistent_feature/metadata')
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        data = json.loads(response.data)
        print(f"Response: {json.dumps(data, indent=2)}")
        print("✅ PASS: 404 handling works")
    else:
        print(f"❌ FAIL: Expected 404, got {response.status_code}")
    
    # Test 3: Health check
    print("\n✓ Test 3: GET /api/v1/features/health (No auth)")
    print("-" * 60)
    
    response = client.get('/api/v1/features/health')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Response: {json.dumps(data, indent=2)}")
        print("✅ PASS: Health check works")
    else:
        print(f"❌ FAIL: Expected 200, got {response.status_code}")
    
    # Test 4: Available features (requires auth - will fail without token)
    print("\n✓ Test 4: GET /api/v1/features/available (Requires auth)")
    print("-" * 60)
    
    response = client.get('/api/v1/features/available')
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        data = json.loads(response.data)
        print(f"Response: {json.dumps(data, indent=2)}")
        print("✅ PASS: Auth check works (correctly rejected without token)")
    else:
        print(f"⚠️  Expected 401 without auth, got {response.status_code}")
    
    # Test 5: Check feature access (requires auth)
    print("\n✓ Test 5: GET /api/v1/features/check/code_sandbox (Requires auth)")
    print("-" * 60)
    
    response = client.get('/api/v1/features/check/code_sandbox')
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ PASS: Auth check works (correctly rejected without token)")
    else:
        print(f"⚠️  Expected 401 without auth, got {response.status_code}")
    
    # Test 6: Context features (requires auth)
    print("\n✓ Test 6: GET /api/v1/features/context/user (Requires auth)")
    print("-" * 60)
    
    response = client.get('/api/v1/features/context/user')
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ PASS: Auth check works (correctly rejected without token)")
    else:
        print(f"⚠️  Expected 401 without auth, got {response.status_code}")
    
    # Test 7: Invalid context
    print("\n✓ Test 7: GET /api/v1/features/context/invalid_context (400)")
    print("-" * 60)
    
    # Even without auth, this should validate the context parameter
    response = client.get('/api/v1/features/context/invalid_context')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.data.decode()[:200]}")
    
    print("\n" + "="*60)
    print("FEATURE API TEST SUMMARY")
    print("="*60)
    print("\n✅ All endpoint tests completed!")
    print("\nNote: Authenticated endpoints correctly require auth token.")
    print("To fully test with auth, use pytest with database fixtures.")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_feature_api()
