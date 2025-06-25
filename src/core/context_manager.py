"""
Context Manager
==============

Manages context and conversation history for AI interactions.
Maintains state between AI calls to provide consistent behavior.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ContextEntry:
    """A single context entry."""
    timestamp: datetime
    action: str
    result: str
    screen_state: Optional[str] = None
    confidence: float = 1.0


class ContextManager:
    """
    Manages context and conversation history for AI interactions.
    
    Provides context to AI calls to maintain consistency and enable
    intelligent decision making based on previous actions.
    """
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.logger = logging.getLogger(__name__)
        self.history: List[ContextEntry] = []
        self.current_scenario = None
        self.current_iteration = 0
        
    def add_entry(self, action: str, result: str, screen_state: Optional[str] = None, confidence: float = 1.0):
        """Add a new entry to the context history."""
        entry = ContextEntry(
            timestamp=datetime.now(),
            action=action,
            result=result,
            screen_state=screen_state,
            confidence=confidence
        )
        
        self.history.append(entry)
        
        # Maintain maximum history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        self.logger.debug(f"Added context entry: {action} -> {result}")
    
    def build_context(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build context dictionary for AI interactions.
        
        Args:
            current_state: Current state information
            
        Returns:
            Dictionary containing context for AI
        """
        context = {
            'scenario': current_state.get('scenario', self.current_scenario),
            'iteration': current_state.get('iteration', self.current_iteration),
            'total_iterations': current_state.get('total_iterations', 1),
            'history': self.get_recent_history(5),  # Last 5 actions
            'current_goal': self._determine_current_goal(current_state),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add scenario-specific context
        if context['scenario'] == 'swap_test':
            context.update({
                'controllers': current_state.get('controllers', '17 HPM 18'),
                'network': current_state.get('network', 'UCN 07'),
                'expected_sequence': [
                    'Navigate to System Status',
                    'Select target network',
                    'Initiate controller swap',
                    'Wait for completion',
                    'Verify success'
                ]
            })
        
        return context
    
    def get_recent_history(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent history entries."""
        recent = self.history[-count:] if len(self.history) >= count else self.history
        
        return [
            {
                'timestamp': entry.timestamp.isoformat(),
                'action': entry.action,
                'result': entry.result,
                'confidence': entry.confidence
            }
            for entry in recent
        ]
    
    def _determine_current_goal(self, current_state: Dict[str, Any]) -> str:
        """Determine the current goal based on state and history."""
        scenario = current_state.get('scenario', 'unknown')
        iteration = current_state.get('iteration', 0)
        
        if scenario == 'swap_test':
            if not self.history:
                return "Navigate to System Status screen"
            
            last_action = self.history[-1].action if self.history else ""
            
            if "navigate" in last_action.lower() and "system status" in last_action.lower():
                return "Select target network (UCN 07)"
            elif "select" in last_action.lower() and "network" in last_action.lower():
                return "Initiate controller swap"
            elif "initiate" in last_action.lower() and "swap" in last_action.lower():
                return "Wait for swap completion"
            elif "wait" in last_action.lower():
                return "Verify swap success"
            else:
                return f"Continue swap test iteration {iteration}"
        
        return f"Execute {scenario}"
    
    def set_scenario(self, scenario: str, iteration: int = 0):
        """Set the current scenario and iteration."""
        self.current_scenario = scenario
        self.current_iteration = iteration
        self.logger.info(f"Set scenario: {scenario}, iteration: {iteration}")
    
    def clear_history(self):
        """Clear the context history."""
        self.history.clear()
        self.logger.info("Context history cleared")
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context."""
        return {
            'scenario': self.current_scenario,
            'iteration': self.current_iteration,
            'history_length': len(self.history),
            'last_action': self.history[-1].action if self.history else None,
            'last_result': self.history[-1].result if self.history else None
        }
    
    def build_ai_prompt_context(self, base_prompt: str, current_state: Dict[str, Any]) -> str:
        """
        Build an enhanced prompt with context for AI interactions.
        
        Args:
            base_prompt: Base prompt text
            current_state: Current state information
            
        Returns:
            Enhanced prompt with context
        """
        context = self.build_context(current_state)
        
        context_text = f"""
Context Information:
- Scenario: {context['scenario']}
- Current Iteration: {context['iteration']}/{context['total_iterations']}
- Current Goal: {context['current_goal']}
"""
        
        if context['history']:
            context_text += "\nRecent Actions:\n"
            for i, entry in enumerate(context['history']):
                context_text += f"{i+1}. {entry['action']} -> {entry['result']}\n"
        
        if context['scenario'] == 'swap_test':
            context_text += f"""
Target Controllers: {context['controllers']}
Target Network: {context['network']}
"""
        
        return f"{context_text}\n{base_prompt}"
