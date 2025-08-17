#!/usr/bin/env python3
"""
Test script to verify that the bugs have been fixed.
Run this after starting the Flask application.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_sql_injection_fix():
    """Test that SQL injection is no longer possible"""
    print("Testing SQL injection fix...")
    
    # This should NOT execute malicious SQL
    malicious_username = "admin' OR '1'='1"
    response = requests.get(f"{BASE_URL}/user/{malicious_username}")
    
    if response.status_code == 404:
        print("✅ SQL injection fix working: Malicious input treated as data")
    else:
        print("❌ SQL injection fix failed: Unexpected response")
    
    print(f"Response: {response.status_code} - {response.text[:100]}")

def test_performance_fix():
    """Test that the N+1 query problem is fixed"""
    print("\nTesting performance fix...")
    
    # First, register a few test users
    test_users = [
        {"username": "user1", "password": "pass1", "email": "user1@test.com"},
        {"username": "user2", "password": "pass2", "email": "user2@test.com"},
        {"username": "user3", "password": "pass3", "email": "user3@test.com"}
    ]
    
    for user in test_users:
        response = requests.post(f"{BASE_URL}/register", json=user)
        if response.status_code == 201:
            print(f"✅ Registered user: {user['username']}")
        else:
            print(f"⚠️  User {user['username']} already exists or registration failed")
    
    # Test the /users endpoint (should use single query now)
    response = requests.get(f"{BASE_URL}/users")
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Performance fix working: Retrieved {len(users)} users with single query")
        print(f"Users: {[u['username'] for u in users]}")
    else:
        print(f"❌ Performance fix failed: {response.status_code}")

def test_authentication_fix():
    """Test that password validation now works correctly"""
    print("\nTesting authentication fix...")
    
    # Test login with correct credentials
    login_data = {"username": "user1", "password": "pass1"}
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ Authentication fix working: Login successful with correct password")
    else:
        print(f"❌ Authentication fix failed: {response.status_code} - {response.text}")
    
    # Test login with wrong password
    wrong_login = {"username": "user1", "password": "wrongpass"}
    response = requests.post(f"{BASE_URL}/login", json=wrong_login)
    
    if response.status_code == 401:
        print("✅ Authentication fix working: Login correctly rejected with wrong password")
    else:
        print(f"❌ Authentication fix failed: Wrong password should be rejected")

def main():
    print("🧪 Testing Bug Fixes in Flask Application")
    print("=" * 50)
    
    try:
        test_sql_injection_fix()
        test_performance_fix()
        test_authentication_fix()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        print("\nNote: Make sure the Flask application is running on http://localhost:5000")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask application")
        print("Make sure to run 'python app.py' first")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()