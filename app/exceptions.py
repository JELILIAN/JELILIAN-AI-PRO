class ToolError(Exception):
    """Raised when a tool encounters an error."""

    def __init__(self, message):
        self.message = message


class JelilianAIProError(Exception):
    """Base exception for all JELILIAN AI PRO errors"""


class TokenLimitExceeded(JelilianAIProError):
    """Exception raised when the token limit is exceeded"""
