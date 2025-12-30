"""
Papertrail - Universal Documentation Standards (UDS) for CodeRef Ecosystem

Provides:
- UDS headers/footers with workorder tracking
- Schema validation for 5 CodeRef doc types
- Health scoring (0-100)
- Template engine with CodeRef extensions
"""

__version__ = "1.0.0"

from .uds import UDSHeader, UDSFooter, DocumentType, DocumentStatus
from .validator import validate_uds, ValidationResult
from .health import calculate_health, HealthScore
from .engine import TemplateEngine, create_template_engine
from .extensions import CodeRefContextExtension, GitExtension, WorkflowExtension

__all__ = [
    "UDSHeader",
    "UDSFooter",
    "DocumentType",
    "DocumentStatus",
    "validate_uds",
    "ValidationResult",
    "calculate_health",
    "HealthScore",
    "TemplateEngine",
    "create_template_engine",
    "CodeRefContextExtension",
    "GitExtension",
    "WorkflowExtension",
]
