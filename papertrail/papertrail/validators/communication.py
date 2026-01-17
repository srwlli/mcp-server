"""
Communication Validator

Validates communication.json files against communication-schema.json.
Prevents data structure errors like files_created as numbers instead of arrays.
"""

from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime
import json
import re

from jsonschema import Draft7Validator, ValidationError as JsonSchemaValidationError


class CommunicationValidator:
    """
    Validator for communication.json files (multi-agent session coordination).

    Validates:
    - JSON schema compliance (communication-schema.json)
    - Required fields present
    - Field format validation (session_id, stub_id, workorder_id, dates)
    - Outputs structure (files_created/files_modified must be arrays, not numbers)
    - No git_metrics object (common error - agents create counts instead of arrays)
    """

    REQUIRED_FIELDS = [
        "session_id",
        "stub_id",
        "feature_name",
        "created_at",
        "agents",
        "status"
    ]

    AGENT_REQUIRED_FIELDS = [
        "agent_id",
        "agent_number",
        "role",
        "status",
        "outputs"
    ]

    OUTPUTS_REQUIRED_FIELDS = [
        "files_created",
        "files_modified",
        "workorders_created",
        "primary_output"
    ]

    def __init__(self, schemas_dir: Optional[Path] = None):
        """
        Initialize communication validator

        Args:
            schemas_dir: Path to schemas directory (default: package schemas/)
        """
        if schemas_dir is None:
            # Try package schemas first, then dashboard schemas
            package_schemas = Path(__file__).parent.parent.parent / "schemas"
            dashboard_schemas = Path.home() / "Desktop" / "coderef-dashboard" / "packages" / "dashboard" / "schemas"

            if (package_schemas / "communication-schema.json").exists():
                schemas_dir = package_schemas
            elif dashboard_schemas.exists():
                schemas_dir = dashboard_schemas
            else:
                schemas_dir = package_schemas  # Default fallback

        self.schemas_dir = schemas_dir
        self.schema = self._load_schema()

    def _load_schema(self) -> dict:
        """Load communication-schema.json"""
        schema_path = self.schemas_dir / "communication-schema.json"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")

        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_file(self, file_path: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a communication.json file

        Args:
            file_path: Path to communication.json file

        Returns:
            Tuple of (is_valid, errors, warnings)
            - is_valid: True if communication.json is valid
            - errors: List of error messages
            - warnings: List of warning messages
        """
        errors = []
        warnings = []

        # Load communication file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                comm = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
            return (False, errors, warnings)
        except Exception as e:
            errors.append(f"Error reading file: {e}")
            return (False, errors, warnings)

        # Validate against JSON schema
        validator = Draft7Validator(self.schema)
        schema_errors = list(validator.iter_errors(comm))

        if schema_errors:
            for error in schema_errors:
                field = ".".join(str(p) for p in error.path) if error.path else "root"
                errors.append(f"[{field}] {error.message}")

        # Additional validation checks
        validation_errors, validation_warnings = self._validate_fields(comm)
        errors.extend(validation_errors)
        warnings.extend(validation_warnings)

        is_valid = len(errors) == 0

        return (is_valid, errors, warnings)

    def _validate_fields(self, comm: dict) -> Tuple[List[str], List[str]]:
        """
        Additional field validation beyond JSON schema

        Args:
            comm: Communication dictionary

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Validate session_id format
        session_id = comm.get("session_id")
        if session_id:
            if not re.match(r'^[A-Z]+-[0-9]+-[0-9]+$', session_id):
                errors.append(f"Invalid session_id format: {session_id} (expected: STUB-###-timestamp)")
        else:
            errors.append("Missing session_id (required field)")

        # Validate stub_id format
        stub_id = comm.get("stub_id")
        if stub_id:
            if not re.match(r'^[A-Z]+-[0-9]+$', stub_id):
                errors.append(f"Invalid stub_id format: {stub_id} (expected: STUB-###)")
        else:
            errors.append("Missing stub_id (required field)")

        # Validate feature_name format (kebab-case)
        feature_name = comm.get("feature_name")
        if feature_name:
            if not re.match(r'^[a-z0-9-]+$', feature_name):
                errors.append(f"Invalid feature_name format: {feature_name} (expected: kebab-case)")

        # Validate created_at is ISO 8601 timestamp
        created_at = comm.get("created_at")
        if created_at:
            try:
                datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"Invalid created_at format: {created_at} (expected: ISO 8601 timestamp)")

        # Validate agents array
        agents = comm.get("agents", [])
        if not agents:
            errors.append("Missing or empty agents array (required field)")
        else:
            for i, agent in enumerate(agents):
                agent_errors, agent_warnings = self._validate_agent(agent, i)
                errors.extend(agent_errors)
                warnings.extend(agent_warnings)

        return errors, warnings

    def _validate_agent(self, agent: dict, index: int) -> Tuple[List[str], List[str]]:
        """
        Validate individual agent structure

        Args:
            agent: Agent dictionary
            index: Agent index in array (for error reporting)

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        agent_id = agent.get("agent_id", f"agent[{index}]")

        # Check required fields
        for field in self.AGENT_REQUIRED_FIELDS:
            if field not in agent:
                errors.append(f"[{agent_id}] Missing required field: {field}")

        # Validate outputs object
        outputs = agent.get("outputs")
        if not outputs:
            errors.append(f"[{agent_id}] Missing outputs object (required field)")
        elif not isinstance(outputs, dict):
            errors.append(f"[{agent_id}] outputs must be an object, not {type(outputs).__name__}")
        else:
            # CRITICAL: Check for git_metrics object (common error)
            if "git_metrics" in outputs:
                errors.append(
                    f"[{agent_id}] outputs contains 'git_metrics' object - this is INVALID. "
                    f"Remove git_metrics and use outputs.files_created[], outputs.files_modified[] arrays instead."
                )

            # Check required outputs fields
            for field in self.OUTPUTS_REQUIRED_FIELDS:
                if field not in outputs:
                    errors.append(f"[{agent_id}.outputs] Missing required field: {field}")

            # CRITICAL: files_created must be array, not number
            files_created = outputs.get("files_created")
            if files_created is not None:
                if isinstance(files_created, (int, float)):
                    errors.append(
                        f"[{agent_id}.outputs.files_created] Must be ARRAY of strings, not number. "
                        f"Got: {files_created} (type: {type(files_created).__name__}). "
                        f"Correct format: [\"path/file.ts (123 lines - description)\", ...]"
                    )
                elif isinstance(files_created, list):
                    for i, item in enumerate(files_created):
                        if not isinstance(item, str):
                            errors.append(
                                f"[{agent_id}.outputs.files_created[{i}]] Must be string, got {type(item).__name__}"
                            )

            # CRITICAL: files_modified must be array, not number
            files_modified = outputs.get("files_modified")
            if files_modified is not None:
                if isinstance(files_modified, (int, float)):
                    errors.append(
                        f"[{agent_id}.outputs.files_modified] Must be ARRAY of strings, not number. "
                        f"Got: {files_modified} (type: {type(files_modified).__name__}). "
                        f"Correct format: [\"path/file.ts (description of changes)\", ...]"
                    )
                elif isinstance(files_modified, list):
                    for i, item in enumerate(files_modified):
                        if not isinstance(item, str):
                            errors.append(
                                f"[{agent_id}.outputs.files_modified[{i}]] Must be string, got {type(item).__name__}"
                            )

            # Validate workorders_created array
            workorders_created = outputs.get("workorders_created")
            if workorders_created is not None:
                if not isinstance(workorders_created, list):
                    errors.append(
                        f"[{agent_id}.outputs.workorders_created] Must be ARRAY of objects, "
                        f"got {type(workorders_created).__name__}"
                    )
                else:
                    for i, wo in enumerate(workorders_created):
                        if not isinstance(wo, dict):
                            errors.append(
                                f"[{agent_id}.outputs.workorders_created[{i}]] Must be object, "
                                f"got {type(wo).__name__}"
                            )
                        else:
                            # Validate workorder_id format
                            wo_id = wo.get("workorder_id")
                            if wo_id and not re.match(r'^WO-[A-Z0-9-]+-[0-9]+$', wo_id):
                                errors.append(
                                    f"[{agent_id}.outputs.workorders_created[{i}].workorder_id] "
                                    f"Invalid format: {wo_id} (expected: WO-{{CATEGORY}}-{{ID}}-###)"
                                )

        # Validate status field
        status = agent.get("status")
        if status:
            valid_statuses = ["pending", "not_started", "in_progress", "complete", "failed"]
            if status not in valid_statuses:
                errors.append(
                    f"[{agent_id}.status] Invalid value: {status} "
                    f"(must be one of: {', '.join(valid_statuses)})"
                )

        return errors, warnings
