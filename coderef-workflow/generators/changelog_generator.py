"""Changelog generator for managing CHANGELOG.json entries."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import jsonschema
import sys

# Add parent directory to path for constants import
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import ChangeType, Severity
from type_defs import ChangeDict, VersionEntryDict


class ChangelogGenerator:
    """Helper class for managing changelog entries."""

    def __init__(self, changelog_path: Path):
        """
        Initialize changelog generator.

        Args:
            changelog_path: Path to CHANGELOG.json file
        """
        self.changelog_path = changelog_path
        self.schema_path = changelog_path.parent / "schema.json"
        self.schema = self._load_schema()

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """
        Load JSON schema for validation (SEC-002).

        Returns:
            Schema dictionary or None if schema file doesn't exist

        Raises:
            json.JSONDecodeError: If schema JSON is malformed
        """
        if not self.schema_path.exists():
            return None

        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Malformed schema file: {self.schema_path}",
                e.doc,
                e.pos
            )

    def validate_changelog(self, data: Dict[str, Any]) -> None:
        """
        Validate changelog data against JSON schema (SEC-002).

        Args:
            data: Changelog dictionary to validate

        Raises:
            jsonschema.ValidationError: If data doesn't match schema
            jsonschema.SchemaError: If schema itself is invalid
        """
        if self.schema is None:
            # No schema available, skip validation
            return

        jsonschema.validate(data, self.schema)

    def read_changelog(self) -> Dict[str, Any]:
        """
        Read current changelog data.

        Returns:
            Dictionary with changelog data

        Raises:
            FileNotFoundError: If changelog doesn't exist
            json.JSONDecodeError: If JSON is malformed
            jsonschema.ValidationError: If data doesn't match schema (SEC-002)
        """
        if not self.changelog_path.exists():
            raise FileNotFoundError(f"Changelog not found: {self.changelog_path}")

        with open(self.changelog_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate against schema (SEC-002)
        self.validate_changelog(data)

        return data

    def write_changelog(self, data: Dict[str, Any]) -> None:
        """
        Write changelog data to file.

        Args:
            data: Changelog dictionary to write

        Raises:
            IOError: If file cannot be written
            jsonschema.ValidationError: If data doesn't match schema (SEC-002)
        """
        # Validate before writing (SEC-002)
        self.validate_changelog(data)

        with open(self.changelog_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Add trailing newline

        # GAP-012: Validate CHANGELOG.json with Papertrail (UDS compliance)
        try:
            from papertrail.validators.general import GeneralValidator
            validator = GeneralValidator()
            result = validator.validate_file(str(self.changelog_path))

            if not result['valid']:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"CHANGELOG.json validation failed (score: {result.get('score', 0)})")
                for error in result.get('errors', []):
                    logger.warning(f"  - {error}")
            else:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"CHANGELOG.json validated successfully (score: {result.get('score', 100)})")
        except ImportError:
            pass  # Papertrail not available
        except Exception:
            pass  # Validation error - continue

    def get_next_change_id(self) -> str:
        """
        Generate next sequential change ID.

        Returns:
            Change ID in format "change-NNN"
        """
        data = self.read_changelog()
        max_id = 0

        for entry in data.get('entries', []):
            for change in entry.get('changes', []):
                change_id = change.get('id', 'change-000')
                # Extract number from "change-123"
                try:
                    num = int(change_id.split('-')[1])
                    max_id = max(max_id, num)
                except (IndexError, ValueError):
                    continue

        return f"change-{max_id + 1:03d}"

    def add_change(
        self,
        version: str,
        change_type: str,
        severity: str,
        title: str,
        description: str,
        files: List[str],
        reason: str,
        impact: str,
        breaking: bool = False,
        migration: Optional[str] = None,
        date: Optional[str] = None,
        summary: Optional[str] = None,
        contributors: Optional[List[str]] = None
    ) -> str:
        """
        Add a new change entry to the changelog.

        Args:
            version: Version number (e.g., "1.0.1")
            change_type: Type of change (bugfix, enhancement, feature, breaking_change, deprecation, security)
            severity: Severity level (critical, major, minor, patch)
            title: Short title of the change
            description: Detailed description
            files: List of files affected
            reason: Why this change was made
            impact: What impact this has on users/system
            breaking: Whether this is a breaking change
            migration: Migration guide (if breaking)
            date: Date of change (defaults to today)
            summary: Version summary (for new versions)
            contributors: List of contributors (defaults to empty list)

        Returns:
            Change ID that was assigned

        Raises:
            ValueError: If parameters are invalid
            IOError: If changelog cannot be updated
        """
        # Validate inputs using enums (QUA-003)
        valid_types = [t.value for t in ChangeType]
        if change_type not in valid_types:
            raise ValueError(f"Invalid change_type. Must be one of: {valid_types}")

        valid_severities = [s.value for s in Severity]
        if severity not in valid_severities:
            raise ValueError(f"Invalid severity. Must be one of: {valid_severities}")

        if not files:
            raise ValueError("Must specify at least one file")

        # Read current changelog
        data = self.read_changelog()

        # Generate change ID
        change_id = self.get_next_change_id()

        # Use today's date if not specified
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Create change object
        change = {
            "id": change_id,
            "type": change_type,
            "severity": severity,
            "title": title,
            "description": description,
            "files": files,
            "reason": reason,
            "impact": impact,
            "breaking": breaking
        }

        if migration:
            change["migration"] = migration

        # Find or create version entry
        version_entry = None
        for entry in data['entries']:
            if entry['version'] == version:
                version_entry = entry
                break

        if version_entry is None:
            # Create new version entry
            version_entry = {
                "version": version,
                "date": date,
                "summary": summary or f"Version {version} changes",
                "changes": [],
                "contributors": contributors or []
            }
            # Insert at beginning (newest first)
            data['entries'].insert(0, version_entry)
        else:
            # Update contributors if provided
            if contributors:
                existing_contributors = set(version_entry.get('contributors', []))
                existing_contributors.update(contributors)
                version_entry['contributors'] = sorted(list(existing_contributors))

        # Add change to version entry
        version_entry['changes'].append(change)

        # Update current_version if this is newer
        if version > data['current_version']:
            data['current_version'] = version

        # Write back to file
        self.write_changelog(data)

        return change_id

    def get_version_changes(self, version: str) -> Optional[VersionEntryDict]:
        """
        Get all changes for a specific version.

        Args:
            version: Version number to retrieve

        Returns:
            Version entry dict or None if not found
        """
        data = self.read_changelog()
        for entry in data['entries']:
            if entry['version'] == version:
                return entry
        return None

    def get_changes_by_type(self, change_type: str) -> List[ChangeDict]:
        """
        Get all changes of a specific type across all versions.

        Args:
            change_type: Type to filter by

        Returns:
            List of change entries matching the type
        """
        data = self.read_changelog()
        results = []

        for entry in data['entries']:
            for change in entry['changes']:
                if change['type'] == change_type:
                    # Include version context
                    change_with_context = change.copy()
                    change_with_context['version'] = entry['version']
                    change_with_context['date'] = entry['date']
                    results.append(change_with_context)

        return results

    def get_breaking_changes(self) -> List[ChangeDict]:
        """
        Get all breaking changes across all versions.

        Returns:
            List of breaking changes with version context
        """
        data = self.read_changelog()
        results = []

        for entry in data['entries']:
            for change in entry['changes']:
                if change.get('breaking', False):
                    change_with_context = change.copy()
                    change_with_context['version'] = entry['version']
                    change_with_context['date'] = entry['date']
                    results.append(change_with_context)

        return results
