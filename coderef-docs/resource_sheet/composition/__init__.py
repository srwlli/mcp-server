"""
Composition Engine - Assembles Modules into Documentation.

WO-RESOURCE-SHEET-MCP-TOOL-001

This module composes selected modules into final documentation output
in multiple formats (markdown, schema, JSDoc).
"""

from .composer import DocumentComposer

__all__ = ["DocumentComposer"]
