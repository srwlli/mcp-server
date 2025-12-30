"""
UDS Validation - Schema validation and metadata checking

Validates documents against CodeRef UDS schemas and ensures
required metadata is present and correctly formatted.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import json
import re
import yaml


class ValidationSeverity(Enum):
    """Validation error severity levels"""
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    WARNING = "WARNING"


@dataclass
class ValidationError:
    """Single validation error"""
    severity: ValidationSeverity
    message: str
    section: Optional[str] = None
    field: Optional[str] = None


@dataclass
class ValidationResult:
    """
    Result of UDS validation

    Attributes:
        valid: True if document passes all CRITICAL checks
        errors: List of validation errors (all severities)
        warnings: List of warning messages
        score: Validation score (0-100)
    """
    valid: bool
    errors: list[ValidationError]
    warnings: list[str]
    score: int  # 0-100


class UDSValidator:
    """
    UDS Validator - Validates documents against CodeRef schemas

    Checks:
    1. Required sections present
    2. Required metadata present and correctly formatted
    3. Workorder ID format (WO-{FEATURE}-{CATEGORY}-###)
    4. MCP attribution present (generated_by)
    5. Timestamps valid (ISO 8601)
    """

    def __init__(self, schemas_dir: Optional[Path] = None):
        """
        Initialize validator with schemas directory

        Args:
            schemas_dir: Path to schemas directory (default: package schemas/)
        """
        if schemas_dir is None:
            # Default to package schemas directory
            schemas_dir = Path(__file__).parent / "schemas"

        self.schemas_dir = schemas_dir
        self._load_schemas()

    def _load_schemas(self):
        """Load all schema files"""
        self.schemas = {}
        schema_files = {
            "plan": "plan.json",
            "deliverables": "deliverables.json",
            "architecture": "architecture.json",
            "readme": "readme.json",
            "api": "api.json"
        }

        for doc_type, filename in schema_files.items():
            schema_path = self.schemas_dir / filename
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    self.schemas[doc_type] = json.load(f)

    def validate(self, document: str, doc_type: str) -> ValidationResult:
        """
        Validate document against UDS schema

        Args:
            document: Document content (markdown or JSON)
            doc_type: Document type (plan, deliverables, architecture, readme, api)

        Returns:
            ValidationResult: Validation results with errors and score
        """
        errors = []
        warnings = []

        # Get schema for doc type
        schema = self.schemas.get(doc_type)
        if not schema:
            errors.append(ValidationError(
                severity=ValidationSeverity.CRITICAL,
                message=f"Unknown document type: {doc_type}"
            ))
            return ValidationResult(valid=False, errors=errors, warnings=warnings, score=0)

        # Extract YAML frontmatter (header)
        header = self._extract_header(document)
        if not header:
            errors.append(ValidationError(
                severity=ValidationSeverity.CRITICAL,
                message="Missing UDS header (YAML frontmatter)"
            ))
            return ValidationResult(valid=False, errors=errors, warnings=warnings, score=0)

        # Validate required metadata
        metadata_errors = self._validate_metadata(header, schema)
        errors.extend(metadata_errors)

        # Validate required sections
        section_errors = self._validate_sections(document, schema)
        errors.extend(section_errors)

        # Calculate validation score
        score = self._calculate_validation_score(errors)

        # Determine if valid (no CRITICAL errors)
        valid = not any(e.severity == ValidationSeverity.CRITICAL for e in errors)

        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            score=score
        )

    def _extract_header(self, document: str) -> Optional[dict]:
        """Extract YAML frontmatter from document"""
        # Look for YAML frontmatter between --- delimiters
        match = re.match(r'^---\n(.*?)\n---', document, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError:
                return None
        return None

    def _validate_metadata(self, header: dict, schema: dict) -> list[ValidationError]:
        """Validate required metadata fields"""
        errors = []
        required_metadata = schema.get("required_metadata", {})

        for field, spec in required_metadata.items():
            # Check if field is present
            if field not in header:
                errors.append(ValidationError(
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Missing required field: {field}",
                    field=field
                ))
                continue

            # Check field format (if pattern specified)
            if isinstance(spec, dict) and "pattern" in spec:
                pattern = spec["pattern"]
                value = str(header[field])
                if not re.match(pattern, value):
                    errors.append(ValidationError(
                        severity=ValidationSeverity.MAJOR,
                        message=f"Field '{field}' does not match required pattern: {pattern}",
                        field=field
                    ))

        return errors

    def _validate_sections(self, document: str, schema: dict) -> list[ValidationError]:
        """Validate required sections are present"""
        errors = []
        required_sections = schema.get("required_sections", [])

        for section in required_sections:
            # Check if section heading exists in document
            # Look for markdown headings (# Section, ## Section, etc.)
            section_pattern = rf'^#+\s+{re.escape(section)}'
            if not re.search(section_pattern, document, re.MULTILINE | re.IGNORECASE):
                errors.append(ValidationError(
                    severity=ValidationSeverity.MAJOR,
                    message=f"Missing required section: {section}",
                    section=section
                ))

        return errors

    def _calculate_validation_score(self, errors: list[ValidationError]) -> int:
        """
        Calculate validation score (0-100) based on errors

        Scoring:
        - CRITICAL error: -50 points
        - MAJOR error: -20 points
        - MINOR error: -10 points
        - WARNING: -5 points
        """
        score = 100

        for error in errors:
            if error.severity == ValidationSeverity.CRITICAL:
                score -= 50
            elif error.severity == ValidationSeverity.MAJOR:
                score -= 20
            elif error.severity == ValidationSeverity.MINOR:
                score -= 10
            elif error.severity == ValidationSeverity.WARNING:
                score -= 5

        return max(0, score)


def validate_uds(document: str, doc_type: str) -> ValidationResult:
    """
    Convenience function to validate document

    Args:
        document: Document content
        doc_type: Document type (plan, deliverables, architecture, readme, api)

    Returns:
        ValidationResult: Validation results
    """
    validator = UDSValidator()
    return validator.validate(document, doc_type)


def validate_workorder_id(workorder_id: str) -> bool:
    """
    Validate workorder ID format: WO-{FEATURE}-{CATEGORY}-###

    Requires at least 2 segments (feature and category) before the 3-digit ID.

    Args:
        workorder_id: Workorder ID to validate

    Returns:
        bool: True if valid format

    Examples:
        >>> validate_workorder_id("WO-AUTH-SYSTEM-001")
        True
        >>> validate_workorder_id("WO-AUTH-001")  # Missing category
        False
        >>> validate_workorder_id("invalid-format")
        False
    """
    # Pattern: WO-{SEGMENT}(-{SEGMENT})+-{3 DIGITS}
    # Ensures at least 2 segments before the final 3 digits
    pattern = r'^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\d{3}$'
    return bool(re.match(pattern, workorder_id))


def validate_feature_id(feature_id: str) -> bool:
    """
    Validate feature ID format: alphanumeric, hyphens, underscores only

    Args:
        feature_id: Feature ID to validate

    Returns:
        bool: True if valid format

    Examples:
        >>> validate_feature_id("auth-system")
        True
        >>> validate_feature_id("Auth System!")
        False
    """
    pattern = r'^[a-z0-9_-]+$'
    return bool(re.match(pattern, feature_id))
