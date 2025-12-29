"""
Papertrail - Universal Documentation Standards (UDS) for CodeRef Ecosystem

Provides:
- UDS headers/footers with workorder tracking
- Schema validation for 5 CodeRef doc types
- Health scoring (0-100)
- Template engine with CodeRef extensions
"""

__version__ = "1.0.0"

from .uds import UDSHeader, UDSFooter, DocumentType
from .validator import validate_uds, ValidationResult
from .health import calculate_health, HealthScore

__all__ = [
    "UDSHeader",
    "UDSFooter",
    "DocumentType",
    "validate_uds",
    "ValidationResult",
    "calculate_health",
    "HealthScore",
]
