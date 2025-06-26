#!/usr/bin/env python3
"""
Detailed Azure OpenAI Connection Test
Tests various aspects of Azure OpenAI connectivity and configuration.
"""

import os
import sys
import socket
import requests
from urllib.parse import urlparse
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
import time

def test_network_connectivity():
    """Test basic network connectivity to Azure OpenAI endpoint."""
    print("🌐 Testing Network Connectivity...")
    
    # Load environment variables with override to prioritize .env file
    load_dotenv(override=True)
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    
    if not endpoint:
        print("❌ AZURE_OPENAI_ENDPOINT not found in environment")
        return False
    
    print(f"   Endpoint: {endpoint}")
    
    # Parse URL
    try:
        parsed = urlparse(endpoint)
        hostname = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        print(f"   Hostname: {hostname}")
        print(f"   Port: {port}")
        
        # Test DNS resolution
        try:
            ip = socket.gethostbyname(hostname)
            print(f"   ✅ DNS Resolution: {hostname} -> {ip}")
        except socket.gaierror as e:
            print(f"   ❌ DNS Resolution failed: {e}")
            return False
        
        # Test socket connection
        try:
            sock = socket.create_connection((hostname, port), timeout=10)
            sock.close()
            print(f"   ✅ Socket connection successful")
        except (socket.timeout, socket.error) as e:
            print(f"   ❌ Socket connection failed: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ URL parsing failed: {e}")
        return False

def test_http_connectivity():
    """Test HTTP connectivity to Azure OpenAI endpoint."""
    print("\n🔗 Testing HTTP Connectivity...")
    
    load_dotenv(override=True)
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not endpoint or not api_key:
        print("❌ Missing endpoint or API key")
        return False
    
    # Test basic HTTP GET to the endpoint
    try:
        # Remove trailing slash and add a basic path
        base_url = endpoint.rstrip('/')
        test_url = f"{base_url}/openai/deployments?api-version=2023-12-01-preview"
        
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        print(f"   Testing URL: {test_url}")
        response = requests.get(test_url, headers=headers, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ HTTP connection successful")
            try:
                data = response.json()
                print(f"   Response data: {json.dumps(data, indent=2)}")
            except:
                print(f"   Response text: {response.text[:200]}...")
            return True
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ HTTP request failed: {e}")
        return False

def test_openai_client():
    """Test Azure OpenAI client creation and basic functionality."""
    print("\n🤖 Testing Azure OpenAI Client...")
    
    load_dotenv(override=True)
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not endpoint or not api_key:
        print("❌ Missing endpoint or API key")
        return False
    
    try:
        # Create client
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2023-12-01-preview"
        )
        print("   ✅ Client created successfully")
        
        # Try to list models/deployments
        try:
            print("   Attempting to list models...")
            # This might not work if we don't have the right permissions
            # but it will help us understand the connection
            response = client.models.list()
            print(f"   ✅ Models list successful: {len(response.data)} models")
            for model in response.data[:3]:  # Show first 3
                print(f"      - {model.id}")
        except Exception as e:
            print(f"   ⚠️  Models list failed (this might be normal): {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Client creation failed: {e}")
        return False

def test_environment_variables():
    """Test all environment variables and configuration."""
    print("\n📋 Testing Environment Configuration...")
    
    load_dotenv(override=True)
    
    # Check required variables
    required_vars = ['AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY']
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Don't print the full API key for security
            if 'API_KEY' in var:
                print(f"   ✅ {var}: {value[:10]}...{value[-10:]}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
            all_good = False
    
    # Check .env file existence
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"   ✅ .env file exists")
        with open(env_file, 'r') as f:
            lines = f.readlines()
            print(f"   .env file has {len(lines)} lines")
    else:
        print(f"   ❌ .env file not found")
        all_good = False
    
    return all_good

def test_proxy_settings():
    """Test if proxy settings might be interfering."""
    print("\n🔒 Testing Proxy Settings...")
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxy_found = False
    
    for var in proxy_vars:
        value = os.getenv(var)
        if value:
            print(f"   ⚠️  {var}: {value}")
            proxy_found = True
    
    if not proxy_found:
        print("   ✅ No proxy settings found")
    else:
        print("   ⚠️  Proxy settings detected - these might interfere with Azure connections")
    
    return not proxy_found

def main():
    """Run all diagnostic tests."""
    print("🔍 Azure OpenAI Detailed Connection Diagnostics")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Network Connectivity", test_network_connectivity),
        ("HTTP Connectivity", test_http_connectivity),
        ("Proxy Settings", test_proxy_settings),
        ("OpenAI Client", test_openai_client),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Azure OpenAI should be working.")
    else:
        print("\n🔧 Some tests failed. Check the details above for troubleshooting.")
        print("\nCommon solutions:")
        print("   1. Verify your Azure OpenAI resource is deployed and running")
        print("   2. Check that your API key is correct and not expired")
        print("   3. Ensure your endpoint URL is correct")
        print("   4. Verify network/firewall settings")
        print("   5. Check if you're behind a corporate proxy")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
