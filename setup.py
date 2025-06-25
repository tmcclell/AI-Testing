#!/usr/bin/env python3
"""
Setup and Installation Script
============================

Automated setup script for the AI testing agent.
"""

import subprocess
import sys
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or later is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")


def install_requirements():
    """Install Python requirements."""
    print("Installing Python dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)


def setup_directories():
    """Create necessary directories."""
    directories = ["logs", "screenshots", "config"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"✓ Directory created: {dir_name}")


def setup_config():
    """Set up configuration files."""
    default_config = Path("config/default.yaml")
    production_config = Path("config/production.yaml")
    
    if not production_config.exists() and default_config.exists():
        import shutil
        shutil.copy(default_config, production_config)
        print("✓ Production config created from default")
        print("⚠️  Please edit config/production.yaml with your Azure credentials")
    else:
        print("✓ Production config already exists")


def check_platform_dependencies():
    """Check platform-specific dependencies."""
    system = platform.system()
    
    if system == "Windows":
        try:
            import win32api
            print("✓ Windows dependencies available")
        except ImportError:
            print("⚠️  Installing Windows-specific dependencies...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "pywin32"
            ])
    
    try:
        import pynput
        print("✓ Input simulation library available")
    except ImportError:
        print("⚠️  Installing input simulation library...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "pynput"
        ])


def main():
    """Main setup function."""
    print("AI-Assisted UI Automation Setup")
    print("=" * 40)
    
    check_python_version()
    setup_directories()
    install_requirements()
    check_platform_dependencies()
    setup_config()
    
    print("\n" + "=" * 40)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit config/production.yaml with your Azure credentials")
    print("2. Start your HPS test application")
    print("3. Run: python src/main.py --help")


if __name__ == "__main__":
    main()
