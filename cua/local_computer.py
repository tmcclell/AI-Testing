"""
Local Computer Interface
=======================

LocalComputer implementation matching Azure CUA sample for cross-platform
computer control using pyautogui.
"""

import asyncio
import base64
import io
import platform
from typing import Tuple, List
import pyautogui
import logging

logger = logging.getLogger(__name__)


class LocalComputer:
    """Use pyautogui to take screenshots and perform actions on the local computer."""

    def __init__(self):
        self.size = None
        # Configure pyautogui for safety
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
    @property
    def environment(self) -> str:
        """Get the current operating system environment."""
        system = platform.system()
        if system == "Windows":
            return "windows"
        elif system == "Darwin":
            return "mac"
        elif system == "Linux":
            return "linux"
        else:
            raise NotImplementedError(f"Unsupported operating system: '{system}'")

    @property
    def dimensions(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        if not self.size:
            screenshot = pyautogui.screenshot()
            self.size = screenshot.size
        return self.size

    async def screenshot(self) -> str:
        """Take a screenshot and return as base64 encoded string."""
        try:
            screenshot = pyautogui.screenshot()
            self.size = screenshot.size
            buffer = io.BytesIO()
            screenshot.save(buffer, format="PNG")
            buffer.seek(0)
            data = bytearray(buffer.getvalue())
            encoded = base64.b64encode(data).decode("utf-8")
            logger.debug(f"Screenshot taken: {self.size}")
            return encoded
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            raise

    async def click(self, x: int, y: int, button: str = "left") -> None:
        """Click at specified coordinates."""
        width, height = self.size or self.dimensions
        if 0 <= x < width and 0 <= y < height:
            button = "middle" if button == "wheel" else button
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.click(x, y, button=button)
            logger.debug(f"Clicked at ({x}, {y}) with {button} button")
        else:
            logger.warning(f"Click coordinates ({x}, {y}) out of bounds ({width}x{height})")

    async def double_click(self, x: int, y: int) -> None:
        """Double-click at specified coordinates."""
        width, height = self.size or self.dimensions
        if 0 <= x < width and 0 <= y < height:
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.doubleClick(x, y)
            logger.debug(f"Double-clicked at ({x}, {y})")
        else:
            logger.warning(f"Double-click coordinates ({x}, {y}) out of bounds ({width}x{height})")

    async def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        """Scroll at specified coordinates."""
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.scroll(-scroll_y)  # Negative for natural scrolling
        pyautogui.hscroll(scroll_x)
        logger.debug(f"Scrolled at ({x}, {y}) by ({scroll_x}, {scroll_y})")

    async def type(self, text: str) -> None:
        """Type text at current cursor position."""
        pyautogui.write(text)
        logger.debug(f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}")

    async def wait(self, ms: int = 1000) -> None:
        """Wait for specified milliseconds."""
        await asyncio.sleep(ms / 1000)
        logger.debug(f"Waited {ms}ms")

    async def move(self, x: int, y: int) -> None:
        """Move mouse to specified coordinates."""
        pyautogui.moveTo(x, y, duration=0.1)
        logger.debug(f"Moved mouse to ({x}, {y})")

    async def keypress(self, keys: List[str]) -> None:
        """Press key combination."""
        keys = [key.lower() for key in keys]
        keymap = {
            "arrowdown": "down",
            "arrowleft": "left", 
            "arrowright": "right",
            "arrowup": "up",
        }
        keys = [keymap.get(key, key) for key in keys]
        
        # Press all keys down
        for key in keys:
            pyautogui.keyDown(key)
        
        # Release all keys in reverse order
        for key in reversed(keys):
            pyautogui.keyUp(key)
            
        logger.debug(f"Pressed key combination: {keys}")

    async def drag(self, path: List[Tuple[int, int]]) -> None:
        """Drag mouse along specified path."""
        if len(path) <= 1:
            logger.warning("Drag path must contain at least 2 points")
            return
        elif len(path) == 2:
            # Simple drag between two points
            pyautogui.moveTo(*path[0], duration=0.5)
            pyautogui.dragTo(*path[1], duration=1.0, button="left")
        else:
            # Complex drag with multiple points
            pyautogui.moveTo(*path[0], duration=0.5)
            pyautogui.mouseDown(button="left")
            for point in path[1:]:
                pyautogui.dragTo(*point, duration=1.0, mouseDownUp=False)
            pyautogui.mouseUp(button="left")
            
        logger.debug(f"Dragged along path with {len(path)} points")
