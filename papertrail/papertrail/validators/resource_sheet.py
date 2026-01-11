"""
Resource Sheet Validator

Validates resource sheets (RSMS v2.0 compliant documentation) against
resource-sheet-metadata-schema.json. Resource sheets document individual
components, services, controllers, and other code elements.
"""

from pathlib import Path
from typing import Optional
import re

from .base import BaseUDSValidator, ValidationError, ValidationSeverity


class ResourceSheetValidator(BaseUDSValidator):
    """
    Validator for resource sheet documentation files.

    Validates:
    - Base UDS fields (agent, date, task)
    - RSMS fields (subject, parent_project, category, version)
    - Resource sheet structure and completeness
    """

    schema_name = "resource-sheet-metadata-schema.json"
    doc_category = "resource_sheet"

    # Recommended sections for resource sheets
    RECOMMENDED_SECTIONS = [
        "Executive Summary",
        "Audience & Intent",
        "Quick Reference",
        "Architecture",
        "Dependencies",
        "Usage",
        "Testing"
    ]

    def validate_specific(
        self, frontmatter: dict, content: str, file_path: Optional[Path] = None
    ) -> tuple[list[ValidationError], list[str]]:
        """
        Resource sheet-specific validation logic.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Validate category enum (required field)
        category = frontmatter.get('category')
        if category:
            valid_categories = [
                "service", "controller", "model", "utility", "integration",
                "component", "middleware", "validator", "schema", "config", "other"
            ]
            if category not in valid_categories:
                errors.append(ValidationError(
                    severity=ValidationSeverity.MAJOR,
                    message=f"Invalid category '{category}'. Must be one of: {', '.join(valid_categories)}",
                    field="category"
                ))

        # Validate version format (semver) if present
        version = frontmatter.get('version')
        if version:
            # Convert to string if it's a float/number from YAML parsing
            version_str = str(version)
            if not re.match(r'^\d+\.\d+\.\d+$', version_str):
                errors.append(ValidationError(
                    severity=ValidationSeverity.MINOR,
                    message=f"Invalid version format '{version_str}'. Expected semver (e.g., 1.0.0)",
                    field="version"
                ))
        else:
            warnings.append("Missing recommended field 'version' (semver format recommended)")

        # Validate related_files format if present
        related_files = frontmatter.get('related_files', [])
        if isinstance(related_files, list):
            for idx, file_ref in enumerate(related_files):
                if not isinstance(file_ref, str):
                    errors.append(ValidationError(
                        severity=ValidationSeverity.MINOR,
                        message=f"related_files[{idx}] must be a string",
                        field=f"related_files[{idx}]"
                    ))
                elif not re.match(r'^[a-zA-Z0-9/_.-]+\.[a-zA-Z0-9]+$', file_ref):
                    errors.append(ValidationError(
                        severity=ValidationSeverity.MINOR,
                        message=f"related_files[{idx}] '{file_ref}' has invalid file path format",
                        field=f"related_files[{idx}]"
                    ))

        # Validate related_docs format if present
        related_docs = frontmatter.get('related_docs', [])
        if isinstance(related_docs, list):
            for idx, doc_ref in enumerate(related_docs):
                if not isinstance(doc_ref, str):
                    errors.append(ValidationError(
                        severity=ValidationSeverity.MINOR,
                        message=f"related_docs[{idx}] must be a string",
                        field=f"related_docs[{idx}]"
                    ))
                elif not re.match(r'^[a-zA-Z0-9/_.-]+\.md$', doc_ref):
                    errors.append(ValidationError(
                        severity=ValidationSeverity.MINOR,
                        message=f"related_docs[{idx}] '{doc_ref}' must be a .md file",
                        field=f"related_docs[{idx}]"
                    ))

        # Validate workorder format if present
        workorder = frontmatter.get('workorder')
        if workorder:
            if not re.match(r'^WO-[A-Z0-9-]+-\d{3}$', workorder):
                errors.append(ValidationError(
                    severity=ValidationSeverity.MINOR,
                    message=f"Invalid workorder format '{workorder}'. Expected: WO-{{CATEGORY}}-{{ID}}-###",
                    field="workorder"
                ))

        # Check for legacy 'component' field (deprecated)
        if 'component' in frontmatter:
            warnings.append(
                "Field 'component' is deprecated. Use 'subject' instead (RSMS v2.0)"
            )

        # Check recommended sections
        missing_sections = self._check_recommended_sections(content)
        if missing_sections:
            warnings.append(
                f"Missing recommended sections: {', '.join(missing_sections)}"
            )

        # Check if filename follows convention (if file_path provided)
        if file_path:
            filename = file_path.name
            if not filename.endswith('-RESOURCE-SHEET.md'):
                warnings.append(
                    f"Filename '{filename}' doesn't follow convention: {{Subject}}-RESOURCE-SHEET.md"
                )

            # Check if subject matches filename
            subject = frontmatter.get('subject')
            if subject and filename.startswith(subject):
                # Good match
                pass
            elif subject:
                warnings.append(
                    f"Subject '{subject}' doesn't match filename prefix '{filename}'"
                )

        # Validate status if present
        status = frontmatter.get('status')
        if status == 'DRAFT':
            warnings.append("Resource sheet status is DRAFT (update to APPROVED when ready)")

        return (errors, warnings)

    def _check_recommended_sections(self, content: str) -> list[str]:
        """Check if recommended sections are present"""
        missing = []

        for section in self.RECOMMENDED_SECTIONS:
            # Look for markdown headers with section name (flexible matching)
            # Match ## Section or # Section
            if f"## {section}" not in content and f"# {section}" not in content:
                missing.append(section)

        return missing
