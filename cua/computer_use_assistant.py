"""
Computer Use Assistant
=====================

Main Computer Use Assistant implementation following Azure CUA patterns.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import openai

from .config import CUAConfig
from .agent import Agent
from .scaler import Scaler
from .local_computer import LocalComputer

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of CUA execution."""
    success: bool
    summary: str
    actions_taken: int
    error_message: Optional[str] = None
    screenshots: List[str] = None


class ComputerUseAssistant:
    """
    Computer Use Assistant for automated GUI interaction.
    
    This class implements the Azure CUA pattern for controlling computer
    interfaces through AI vision and natural language instructions.
    """
    
    def __init__(self, config: CUAConfig):
        self.config = config
        self.client = None
        self.computer = None
        self.agent = None
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize the Computer Use Assistant."""
        try:
            # Initialize OpenAI client
            if self.config.is_azure_endpoint:
                self.client = openai.AsyncAzureOpenAI(
                    azure_endpoint=self.config.azure_endpoint,
                    api_key=self.config.azure_api_key,
                    api_version=self.config.azure_api_version,
                )
                self.logger.info("Initialized Azure OpenAI client")
            else:
                self.client = openai.AsyncOpenAI(
                    api_key=self.config.openai_api_key
                )
                self.logger.info("Initialized OpenAI client")
            
            # Initialize computer interface
            local_computer = LocalComputer()
            
            # Apply screen scaling if configured
            if self.config.scale_dimensions:
                self.computer = Scaler(local_computer, self.config.scale_dimensions)
                self.logger.info(f"Screen scaling enabled: {self.config.scale_dimensions}")
            else:
                self.computer = local_computer
                self.logger.info("Screen scaling disabled")
            
            # Initialize agent
            self.agent = Agent(
                client=self.client,
                model=self.config.model,
                computer=self.computer,
                logger_instance=self.logger
            )
            
            self.logger.info("Computer Use Assistant initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CUA: {e}")
            raise
    
    async def execute_instructions(self, instructions: str) -> ExecutionResult:
        """
        Execute natural language instructions using the CUA.
        
        Args:
            instructions: Natural language instructions to execute
            
        Returns:
            ExecutionResult with success status and details
        """
        if not self.agent:
            raise RuntimeError("CUA not initialized. Call initialize() first.")
            
        self.logger.info(f"Starting task execution: {instructions}")
        
        actions_taken = 0
        screenshots = []
        
        try:
            # Start the task
            self.agent.start_task()
            user_input = instructions
            
            # Main execution loop
            while actions_taken < self.config.max_actions:
                self.logger.debug(f"Execution loop iteration {actions_taken + 1}")
                
                # Continue the task
                if not user_input and self.agent.requires_user_input:
                    self.logger.info("Agent requires additional input, but none provided")
                    break
                    
                await self.agent.continue_task(user_input)
                user_input = None  # Clear after first use
                
                # Handle consent requirements
                if self.agent.requires_consent and not self.config.autoplay:
                    if self.config.require_consent:
                        consent = await self._get_user_consent()
                        if not consent:
                            self.logger.info("User denied consent for action")
                            break
                
                # Handle safety checks
                if self.agent.pending_safety_checks and not self.config.autoplay:
                    if self.config.safety_checks_enabled:
                        safety_consent = await self._handle_safety_checks(
                            self.agent.pending_safety_checks
                        )
                        if not safety_consent:
                            self.logger.info("User denied safety check consent")
                            break
                
                # Log reasoning and actions
                if self.agent.reasoning_summary:
                    self.logger.info(f"AI Reasoning: {self.agent.reasoning_summary}")
                
                actions = self.agent.actions
                if actions:
                    for action, action_args in actions:
                        self.logger.info(f"Executing action: {action} with args: {action_args}")
                        actions_taken += 1
                        
                        # Add delay between actions if configured
                        if self.config.action_delay > 0:
                            await asyncio.sleep(self.config.action_delay)
                
                # Log agent messages
                messages = self.agent.messages
                if messages:
                    for message in messages:
                        self.logger.info(f"Agent: {message}")
                
                # Check if task is complete
                if not self.agent.requires_user_input and not actions:
                    self.logger.info("Task appears to be complete")
                    break
                    
                # Safety check to prevent infinite loops
                if actions_taken >= self.config.max_actions:
                    self.logger.warning(f"Reached maximum actions limit: {self.config.max_actions}")
                    break
            
            # Capture final screenshot
            try:
                final_screenshot = await self.computer.screenshot()
                screenshots.append(final_screenshot)
            except Exception as e:
                self.logger.warning(f"Failed to capture final screenshot: {e}")
            
            success_message = f"Task completed successfully with {actions_taken} actions"
            self.logger.info(success_message)
            
            return ExecutionResult(
                success=True,
                summary=success_message,
                actions_taken=actions_taken,
                screenshots=screenshots
            )
            
        except Exception as e:
            error_message = f"Task execution failed: {e}"
            self.logger.error(error_message, exc_info=True)
            
            return ExecutionResult(
                success=False,
                summary=f"Failed after {actions_taken} actions",
                actions_taken=actions_taken,
                error_message=error_message,
                screenshots=screenshots
            )
    
    async def _get_user_consent(self) -> bool:
        """Get user consent for computer actions."""
        if self.config.autoplay:
            return True
            
        # In a real implementation, this might show a GUI dialog
        # For now, we'll assume consent in autoplay mode
        self.logger.info("User consent required for computer action")
        return True
    
    async def _handle_safety_checks(self, safety_checks: List[str]) -> bool:
        """Handle safety check notifications."""
        if self.config.autoplay:
            self.logger.info(f"Safety checks acknowledged (autoplay): {safety_checks}")
            return True
            
        self.logger.warning(f"Safety checks required: {safety_checks}")
        # In a real implementation, this might require user interaction
        return True
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up Computer Use Assistant")
        
        # Close OpenAI client if needed
        if self.client and hasattr(self.client, 'close'):
            try:
                await self.client.close()
            except Exception as e:
                self.logger.warning(f"Error closing client: {e}")
        
        self.logger.info("Cleanup completed")
