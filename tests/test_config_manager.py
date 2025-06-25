"""
Unit tests for configuration manager.
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from src.core.config_manager import Config, ConfigManager


class TestConfig:
    """Test the Config dataclass."""
    
    def test_config_creation_with_defaults(self):
        """Test creating config with default values."""
        config = Config()
        assert config.scenario == "swap_test"
        assert config.iteration_count == 1
        assert config.dry_run is False
    
    def test_config_validation_missing_azure_endpoint(self):
        """Test config validation fails without Azure endpoint."""
        with pytest.raises(ValueError, match="Azure endpoint is required"):
            Config(azure_endpoint="", azure_api_key="test-key")
    
    def test_config_validation_missing_api_key(self):
        """Test config validation fails without API key."""
        with pytest.raises(ValueError, match="Azure API key is required"):
            Config(azure_endpoint="https://test.com", azure_api_key="")


class TestConfigManager:
    """Test the ConfigManager class."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        config_data = {
            'scenario': 'test_scenario',
            'iteration_count': 5,
            'azure_endpoint': 'https://test.openai.azure.com/',
            'azure_api_key': 'test-api-key',
            'dry_run': True
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            return Path(f.name)
    
    @pytest.mark.asyncio
    async def test_load_existing_config(self, temp_config_file):
        """Test loading an existing config file."""
        manager = ConfigManager(temp_config_file)
        config = await manager.load_config()
        
        assert config.scenario == 'test_scenario'
        assert config.iteration_count == 5
        assert config.dry_run is True
        
        # Clean up
        temp_config_file.unlink()
    
    @pytest.mark.asyncio
    async def test_create_default_config(self, tmp_path):
        """Test creating a default config when file doesn't exist."""
        config_path = tmp_path / "test_config.yaml"
        manager = ConfigManager(config_path)
        
        config = await manager.load_config()
        
        # Check that file was created
        assert config_path.exists()
        
        # Check default values
        assert config.scenario == 'swap_test'
        assert config.iteration_count == 1
    
    def test_validate_config_success(self):
        """Test successful config validation."""
        manager = ConfigManager(Path("dummy.yaml"))
        config = Config(
            azure_endpoint="https://test.com",
            azure_api_key="valid-key"
        )
        
        errors = manager.validate_config(config)
        assert len(errors) == 0
    
    def test_validate_config_errors(self):
        """Test config validation with errors."""
        manager = ConfigManager(Path("dummy.yaml"))
        config = Config(
            azure_endpoint="",
            azure_api_key="your-api-key-here",
            iteration_count=0
        )
        
        errors = manager.validate_config(config)
        assert len(errors) >= 3  # Should have multiple validation errors
