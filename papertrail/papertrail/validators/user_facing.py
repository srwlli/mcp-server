"""
User-Facing Document Validator

Validates user-facing documentation (guides, tutorials, FAQs in coderef/user/) against UDS schema.
Note: User docs are ALLOWED to contain emojis per EMOJI-TIMESTAMP-POLICY.md.
"""

from pathlib import Path
from typing import Optional

from .base import BaseUDSValidator, ValidationError, ValidationSeverity


class UserFacingDocValidator(BaseUDSValidator):
    """
    Validator for user-facing documentation files.

    Validates:
    - Base UDS fields (agent, date, task)
    - User-facing fields (audience, doc_type, difficulty, estimated_time)
    - Does NOT check for emojis (user docs are exempt)
    """

    schema_name = "user-facing-doc-frontmatter-schema.json"
    doc_category = "user-facing"

    def validate_specific(
        self, frontmatter: dict, content: str, file_path: Optional[Path] = None
    ) -> tuple[list[ValidationError], list[str]]:
        """
        User-facing-specific validation logic.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Check estimated_time format if present
        estimated_time = frontmatter.get('estimated_time')
        if estimated_time:
            import re
            if not re.match(r'^\d+\s*(min|mins|minutes|hour|hours|hr|hrs)$', estimated_time):
                warnings.append(
                    f"estimated_time '{estimated_time}' should follow pattern '10 minutes' or '1 hour'"
                )

        # Check difficulty is appropriate for doc_type
        doc_type = frontmatter.get('doc_type')
        difficulty = frontmatter.get('difficulty')
        if doc_type == 'quickstart' and difficulty not in [None, 'beginner']:
            warnings.append(
                f"Quickstart guides should typically be 'beginner' difficulty (currently '{difficulty}')"
            )

        # Check audience is specified
        audience = frontmatter.get('audience')
        if not audience:
            warnings.append("Consider specifying 'audience' field for better targeting")

        return (errors, warnings)
