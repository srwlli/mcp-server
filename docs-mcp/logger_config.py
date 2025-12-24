"""
Logging configuration for coderef-docs server (ARCH-003).

Provides structured logging with configurable levels for debugging,
security audit trails, and usage analytics.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

__all__ = [
    'setup_logger',
    'setup_logging',  # Alias for coderef-mcp compatibility
    'logger',
    'log_tool_call',
    'log_security_event',
    'log_error',
    'log_performance',
    'set_log_level',
]


def setup_logger(
    name: str = 'coderef-docs',
    level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up structured logging for the MCP server.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # Create formatter with timestamp, level, and message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler (stderr to not interfere with MCP stdio)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logger()

# Compatibility aliases for coderef-mcp
setup_logging = setup_logger
get_logger = lambda name='coderef-mcp': logging.getLogger(name)


def log_tool_call(tool_name: str, **kwargs) -> None:
    """
    Log a tool invocation with context.

    Args:
        tool_name: Name of the tool being called
        **kwargs: Additional context to log (sanitized)
    """
    # Sanitize sensitive data
    safe_kwargs = {k: v for k, v in kwargs.items() if k not in ['password', 'token', 'secret']}
    logger.info(f"Tool called: {tool_name}", extra={'tool': tool_name, **safe_kwargs})


def log_security_event(event_type: str, detail: str, **kwargs) -> None:
    """
    Log a security-relevant event.

    Args:
        event_type: Type of security event (e.g., 'path_traversal_blocked', 'validation_failed')
        detail: Human-readable description
        **kwargs: Additional context
    """
    logger.warning(f"Security event - {event_type}: {detail}", extra={'event_type': event_type, **kwargs})


def log_error(error_type: str, detail: str, **kwargs) -> None:
    """
    Log an error with context.

    Args:
        error_type: Type of error (e.g., 'FileNotFoundError', 'ValidationError')
        detail: Error details
        **kwargs: Additional context
    """
    logger.error(f"{error_type}: {detail}", extra={'error_type': error_type, **kwargs})


def log_performance(operation: str, duration_ms: float, **kwargs) -> None:
    """
    Log performance metrics.

    Args:
        operation: Operation name
        duration_ms: Duration in milliseconds
        **kwargs: Additional context
    """
    logger.debug(f"Performance - {operation}: {duration_ms:.2f}ms", extra={'operation': operation, 'duration_ms': duration_ms, **kwargs})


def set_log_level(level: int) -> None:
    """
    Change the logging level dynamically.

    Args:
        level: New logging level (logging.DEBUG, INFO, WARNING, ERROR)
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
