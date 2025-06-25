#!/usr/bin/env python3
"""
Test Configuration Loading
=========================

Simple test to verify that the CUA configuration loads properly from .env file.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from cua.config import CUAConfig
from cua.logger import setup_logging

def test_config_loading():
    """Test that configuration loads properly."""
    print("🔧 Testing CUA Configuration Loading...")
    
    try:
        # Set up basic logging
        setup_logging("DEBUG")
        
        # Create configuration
        config = CUAConfig()
        
        print(f"✅ Configuration loaded successfully!")
        print(f"   Model: {config.model}")
        print(f"   Endpoint: {config.endpoint}")
        print(f"   Azure Endpoint: {config.azure_endpoint}")
        print(f"   API Key: {'SET' if config.azure_api_key and config.azure_api_key != 'your-actual-api-key-here' else 'NOT SET'}")
        print(f"   API Version: {config.azure_api_version}")
        print(f"   Autoplay: {config.autoplay}")
        print(f"   Max Actions: {config.max_actions}")
        print(f"   Scale Dimensions: {config.scale_dimensions}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def test_imports():
    """Test that all CUA modules can be imported."""
    print("\n🔧 Testing CUA Module Imports...")
    
    try:
        from cua import Agent, Scaler, LocalComputer, ComputerUseAssistant
        print("✅ All CUA modules imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_local_computer():
    """Test LocalComputer basic functionality."""
    print("\n🔧 Testing LocalComputer...")
    
    try:
        from cua.local_computer import LocalComputer
        
        computer = LocalComputer()
        print(f"✅ LocalComputer created successfully!")
        print(f"   Environment: {computer.environment}")
        print(f"   Dimensions: {computer.dimensions}")
        
        return True
    except Exception as e:
        print(f"❌ LocalComputer test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CUA Application Testing & Debugging")
    print("=" * 50)
    
    all_passed = True
    
    # Test configuration loading
    all_passed &= test_config_loading()
    
    # Test imports
    all_passed &= test_imports()
    
    # Test LocalComputer
    all_passed &= test_local_computer()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nNext steps:")
        print("1. Set your actual Azure OpenAI API key in .env file")
        print("2. Run: python simple_cua.py --instructions 'Take a screenshot'")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("\n💡 Tip: Update AZURE_OPENAI_API_KEY in .env file with your real key to test Azure OpenAI connectivity.")
