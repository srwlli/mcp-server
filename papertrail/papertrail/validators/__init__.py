"""
UDS Validators - Document validation for CodeRef ecosystem

This module provides specialized validators for all document types
across the CodeRef ecosystem, with automatic validator detection
based on file path patterns and frontmatter inspection.
"""

from .factory import ValidatorFactory
from .base import BaseUDSValidator

__all__ = ["ValidatorFactory", "BaseUDSValidator"]
