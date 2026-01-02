"""
Detection Engine - Code Analysis and Characteristics Detection.

WO-RESOURCE-SHEET-MCP-TOOL-001

This module analyzes code to detect characteristics that determine
which documentation modules should be included.
"""

from .analyzer import CodeAnalyzer
from .characteristics import CharacteristicsDetector

__all__ = ["CodeAnalyzer", "CharacteristicsDetector"]
