"""Logging configuration for coderef-mcp service."""

import logging
import sys
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger


def setup_logging(level=logging.INFO):
    """Configure JSON logging for the service."""
    logger = logging.getLogger()
    logger.setLevel(level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler with JSON formatter (stderr to not interfere with MCP stdio)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)

    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s',
        timestamp=True
    )
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name):
    """Get a logger instance with the given name."""
    return logging.getLogger(name)
