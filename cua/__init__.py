"""
Computer Use Assistant (CUA) Package
===================================

Azure-aligned Computer Use Assistant implementation for HPS testing.
"""

from .computer_use_assistant import ComputerUseAssistant
from .config import CUAConfig
from .logger import setup_logging
from .agent import Agent
from .scaler import Scaler
from .local_computer import LocalComputer

__all__ = [
    'ComputerUseAssistant',
    'CUAConfig', 
    'setup_logging',
    'Agent',
    'Scaler',
    'LocalComputer'
]
