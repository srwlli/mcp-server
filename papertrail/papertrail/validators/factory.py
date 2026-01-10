"""
Validator Factory

Auto-detects the appropriate validator for a document based on:
1. File path patterns (e.g., RESOURCE-SHEET.md, plan.json, DELIVERABLES.md)
2. Frontmatter inspection (doc_type, category, etc.)
3. File location (coderef/foundation-docs/, coderef/workorder/, etc.)
"""

from pathlib import Path
from typing import Optional, Union
import re

from .base import BaseUDSValidator


class ValidatorFactory:
    """
    Factory for auto-detecting and creating appropriate validators

    Usage:
        validator = ValidatorFactory.get_validator("/path/to/README.md")
        result = validator.validate_file("/path/to/README.md")
    """

    # Path pattern to validator type mapping
    PATH_PATTERNS = {
        # Resource sheets
        r".*-RESOURCE-SHEET\.md$": "resource_sheet",
        r".*/docs/.*-RESOURCE-SHEET\.md$": "resource_sheet",

        # Foundation docs
        r".*/coderef/foundation-docs/README\.md$": "foundation",
        r".*/coderef/foundation-docs/ARCHITECTURE\.md$": "foundation",
        r".*/coderef/foundation-docs/API\.md$": "foundation",
        r".*/coderef/foundation-docs/SCHEMA\.md$": "foundation",
        r".*/coderef/foundation-docs/COMPONENTS\.md$": "foundation",
        r".*/README\.md$": "foundation",  # Root README

        # Workorder docs
        r".*/coderef/workorder/.*/context\.json$": "workorder",
        r".*/coderef/workorder/.*/analysis\.json$": "analysis",  # New: AnalysisValidator
        r".*/coderef/workorder/.*/execution-log\.json$": "execution_log",  # New: ExecutionLogValidator
        r".*/coderef/workorder/.*/plan\.json$": "plan",  # Special: uses existing plan validator
        r".*/coderef/workorder/.*/DELIVERABLES\.md$": "workorder",

        # System docs
        r".*/CLAUDE\.md$": "system",
        r".*/coderef/sessions/SESSION-INDEX\.md$": "system",

        # Standards docs
        r".*/standards/.*-standards\.md$": "standards",
        r".*/standards/documentation/global-documentation-standards\.md$": "standards",

        # Session docs (communication.json)
        r".*/coderef/sessions/.*/communication\.json$": "session",
        r".*/coderef/sessions/.*/instructions\.json$": "session",

        # Infrastructure docs
        r".*/FILE-TREE\.md$": "infrastructure",
        r".*/.*-INVENTORY\.md$": "infrastructure",
        r".*/.*-INDEX\.md$": "infrastructure",

        # Migration/Audit docs
        r".*/MIGRATION-.*\.md$": "migration",
        r".*/AUDIT-.*\.md$": "migration",
        r".*/COMPLETION-.*\.md$": "migration",
        r".*/SUMMARY-.*\.md$": "migration",

        # User-facing docs
        r".*/USER-GUIDE\.md$": "user_facing",
        r".*/TUTORIAL-.*\.md$": "user_facing",
        r".*/HOW-TO-.*\.md$": "user_facing",
    }

    @classmethod
    def get_validator(cls, file_path: Union[str, Path], schemas_dir: Optional[Path] = None) -> BaseUDSValidator:
        """
        Get appropriate validator for a file

        Args:
            file_path: Path to file to validate
            schemas_dir: Optional schemas directory path

        Returns:
            BaseUDSValidator subclass instance

        Raises:
            ValueError: If no validator found for file type
        """
        file_path = Path(file_path)
        path_str = str(file_path).replace("\\", "/")  # Normalize for Windows

        # Try path pattern matching first
        validator_type = cls._detect_from_path(path_str)

        # If no match, try frontmatter inspection
        if validator_type is None and file_path.suffix in ['.md', '.json']:
            validator_type = cls._detect_from_frontmatter(file_path)

        # If still no match, default based on file extension
        if validator_type is None:
            if file_path.suffix == '.md':
                validator_type = "general"  # General markdown validator
            else:
                raise ValueError(f"Cannot determine validator type for: {file_path}")

        # Create validator instance
        return cls._create_validator(validator_type, schemas_dir)

    @classmethod
    def _detect_from_path(cls, path_str: str) -> Optional[str]:
        """Detect validator type from file path pattern"""
        for pattern, validator_type in cls.PATH_PATTERNS.items():
            if re.match(pattern, path_str, re.IGNORECASE):
                return validator_type
        return None

    @classmethod
    def _detect_from_frontmatter(cls, file_path: Path) -> Optional[str]:
        """Detect validator type from frontmatter inspection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not match:
                return None

            import yaml
            frontmatter = yaml.safe_load(match.group(1))

            if not isinstance(frontmatter, dict):
                return None

            # Check doc_type field
            doc_type = frontmatter.get('doc_type')
            if doc_type in ['readme', 'architecture', 'api', 'schema', 'components']:
                return "foundation"

            # Check category field (resource sheets)
            if 'subject' in frontmatter and 'parent_project' in frontmatter and 'category' in frontmatter:
                return "resource_sheet"

            # Check workorder_id field
            if 'workorder_id' in frontmatter and 'feature_id' in frontmatter:
                return "workorder"

            # Check generated_by field
            generated_by = frontmatter.get('generated_by', '')
            if 'coderef-docs' in generated_by:
                return "foundation"

        except Exception:
            pass

        return None

    @classmethod
    def _create_validator(cls, validator_type: str, schemas_dir: Optional[Path] = None) -> BaseUDSValidator:
        """Create validator instance based on type"""
        # Import validators dynamically to avoid circular imports
        from . import foundation, workorder, system, standards, session, infrastructure, migration, user_facing, general, execution_log, analysis

        validator_map = {
            "foundation": foundation.FoundationDocValidator,
            "workorder": workorder.WorkorderDocValidator,
            "system": system.SystemDocValidator,
            "standards": standards.StandardsDocValidator,
            "session": session.SessionDocValidator,
            "infrastructure": infrastructure.InfrastructureDocValidator,
            "migration": migration.MigrationDocValidator,
            "user_facing": user_facing.UserFacingDocValidator,
            "general": general.GeneralMarkdownValidator,
            "execution_log": execution_log.ExecutionLogValidator,  # New: execution-log.json
            "analysis": None,  # Coming next (Phase 3)
            "resource_sheet": None,  # Will use existing resource-sheets/validate.ps1 for now
            "plan": None,  # Will use existing plans/validate.py for now
        }

        validator_class = validator_map.get(validator_type)

        if validator_class is None:
            raise ValueError(f"Validator type '{validator_type}' not yet implemented (coming in future phases)")

        return validator_class(schemas_dir=schemas_dir)

    @classmethod
    def detect_validator_type(cls, file_path: Union[str, Path]) -> str:
        """
        Detect validator type for a file without creating instance

        Args:
            file_path: Path to file

        Returns:
            Validator type string (foundation, workorder, system, etc.)

        Raises:
            ValueError: If no validator found
        """
        file_path = Path(file_path)
        path_str = str(file_path).replace("\\", "/")

        # Try path pattern matching
        validator_type = cls._detect_from_path(path_str)

        # Try frontmatter inspection
        if validator_type is None and file_path.suffix in ['.md', '.json']:
            validator_type = cls._detect_from_frontmatter(file_path)

        # Default
        if validator_type is None:
            if file_path.suffix == '.md':
                validator_type = "general"
            else:
                raise ValueError(f"Cannot determine validator type for: {file_path}")

        return validator_type
