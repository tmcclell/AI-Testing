"""
Action Executor
==============

Executes UI actions based on AI recommendations.
Handles keyboard and mouse input simulation for Windows and Linux.
"""

import asyncio
import logging
import platform
from typing import Dict, Any, List
import time

# Platform-specific imports
if platform.system() == "Windows":
    import win32api
    import win32con
    import win32gui
    import pynput.keyboard as keyboard
    import pynput.mouse as mouse
else:
    # Linux imports
    try:
        import subprocess
        from pynput import keyboard, mouse
    except ImportError:
        pass

from .config_manager import Config
from utils.exceptions import ActionExecutionError


class ActionExecutor:
    """
    Executes UI actions on the target application.
    
    Supports keyboard input simulation (primary method for HPS app)
    and mouse operations as needed.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.keyboard_controller = None
        self.mouse_controller = None
        
        # Key mappings for HPS application
        self.key_mappings = {
            'click': 'num_add',  # '+' key for click simulation
            'enter': 'enter',
            'escape': 'escape',
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
            'tab': 'tab',
            'space': 'space'
        }
    
    async def initialize(self):
        """Initialize the action executor."""
        self.logger.info("Initializing action executor...")
        
        try:
            # Initialize input controllers
            if platform.system() == "Windows":
                await self._initialize_windows()
            else:
                await self._initialize_linux()
            
            self.logger.info("Action executor initialized successfully")
            
        except Exception as e:
            raise ActionExecutionError(f"Failed to initialize action executor: {e}")
    
    async def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up action executor...")
        # No special cleanup needed
    
    async def _initialize_windows(self):
        """Initialize Windows-specific input handling."""
        from pynput import keyboard, mouse
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()
    
    async def _initialize_linux(self):
        """Initialize Linux-specific input handling."""
        from pynput import keyboard, mouse
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()
    
    async def execute_action(self, action: Dict[str, Any]):
        """
        Execute an action based on AI recommendation.
        
        Args:
            action: Dictionary containing action details
                - type: 'key_press', 'key_sequence', 'click', 'wait'
                - Additional parameters based on type
        """
        action_type = action.get('type')
        
        if not action_type:
            raise ActionExecutionError("Action type not specified")
        
        self.logger.info(f"Executing action: {action_type}")
        
        try:
            if action_type == 'key_press':
                await self._execute_key_press(action)
            elif action_type == 'key_sequence':
                await self._execute_key_sequence(action)
            elif action_type == 'click':
                await self._execute_click(action)
            elif action_type == 'wait':
                await self._execute_wait(action)
            elif action_type == 'focus_window':
                await self._execute_focus_window()
            else:
                raise ActionExecutionError(f"Unknown action type: {action_type}")
            
            # Brief pause after action
            await asyncio.sleep(self.config.action_delay)
            
        except Exception as e:
            self.logger.error(f"Action execution failed: {e}")
            raise ActionExecutionError(f"Failed to execute {action_type}: {e}")
    
    async def _execute_key_press(self, action: Dict[str, Any]):
        """Execute a single key press."""
        key_name = action.get('key', '').lower()
        
        if not key_name:
            raise ActionExecutionError("Key name not specified")
        
        # Map common key names
        if key_name in self.key_mappings:
            key_name = self.key_mappings[key_name]
        
        self.logger.debug(f"Pressing key: {key_name}")
        
        try:
            # Handle special keys
            if key_name == 'num_add':
                # Numpad + key (used for clicking in HPS app)
                if platform.system() == "Windows":
                    win32api.keybd_event(win32con.VK_ADD, 0, 0, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(win32con.VK_ADD, 0, win32con.KEYEVENTF_KEYUP, 0)
                else:
                    key = keyboard.Key.ctrl  # Placeholder for Linux
                    self.keyboard_controller.press(key)
                    self.keyboard_controller.release(key)
            
            elif hasattr(keyboard.Key, key_name):
                # Special keys (arrows, enter, etc.)
                key = getattr(keyboard.Key, key_name)
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
            
            else:
                # Regular character keys
                self.keyboard_controller.press(key_name)
                self.keyboard_controller.release(key_name)
                
        except Exception as e:
            raise ActionExecutionError(f"Failed to press key '{key_name}': {e}")
    
    async def _execute_key_sequence(self, action: Dict[str, Any]):
        """Execute a sequence of key presses."""
        keys = action.get('keys', [])
        
        if not keys:
            raise ActionExecutionError("Key sequence not specified")
        
        self.logger.debug(f"Executing key sequence: {keys}")
        
        for key in keys:
            await self._execute_key_press({'key': key})
            await asyncio.sleep(0.1)  # Brief pause between keys
    
    async def _execute_click(self, action: Dict[str, Any]):
        """Execute a mouse click."""
        coordinates = action.get('coordinates')
        
        if coordinates:
            # Click at specific coordinates
            x, y = coordinates
            self.logger.debug(f"Clicking at coordinates: ({x}, {y})")
            
            self.mouse_controller.position = (x, y)
            await asyncio.sleep(0.1)
            self.mouse_controller.click(mouse.Button.left, 1)
        
        else:
            # Use keyboard shortcut for HPS app (numpad +)
            self.logger.debug("Executing click via numpad +")
            await self._execute_key_press({'key': 'click'})
    
    async def _execute_wait(self, action: Dict[str, Any]):
        """Execute a wait/pause."""
        duration = action.get('duration', 1.0)
        self.logger.debug(f"Waiting for {duration} seconds")
        await asyncio.sleep(duration)
    
    async def _execute_focus_window(self):
        """Bring the target application window to focus."""
        self.logger.debug("Focusing target window")
        # This would typically be handled by the screen capture module
        # which has window handle information
        pass
    
    async def send_text(self, text: str):
        """
        Send text input to the application.
        
        Args:
            text: Text to type
        """
        self.logger.debug(f"Sending text: {text}")
        
        try:
            self.keyboard_controller.type(text)
            await asyncio.sleep(0.1)
            
        except Exception as e:
            raise ActionExecutionError(f"Failed to send text '{text}': {e}")
    
    async def press_key_combination(self, keys: List[str]):
        """
        Press a combination of keys simultaneously.
        
        Args:
            keys: List of keys to press together (e.g., ['ctrl', 'c'])
        """
        self.logger.debug(f"Pressing key combination: {keys}")
        
        try:
            # Press all keys
            key_objects = []
            for key_name in keys:
                if hasattr(keyboard.Key, key_name):
                    key = getattr(keyboard.Key, key_name)
                else:
                    key = key_name
                key_objects.append(key)
                self.keyboard_controller.press(key)
            
            await asyncio.sleep(0.1)
            
            # Release all keys in reverse order
            for key in reversed(key_objects):
                self.keyboard_controller.release(key)
                
        except Exception as e:
            raise ActionExecutionError(f"Failed to press key combination {keys}: {e}")
    
    def translate_ai_action(self, ai_action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate an AI-recommended action to executor format.
        
        Args:
            ai_action: Action dictionary from AI
            
        Returns:
            Action dictionary in executor format
        """
        action_type = ai_action.get('type', '').lower()
        
        if action_type == 'click' or action_type == 'press':
            # For HPS app, translate clicks to numpad + key
            return {
                'type': 'key_press',
                'key': 'click'
            }
        
        elif action_type == 'key_press':
            return {
                'type': 'key_press',
                'key': ai_action.get('key', '')
            }
        
        elif action_type == 'key_sequence':
            return {
                'type': 'key_sequence',
                'keys': ai_action.get('keys', [])
            }
        
        elif action_type == 'navigate':
            # Translate navigation to arrow key sequences
            direction = ai_action.get('direction', '').lower()
            count = ai_action.get('count', 1)
            
            if direction in ['up', 'down', 'left', 'right']:
                return {
                    'type': 'key_sequence',
                    'keys': [direction] * count
                }
        
        # Default to the original action
        return ai_action
    
    async def test_input(self):
        """Test input functionality."""
        self.logger.info("Testing input functionality...")
        
        try:
            # Test basic key press
            await self._execute_key_press({'key': 'space'})
            await asyncio.sleep(0.5)
            
            # Test key sequence
            await self._execute_key_sequence({'keys': ['tab', 'tab']})
            await asyncio.sleep(0.5)
            
            self.logger.info("Input test completed successfully")
            
        except Exception as e:
            self.logger.error(f"Input test failed: {e}")
            raise ActionExecutionError(f"Input test failed: {e}")
