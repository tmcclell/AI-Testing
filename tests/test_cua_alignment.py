"""
Test CUA Implementation
======================

Basic test to verify the CUA implementation matches Azure sample patterns.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from cua.config import CUAConfig
from cua.local_computer import LocalComputer
from cua.scaler import Scaler
from cua.agent import Agent
from cua.computer_use_assistant import ComputerUseAssistant


class TestCUAImplementation:
    """Test CUA implementation alignment with Azure sample."""
    
    @patch.dict('os.environ', {
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-key'
    })
    def test_config_creation(self):
        """Test CUA configuration creation."""
        config = CUAConfig(
            model="computer-use-preview",
            endpoint="azure",
            autoplay=True,
            max_actions=10
        )
        
        assert config.model == "computer-use-preview"
        assert config.endpoint == "azure"
        assert config.autoplay is True
        assert config.max_actions == 10
    
    def test_local_computer_properties(self):
        """Test LocalComputer properties match Azure sample."""
        computer = LocalComputer()
        
        # Should have required properties
        assert hasattr(computer, 'environment')
        assert hasattr(computer, 'dimensions')
        
        # Environment should be valid
        env = computer.environment
        assert env in ['windows', 'mac', 'linux']
    
    def test_scaler_initialization(self):
        """Test Scaler initialization with computer."""
        mock_computer = Mock()
        mock_computer.environment = "windows"
        mock_computer.dimensions = (1920, 1080)
        
        scaler = Scaler(mock_computer, (1024, 768))
        
        assert scaler.computer == mock_computer
        assert scaler.size == (1024, 768)
        assert scaler.environment == "windows"
    
    @patch('openai.AsyncAzureOpenAI')
    def test_agent_initialization(self, mock_client):
        """Test Agent initialization."""
        mock_computer = Mock()
        mock_computer.environment = "windows"
        mock_computer.dimensions = (1024, 768)
        
        agent = Agent(
            client=mock_client,
            model="computer-use-preview",
            computer=mock_computer
        )
        
        assert agent.client == mock_client
        assert agent.model == "computer-use-preview"
        assert agent.computer == mock_computer
        assert agent.response is None  # Should start with no response
    
    @patch.dict('os.environ', {
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-key'
    })
    def test_computer_use_assistant_config(self):
        """Test ComputerUseAssistant configuration."""
        config = CUAConfig(
            model="computer-use-preview",
            endpoint="azure",
            autoplay=True
        )
        
        cua = ComputerUseAssistant(config)
        
        assert cua.config == config
        assert cua.client is None  # Should be None before initialization
        assert cua.computer is None  # Should be None before initialization
        assert cua.agent is None  # Should be None before initialization


class TestCUAAlignmentWithAzureSample:
    """Test alignment with Azure CUA sample structure."""
    
    def test_has_required_cua_components(self):
        """Test that all required CUA components exist."""
        # Test imports work (components exist)
        from cua import Agent, Scaler, LocalComputer, ComputerUseAssistant, CUAConfig
        
        # All components should be importable
        assert Agent is not None
        assert Scaler is not None  
        assert LocalComputer is not None
        assert ComputerUseAssistant is not None
        assert CUAConfig is not None
    
    def test_local_computer_has_azure_sample_methods(self):
        """Test LocalComputer has all methods from Azure sample."""
        computer = LocalComputer()
        
        # Check for all required async methods from Azure sample
        required_methods = [
            'screenshot', 'click', 'double_click', 'scroll', 
            'type', 'wait', 'move', 'keypress', 'drag'
        ]
        
        for method in required_methods:
            assert hasattr(computer, method), f"Missing method: {method}"
            assert asyncio.iscoroutinefunction(getattr(computer, method)), f"Method {method} should be async"
    
    def test_scaler_has_azure_sample_methods(self):
        """Test Scaler has all methods from Azure sample."""
        mock_computer = Mock()
        mock_computer.environment = "windows"
        mock_computer.dimensions = (1920, 1080)
        scaler = Scaler(mock_computer)
        
        # Check for all required async methods from Azure sample
        required_methods = [
            'screenshot', 'click', 'double_click', 'scroll', 
            'type', 'wait', 'move', 'keypress', 'drag'
        ]
        
        for method in required_methods:
            assert hasattr(scaler, method), f"Missing method: {method}"
            assert asyncio.iscoroutinefunction(getattr(scaler, method)), f"Method {method} should be async"
    
    def test_agent_has_azure_sample_properties(self):
        """Test Agent has all properties from Azure sample."""
        mock_client = Mock()
        mock_computer = Mock()
        mock_computer.environment = "windows"
        mock_computer.dimensions = (1024, 768)
        
        agent = Agent(mock_client, "computer-use-preview", mock_computer)
        
        # Check for all required properties from Azure sample
        required_properties = [
            'requires_user_input', 'requires_consent', 'pending_safety_checks',
            'reasoning_summary', 'messages', 'actions'
        ]
        
        for prop in required_properties:
            assert hasattr(agent, prop), f"Missing property: {prop}"
    
    def test_simple_cua_script_exists(self):
        """Test that simple_cua.py exists and follows Azure pattern."""
        simple_cua_path = Path("simple_cua.py")
        assert simple_cua_path.exists(), "simple_cua.py should exist"
        
        # Read the content to verify it follows Azure pattern
        content = simple_cua_path.read_text()
        
        # Should have key elements from Azure sample
        assert "argparse" in content
        assert "LocalComputer" in content
        assert "Scaler" in content
        assert "Agent" in content
        assert "openai.AsyncAzureOpenAI" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
