#!/usr/bin/env python3
"""
Test Azure OpenAI Connection - End-to-End
==========================================

Simple test to verify the Azure OpenAI connection is working completely.
"""

import asyncio
import logging
from dotenv import load_dotenv
import os
from openai import AsyncAzureOpenAI

# Load .env with override
load_dotenv(override=True)

async def test_azure_openai_connection():
    """Test Azure OpenAI with a simple completion."""
    print("🔗 Testing Azure OpenAI Connection End-to-End...")
    
    try:
        # Create client
        client = AsyncAzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version="2025-03-01-preview",
        )
        
        print(f"   ✅ Client created with endpoint: {os.environ['AZURE_OPENAI_ENDPOINT']}")
        
        # Test a simple completion
        response = await client.chat.completions.create(
            model="computer-use-preview",
            messages=[
                {"role": "user", "content": "Say 'Hello from Azure OpenAI!' and nothing else."}
            ],
            max_tokens=10
        )
        
        print(f"   ✅ Chat completion successful!")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Model used: {response.model}")
        print(f"   Tokens used: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def main():
    """Run the connection test."""
    print("🚀 Azure OpenAI End-to-End Connection Test")
    print("=" * 45)
    
    success = await test_azure_openai_connection()
    
    if success:
        print("\n🎉 SUCCESS: Azure OpenAI connection is working perfectly!")
        print("   The CUA system should now work end-to-end.")
    else:
        print("\n❌ FAILED: There are still connection issues.")
        
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
