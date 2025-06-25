"""
Environment Validator
===================

Validates the environment setup for the AI testing agent.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import List, Tuple


class EnvironmentValidator:
    """Validates environment setup and dependencies."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("Validating environment setup...")
        print("=" * 40)
        
        self.check_python_version()
        self.check_dependencies()
        self.check_configuration()
        self.check_directories()
        self.check_azure_connectivity()
        
        self.print_results()
        return len(self.errors) == 0
    
    def check_python_version(self):
        """Check Python version compatibility."""
        if sys.version_info < (3, 8):
            self.errors.append("Python 3.8 or later is required")
        else:
            print(f"✓ Python {sys.version.split()[0]}")
    
    def check_dependencies(self):
        """Check required Python packages."""
        required_packages = [
            'aiohttp',
            'pyyaml',
            'pillow'
        ]
        
        platform_packages = {
            'Windows': ['pywin32', 'pynput'],
            'Linux': ['pynput'],
            'Darwin': ['pynput']  # macOS
        }
        
        system = platform.system()
        if system in platform_packages:
            required_packages.extend(platform_packages[system])
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✓ {package}")
            except ImportError:
                self.errors.append(f"Missing package: {package}")
    
    def check_configuration(self):
        """Check configuration files."""
        config_file = Path("config/production.yaml")
        
        if not config_file.exists():
            self.errors.append("Missing config/production.yaml")
            return
        
        try:
            import yaml
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            # Check required fields
            required_fields = [
                'azure_endpoint',
                'azure_api_key',
                'azure_deployment_name'
            ]
            
            for field in required_fields:
                if not config.get(field):
                    self.errors.append(f"Missing config field: {field}")
                elif config[field] in ['your-api-key-here', 'your-azure-endpoint']:
                    self.warnings.append(f"Default placeholder value for: {field}")
            
            print("✓ Configuration file exists")
            
        except Exception as e:
            self.errors.append(f"Invalid configuration file: {e}")
    
    def check_directories(self):
        """Check required directories exist."""
        required_dirs = ['logs', 'screenshots', 'config']
        
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True)
                    print(f"✓ Created directory: {dir_name}")
                except Exception as e:
                    self.errors.append(f"Cannot create directory {dir_name}: {e}")
            else:
                print(f"✓ Directory exists: {dir_name}")
    
    def check_azure_connectivity(self):
        """Check Azure connectivity (basic DNS resolution)."""
        try:
            import socket
            socket.gethostbyname('openai.azure.com')
            print("✓ Azure DNS resolution")
        except Exception:
            self.warnings.append("Cannot resolve Azure domains - check network connectivity")
    
    def print_results(self):
        """Print validation results."""
        print("\n" + "=" * 40)
        
        if self.errors:
            print("❌ ERRORS FOUND:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ All checks passed!")
        elif not self.errors:
            print("✅ No critical errors found")
        
        print("=" * 40)


def main():
    """Main validation function."""
    validator = EnvironmentValidator()
    success = validator.validate_all()
    
    if not success:
        print("\nPlease fix the errors above before running the agent.")
        sys.exit(1)
    else:
        print("\nEnvironment validation completed successfully!")


if __name__ == "__main__":
    main()
