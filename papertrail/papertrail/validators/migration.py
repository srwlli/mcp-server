"""
Migration Document Validator

Validates migration documentation (upgrade guides, deprecation notices) against UDS schema.
Migration docs describe how to transition from old to new systems.
"""

from pathlib import Path
from typing import Optional

from .base import BaseUDSValidator, ValidationError, ValidationSeverity


class MigrationDocValidator(BaseUDSValidator):
    """
    Validator for migration documentation files.

    Validates:
    - Base UDS fields (agent, date, task)
    - Migration fields (migration_type, from_version, to_version)
    - Recommended sections for migration docs
    """

    schema_name = "migration-doc-frontmatter-schema.json"
    doc_category = "migration"

    # Recommended sections for migration docs
    MIGRATION_SECTIONS = [
        "Overview",
        "Breaking Changes",
        "Migration Steps",
        "Testing",
        "Rollback"
    ]

    def validate_specific(
        self, frontmatter: dict, content: str, file_path: Optional[Path] = None
    ) -> tuple[list[ValidationError], list[str]]:
        """
        Migration-specific validation logic.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Check for recommended migration sections
        missing_sections = self._check_migration_sections(content)
        if missing_sections:
            warnings.append(
                f"Missing recommended migration sections: {', '.join(missing_sections)}"
            )

        # Check breaking_changes flag matches migration_type
        migration_type = frontmatter.get('migration_type')
        breaking_changes = frontmatter.get('breaking_changes')
        
        if migration_type == 'breaking-change' and not breaking_changes:
            warnings.append(
                "migration_type is 'breaking-change' but breaking_changes flag is not set to true"
            )

        # Check automated flag is specified for upgrades
        if migration_type == 'upgrade' and 'automated' not in frontmatter:
            warnings.append(
                "Consider specifying 'automated' flag for upgrade migrations (is there a migration script?)"
            )

        return (errors, warnings)

    def _check_migration_sections(self, content: str) -> list[str]:
        """Check for recommended migration documentation sections."""
        missing = []
        for section in self.MIGRATION_SECTIONS:
            if f"# {section}" not in content and f"## {section}" not in content:
                missing.append(section)
        return missing
