#!/usr/bin/env python3
"""
Security Test Script for KYC Backend
This script tests the API key authentication to ensure your backend is properly secured.
"""

import requests
import websocket
import json
import os
import sys
from urllib.parse import urlparse

# Configuration
BACKEND_URL = "https://kyc-backend-7f7c.onrender.com"
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    print("❌ ERROR: API_KEY environment variable not set!")
    print("   Please set your API key: export API_KEY=your-secure-key-here")
    sys.exit(1)

def test_health_endpoint():
    """Test the health endpoint (should work without API key)"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint accessible (expected)")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_protected_endpoint_without_key():
    """Test protected endpoint without API key (should fail)"""
    print("🔍 Testing protected endpoint without API key...")
    try:
        response = requests.get(f"{BACKEND_URL}/api-key")
        if response.status_code in [401, 403]:
            print("✅ Protected endpoint properly blocked (expected)")
            return True
        else:
            print(f"❌ Protected endpoint accessible without key: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Protected endpoint test error: {e}")
        return False

def test_protected_endpoint_with_invalid_key():
    """Test protected endpoint with invalid API key (should fail)"""
    print("🔍 Testing protected endpoint with invalid API key...")
    try:
        headers = {"X-API-Key": "invalid-key-123"}
        response = requests.get(f"{BACKEND_URL}/api-key", headers=headers)
        if response.status_code in [401, 403]:
            print("✅ Protected endpoint properly blocked with invalid key (expected)")
            return True
        else:
            print(f"❌ Protected endpoint accessible with invalid key: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid key test error: {e}")
        return False

def test_protected_endpoint_with_valid_key():
    """Test protected endpoint with valid API key (should work)"""
    print("🔍 Testing protected endpoint with valid API key...")
    try:
        headers = {"X-API-Key": API_KEY}
        response = requests.get(f"{BACKEND_URL}/api-key", headers=headers)
        if response.status_code == 200:
            print("✅ Protected endpoint accessible with valid key (expected)")
            data = response.json()
            print(f"   Response: {data}")
            return True
        else:
            print(f"❌ Protected endpoint failed with valid key: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Valid key test error: {e}")
        return False

def test_websocket_without_key():
    """Test WebSocket connection without API key (should fail)"""
    print("🔍 Testing WebSocket connection without API key...")
    try:
        ws_url = BACKEND_URL.replace("https://", "wss://") + "/ws"
        ws = websocket.create_connection(ws_url, timeout=5)
        ws.close()
        print("❌ WebSocket connected without API key (security issue!)")
        return False
    except Exception as e:
        if "4001" in str(e) or "Invalid API key" in str(e):
            print("✅ WebSocket properly blocked without API key (expected)")
            return True
        else:
            print(f"❌ WebSocket test error: {e}")
            return False

def test_websocket_with_valid_key():
    """Test WebSocket connection with valid API key (should work)"""
    print("🔍 Testing WebSocket connection with valid API key...")
    try:
        ws_url = BACKEND_URL.replace("https://", "wss://") + f"/ws?api_key={API_KEY}"
        ws = websocket.create_connection(ws_url, timeout=5)
        
        # Wait for initial message
        result = ws.recv()
        data = json.loads(result)
        
        if data.get("event") == "user_id":
            print("✅ WebSocket connected with valid API key (expected)")
            ws.close()
            return True
        else:
            print(f"❌ Unexpected WebSocket response: {data}")
            ws.close()
            return False
    except Exception as e:
        print(f"❌ WebSocket with valid key error: {e}")
        return False

def main():
    """Run all security tests"""
    print("🔐 KYC Backend Security Test Suite")
    print("=" * 50)
    
    # API key validation already done above
    
    tests = [
        test_health_endpoint,
        test_protected_endpoint_without_key,
        test_protected_endpoint_with_invalid_key,
        test_protected_endpoint_with_valid_key,
        test_websocket_without_key,
        test_websocket_with_valid_key
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All security tests passed! Your backend is properly secured.")
        return 0
    else:
        print("❌ Some security tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    # Install websocket-client if not available
    try:
        import websocket
    except ImportError:
        print("Installing required dependency: websocket-client")
        os.system("pip install websocket-client")
        import websocket
    
    sys.exit(main())
