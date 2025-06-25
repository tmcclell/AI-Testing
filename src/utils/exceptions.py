"""
Custom Exceptions
================

Custom exception classes for the AI testing agent.
"""


class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass


class UIError(AgentError):
    """Raised when UI interaction fails."""
    pass


class AIError(AgentError):
    """Raised when AI service fails."""
    pass


class ConfigError(AgentError):
    """Raised when configuration is invalid."""
    pass


class ScreenCaptureError(AgentError):
    """Raised when screen capture fails."""
    pass


class ActionExecutionError(AgentError):
    """Raised when action execution fails."""
    pass


class TimeoutError(AgentError):
    """Raised when operations timeout."""
    pass


class ApplicationNotFoundError(AgentError):
    """Raised when target application cannot be found."""
    pass
