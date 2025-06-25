#!/usr/bin/env python3
"""
AI-Assisted UI Automation for HPS Testing
==========================================

Main entry point for the AI agent that automates interaction with 
Honeywell Process Solutions test application using Azure Computer Vision.

Author: Microsoft AI Testing Team
Date: June 2025
"""

import sys
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional

from core.agent_orchestrator import AgentOrchestrator
from core.config_manager import ConfigManager
from core.logger import setup_logging
from utils.exceptions import AgentError


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI-Assisted UI Automation for HPS Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --scenario swap_test --count 10
  python main.py --scenario swap_test --count 5 --dry-run
  python main.py --config custom_config.yaml --scenario startup_test
        """
    )
    
    parser.add_argument(
        '--scenario', 
        type=str, 
        default='swap_test',
        choices=['swap_test', 'startup_test', 'status_check'],
        help='Test scenario to execute (default: swap_test)'
    )
    
    parser.add_argument(
        '--count', 
        type=int, 
        default=1,
        help='Number of iterations to perform (default: 1)'
    )
    
    parser.add_argument(
        '--config', 
        type=Path,
        default=Path('config/default.yaml'),
        help='Configuration file path (default: config/default.yaml)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate actions without executing them'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('logs'),
        help='Output directory for logs and reports (default: logs)'
    )
    
    return parser.parse_args()


async def main() -> int:
    """Main entry point for the AI automation agent."""
    args = parse_arguments()
    
    try:
        # Setup logging
        setup_logging(args.log_level, args.output_dir)
        logger = logging.getLogger(__name__)
        
        logger.info("Starting AI-Assisted UI Automation for HPS Testing")
        logger.info(f"Scenario: {args.scenario}")
        logger.info(f"Iterations: {args.count}")
        logger.info(f"Dry run: {args.dry_run}")
        
        # Load configuration
        config_manager = ConfigManager(args.config)
        config = await config_manager.load_config()
        
        # Override config with command line arguments
        config.scenario = args.scenario
        config.iteration_count = args.count
        config.dry_run = args.dry_run
        config.output_dir = args.output_dir
        
        # Initialize and run the agent orchestrator
        orchestrator = AgentOrchestrator(config)
        result = await orchestrator.run()
        
        if result.success:
            logger.info(f"Test completed successfully: {result.summary}")
            return 0
        else:
            logger.error(f"Test failed: {result.error_message}")
            return 1
            
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Test interrupted by user")
        return 130  # Standard exit code for SIGINT
        
    except AgentError as e:
        logging.getLogger(__name__).error(f"Agent error: {e}")
        return 1
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit(130)
