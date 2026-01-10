"""
Session Document Validator

Validates session documentation (communication.json, instructions.json) against UDS schema.
Session docs coordinate multi-agent work.
"""

from pathlib import Path
from typing import Optional

from .base import BaseUDSValidator, ValidationError, ValidationSeverity


class SessionDocValidator(BaseUDSValidator):
    """
    Validator for session documentation files.

    Validates:
    - Base UDS fields (agent, date, task)
    - Session fields (session_type, session_id, orchestrator)
    - Session naming conventions
    """

    schema_name = "session-doc-frontmatter-schema.json"
    doc_category = "session"

    def validate_specific(
        self, frontmatter: dict, content: str, file_path: Optional[Path] = None
    ) -> tuple[list[ValidationError], list[str]]:
        """
        Session-specific validation logic.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Check session_id format (kebab-case)
        session_id = frontmatter.get('session_id')
        if session_id:
            import re
            if not re.match(r'^[a-z0-9-]+$', session_id):
                errors.append(
                    ValidationError(
                        severity=ValidationSeverity.MAJOR,
                        message=f"session_id '{session_id}' must be kebab-case (lowercase letters, numbers, hyphens only)",
                        field='session_id'
                    )
                )

        # Check orchestrator is specified for communication docs
        session_type = frontmatter.get('session_type')
        orchestrator = frontmatter.get('orchestrator')
        if session_type == 'communication' and not orchestrator:
            warnings.append(
                "Communication docs should specify 'orchestrator' field (which agent is coordinating?)"
            )

        # Check participants are specified for coordination docs
        participants = frontmatter.get('participants')
        if session_type in ['communication', 'coordination'] and not participants:
            warnings.append(
                "Coordination/communication docs should specify 'participants' field (list of agents)"
            )

        return (errors, warnings)
