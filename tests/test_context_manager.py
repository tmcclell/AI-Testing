"""
Unit tests for context manager.
"""

import pytest
from datetime import datetime

from src.core.context_manager import ContextManager, ContextEntry


class TestContextEntry:
    """Test the ContextEntry dataclass."""
    
    def test_context_entry_creation(self):
        """Test creating a context entry."""
        entry = ContextEntry(
            timestamp=datetime.now(),
            action="test action",
            result="test result"
        )
        
        assert entry.action == "test action"
        assert entry.result == "test result"
        assert entry.confidence == 1.0  # Default value


class TestContextManager:
    """Test the ContextManager class."""
    
    def test_initialization(self):
        """Test context manager initialization."""
        manager = ContextManager(max_history=5)
        assert manager.max_history == 5
        assert len(manager.history) == 0
        assert manager.current_scenario is None
    
    def test_add_entry(self):
        """Test adding entries to context."""
        manager = ContextManager()
        
        manager.add_entry("action1", "result1")
        manager.add_entry("action2", "result2", confidence=0.8)
        
        assert len(manager.history) == 2
        assert manager.history[0].action == "action1"
        assert manager.history[1].confidence == 0.8
    
    def test_max_history_limit(self):
        """Test that history respects maximum size."""
        manager = ContextManager(max_history=3)
        
        # Add more entries than the limit
        for i in range(5):
            manager.add_entry(f"action{i}", f"result{i}")
        
        # Should only keep the last 3 entries
        assert len(manager.history) == 3
        assert manager.history[0].action == "action2"  # First entry should be removed
        assert manager.history[-1].action == "action4"  # Last entry should be kept
    
    def test_build_context_swap_test(self):
        """Test building context for swap test scenario."""
        manager = ContextManager()
        manager.set_scenario("swap_test", 3)
        
        # Add some history
        manager.add_entry("Navigate to System Status", "Success")
        manager.add_entry("Select network", "Success")
        
        current_state = {
            'controllers': '17 HPM 18',
            'network': 'UCN 07',
            'total_iterations': 10
        }
        
        context = manager.build_context(current_state)
        
        assert context['scenario'] == 'swap_test'
        assert context['iteration'] == 3
        assert context['total_iterations'] == 10
        assert len(context['history']) == 2
        assert 'expected_sequence' in context
    
    def test_get_recent_history(self):
        """Test getting recent history entries."""
        manager = ContextManager()
        
        # Add several entries
        for i in range(10):
            manager.add_entry(f"action{i}", f"result{i}")
        
        # Get last 3 entries
        recent = manager.get_recent_history(3)
        
        assert len(recent) == 3
        assert recent[0]['action'] == "action7"
        assert recent[-1]['action'] == "action9"
    
    def test_determine_current_goal(self):
        """Test goal determination based on history."""
        manager = ContextManager()
        
        # Test initial goal
        current_state = {'scenario': 'swap_test'}
        context = manager.build_context(current_state)
        assert "Navigate to System Status" in context['current_goal']
        
        # Test goal after navigation
        manager.add_entry("Navigate to System Status", "Success")
        context = manager.build_context(current_state)
        assert "Select target network" in context['current_goal']
    
    def test_clear_history(self):
        """Test clearing context history."""
        manager = ContextManager()
        
        # Add some entries
        manager.add_entry("action1", "result1")
        manager.add_entry("action2", "result2")
        
        assert len(manager.history) == 2
        
        # Clear history
        manager.clear_history()
        
        assert len(manager.history) == 0
    
    def test_build_ai_prompt_context(self):
        """Test building AI prompt with context."""
        manager = ContextManager()
        manager.set_scenario("swap_test", 1)
        manager.add_entry("Test action", "Test result")
        
        current_state = {
            'controllers': '17 HPM 18',
            'total_iterations': 5
        }
        
        base_prompt = "What should I do next?"
        enhanced_prompt = manager.build_ai_prompt_context(base_prompt, current_state)
        
        assert "swap_test" in enhanced_prompt
        assert "Test action" in enhanced_prompt
        assert "What should I do next?" in enhanced_prompt
        assert "17 HPM 18" in enhanced_prompt
