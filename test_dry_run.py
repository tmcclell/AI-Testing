#!/usr/bin/env python3
"""
CUA Dry Run Test
===============

Test the CUA application without making actual API calls.
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from cua.config import CUAConfig
from cua.logger import setup_logging
from cua.local_computer import LocalComputer
from cua.scaler import Scaler

async def test_screenshot():
    """Test taking a screenshot without AI."""
    print("📸 Testing Screenshot Functionality...")
    
    try:
        # Create computer interface
        computer = LocalComputer()
        print(f"✅ Computer interface created: {computer.environment}")
        
        # Take a screenshot
        screenshot = await computer.screenshot()
        print(f"✅ Screenshot taken: {len(screenshot)} bytes (base64)")
        
        # Test scaler
        scaler = Scaler(computer, (1024, 768))
        scaled_screenshot = await scaler.screenshot()
        print(f"✅ Scaled screenshot: {len(scaled_screenshot)} bytes")
        print(f"   Original dimensions: {computer.dimensions}")
        print(f"   Scaled dimensions: {scaler.dimensions}")
        
        return True
        
    except Exception as e:
        print(f"❌ Screenshot test failed: {e}")
        return False

async def test_computer_actions():
    """Test computer actions without AI."""
    print("\n🖱️ Testing Computer Actions...")
    
    try:
        computer = LocalComputer()
        
        # Test mouse move (safe action)
        print("   Testing mouse move...")
        await computer.move(100, 100)
        print("   ✅ Mouse move successful")
        
        # Test wait
        print("   Testing wait...")
        await computer.wait(100)  # 100ms
        print("   ✅ Wait successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Computer actions test failed: {e}")
        return False

def test_configuration_validation():
    """Test configuration validation with different scenarios."""
    print("\n⚙️ Testing Configuration Validation...")
    
    try:
        setup_logging("INFO")
        
        # Test with current config
        print("   Testing current configuration...")
        config = CUAConfig()
        
        api_key_status = "SET" if (config.azure_api_key and 
                                 config.azure_api_key != 'your-actual-api-key-here') else "NOT SET"
        
        print(f"   ✅ Config loaded - API Key: {api_key_status}")
        
        if api_key_status == "NOT SET":
            print("   ⚠️ You need to set AZURE_OPENAI_API_KEY in .env file")
            print("   💡 Edit .env file and replace 'your-actual-api-key-here' with your real key")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def main():
    """Run all dry-run tests."""
    print("🧪 CUA Dry Run Testing")
    print("=" * 50)
    
    all_passed = True
    
    # Test configuration
    all_passed &= test_configuration_validation()
    
    # Test screenshot
    all_passed &= await test_screenshot()
    
    # Test computer actions
    all_passed &= await test_computer_actions()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All dry-run tests passed!")
        print("\n✅ Your CUA application is working correctly!")
        print("\n📋 Next Steps:")
        print("1. Get your Azure OpenAI API key from Azure portal")
        print("2. Edit .env file and replace 'your-actual-api-key-here'")
        print("3. Run: python simple_cua.py --instructions 'Take a screenshot'")
        print("\n💡 The application can take screenshots and control the computer.")
        print("   It just needs a valid API key to connect to Azure OpenAI.")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
