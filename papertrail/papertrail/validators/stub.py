"""
Stub Validator

Validates stub.json files against stub-schema.json.
Provides auto-fill capabilities for missing required fields.
"""

from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import date
import json
import re

from jsonschema import Draft7Validator, ValidationError as JsonSchemaValidationError


class StubValidator:
    """
    Validator for stub.json files.

    Validates:
    - JSON schema compliance (stub-schema.json)
    - Required fields present
    - Field format validation (stub_id, feature_name, dates)
    - Auto-fills missing required fields with defaults
    """

    # Schema defaults for auto-fill
    SCHEMA_DEFAULTS = {
        "category": "feature",
        "priority": "medium",
        "status": "planning",
        "created": str(date.today())
    }

    REQUIRED_FIELDS = [
        "stub_id",
        "feature_name",
        "description",
        "category",
        "priority",
        "status",
        "created"
    ]

    def __init__(self, schemas_dir: Optional[Path] = None):
        """
        Initialize stub validator

        Args:
            schemas_dir: Path to schemas directory (default: package schemas/)
        """
        if schemas_dir is None:
            schemas_dir = Path(__file__).parent.parent.parent / "schemas"

        self.schemas_dir = schemas_dir
        self.schema = self._load_schema()

    def _load_schema(self) -> dict:
        """Load stub-schema.json"""
        schema_path = self.schemas_dir / "stub-schema.json"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")

        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_file(self, file_path: Path, auto_fill: bool = False) -> Tuple[bool, List[str], List[str], Optional[dict]]:
        """
        Validate a stub.json file

        Args:
            file_path: Path to stub.json file
            auto_fill: If True, auto-fill missing required fields

        Returns:
            Tuple of (is_valid, errors, warnings, updated_stub)
            - is_valid: True if stub is valid
            - errors: List of error messages
            - warnings: List of warning messages
            - updated_stub: Updated stub dict if auto_fill=True, else None
        """
        errors = []
        warnings = []
        updated_stub = None

        # Load stub file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                stub = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
            return (False, errors, warnings, None)
        except Exception as e:
            errors.append(f"Error reading file: {e}")
            return (False, errors, warnings, None)

        # Auto-fill if requested
        changes = []
        if auto_fill:
            stub, changes = self._auto_fill(stub, file_path)
            if changes:
                updated_stub = stub
                for change in changes:
                    warnings.append(f"Auto-filled: {change}")

        # Validate against JSON schema
        validator = Draft7Validator(self.schema)
        schema_errors = list(validator.iter_errors(stub))

        if schema_errors:
            for error in schema_errors:
                field = ".".join(str(p) for p in error.path) if error.path else "root"
                errors.append(f"[{field}] {error.message}")

        # Additional validation checks
        validation_errors, validation_warnings = self._validate_fields(stub)
        errors.extend(validation_errors)
        warnings.extend(validation_warnings)

        is_valid = len(errors) == 0

        return (is_valid, errors, warnings, updated_stub)

    def _auto_fill(self, stub: dict, file_path: Path) -> Tuple[dict, List[str]]:
        """
        Auto-fill missing required fields

        Args:
            stub: Stub dictionary
            file_path: Path to stub.json (used to derive feature_name)

        Returns:
            Tuple of (updated_stub, list_of_changes)
        """
        changes = []
        stub = stub.copy()  # Don't modify original

        # Derive feature_name from folder name if missing
        folder_name = file_path.parent.name

        # Check and fill required fields
        if "feature_name" not in stub or not stub["feature_name"]:
            stub["feature_name"] = folder_name
            changes.append(f"feature_name = {folder_name}")

        if "description" not in stub or not stub["description"]:
            stub["description"] = f"TODO: Add description for {folder_name}"
            changes.append("description = TODO placeholder")

        for field in ["category", "priority", "status", "created"]:
            if field not in stub or not stub[field]:
                stub[field] = self.SCHEMA_DEFAULTS[field]
                changes.append(f"{field} = {self.SCHEMA_DEFAULTS[field]}")

        return stub, changes

    def _validate_fields(self, stub: dict) -> Tuple[List[str], List[str]]:
        """
        Additional field validation beyond JSON schema

        Args:
            stub: Stub dictionary

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Validate stub_id format
        stub_id = stub.get("stub_id")
        if stub_id:
            if not re.match(r'^STUB-\d{3}$', stub_id):
                errors.append(f"Invalid stub_id format: {stub_id} (expected: STUB-###)")
        else:
            warnings.append("Missing stub_id (required field)")

        # Validate feature_name format (kebab-case)
        feature_name = stub.get("feature_name")
        if feature_name:
            if not re.match(r'^[a-z0-9-]+$', feature_name):
                errors.append(f"Invalid feature_name format: {feature_name} (expected: kebab-case)")

        # Validate created date format
        created = stub.get("created")
        if created:
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', created):
                errors.append(f"Invalid created date format: {created} (expected: YYYY-MM-DD)")

        # Validate promoted_to format if present
        promoted_to = stub.get("promoted_to")
        if promoted_to:
            if not re.match(r'^WO-[A-Z0-9-]+-\d{3}$', promoted_to):
                errors.append(f"Invalid promoted_to format: {promoted_to} (expected: WO-{{CATEGORY}}-{{ID}}-###)")

        # Check status consistency
        status = stub.get("status")
        if status == "promoted" and not promoted_to:
            warnings.append("Status is 'promoted' but promoted_to field is missing")

        return errors, warnings

    def save_stub(self, stub: dict, file_path: Path):
        """
        Save updated stub to file

        Args:
            stub: Stub dictionary
            file_path: Path to save stub.json
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(stub, f, indent=2, ensure_ascii=False)
