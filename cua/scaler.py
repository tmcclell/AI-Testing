"""
Screen Scaler
============

Scaler implementation matching Azure CUA sample for resizing screenshots
and translating coordinates.
"""

import asyncio
import base64
import io
import logging
from typing import Tuple, List, Optional
import PIL.Image

logger = logging.getLogger(__name__)


class Scaler:
    """Wrapper for a computer that performs resizing and coordinate translation."""

    def __init__(self, computer, dimensions: Optional[Tuple[int, int]] = None):
        self.computer = computer
        self.size = dimensions
        self.screen_width = -1
        self.screen_height = -1

    @property
    def environment(self) -> str:
        """Get the computer environment."""
        return self.computer.environment

    @property
    def dimensions(self) -> Tuple[int, int]:
        """Get the scaled dimensions."""
        if not self.size:
            # If no dimensions are given, take a screenshot and scale to fit in 2048px
            # https://platform.openai.com/docs/guides/images
            width, height = self.computer.dimensions
            max_size = 2048
            longest = max(width, height)
            if longest <= max_size:
                self.size = (width, height)
            else:
                scale = max_size / longest
                self.size = (int(width * scale), int(height * scale))
        return self.size

    async def screenshot(self) -> str:
        """Take a screenshot from the actual computer and scale it."""
        try:
            # Take a screenshot from the actual computer
            screenshot = await self.computer.screenshot()
            screenshot = base64.b64decode(screenshot)
            buffer = io.BytesIO(screenshot)
            image = PIL.Image.open(buffer)
            
            # Scale the screenshot
            self.screen_width, self.screen_height = image.size
            width, height = self.dimensions
            ratio = min(width / self.screen_width, height / self.screen_height)
            new_width = int(self.screen_width * ratio)
            new_height = int(self.screen_height * ratio)
            new_size = (new_width, new_height)
            
            # Resize with high quality
            resized_image = image.resize(new_size, PIL.Image.Resampling.LANCZOS)
            
            # Create a new image with the target dimensions and paste the resized image
            image = PIL.Image.new("RGB", (width, height), (0, 0, 0))
            image.paste(resized_image, (0, 0))
            
            # Convert back to base64
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            data = bytearray(buffer.getvalue())
            encoded = base64.b64encode(data).decode("utf-8")
            
            logger.debug(f"Screenshot scaled from {self.screen_width}x{self.screen_height} to {width}x{height}")
            return encoded
            
        except Exception as e:
            logger.error(f"Failed to take scaled screenshot: {e}")
            raise

    async def click(self, x: int, y: int, button: str = "left") -> None:
        """Click at scaled coordinates."""
        x, y = self._point_to_screen_coords(x, y)
        await self.computer.click(x, y, button=button)

    async def double_click(self, x: int, y: int) -> None:
        """Double-click at scaled coordinates."""
        x, y = self._point_to_screen_coords(x, y)
        await self.computer.double_click(x, y)

    async def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        """Scroll at scaled coordinates."""
        x, y = self._point_to_screen_coords(x, y)
        await self.computer.scroll(x, y, scroll_x, scroll_y)

    async def type(self, text: str) -> None:
        """Type text."""
        await self.computer.type(text)

    async def wait(self, ms: int = 1000) -> None:
        """Wait for specified milliseconds."""
        await self.computer.wait(ms)

    async def move(self, x: int, y: int) -> None:
        """Move mouse to scaled coordinates."""
        x, y = self._point_to_screen_coords(x, y)
        await self.computer.move(x, y)

    async def keypress(self, keys: List[str]) -> None:
        """Press key combination."""
        await self.computer.keypress(keys)

    async def drag(self, path: List[Tuple[int, int]]) -> None:
        """Drag mouse along scaled path."""
        path = [self._point_to_screen_coords(*point) for point in path]
        await self.computer.drag(path)

    def _point_to_screen_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Convert scaled coordinates to actual screen coordinates."""
        width, height = self.dimensions
        
        # Calculate the scaling ratio
        ratio = min(width / self.screen_width, height / self.screen_height)
        
        # Convert scaled coordinates back to screen coordinates
        screen_x = x / ratio
        screen_y = y / ratio
        
        return int(screen_x), int(screen_y)
