#!/usr/bin/env python3
"""
Check Available Models in Azure OpenAI Deployment
================================================

Check what models are available and test with a working model.
"""

import asyncio
import logging
from dotenv import load_dotenv
import os
from openai import AsyncAzureOpenAI

# Load .env with override
load_dotenv(override=True)

async def list_available_models():
    """List all available models in the Azure OpenAI deployment."""
    print("📋 Listing Available Models...")
    
    try:
        # Create client
        client = AsyncAzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version="2025-03-01-preview",
        )
        
        models = await client.models.list()
        
        print(f"   ✅ Found {len(models.data)} models:")
        
        # Group models by type for better readability
        gpt_models = []
        embedding_models = []
        other_models = []
        
        for model in models.data:
            if 'gpt' in model.id.lower():
                gpt_models.append(model.id)
            elif 'embedding' in model.id.lower():
                embedding_models.append(model.id)
            else:
                other_models.append(model.id)
        
        if gpt_models:
            print(f"\n   🤖 GPT Models ({len(gpt_models)}):")
            for model in sorted(gpt_models)[:10]:  # Show first 10
                print(f"      - {model}")
            if len(gpt_models) > 10:
                print(f"      ... and {len(gpt_models) - 10} more")
        
        if embedding_models:
            print(f"\n   📊 Embedding Models ({len(embedding_models)}):")
            for model in sorted(embedding_models)[:5]:  # Show first 5
                print(f"      - {model}")
            if len(embedding_models) > 5:
                print(f"      ... and {len(embedding_models) - 5} more")
        
        if other_models:
            print(f"\n   🔧 Other Models ({len(other_models)}):")
            for model in sorted(other_models)[:10]:  # Show first 10
                print(f"      - {model}")
            if len(other_models) > 10:
                print(f"      ... and {len(other_models) - 10} more")
        
        return gpt_models
        
    except Exception as e:
        print(f"   ❌ Failed to list models: {e}")
        return []

async def test_with_available_model(model_name):
    """Test Azure OpenAI with an available model."""
    print(f"\n🧪 Testing with model: {model_name}")
    
    try:
        client = AsyncAzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version="2025-03-01-preview",
        )
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Hello! Please respond with 'Azure OpenAI is working!' and nothing else."}
            ],
            max_tokens=20
        )
        
        print(f"   ✅ Test successful!")
        print(f"   Response: {response.choices[0].message.content}")
        print(f"   Model: {response.model}")
        print(f"   Tokens: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🔍 Azure OpenAI Model Discovery and Testing")
    print("=" * 50)
    
    # List available models
    gpt_models = await list_available_models()
    
    if not gpt_models:
        print("\n❌ No GPT models found or accessible.")
        return False
    
    # Test with the first available GPT model
    test_model = gpt_models[0]
    print(f"\n🎯 Testing with first available GPT model: {test_model}")
    
    success = await test_with_available_model(test_model)
    
    if success:
        print(f"\n🎉 SUCCESS: Azure OpenAI is working with model '{test_model}'!")
        print("\n💡 For the CUA system, you should:")
        print(f"   1. Update the model parameter to use '{test_model}' instead of 'computer-use-preview'")
        print("   2. Note that this model may not have computer vision capabilities")
        print("   3. Consider deploying a vision-capable model for full CUA functionality")
    else:
        print(f"\n❌ FAILED: Could not connect with model '{test_model}'")
        
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
