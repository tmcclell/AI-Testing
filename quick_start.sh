#!/bin/bash
# Quick start script for AI testing agent

echo "AI-Assisted UI Automation - Quick Start"
echo "======================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    exit 1
fi

echo "✓ Python 3 found"

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Validate environment
echo "Validating environment..."
python3 validate_env.py
if [ $? -ne 0 ]; then
    echo "Environment validation failed. Please fix issues and try again."
    exit 1
fi

# Show available commands
echo ""
echo "Environment validation successful!"
echo ""
echo "Available commands:"
echo "  python3 src/main.py --help                    # Show help"
echo "  python3 src/main.py --scenario swap_test --count 5   # Run 5 swaps"
echo "  python3 src/main.py --dry-run --scenario swap_test   # Dry run mode"
echo ""
echo "Configuration:"
echo "  Edit config/production.yaml with your Azure credentials"
echo ""
echo "Logs and reports will be saved in the 'logs/' directory"
echo ""

# Ask if user wants to run a test
read -p "Would you like to run a dry-run test now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running dry-run test..."
    python3 src/main.py --dry-run --scenario swap_test --count 1
fi
