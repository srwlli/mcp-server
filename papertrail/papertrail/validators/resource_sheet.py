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

        # Check directory location and filename format (if file_path provided)
        if file_path:
            # 1. DIRECTORY LOCATION CHECK
            # Resource sheets must be in coderef/resources-sheets/ directory
            parent_dir = file_path.parent.name

            if parent_dir != "resources-sheets":
                errors.append(ValidationError(
                    severity=ValidationSeverity.MAJOR,
                    message=f"File must be in 'coderef/resources-sheets/' directory (found in '{parent_dir}/')",
                    field="file_location"
                ))

            # Check for deprecated directory name
            if "reference-sheets" in str(file_path):
                errors.append(ValidationError(
                    severity=ValidationSeverity.MAJOR,
                    message="Deprecated directory 'reference-sheets' - use 'resources-sheets' instead",
                    field="file_location"
                ))

            # 2. FILENAME FORMAT VALIDATION
            filename = file_path.name

            # Check suffix
            if not filename.endswith('-RESOURCE-SHEET.md'):
                errors.append(ValidationError(
                    severity=ValidationSeverity.MAJOR,
                    message=f"Filename '{filename}' must end with '-RESOURCE-SHEET.md'",
                    field="filename"
                ))
            else:
                # Extract component name from filename
                component_name = filename.replace('-RESOURCE-SHEET.md', '')

                # 3. PASCALCASE-WITH-HYPHENS FORMAT CHECK
                # Pattern: ^[A-Z][a-z0-9]*(-[A-Z][a-z0-9]*)*$
                # Examples: Auth-Service, Widget-System, File-Api-Route

                # Check for ALL-CAPS format (MAJOR ERROR - upgraded from WARNING)
                if component_name.replace('-', '').isupper() and component_name.replace('-', '').isalpha():
                    errors.append(ValidationError(
                        severity=ValidationSeverity.MAJOR,
                        message=f"ALL-CAPS filename '{component_name}' - use PascalCase-with-hyphens (e.g., 'Auth-Service', not 'AUTH-SERVICE')",
                        field="filename"
                    ))
                # Check for lowercase format
                elif component_name.replace('-', '').islower():
                    errors.append(ValidationError(
                        severity=ValidationSeverity.MAJOR,
                        message=f"lowercase filename '{component_name}' - use PascalCase-with-hyphens (e.g., 'Auth-Service', not 'auth-service')",
                        field="filename"
                    ))
                # Check PascalCase-with-hyphens pattern
                elif not re.match(r'^[A-Z][a-z0-9]*(-[A-Z][a-z0-9]*)*$', component_name):
                    errors.append(ValidationError(
                        severity=ValidationSeverity.MAJOR,
                        message=f"Invalid filename format '{component_name}' - use PascalCase-with-hyphens (e.g., 'Auth-Service', 'Widget-System', 'File-Api-Route')",
                        field="filename"
                    ))

                # 4. SUBJECT CONSISTENCY CHECK
                subject = frontmatter.get('subject')
                if subject:
                    # Convert subject to expected filename format
                    # Example: "Auth Service" -> "Auth-Service"
                    expected_component = self._convert_subject_to_filename(subject)

                    if component_name != expected_component:
                        warnings.append(
                            f"Filename component '{component_name}' doesn't match subject '{subject}' (expected: '{expected_component}-RESOURCE-SHEET.md')"
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

    def _convert_subject_to_filename(self, subject: str) -> str:
        """
        Convert subject field to expected filename component.

        Converts subject to PascalCase-with-hyphens format:
        - "Auth Service" -> "Auth-Service"
        - "Widget System" -> "Widget-System"
        - "File API Route" -> "File-Api-Route"

        Args:
            subject: Subject field from YAML frontmatter

        Returns:
            Expected filename component (without -RESOURCE-SHEET.md suffix)
        """
        # Split by spaces and hyphens
        words = re.split(r'[\s-]+', subject.strip())

        # Convert each word to PascalCase (first letter uppercase, rest lowercase)
        pascal_words = []
        for word in words:
            if word:  # Skip empty strings
                # Handle acronyms like "API" -> "Api"
                pascal_word = word[0].upper() + word[1:].lower()
                pascal_words.append(pascal_word)

        # Join with hyphens
        return '-'.join(pascal_words)
