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


class UserGuideValidator(UserFacingDocValidator):
    """Validates user guide documents (doc_type: guide)"""

    doc_category = "user-guide"

    def validate_specific(self, frontmatter: dict, content: str, file_path: Optional[Path] = None) -> tuple[list[ValidationError], list[str]]:
        """Guide-specific validation"""
        errors, warnings = super().validate_specific(frontmatter, content, file_path)

        # Guides should have examples section
        if "## Examples" not in content and "# Examples" not in content:
            warnings.append("User guides should include an Examples section")

        # Check doc_type is 'guide'
        doc_type = frontmatter.get('doc_type')
        if doc_type and doc_type != 'guide':
            errors.append(ValidationError(
                severity=ValidationSeverity.MAJOR,
                message=f"Expected doc_type 'guide', got '{doc_type}'",
                field="doc_type"
            ))

        return (errors, warnings)


class QuickrefValidator(UserFacingDocValidator):
    """Validates quickref/quickstart documents"""

    doc_category = "quickref"

    def validate_specific(self, frontmatter: dict, content: str, file_path: Optional[Path] = None) -> tuple[list[ValidationError], list[str]]:
        """Quickref-specific validation"""
        errors, warnings = super().validate_specific(frontmatter, content, file_path)

        # Check doc_type is 'quickstart' or 'reference'
        doc_type = frontmatter.get('doc_type')
        if doc_type and doc_type not in ['quickstart', 'reference']:
            errors.append(ValidationError(
                severity=ValidationSeverity.MAJOR,
                message=f"Expected doc_type 'quickstart' or 'reference', got '{doc_type}'",
                field="doc_type"
            ))

        # Quickstart should be concise (< 500 lines)
        if doc_type == 'quickstart':
            line_count = len(content.split('\n'))
            if line_count > 500:
                warnings.append(f"Quickstart docs should be concise (current: {line_count} lines, recommended: < 500)")

        return (errors, warnings)
