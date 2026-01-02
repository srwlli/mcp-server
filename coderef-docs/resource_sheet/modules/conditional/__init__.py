"""
Conditional documentation modules.

WO-RESOURCE-SHEET-MCP-TOOL-001

Conditional modules are only included when specific code characteristics
are detected (e.g., UI modules only for components with JSX).
"""

from .ui.props import props_module
from .ui.events import events_module
from .ui.accessibility import accessibility_module
from .state.state_management import state_module
from .state.lifecycle import lifecycle_module
from .network.endpoints import endpoints_module
from .network.auth import auth_module
from .network.retry import retry_module
from .network.errors import error_handling_module
from .hooks.signature import hook_signature_module
from .hooks.side_effects import hook_side_effects_module

__all__ = [
    # UI modules
    "props_module",
    "events_module",
    "accessibility_module",
    # State modules
    "state_module",
    "lifecycle_module",
    # Network modules
    "endpoints_module",
    "auth_module",
    "retry_module",
    "error_handling_module",
    # Hook modules
    "hook_signature_module",
    "hook_side_effects_module",
]
