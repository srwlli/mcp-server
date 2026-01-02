"""
Resource Sheet MCP Tool - Composable Documentation Module System.

WO-RESOURCE-SHEET-MCP-TOOL-001

This package provides a composable module-based approach to generating
authoritative technical documentation for code elements.

Instead of 20 rigid templates, it uses ~30-40 small modules that compose
intelligently based on code characteristics.
"""

from .modules import ModuleRegistry
from .detection import CodeAnalyzer, CharacteristicsDetector
from .composition import DocumentComposer

__all__ = [
    "ModuleRegistry",
    "CodeAnalyzer",
    "CharacteristicsDetector",
    "DocumentComposer",
]

__version__ = "0.1.0"
