"""
Screen Capture Module
====================

Handles capturing screenshots of the target application window.
Supports both Windows and Linux platforms.
"""

import asyncio
import logging
import platform
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import base64
import io

# Platform-specific imports
if platform.system() == "Windows":
    import win32gui
    import win32ui
    import win32con
    from PIL import Image
else:
    # Linux imports
    try:
        import subprocess
        from PIL import Image
    except ImportError:
        pass

from .config_manager import Config
from utils.exceptions import ScreenCaptureError, ApplicationNotFoundError


class ScreenCaptureModule:
    """
    Handles screen capture operations for the target application.
    
    Supports capturing specific application windows on both Windows and Linux.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.target_hwnd = None  # Windows handle
        self.last_screenshot = None
        self.screenshot_counter = 0
        
    async def initialize(self):
        """Initialize the screen capture module."""
        self.logger.info("Initializing screen capture module...")
        
        # Find the target application window
        await self._find_target_window()
        
        # Test screen capture
        test_screenshot = await self.capture_screen()
        if test_screenshot is None:
            raise ScreenCaptureError("Failed to capture initial screenshot")
        
        self.logger.info("Screen capture module initialized successfully")
    
    async def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up screen capture module...")
        # No special cleanup needed for screen capture
    
    async def capture_screen(self) -> Optional[bytes]:
        """
        Capture a screenshot of the target application.
        
        Returns:
            bytes: PNG image data, or None if capture fails
        """
        try:
            if platform.system() == "Windows":
                image_data = await self._capture_windows()
            else:
                image_data = await self._capture_linux()
            
            if image_data and self.config.save_screenshots:
                await self._save_screenshot(image_data)
            
            self.last_screenshot = image_data
            return image_data
            
        except Exception as e:
            self.logger.error(f"Screen capture failed: {e}")
            raise ScreenCaptureError(f"Failed to capture screen: {e}")
    
    async def _find_target_window(self):
        """Find the target application window."""
        if platform.system() == "Windows":
            self.target_hwnd = await self._find_window_windows()
        else:
            # For Linux, we'll use the window title to identify the window
            await self._find_window_linux()
        
        if not self.target_hwnd and platform.system() == "Windows":
            raise ApplicationNotFoundError(
                f"Could not find window with title: {self.config.app_window_title}"
            )
    
    async def _find_window_windows(self) -> Optional[int]:
        """Find target window on Windows."""
        def enum_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if self.config.app_window_title.lower() in window_title.lower():
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(enum_window_callback, windows)
        
        if windows:
            hwnd = windows[0]  # Use first match
            window_title = win32gui.GetWindowText(hwnd)
            self.logger.info(f"Found target window: {window_title} (HWND: {hwnd})")
            return hwnd
        
        return None
    
    async def _find_window_linux(self):
        """Find target window on Linux."""
        # For Linux, we'll rely on window manager tools
        # This is a placeholder - actual implementation would use xwininfo, wmctrl, etc.
        self.logger.info(f"Looking for window: {self.config.app_window_title}")
        # Implementation would go here
    
    async def _capture_windows(self) -> bytes:
        """Capture screenshot on Windows."""
        if not self.target_hwnd:
            raise ScreenCaptureError("No target window found")
        
        # Get window dimensions
        left, top, right, bottom = win32gui.GetWindowRect(self.target_hwnd)
        width = right - left
        height = bottom - top
        
        # Create device context
        hwnd_dc = win32gui.GetWindowDC(self.target_hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        
        # Create bitmap
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bitmap)
        
        # Copy window content to bitmap
        save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)
        
        # Convert to PIL Image
        bmp_info = save_bitmap.GetInfo()
        bmp_str = save_bitmap.GetBitmapBits(True)
        
        image = Image.frombuffer(
            'RGB',
            (bmp_info['bmWidth'], bmp_info['bmHeight']),
            bmp_str, 'raw', 'BGRX', 0, 1
        )
        
        # Clean up
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self.target_hwnd, hwnd_dc)
        
        # Convert to PNG bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        return img_buffer.getvalue()
    
    async def _capture_linux(self) -> bytes:
        """Capture screenshot on Linux."""
        try:
            # Use xwininfo and import to capture specific window
            # This is a simplified implementation
            result = subprocess.run([
                'import', '-window', 'root', 
                '-crop', '800x600+0+0',  # Adjust based on actual window
                'png:-'
            ], capture_output=True, check=True)
            
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            raise ScreenCaptureError(f"Linux screen capture failed: {e}")
        except FileNotFoundError:
            raise ScreenCaptureError("ImageMagick 'import' command not found")
    
    async def _save_screenshot(self, image_data: bytes):
        """Save screenshot to disk."""
        if not self.config.save_screenshots:
            return
        
        self.screenshot_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}_{self.screenshot_counter:04d}.png"
        filepath = self.config.screenshot_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        self.logger.debug(f"Screenshot saved: {filepath}")
    
    def get_last_screenshot_base64(self) -> Optional[str]:
        """
        Get the last screenshot as base64 string for AI analysis.
        
        Returns:
            str: Base64 encoded image data
        """
        if self.last_screenshot:
            return base64.b64encode(self.last_screenshot).decode('utf-8')
        return None
    
    async def focus_target_window(self):
        """Bring the target window to the foreground."""
        if platform.system() == "Windows" and self.target_hwnd:
            try:
                win32gui.SetForegroundWindow(self.target_hwnd)
                await asyncio.sleep(0.5)  # Brief pause for window to focus
                self.logger.debug("Target window focused")
            except Exception as e:
                self.logger.warning(f"Failed to focus window: {e}")
    
    def get_window_info(self) -> dict:
        """Get information about the target window."""
        if platform.system() == "Windows" and self.target_hwnd:
            try:
                left, top, right, bottom = win32gui.GetWindowRect(self.target_hwnd)
                window_title = win32gui.GetWindowText(self.target_hwnd)
                
                return {
                    'title': window_title,
                    'hwnd': self.target_hwnd,
                    'position': (left, top),
                    'size': (right - left, bottom - top),
                    'visible': win32gui.IsWindowVisible(self.target_hwnd)
                }
            except Exception as e:
                self.logger.warning(f"Failed to get window info: {e}")
        
        return {'title': 'Unknown', 'hwnd': None}
