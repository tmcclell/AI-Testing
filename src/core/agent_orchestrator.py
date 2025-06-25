"""
Core Agent Orchestrator
======================

The main orchestrator that coordinates all modules to execute AI-driven testing.
This is the "brain" that manages the test workflow, AI calls, and decision making.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .config_manager import Config
from .screen_capture import ScreenCaptureModule
from .azure_ai_client import AzureAIClient
from .action_executor import ActionExecutor
from .test_reporter import TestReporter
from .context_manager import ContextManager
from utils.exceptions import AgentError, UIError, AIError


@dataclass
class TestResult:
    """Result of a test execution."""
    success: bool
    summary: str
    error_message: Optional[str] = None
    iterations_completed: int = 0
    total_time_seconds: float = 0.0
    log_file_path: Optional[str] = None


class AgentOrchestrator:
    """
    Main orchestrator for the AI testing agent.
    
    Coordinates between screen capture, AI analysis, action execution,
    and reporting to automate UI testing workflows.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize core modules
        self.screen_capture = ScreenCaptureModule(config)
        self.ai_client = AzureAIClient(config)
        self.action_executor = ActionExecutor(config)
        self.test_reporter = TestReporter(config)
        self.context_manager = ContextManager()
        
        # Test state
        self.current_iteration = 0
        self.test_start_time = None
        self.is_paused = False
        self.should_abort = False
        
    async def run(self) -> TestResult:
        """
        Execute the main test workflow.
        
        Returns:
            TestResult: Summary of test execution
        """
        self.test_start_time = datetime.now()
        
        try:
            # Initialize all modules
            await self._initialize_modules()
            
            # Verify application is ready
            await self._verify_application_ready()
            
            # Execute the test scenario
            if self.config.scenario == 'swap_test':
                result = await self._execute_swap_test()
            elif self.config.scenario == 'startup_test':
                result = await self._execute_startup_test()
            elif self.config.scenario == 'status_check':
                result = await self._execute_status_check()
            else:
                raise AgentError(f"Unknown scenario: {self.config.scenario}")
            
            # Generate final report
            await self._generate_final_report(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}", exc_info=True)
            
            # Generate error report
            error_result = TestResult(
                success=False,
                summary=f"Test failed: {str(e)}",
                error_message=str(e),
                iterations_completed=self.current_iteration,
                total_time_seconds=(datetime.now() - self.test_start_time).total_seconds()
            )
            
            await self._generate_final_report(error_result)
            return error_result
            
        finally:
            await self._cleanup_modules()
    
    async def _initialize_modules(self):
        """Initialize all core modules."""
        self.logger.info("Initializing agent modules...")
        
        await self.screen_capture.initialize()
        await self.ai_client.initialize()
        await self.action_executor.initialize()
        await self.test_reporter.initialize()
        
        self.logger.info("All modules initialized successfully")
    
    async def _cleanup_modules(self):
        """Clean up all modules."""
        self.logger.info("Cleaning up agent modules...")
        
        try:
            await self.screen_capture.cleanup()
            await self.ai_client.cleanup()
            await self.action_executor.cleanup()
            await self.test_reporter.cleanup()
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
    
    async def _verify_application_ready(self):
        """Verify the target application is ready for testing."""
        self.logger.info("Verifying target application is ready...")
        
        # Capture initial screen
        screenshot = await self.screen_capture.capture_screen()
        
        # Ask AI to verify we're looking at the correct application
        verification_prompt = self._build_verification_prompt()
        response = await self.ai_client.analyze_screen(screenshot, verification_prompt)
        
        if not response.get('application_ready', False):
            raise UIError(f"Application not ready: {response.get('reason', 'Unknown')}")
        
        self.logger.info("Application verification successful")
    
    async def _execute_swap_test(self) -> TestResult:
        """Execute the controller swap test scenario."""
        self.logger.info(f"Starting swap test with {self.config.iteration_count} iterations")
        
        successful_swaps = 0
        
        for iteration in range(1, self.config.iteration_count + 1):
            self.current_iteration = iteration
            
            if self.should_abort:
                break
                
            self.logger.info(f"Starting swap iteration {iteration}/{self.config.iteration_count}")
            
            try:
                # Execute single swap
                await self._execute_single_swap(iteration)
                successful_swaps += 1
                
                self.logger.info(f"Swap {iteration} completed successfully")
                
                # Brief pause between iterations
                if iteration < self.config.iteration_count:
                    await asyncio.sleep(self.config.inter_iteration_delay)
                    
            except Exception as e:
                self.logger.error(f"Swap {iteration} failed: {e}")
                
                # Decide whether to continue or abort
                if self.config.stop_on_error:
                    break
                else:
                    # Try to recover and continue
                    await self._attempt_recovery()
        
        total_time = (datetime.now() - self.test_start_time).total_seconds()
        
        if successful_swaps == self.config.iteration_count:
            return TestResult(
                success=True,
                summary=f"All {successful_swaps} swaps completed successfully",
                iterations_completed=successful_swaps,
                total_time_seconds=total_time
            )
        else:
            return TestResult(
                success=False,
                summary=f"Only {successful_swaps}/{self.config.iteration_count} swaps completed",
                error_message=f"Failed after {successful_swaps} successful iterations",
                iterations_completed=successful_swaps,
                total_time_seconds=total_time
            )
    
    async def _execute_single_swap(self, iteration: int):
        """Execute a single controller swap operation."""
        # Build context for this iteration
        context = self.context_manager.build_context({
            'scenario': 'swap_test',
            'iteration': iteration,
            'total_iterations': self.config.iteration_count,
            'controllers': self.config.target_controllers
        })
        
        # Main swap workflow
        await self._navigate_to_system_status(context)
        await self._select_target_network(context)
        await self._initiate_controller_swap(context)
        await self._wait_for_swap_completion(context)
        await self._verify_swap_success(context)
    
    async def _navigate_to_system_status(self, context: Dict[str, Any]):
        """Navigate to the System Status screen."""
        self.logger.info("Navigating to System Status screen...")
        
        screenshot = await self.screen_capture.capture_screen()
        prompt = self._build_navigation_prompt("system_status", context)
        
        response = await self.ai_client.analyze_screen(screenshot, prompt)
        
        if response.get('action_needed'):
            action = response.get('recommended_action')
            await self._execute_ai_action(action, "Navigate to System Status")
            
            # Wait for screen to load
            await self._wait_for_screen_change("system_status")
    
    async def _select_target_network(self, context: Dict[str, Any]):
        """Select the target network (UCN 07 / NM 44)."""
        self.logger.info(f"Selecting target network: {self.config.target_network}")
        
        screenshot = await self.screen_capture.capture_screen()
        prompt = self._build_selection_prompt("network", context)
        
        response = await self.ai_client.analyze_screen(screenshot, prompt)
        
        if response.get('action_needed'):
            action = response.get('recommended_action')
            await self._execute_ai_action(action, f"Select network {self.config.target_network}")
            
            # Wait for network status screen
            await self._wait_for_screen_change("network_status")
    
    async def _initiate_controller_swap(self, context: Dict[str, Any]):
        """Initiate the controller swap operation."""
        self.logger.info("Initiating controller swap...")
        
        screenshot = await self.screen_capture.capture_screen()
        prompt = self._build_swap_prompt(context)
        
        response = await self.ai_client.analyze_screen(screenshot, prompt)
        
        if response.get('action_needed'):
            action = response.get('recommended_action')
            await self._execute_ai_action(action, "Initiate controller swap")
    
    async def _wait_for_swap_completion(self, context: Dict[str, Any]):
        """Wait for the controller swap to complete."""
        self.logger.info("Waiting for swap completion...")
        
        max_wait_time = self.config.swap_completion_timeout
        poll_interval = self.config.status_poll_interval
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            screenshot = await self.screen_capture.capture_screen()
            prompt = self._build_status_check_prompt(context)
            
            response = await self.ai_client.analyze_screen(screenshot, prompt)
            
            if response.get('swap_completed'):
                self.logger.info(f"Swap completed in {elapsed_time:.1f} seconds")
                return
            
            if response.get('error_detected'):
                raise UIError(f"Error detected during swap: {response.get('error_message')}")
            
            await asyncio.sleep(poll_interval)
            elapsed_time += poll_interval
            
            # Log progress periodically
            if elapsed_time % 30 == 0:  # Every 30 seconds
                self.logger.info(f"Still waiting for swap completion... ({elapsed_time}s elapsed)")
        
        raise UIError(f"Swap did not complete within {max_wait_time} seconds")
    
    async def _verify_swap_success(self, context: Dict[str, Any]):
        """Verify the swap completed successfully."""
        self.logger.info("Verifying swap success...")
        
        screenshot = await self.screen_capture.capture_screen()
        prompt = self._build_verification_prompt("swap_success", context)
        
        response = await self.ai_client.analyze_screen(screenshot, prompt)
        
        if not response.get('swap_successful'):
            raise UIError(f"Swap verification failed: {response.get('reason')}")
        
        self.logger.info("Swap verification successful")
    
    async def _execute_ai_action(self, action: Dict[str, Any], description: str):
        """Execute an action recommended by the AI."""
        if self.config.dry_run:
            self.logger.info(f"[DRY RUN] Would execute: {description} - {action}")
            return
        
        self.logger.info(f"Executing: {description}")
        await self.action_executor.execute_action(action)
        
        # Brief pause after action
        await asyncio.sleep(self.config.action_delay)
    
    async def _wait_for_screen_change(self, expected_screen: str):
        """Wait for the screen to change to the expected state."""
        max_wait_time = self.config.screen_change_timeout
        poll_interval = self.config.screen_poll_interval
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            screenshot = await self.screen_capture.capture_screen()
            prompt = f"Is this the {expected_screen} screen? Respond with yes/no and brief explanation."
            
            response = await self.ai_client.analyze_screen(screenshot, prompt)
            
            if response.get('screen_matches', False):
                return
            
            await asyncio.sleep(poll_interval)
            elapsed_time += poll_interval
        
        raise UIError(f"Screen did not change to {expected_screen} within {max_wait_time} seconds")
    
    async def _attempt_recovery(self):
        """Attempt to recover from an error state."""
        self.logger.info("Attempting error recovery...")
        
        # Take a screenshot to assess current state
        screenshot = await self.screen_capture.capture_screen()
        
        # Ask AI what recovery action to take
        recovery_prompt = "The test encountered an error. What recovery action should be taken?"
        response = await self.ai_client.analyze_screen(screenshot, recovery_prompt)
        
        if response.get('recovery_possible'):
            action = response.get('recovery_action')
            await self._execute_ai_action(action, "Recovery action")
        else:
            self.logger.warning("No recovery action available")
    
    async def _execute_startup_test(self) -> TestResult:
        """Execute startup test scenario (placeholder)."""
        # TODO: Implement startup test logic
        raise NotImplementedError("Startup test not yet implemented")
    
    async def _execute_status_check(self) -> TestResult:
        """Execute status check scenario (placeholder)."""
        # TODO: Implement status check logic
        raise NotImplementedError("Status check not yet implemented")
    
    def _build_verification_prompt(self, verification_type: str = "application", context: Dict[str, Any] = None) -> str:
        """Build prompt for application/state verification."""
        if verification_type == "application":
            return """
            You are looking at a screen capture of the Honeywell Process Solutions test application.
            Please verify:
            1. Is this the correct HPS application?
            2. Is the main menu visible?
            3. Are we ready to begin testing?
            
            Respond in JSON format:
            {
                "application_ready": true/false,
                "reason": "explanation of readiness state"
            }
            """
        elif verification_type == "swap_success":
            return f"""
            You are verifying the success of a controller swap operation.
            Expected controllers: {context.get('controllers', 'Unknown')}
            
            Please check:
            1. Are both controllers showing expected status?
            2. Is one controller primary and one backup?
            3. Are there any error indicators?
            
            Respond in JSON format:
            {{
                "swap_successful": true/false,
                "reason": "explanation of current state"
            }}
            """
        
        return "Please analyze this screen and provide assessment."
    
    def _build_navigation_prompt(self, target: str, context: Dict[str, Any]) -> str:
        """Build prompt for navigation actions."""
        return f"""
        You are controlling the HPS test application. Current goal: Navigate to {target}.
        
        Please analyze the current screen and determine:
        1. What screen are we currently on?
        2. What action is needed to reach {target}?
        3. What specific UI element should be activated?
        
        Respond in JSON format:
        {{
            "current_screen": "description",
            "action_needed": true/false,
            "recommended_action": {{
                "type": "key_press" or "click",
                "target": "UI element description",
                "key": "key name (if key_press)",
                "coordinates": [x, y] // if click
            }}
        }}
        """
    
    def _build_selection_prompt(self, selection_type: str, context: Dict[str, Any]) -> str:
        """Build prompt for selection actions."""
        return f"""
        You are selecting {selection_type} in the HPS application.
        Target: {context.get('target_network', 'UCN 07 / NM 44')}
        
        Please:
        1. Identify the target item in the list
        2. Determine how to select it (arrow keys + enter)
        3. Provide the action sequence
        
        Respond in JSON format:
        {{
            "target_found": true/false,
            "action_needed": true/false,
            "recommended_action": {{
                "type": "key_sequence",
                "keys": ["Down", "Down", "Enter"] // example
            }}
        }}
        """
    
    def _build_swap_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for swap initiation."""
        return f"""
        You are initiating a controller swap operation.
        Target controllers: {context.get('controllers', '17 HPM 18')}
        
        Please:
        1. Locate the "Swap Primary" option
        2. Determine the action to activate it
        3. Handle any confirmation dialogs
        
        Respond in JSON format:
        {{
            "swap_option_found": true/false,
            "action_needed": true/false,
            "recommended_action": {{
                "type": "key_press",
                "key": "+" // or other action
            }}
        }}
        """
    
    def _build_status_check_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for status checking."""
        return f"""
        You are monitoring the status of controllers after a swap operation.
        Expected progression: OFFLINE -> PARTFAIL/BKUP_PF (or similar recovery state)
        
        Please analyze:
        1. Current status of both controllers
        2. Whether swap is complete
        3. Any error conditions
        
        Respond in JSON format:
        {{
            "controller_status": "current status description",
            "swap_completed": true/false,
            "error_detected": true/false,
            "error_message": "description if error"
        }}
        """
    
    async def _generate_final_report(self, result: TestResult):
        """Generate the final test report."""
        await self.test_reporter.generate_report(result)
