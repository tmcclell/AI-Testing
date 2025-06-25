#!/usr/bin/env python3
"""
Computer Use Assistant (CUA) for HPS Testing
===========================================

Azure Computer Use Assistant implementation for Honeywell Process Solutions testing.
This follows the Azure CUA pattern for computer control through AI models.

Based on: https://github.com/Azure-Samples/computer-use-model
"""

import asyncio
import logging
import os
from pathlib import Path
import click
from typing import Optional

from cua.computer_use_assistant import ComputerUseAssistant
from cua.config import CUAConfig
from cua.logger import setup_logging


@click.command()
@click.option(
    '--instructions', 
    default="Perform controller swap test on HPS application",
    help='Instructions for the AI to execute'
)
@click.option(
    '--model',
    default="computer-use-preview", 
    help='AI model to use (default: computer-use-preview)'
)
@click.option(
    '--endpoint',
    type=click.Choice(['azure', 'openai']),
    default='azure',
    help='API endpoint to use (default: azure)'
)
@click.option(
    '--autoplay',
    is_flag=True,
    default=False,
    help='Automatically execute actions without confirmation'
)
@click.option(
    '--max-actions',
    default=50,
    help='Maximum number of actions to perform (default: 50)'
)
@click.option(
    '--delay',
    default=2.0,
    help='Delay between actions in seconds (default: 2.0)'
)
@click.option(
    '--log-level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
    default='INFO',
    help='Logging level (default: INFO)'
)
@click.option(
    '--output-dir',
    type=click.Path(),
    default='logs',
    help='Output directory for logs and screenshots (default: logs)'
)
async def main(
    instructions: str,
    model: str,
    endpoint: str,
    autoplay: bool,
    max_actions: int,
    delay: float,
    log_level: str,
    output_dir: str
):
    """
    Computer Use Assistant for HPS Testing.
    
    This tool uses Azure's Computer Use model to automate interaction with
    the Honeywell Process Solutions test application through natural language
    instructions.
    """
    
    # Setup logging
    setup_logging(log_level, Path(output_dir))
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Computer Use Assistant for HPS Testing")
    logger.info(f"Instructions: {instructions}")
    logger.info(f"Model: {model}")
    logger.info(f"Endpoint: {endpoint}")
    logger.info(f"Autoplay: {autoplay}")
    
    try:
        # Load configuration
        config = CUAConfig(
            model=model,
            endpoint=endpoint,
            autoplay=autoplay,
            max_actions=max_actions,
            action_delay=delay,
            output_dir=Path(output_dir),
            log_level=log_level
        )
        
        # Initialize Computer Use Assistant
        cua = ComputerUseAssistant(config)
        await cua.initialize()
        
        # Execute the instructions
        result = await cua.execute_instructions(instructions)
        
        if result.success:
            logger.info(f"Task completed successfully: {result.summary}")
            return 0
        else:
            logger.error(f"Task failed: {result.error_message}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Task interrupted by user")
        return 130
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
        
    finally:
        if 'cua' in locals():
            await cua.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
