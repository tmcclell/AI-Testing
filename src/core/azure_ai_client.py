"""
Azure AI Client
==============

Handles communication with Azure OpenAI Computer Vision API.
Provides intelligent screen analysis and decision making capabilities.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
import aiohttp
import base64
from datetime import datetime

from .config_manager import Config
from utils.exceptions import AIError


class AzureAIClient:
    """
    Client for Azure OpenAI Computer Vision API.
    
    Handles sending screenshots to Azure AI and receiving intelligent
    analysis and action recommendations.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.request_count = 0
        self.last_request_time = None
        
        # Build the full API endpoint
        self.api_url = f"{self.config.azure_endpoint.rstrip('/')}/openai/deployments/{self.config.azure_deployment_name}/chat/completions"
        
        # Headers for API requests
        self.headers = {
            'Content-Type': 'application/json',
            'api-key': self.config.azure_api_key
        }
    
    async def initialize(self):
        """Initialize the Azure AI client."""
        self.logger.info("Initializing Azure AI client...")
        
        # Create aiohttp session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        )
        
        # Test connection
        await self._test_connection()
        
        self.logger.info("Azure AI client initialized successfully")
    
    async def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up Azure AI client...")
        
        if self.session:
            await self.session.close()
    
    async def _test_connection(self):
        """Test connection to Azure AI service."""
        try:
            # Simple test message
            test_message = "Test connection - respond with 'OK'"
            response = await self._make_request(test_message, None)
            
            if response and "ok" in response.get("content", "").lower():
                self.logger.info("Azure AI connection test successful")
            else:
                self.logger.warning("Azure AI connection test returned unexpected response")
                
        except Exception as e:
            raise AIError(f"Failed to connect to Azure AI: {e}")
    
    async def analyze_screen(self, screenshot_data: bytes, prompt: str) -> Dict[str, Any]:
        """
        Analyze a screenshot using Azure AI.
        
        Args:
            screenshot_data: PNG image data
            prompt: Analysis prompt
            
        Returns:
            Dict containing AI analysis results
        """
        self.logger.debug(f"Analyzing screen with prompt: {prompt[:100]}...")
        
        try:
            # Convert image to base64
            image_b64 = base64.b64encode(screenshot_data).decode('utf-8')
            
            # Make API request
            response = await self._make_request(prompt, image_b64)
            
            # Parse response
            return self._parse_ai_response(response)
            
        except Exception as e:
            self.logger.error(f"Screen analysis failed: {e}")
            raise AIError(f"Failed to analyze screen: {e}")
    
    async def _make_request(self, prompt: str, image_b64: Optional[str] = None) -> Dict[str, Any]:
        """Make a request to Azure OpenAI API."""
        self.request_count += 1
        self.last_request_time = datetime.now()
        
        # Build message content
        message_content = [
            {
                "type": "text",
                "text": prompt
            }
        ]
        
        if image_b64:
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_b64}"
                }
            })
        
        # Build request payload
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1,  # Low temperature for consistent responses
            "api-version": self.config.azure_api_version
        }
        
        self.logger.debug(f"Making API request #{self.request_count}")
        
        async with self.session.post(
            self.api_url,
            headers=self.headers,
            json=payload
        ) as response:
            
            if response.status != 200:
                error_text = await response.text()
                raise AIError(f"API request failed with status {response.status}: {error_text}")
            
            result = await response.json()
            
            # Extract the response content
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                return {'content': content, 'raw_response': result}
            else:
                raise AIError(f"Unexpected API response format: {result}")
    
    def _parse_ai_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse AI response content.
        
        Attempts to parse JSON responses, falls back to plain text.
        """
        content = response.get('content', '')
        
        # Try to parse as JSON first
        try:
            # Look for JSON in the response
            if '{' in content and '}' in content:
                # Extract JSON portion
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                
                parsed = json.loads(json_str)
                self.logger.debug(f"Parsed JSON response: {parsed}")
                return parsed
                
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.debug(f"Failed to parse JSON response: {e}")
        
        # Fall back to plain text analysis
        return self._parse_text_response(content)
    
    def _parse_text_response(self, content: str) -> Dict[str, Any]:
        """Parse plain text response when JSON parsing fails."""
        content_lower = content.lower()
        
        result = {
            'content': content,
            'confidence': 0.5  # Default confidence for text responses
        }
        
        # Look for common keywords to infer meaning
        if 'yes' in content_lower or 'true' in content_lower:
            result['action_needed'] = True
        elif 'no' in content_lower or 'false' in content_lower:
            result['action_needed'] = False
        
        if 'error' in content_lower or 'fail' in content_lower:
            result['error_detected'] = True
            result['error_message'] = content
        
        if 'complete' in content_lower or 'success' in content_lower:
            result['completed'] = True
        
        # Look for specific UI elements
        if 'button' in content_lower:
            result['ui_element_type'] = 'button'
        elif 'menu' in content_lower:
            result['ui_element_type'] = 'menu'
        elif 'dialog' in content_lower:
            result['ui_element_type'] = 'dialog'
        
        return result
    
    async def get_recovery_suggestion(self, error_context: str, screenshot_data: bytes) -> Dict[str, Any]:
        """
        Get AI suggestion for error recovery.
        
        Args:
            error_context: Description of the error
            screenshot_data: Current screen state
            
        Returns:
            Dict with recovery suggestions
        """
        prompt = f"""
        An error occurred during test execution: {error_context}
        
        Please analyze the current screen and suggest recovery actions.
        
        Respond in JSON format:
        {{
            "error_analysis": "description of what you see",
            "recovery_possible": true/false,
            "recovery_action": {{
                "type": "action type",
                "description": "what to do",
                "steps": ["step 1", "step 2"]
            }},
            "confidence": 0.0-1.0
        }}
        """
        
        return await self.analyze_screen(screenshot_data, prompt)
    
    async def verify_expected_state(self, expected_state: str, screenshot_data: bytes) -> Dict[str, Any]:
        """
        Verify that the application is in the expected state.
        
        Args:
            expected_state: Description of expected state
            screenshot_data: Current screen
            
        Returns:
            Dict with verification results
        """
        prompt = f"""
        Please verify if the application is in the expected state: {expected_state}
        
        Analyze the current screen and respond in JSON format:
        {{
            "state_matches": true/false,
            "current_state": "description of current state",
            "confidence": 0.0-1.0,
            "differences": ["any differences from expected state"]
        }}
        """
        
        return await self.analyze_screen(screenshot_data, prompt)
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        return {
            'total_requests': self.request_count,
            'last_request_time': self.last_request_time.isoformat() if self.last_request_time else None,
            'endpoint': self.api_url
        }
