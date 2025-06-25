"""
Configuration Manager
===================

Manages configuration loading and validation for the AI testing agent.
Supports YAML configuration files with sensible defaults.
"""

import yaml
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class Config:
    """Configuration settings for the AI testing agent."""
    
    # Test scenario settings
    scenario: str = "swap_test"
    iteration_count: int = 1
    target_controllers: str = "17 HPM 18"
    target_network: str = "UCN 07"
    target_network_node: str = "NM 44"
    
    # Azure AI settings
    azure_endpoint: str = ""
    azure_api_key: str = ""
    azure_api_version: str = "2024-02-01"
    azure_deployment_name: str = "gpt-4-vision"
    
    # Application settings
    app_window_title: str = "HPS Test Application"
    app_executable_path: Optional[str] = None
    
    # Timing settings (in seconds)
    action_delay: float = 1.0
    inter_iteration_delay: float = 2.0
    screen_change_timeout: float = 30.0
    swap_completion_timeout: float = 120.0
    screen_poll_interval: float = 2.0
    status_poll_interval: float = 5.0
    
    # Behavior settings
    dry_run: bool = False
    stop_on_error: bool = True
    max_retries: int = 3
    
    # I/O settings
    output_dir: Path = field(default_factory=lambda: Path("logs"))
    screenshot_dir: Path = field(default_factory=lambda: Path("screenshots"))
    save_screenshots: bool = True
    
    # Advanced settings
    ai_confidence_threshold: float = 0.8
    max_context_history: int = 10
    enable_recovery: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.azure_endpoint:
            raise ValueError("Azure endpoint is required")
        if not self.azure_api_key:
            raise ValueError("Azure API key is required")
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.save_screenshots:
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)


class ConfigManager:
    """Manages loading and validation of configuration files."""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
    
    async def load_config(self) -> Config:
        """
        Load configuration from file.
        
        Returns:
            Config: Loaded and validated configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        self.logger.info(f"Loading configuration from {self.config_path}")
        
        if not self.config_path.exists():
            self.logger.warning(f"Config file not found: {self.config_path}")
            self.logger.info("Creating default configuration file")
            await self._create_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}
            
            # Create config object with loaded data
            config = Config(**config_data)
            
            self.logger.info("Configuration loaded successfully")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise ValueError(f"Invalid configuration file: {e}")
    
    async def _create_default_config(self):
        """Create a default configuration file."""
        default_config = {
            'scenario': 'swap_test',
            'iteration_count': 1,
            'target_controllers': '17 HPM 18',
            'target_network': 'UCN 07',
            'target_network_node': 'NM 44',
            
            'azure_endpoint': 'https://your-azure-endpoint.openai.azure.com/',
            'azure_api_key': 'your-api-key-here',
            'azure_api_version': '2024-02-01',
            'azure_deployment_name': 'gpt-4-vision',
            
            'app_window_title': 'HPS Test Application',
            'app_executable_path': None,
            
            'action_delay': 1.0,
            'inter_iteration_delay': 2.0,
            'screen_change_timeout': 30.0,
            'swap_completion_timeout': 120.0,
            'screen_poll_interval': 2.0,
            'status_poll_interval': 5.0,
            
            'dry_run': False,
            'stop_on_error': True,
            'max_retries': 3,
            
            'output_dir': 'logs',
            'screenshot_dir': 'screenshots',
            'save_screenshots': True,
            
            'ai_confidence_threshold': 0.8,
            'max_context_history': 10,
            'enable_recovery': True
        }
        
        # Ensure parent directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        self.logger.info(f"Created default configuration file: {self.config_path}")
        self.logger.warning("Please update the Azure credentials in the configuration file")
    
    def validate_config(self, config: Config) -> List[str]:
        """
        Validate configuration settings.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Required fields
        if not config.azure_endpoint:
            errors.append("Azure endpoint is required")
        if not config.azure_api_key or config.azure_api_key == "your-api-key-here":
            errors.append("Valid Azure API key is required")
        
        # Numeric ranges
        if config.iteration_count < 1:
            errors.append("Iteration count must be at least 1")
        if config.action_delay < 0:
            errors.append("Action delay cannot be negative")
        if config.ai_confidence_threshold < 0 or config.ai_confidence_threshold > 1:
            errors.append("AI confidence threshold must be between 0 and 1")
        
        # File paths
        if config.app_executable_path and not Path(config.app_executable_path).exists():
            errors.append(f"Application executable not found: {config.app_executable_path}")
        
        return errors
