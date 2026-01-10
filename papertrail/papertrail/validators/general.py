"""
General Markdown Validator

Validates general markdown documents that don't fit specific categories.
Only validates base UDS fields (agent, date, task) without category-specific requirements.
"""

from pathlib import Path
from typing import Optional

from .base import BaseUDSValidator, ValidationError


class GeneralMarkdownValidator(BaseUDSValidator):
    """
    Validator for general markdown documents.

    Validates only base UDS fields without category-specific requirements.
    Used as fallback for documents that don't match other validators.
    """

    schema_name = "base-frontmatter-schema.json"
    doc_category = "general"

    def validate_specific(
        self, frontmatter: dict, content: str, file_path: Optional[Path] = None
    ) -> tuple[list[ValidationError], list[str]]:
        """
        General markdown validation (minimal checks).

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        # No category-specific validation for general markdown
        return ([], [])
