"""
CUA Configuration
================

Configuration management for Computer Use Assistant following Azure patterns.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CUAConfig:
    """Configuration for Computer Use Assistant."""
    
    # Core AI settings
    model: str = "computer-use-preview"
    endpoint: str = "azure"  # 'azure' or 'openai'
    temperature: Optional[float] = None
    
    # Execution settings
    autoplay: bool = False
    max_actions: int = 50
    action_delay: float = 2.0
    
    # Output and logging
    output_dir: Path = Path("logs")
    log_level: str = "INFO"
    
    # Azure-specific settings
    azure_endpoint: Optional[str] = None
    azure_api_key: Optional[str] = None
    azure_api_version: str = "2025-03-01-preview"
    
    # OpenAI settings (if using OpenAI directly)
    openai_api_key: Optional[str] = None
    
    # Safety and consent
    require_consent: bool = True
    safety_checks_enabled: bool = True
    
    # Screen scaling
    scale_dimensions: Optional[tuple] = (1024, 768)
    
    def __post_init__(self):
        """Initialize configuration after creation."""
        self._load_environment_variables()
        self._validate_configuration()
        
    def _load_environment_variables(self):
        """Load configuration from environment variables."""
        # Azure OpenAI settings
        if not self.azure_endpoint:
            self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not self.azure_api_key:
            self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
            
        # OpenAI settings
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            
        # Override autoplay from environment if set
        if os.getenv("CUA_AUTOPLAY", "").lower() in ("true", "1", "yes"):
            self.autoplay = True
            
        # Override log level from environment if set
        env_log_level = os.getenv("CUA_LOG_LEVEL")
        if env_log_level:
            self.log_level = env_log_level.upper()
            
    def _validate_configuration(self):
        """Validate the configuration."""
        if self.endpoint == "azure":
            if not self.azure_endpoint:
                raise ValueError(
                    "Azure endpoint is required when using Azure OpenAI. "
                    "Set AZURE_OPENAI_ENDPOINT environment variable."
                )
            if not self.azure_api_key:
                raise ValueError(
                    "Azure API key is required when using Azure OpenAI. "
                    "Set AZURE_OPENAI_API_KEY environment variable."
                )
        elif self.endpoint == "openai":
            if not self.openai_api_key:
                raise ValueError(
                    "OpenAI API key is required when using OpenAI directly. "
                    "Set OPENAI_API_KEY environment variable."
                )
        else:
            raise ValueError(f"Unsupported endpoint: {self.endpoint}")
            
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {self.log_level}. Must be one of {valid_levels}")
            
        logger.debug(f"Configuration validated successfully: endpoint={self.endpoint}")
        
    @property
    def is_azure_endpoint(self) -> bool:
        """Check if using Azure endpoint."""
        return self.endpoint == "azure"
        
    @property
    def is_openai_endpoint(self) -> bool:
        """Check if using OpenAI endpoint."""
        return self.endpoint == "openai"
