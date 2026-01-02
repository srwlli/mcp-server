"""
Universal Modules - Always Included.

WO-RESOURCE-SHEET-MCP-TOOL-001

These modules are included in every resource sheet regardless of
element type or characteristics.
"""

from .architecture import architecture_module
from .integration import integration_module
from .testing import testing_module
from .performance import performance_module

__all__ = [
    "architecture_module",
    "integration_module",
    "testing_module",
    "performance_module",
]
