#!/usr/bin/env python3
"""
Azure OpenAI Connection Test
===========================

Test the Azure OpenAI connection directly to diagnose issues.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

import openai
from cua.config import CUAConfig
from cua.logger import setup_logging
from dotenv import load_dotenv

async def test_azure_openai_connection():
    """Test direct connection to Azure OpenAI."""
    print("🔧 Testing Azure OpenAI Connection...")
    
    # Load environment
    load_dotenv()
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    print(f"Endpoint: {endpoint}")
    print(f"API Key: {'*' * 10 + api_key[-10:] if api_key else 'NOT SET'}")
    
    try:
        # Create Azure OpenAI client
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2025-03-01-preview",
        )
        
        print("✅ Azure OpenAI client created successfully")
        
        # Test a simple chat completion (not computer use yet)
        print("🔧 Testing basic chat completion...")
        response = await client.chat.completions.create(
            model="gpt-4o", # Standard chat model
            messages=[{"role": "user", "content": "Hello, can you respond with just 'Connection successful'?"}],
            max_tokens=10
        )
        
        print(f"✅ Chat completion successful: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Azure OpenAI connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Give specific suggestions based on error type
        if "getaddrinfo failed" in str(e):
            print("\n💡 DNS resolution failed. Check:")
            print("   - Network connectivity")
            print("   - Endpoint URL format")
            print("   - VPN/proxy settings")
        elif "401" in str(e) or "authentication" in str(e).lower():
            print("\n💡 Authentication failed. Check:")
            print("   - API key is correct")
            print("   - Resource is active in Azure")
        elif "404" in str(e):
            print("\n💡 Resource not found. Check:")
            print("   - Endpoint URL is correct")
            print("   - Resource exists in Azure")
        
        return False

async def test_computer_use_model():
    """Test computer use model specifically."""
    print("\n🔧 Testing Computer Use Model...")
    
    load_dotenv()
    
    try:
        config = CUAConfig()
        
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=config.azure_endpoint,
            api_key=config.azure_api_key,
            api_version=config.azure_api_version,
        )
        
        # Test computer use model
        print("🔧 Testing computer-use-preview model...")
        
        # Create a simple test without actual screenshot
        response = await client.responses.create(
            model="computer-use-preview",
            input=[
                {
                    "type": "message",
                    "role": "user", 
                    "content": "Hello, can you respond that you're ready to help with computer use?"
                }
            ],
            tools=[
                {
                    "type": "computer_use_preview",
                    "display_width": 1024,
                    "display_height": 768,
                    "environment": "windows"
                }
            ]
        )
        
        print(f"✅ Computer Use model test successful!")
        print(f"   Response status: {response.status}")
        return True
        
    except Exception as e:
        print(f"❌ Computer Use model test failed: {e}")
        return False

async def main():
    """Run all connection tests."""
    print("🚀 Azure OpenAI Connection Diagnostics")
    print("=" * 50)
    
    # Test basic connection
    basic_success = await test_azure_openai_connection()
    
    if basic_success:
        # Test computer use model
        cua_success = await test_computer_use_model()
        
        if cua_success:
            print("\n🎉 All tests passed! Azure OpenAI Computer Use is ready!")
            print("\n✅ Your CUA application should work now.")
        else:
            print("\n⚠️ Basic connection works, but Computer Use model failed.")
            print("   This might be a model availability issue.")
    else:
        print("\n❌ Basic connection failed. Fix connection issues first.")

if __name__ == "__main__":
    asyncio.run(main())
