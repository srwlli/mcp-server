"""
Unit tests for ChangelogGenerator

Tests the changelog generation including:
- Initialization and schema loading
- CHANGELOG.json read/write operations
- Schema validation (SEC-002)
- Change ID generation
- Change entry management
- Query operations

Part of WO-COMPREHENSIVE-TESTING-SUITE-002.
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from generators.changelog_generator import ChangelogGenerator


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def changelog_dir(tmp_path):
    """Create a changelog directory with valid files."""
    changelog_dir = tmp_path / "coderef" / "changelog"
    changelog_dir.mkdir(parents=True)
    return changelog_dir


@pytest.fixture
def valid_schema(changelog_dir):
    """Create a valid JSON schema file."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["project_name", "current_version", "entries"],
        "properties": {
            "project_name": {"type": "string"},
            "current_version": {"type": "string"},
            "entries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["version", "date", "changes"],
                    "properties": {
                        "version": {"type": "string"},
                        "date": {"type": "string"},
                        "summary": {"type": "string"},
                        "changes": {"type": "array"},
                        "contributors": {"type": "array"}
                    }
                }
            }
        }
    }
    schema_path = changelog_dir / "schema.json"
    schema_path.write_text(json.dumps(schema, indent=2))
    return schema_path


@pytest.fixture
def valid_changelog(changelog_dir, valid_schema):
    """Create a valid CHANGELOG.json file."""
    changelog = {
        "project_name": "test-project",
        "current_version": "1.0.0",
        "entries": [
            {
                "version": "1.0.0",
                "date": "2025-01-01",
                "summary": "Initial release",
                "changes": [
                    {
                        "id": "change-001",
                        "type": "feature",
                        "severity": "major",
                        "title": "Initial feature",
                        "description": "First feature added",
                        "files": ["src/main.py"],
                        "reason": "Project initialization",
                        "impact": "New project",
                        "breaking": False
                    }
                ],
                "contributors": ["Developer A"]
            }
        ]
    }
    changelog_path = changelog_dir / "CHANGELOG.json"
    changelog_path.write_text(json.dumps(changelog, indent=2))
    return changelog_path


@pytest.fixture
def changelog_generator(valid_changelog, valid_schema):
    """Create a ChangelogGenerator instance with valid files."""
    return ChangelogGenerator(valid_changelog)


@pytest.fixture
def empty_changelog(changelog_dir, valid_schema):
    """Create a changelog with no entries."""
    changelog = {
        "project_name": "empty-project",
        "current_version": "0.0.0",
        "entries": []
    }
    changelog_path = changelog_dir / "CHANGELOG.json"
    changelog_path.write_text(json.dumps(changelog, indent=2))
    return changelog_path


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestChangelogGeneratorInit:
    """Test ChangelogGenerator initialization."""

    def test_init_with_valid_path(self, valid_changelog):
        """Should initialize with valid changelog path."""
        gen = ChangelogGenerator(valid_changelog)
        assert gen.changelog_path == valid_changelog
        assert gen.schema_path == valid_changelog.parent / "schema.json"

    def test_init_loads_schema(self, valid_changelog, valid_schema):
        """Should load schema during initialization."""
        gen = ChangelogGenerator(valid_changelog)
        assert gen.schema is not None
        assert "$schema" in gen.schema

    def test_init_without_schema(self, changelog_dir):
        """Should handle missing schema file gracefully."""
        changelog_path = changelog_dir / "CHANGELOG.json"
        changelog_path.write_text('{"project_name": "test", "current_version": "1.0.0", "entries": []}')

        gen = ChangelogGenerator(changelog_path)
        assert gen.schema is None

    def test_init_stores_paths_as_path_objects(self, valid_changelog):
        """Paths should be Path objects."""
        gen = ChangelogGenerator(valid_changelog)
        assert isinstance(gen.changelog_path, Path)
        assert isinstance(gen.schema_path, Path)


# ============================================================================
# SCHEMA LOADING TESTS
# ============================================================================

class TestLoadSchema:
    """Test _load_schema() method."""

    def test_load_schema_returns_dict(self, valid_changelog, valid_schema):
        """Should return dictionary for valid schema."""
        gen = ChangelogGenerator(valid_changelog)
        assert isinstance(gen.schema, dict)

    def test_load_schema_missing_file(self, changelog_dir):
        """Should return None when schema file doesn't exist."""
        changelog_path = changelog_dir / "CHANGELOG.json"
        changelog_path.write_text('{}')

        gen = ChangelogGenerator(changelog_path)
        # Schema file doesn't exist
        assert gen.schema is None

    def test_load_schema_malformed_json(self, changelog_dir):
        """Should raise JSONDecodeError for malformed schema."""
        changelog_path = changelog_dir / "CHANGELOG.json"
        changelog_path.write_text('{}')

        schema_path = changelog_dir / "schema.json"
        schema_path.write_text('{invalid json}')

        with pytest.raises(json.JSONDecodeError):
            ChangelogGenerator(changelog_path)


# ============================================================================
# VALIDATE CHANGELOG TESTS
# ============================================================================

class TestValidateChangelog:
    """Test validate_changelog() method."""

    def test_validate_valid_data(self, changelog_generator):
        """Should not raise for valid data."""
        valid_data = {
            "project_name": "test",
            "current_version": "1.0.0",
            "entries": []
        }
        # Should not raise
        changelog_generator.validate_changelog(valid_data)

    def test_validate_invalid_data(self, changelog_generator):
        """Should raise ValidationError for invalid data."""
        import jsonschema
        invalid_data = {
            "project_name": 123,  # Should be string
            "current_version": "1.0.0",
            "entries": []
        }
        with pytest.raises(jsonschema.ValidationError):
            changelog_generator.validate_changelog(invalid_data)

    def test_validate_missing_required_field(self, changelog_generator):
        """Should raise ValidationError for missing required fields."""
        import jsonschema
        invalid_data = {
            "project_name": "test"
            # Missing current_version and entries
        }
        with pytest.raises(jsonschema.ValidationError):
            changelog_generator.validate_changelog(invalid_data)

    def test_validate_skipped_without_schema(self, changelog_dir):
        """Should skip validation when no schema is loaded."""
        changelog_path = changelog_dir / "CHANGELOG.json"
        changelog_path.write_text('{}')

        gen = ChangelogGenerator(changelog_path)
        # Should not raise even for invalid data
        gen.validate_changelog({"anything": "goes"})


# ============================================================================
# READ CHANGELOG TESTS
# ============================================================================

class TestReadChangelog:
    """Test read_changelog() method."""

    def test_read_returns_dict(self, changelog_generator):
        """Should return dictionary."""
        data = changelog_generator.read_changelog()
        assert isinstance(data, dict)

    def test_read_contains_expected_keys(self, changelog_generator):
        """Should contain project_name, current_version, entries."""
        data = changelog_generator.read_changelog()
        assert "project_name" in data
        assert "current_version" in data
        assert "entries" in data

    def test_read_missing_file(self, changelog_dir, valid_schema):
        """Should raise FileNotFoundError for missing file."""
        missing_path = changelog_dir / "NONEXISTENT.json"
        gen = ChangelogGenerator(missing_path)

        with pytest.raises(FileNotFoundError):
            gen.read_changelog()

    def test_read_malformed_json(self, changelog_dir, valid_schema):
        """Should raise JSONDecodeError for malformed JSON."""
        changelog_path = changelog_dir / "CHANGELOG.json"
        changelog_path.write_text('{not valid json')

        gen = ChangelogGenerator(changelog_path)
        with pytest.raises(json.JSONDecodeError):
            gen.read_changelog()

    def test_read_validates_against_schema(self, changelog_dir, valid_schema):
        """Should validate data against schema on read."""
        import jsonschema
        # Create changelog that doesn't match schema
        changelog_path = changelog_dir / "CHANGELOG.json"
        changelog_path.write_text('{"invalid": "data"}')

        gen = ChangelogGenerator(changelog_path)
        with pytest.raises(jsonschema.ValidationError):
            gen.read_changelog()


# ============================================================================
# WRITE CHANGELOG TESTS
# ============================================================================

class TestWriteChangelog:
    """Test write_changelog() method."""

    def test_write_creates_file(self, changelog_generator):
        """Should write data to file."""
        data = changelog_generator.read_changelog()
        data["project_name"] = "updated-project"

        changelog_generator.write_changelog(data)

        # Verify write
        with open(changelog_generator.changelog_path) as f:
            written = json.load(f)
        assert written["project_name"] == "updated-project"

    def test_write_formats_json(self, changelog_generator):
        """Should write formatted JSON with indent."""
        data = changelog_generator.read_changelog()
        changelog_generator.write_changelog(data)

        content = changelog_generator.changelog_path.read_text()
        # Should be indented (contains newlines within JSON)
        assert '\n  ' in content

    def test_write_adds_trailing_newline(self, changelog_generator):
        """Should add trailing newline."""
        data = changelog_generator.read_changelog()
        changelog_generator.write_changelog(data)

        content = changelog_generator.changelog_path.read_text()
        assert content.endswith('\n')

    def test_write_validates_before_writing(self, changelog_generator):
        """Should validate data before writing."""
        import jsonschema
        invalid_data = {
            "invalid": "data"
        }
        with pytest.raises(jsonschema.ValidationError):
            changelog_generator.write_changelog(invalid_data)

    def test_write_preserves_unicode(self, changelog_generator):
        """Should preserve unicode characters."""
        data = changelog_generator.read_changelog()
        data["project_name"] = "test-unicode-\u00e9\u00e0\u00fc"

        changelog_generator.write_changelog(data)

        with open(changelog_generator.changelog_path, encoding='utf-8') as f:
            written = json.load(f)
        assert written["project_name"] == "test-unicode-\u00e9\u00e0\u00fc"


# ============================================================================
# GET NEXT CHANGE ID TESTS
# ============================================================================

class TestGetNextChangeId:
    """Test get_next_change_id() method."""

    def test_generates_id_format(self, changelog_generator):
        """Should generate IDs in 'change-NNN' format."""
        change_id = changelog_generator.get_next_change_id()
        assert change_id.startswith('change-')
        assert len(change_id) == 10  # 'change-NNN'

    def test_increments_from_existing(self, changelog_generator):
        """Should increment from highest existing ID."""
        # Existing changelog has change-001
        change_id = changelog_generator.get_next_change_id()
        assert change_id == 'change-002'

    def test_starts_at_001_for_empty(self, empty_changelog, valid_schema):
        """Should start at 001 for empty changelog."""
        gen = ChangelogGenerator(empty_changelog)
        change_id = gen.get_next_change_id()
        assert change_id == 'change-001'

    def test_handles_multiple_entries(self, changelog_dir, valid_schema):
        """Should find max ID across all entries."""
        changelog = {
            "project_name": "test",
            "current_version": "2.0.0",
            "entries": [
                {
                    "version": "2.0.0",
                    "date": "2025-02-01",
                    "changes": [{"id": "change-010"}],
                    "contributors": []
                },
                {
                    "version": "1.0.0",
                    "date": "2025-01-01",
                    "changes": [{"id": "change-005"}, {"id": "change-006"}],
                    "contributors": []
                }
            ]
        }
        changelog_path = changelog_dir / "CHANGELOG.json"
        changelog_path.write_text(json.dumps(changelog))

        gen = ChangelogGenerator(changelog_path)
        change_id = gen.get_next_change_id()
        assert change_id == 'change-011'

    def test_handles_malformed_ids(self, changelog_dir, valid_schema):
        """Should handle malformed change IDs gracefully."""
        changelog = {
            "project_name": "test",
            "current_version": "1.0.0",
            "entries": [
                {
                    "version": "1.0.0",
                    "date": "2025-01-01",
                    "changes": [
                        {"id": "change-005"},
                        {"id": "invalid-id"},
                        {"id": "change-abc"},  # Non-numeric
                        {"id": "change-003"}
                    ],
                    "contributors": []
                }
            ]
        }
        changelog_path = changelog_dir / "CHANGELOG.json"
        changelog_path.write_text(json.dumps(changelog))

        gen = ChangelogGenerator(changelog_path)
        change_id = gen.get_next_change_id()
        assert change_id == 'change-006'


# ============================================================================
# ADD CHANGE TESTS
# ============================================================================

class TestAddChange:
    """Test add_change() method."""

    def test_add_change_returns_id(self, changelog_generator):
        """Should return assigned change ID."""
        change_id = changelog_generator.add_change(
            version="1.1.0",
            change_type="feature",
            severity="minor",
            title="New feature",
            description="Added new feature",
            files=["src/new.py"],
            reason="User request",
            impact="New capability"
        )
        assert change_id.startswith('change-')

    def test_add_change_to_existing_version(self, changelog_generator):
        """Should add to existing version entry."""
        changelog_generator.add_change(
            version="1.0.0",  # Existing version
            change_type="bugfix",
            severity="minor",
            title="Bug fix",
            description="Fixed bug",
            files=["src/fix.py"],
            reason="Bug report",
            impact="Bug resolved"
        )

        data = changelog_generator.read_changelog()
        version_entry = next(e for e in data['entries'] if e['version'] == "1.0.0")
        assert len(version_entry['changes']) == 2

    def test_add_change_creates_new_version(self, changelog_generator):
        """Should create new version entry if version doesn't exist."""
        changelog_generator.add_change(
            version="2.0.0",  # New version
            change_type="feature",
            severity="major",
            title="Major feature",
            description="Added major feature",
            files=["src/major.py"],
            reason="Feature request",
            impact="Major improvement"
        )

        data = changelog_generator.read_changelog()
        versions = [e['version'] for e in data['entries']]
        assert "2.0.0" in versions

    def test_add_change_updates_current_version(self, changelog_generator):
        """Should update current_version if new version is higher."""
        changelog_generator.add_change(
            version="2.0.0",
            change_type="feature",
            severity="major",
            title="New version",
            description="New version release",
            files=["src/new.py"],
            reason="Update",
            impact="New version"
        )

        data = changelog_generator.read_changelog()
        assert data['current_version'] == "2.0.0"

    def test_add_change_validates_change_type(self, changelog_generator):
        """Should reject invalid change_type."""
        with pytest.raises(ValueError, match="Invalid change_type"):
            changelog_generator.add_change(
                version="1.1.0",
                change_type="invalid_type",  # Invalid
                severity="minor",
                title="Test",
                description="Test",
                files=["test.py"],
                reason="Test",
                impact="Test"
            )

    def test_add_change_validates_severity(self, changelog_generator):
        """Should reject invalid severity."""
        with pytest.raises(ValueError, match="Invalid severity"):
            changelog_generator.add_change(
                version="1.1.0",
                change_type="feature",
                severity="invalid_severity",  # Invalid
                title="Test",
                description="Test",
                files=["test.py"],
                reason="Test",
                impact="Test"
            )

    def test_add_change_requires_files(self, changelog_generator):
        """Should require at least one file."""
        with pytest.raises(ValueError, match="at least one file"):
            changelog_generator.add_change(
                version="1.1.0",
                change_type="feature",
                severity="minor",
                title="Test",
                description="Test",
                files=[],  # Empty
                reason="Test",
                impact="Test"
            )

    def test_add_change_uses_today_as_default_date(self, changelog_generator):
        """Should use today's date when not specified."""
        changelog_generator.add_change(
            version="1.1.0",
            change_type="feature",
            severity="minor",
            title="Test",
            description="Test",
            files=["test.py"],
            reason="Test",
            impact="Test"
        )

        data = changelog_generator.read_changelog()
        version_entry = next(e for e in data['entries'] if e['version'] == "1.1.0")
        assert version_entry['date'] == datetime.now().strftime("%Y-%m-%d")

    def test_add_change_with_breaking_flag(self, changelog_generator):
        """Should handle breaking flag."""
        changelog_generator.add_change(
            version="2.0.0",
            change_type="breaking_change",
            severity="critical",
            title="Breaking change",
            description="This breaks things",
            files=["src/api.py"],
            reason="Major refactor",
            impact="Breaks existing code",
            breaking=True,
            migration="Update imports to new format"
        )

        data = changelog_generator.read_changelog()
        version_entry = next(e for e in data['entries'] if e['version'] == "2.0.0")
        change = version_entry['changes'][0]
        assert change['breaking'] is True
        assert change['migration'] == "Update imports to new format"

    def test_add_change_with_contributors(self, changelog_generator):
        """Should handle contributors list."""
        changelog_generator.add_change(
            version="1.1.0",
            change_type="feature",
            severity="minor",
            title="Contributed feature",
            description="Community contribution",
            files=["src/contrib.py"],
            reason="Community PR",
            impact="New feature",
            contributors=["Contributor A", "Contributor B"]
        )

        data = changelog_generator.read_changelog()
        version_entry = next(e for e in data['entries'] if e['version'] == "1.1.0")
        assert "Contributor A" in version_entry['contributors']
        assert "Contributor B" in version_entry['contributors']

    def test_add_change_merges_contributors(self, changelog_generator):
        """Should merge contributors when adding to existing version."""
        # First change with contributor A
        changelog_generator.add_change(
            version="1.0.0",  # Existing version
            change_type="bugfix",
            severity="minor",
            title="Fix 1",
            description="First fix",
            files=["fix1.py"],
            reason="Bug",
            impact="Fixed",
            contributors=["New Contributor"]
        )

        data = changelog_generator.read_changelog()
        version_entry = next(e for e in data['entries'] if e['version'] == "1.0.0")
        # Should have both original and new contributors
        assert "Developer A" in version_entry['contributors']
        assert "New Contributor" in version_entry['contributors']


class TestAddChangeValidTypes:
    """Test add_change() with all valid change types."""

    @pytest.mark.parametrize("change_type", [
        "bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"
    ])
    def test_accepts_valid_change_types(self, changelog_generator, change_type):
        """Should accept all valid change types."""
        change_id = changelog_generator.add_change(
            version="1.1.0",
            change_type=change_type,
            severity="minor",
            title=f"Test {change_type}",
            description="Test description",
            files=["test.py"],
            reason="Testing",
            impact="Test impact"
        )
        assert change_id is not None


class TestAddChangeValidSeverities:
    """Test add_change() with all valid severities."""

    @pytest.mark.parametrize("severity", [
        "critical", "major", "minor", "patch"
    ])
    def test_accepts_valid_severities(self, changelog_generator, severity):
        """Should accept all valid severities."""
        change_id = changelog_generator.add_change(
            version="1.1.0",
            change_type="feature",
            severity=severity,
            title=f"Test {severity}",
            description="Test description",
            files=["test.py"],
            reason="Testing",
            impact="Test impact"
        )
        assert change_id is not None


# ============================================================================
# GET VERSION CHANGES TESTS
# ============================================================================

class TestGetVersionChanges:
    """Test get_version_changes() method."""

    def test_returns_version_entry(self, changelog_generator):
        """Should return version entry for existing version."""
        result = changelog_generator.get_version_changes("1.0.0")
        assert result is not None
        assert result['version'] == "1.0.0"

    def test_returns_none_for_missing_version(self, changelog_generator):
        """Should return None for non-existent version."""
        result = changelog_generator.get_version_changes("99.99.99")
        assert result is None

    def test_includes_changes_array(self, changelog_generator):
        """Should include changes array in result."""
        result = changelog_generator.get_version_changes("1.0.0")
        assert 'changes' in result
        assert isinstance(result['changes'], list)

    def test_includes_metadata(self, changelog_generator):
        """Should include version metadata."""
        result = changelog_generator.get_version_changes("1.0.0")
        assert 'date' in result
        assert 'summary' in result
        assert 'contributors' in result


# ============================================================================
# GET CHANGES BY TYPE TESTS
# ============================================================================

class TestGetChangesByType:
    """Test get_changes_by_type() method."""

    def test_returns_matching_changes(self, changelog_generator):
        """Should return changes matching type."""
        result = changelog_generator.get_changes_by_type("feature")
        assert len(result) == 1
        assert result[0]['type'] == "feature"

    def test_returns_empty_for_no_matches(self, changelog_generator):
        """Should return empty list when no matches."""
        result = changelog_generator.get_changes_by_type("security")
        assert result == []

    def test_includes_version_context(self, changelog_generator):
        """Should include version and date in results."""
        result = changelog_generator.get_changes_by_type("feature")
        assert result[0]['version'] == "1.0.0"
        assert 'date' in result[0]

    def test_finds_across_multiple_versions(self, changelog_generator):
        """Should find changes across all versions."""
        # Add more features to different versions
        changelog_generator.add_change(
            version="2.0.0",
            change_type="feature",
            severity="major",
            title="Second feature",
            description="Another feature",
            files=["feature2.py"],
            reason="More features",
            impact="More capability"
        )

        result = changelog_generator.get_changes_by_type("feature")
        assert len(result) == 2
        versions = [r['version'] for r in result]
        assert "1.0.0" in versions
        assert "2.0.0" in versions


# ============================================================================
# GET BREAKING CHANGES TESTS
# ============================================================================

class TestGetBreakingChanges:
    """Test get_breaking_changes() method."""

    def test_returns_empty_when_no_breaking(self, changelog_generator):
        """Should return empty list when no breaking changes."""
        result = changelog_generator.get_breaking_changes()
        assert result == []

    def test_finds_breaking_changes(self, changelog_generator):
        """Should find breaking changes."""
        changelog_generator.add_change(
            version="2.0.0",
            change_type="breaking_change",
            severity="critical",
            title="Breaking API change",
            description="Changed API signature",
            files=["api.py"],
            reason="Better design",
            impact="Existing code will break",
            breaking=True,
            migration="Update code to use new_api() instead of old_api()"
        )

        result = changelog_generator.get_breaking_changes()
        assert len(result) == 1
        assert result[0]['breaking'] is True

    def test_includes_version_context_for_breaking(self, changelog_generator):
        """Should include version context in breaking changes."""
        changelog_generator.add_change(
            version="2.0.0",
            change_type="breaking_change",
            severity="critical",
            title="Breaking",
            description="Breaking change",
            files=["break.py"],
            reason="Necessary",
            impact="Breaks things",
            breaking=True,
            migration="See migration guide: https://docs.example.com/v2-upgrade"
        )

        result = changelog_generator.get_breaking_changes()
        assert result[0]['version'] == "2.0.0"
        assert 'date' in result[0]


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_empty_changelog(self, empty_changelog, valid_schema):
        """Should handle changelog with no entries."""
        gen = ChangelogGenerator(empty_changelog)
        data = gen.read_changelog()
        assert data['entries'] == []

    def test_handles_special_characters_in_strings(self, changelog_generator):
        """Should handle special characters in string fields."""
        change_id = changelog_generator.add_change(
            version="1.1.0",
            change_type="feature",
            severity="minor",
            title="Test \"quotes\" and 'apostrophes'",
            description="Description with\nnewlines\tand\ttabs",
            files=["src/special.py"],
            reason="Testing special chars: < > & \"",
            impact="No impact"
        )

        data = changelog_generator.read_changelog()
        version_entry = next(e for e in data['entries'] if e['version'] == "1.1.0")
        change = next(c for c in version_entry['changes'] if c['id'] == change_id)
        assert "\"quotes\"" in change['title']
        assert '\n' in change['description']

    def test_handles_long_file_lists(self, changelog_generator):
        """Should handle large file lists."""
        files = [f"src/module{i}/file{j}.py" for i in range(10) for j in range(10)]

        change_id = changelog_generator.add_change(
            version="1.1.0",
            change_type="feature",
            severity="major",
            title="Large change",
            description="Many files changed",
            files=files,
            reason="Refactor",
            impact="Widespread changes"
        )

        data = changelog_generator.read_changelog()
        version_entry = next(e for e in data['entries'] if e['version'] == "1.1.0")
        change = next(c for c in version_entry['changes'] if c['id'] == change_id)
        assert len(change['files']) == 100


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestChangelogGeneratorIntegration:
    """Test full workflows."""

    def test_complete_workflow(self, empty_changelog, valid_schema):
        """Test complete add-read-query workflow."""
        gen = ChangelogGenerator(empty_changelog)

        # Add initial release
        gen.add_change(
            version="1.0.0",
            change_type="feature",
            severity="major",
            title="Initial release",
            description="First release of the project",
            files=["src/main.py", "src/utils.py"],
            reason="Project launch",
            impact="New project available",
            contributors=["Developer A"]
        )

        # Add bug fix
        gen.add_change(
            version="1.0.1",
            change_type="bugfix",
            severity="patch",
            title="Fix startup bug",
            description="Fixed crash on startup",
            files=["src/main.py"],
            reason="Bug report #123",
            impact="Stable startup"
        )

        # Add breaking change
        gen.add_change(
            version="2.0.0",
            change_type="breaking_change",
            severity="critical",
            title="API redesign",
            description="Complete API overhaul",
            files=["src/api.py"],
            reason="Better architecture",
            impact="All clients must update",
            breaking=True,
            migration="See migration guide"
        )

        # Verify queries
        data = gen.read_changelog()
        assert data['current_version'] == "2.0.0"
        assert len(data['entries']) == 3

        # Query by type
        features = gen.get_changes_by_type("feature")
        assert len(features) == 1

        bugfixes = gen.get_changes_by_type("bugfix")
        assert len(bugfixes) == 1

        # Query breaking
        breaking = gen.get_breaking_changes()
        assert len(breaking) == 1
        assert breaking[0]['version'] == "2.0.0"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance characteristics."""

    def test_handles_large_changelog(self, changelog_dir, valid_schema):
        """Should handle large changelog efficiently."""
        import time

        # Create large changelog
        entries = []
        for v in range(100):
            changes = [
                {
                    "id": f"change-{v*10+c:04d}",
                    "type": "feature",
                    "severity": "minor",
                    "title": f"Change {v*10+c}",
                    "description": "Description",
                    "files": ["file.py"],
                    "reason": "Reason",
                    "impact": "Impact",
                    "breaking": False
                }
                for c in range(10)
            ]
            entries.append({
                "version": f"{v//10}.{v%10}.0",
                "date": "2025-01-01",
                "summary": f"Version {v//10}.{v%10}.0",
                "changes": changes,
                "contributors": []
            })

        changelog = {
            "project_name": "large-project",
            "current_version": "9.9.0",
            "entries": entries
        }
        changelog_path = changelog_dir / "CHANGELOG.json"
        changelog_path.write_text(json.dumps(changelog))

        gen = ChangelogGenerator(changelog_path)

        # Time read operation
        start = time.perf_counter()
        data = gen.read_changelog()
        read_time = time.perf_counter() - start
        assert read_time < 1.0, f"Read too slow: {read_time:.3f}s"

        # Time query operation
        start = time.perf_counter()
        gen.get_changes_by_type("feature")
        query_time = time.perf_counter() - start
        assert query_time < 0.5, f"Query too slow: {query_time:.3f}s"

        # Time add operation
        start = time.perf_counter()
        gen.add_change(
            version="10.0.0",
            change_type="feature",
            severity="major",
            title="New feature",
            description="Testing add performance",
            files=["new.py"],
            reason="Test",
            impact="Test"
        )
        add_time = time.perf_counter() - start
        assert add_time < 1.0, f"Add too slow: {add_time:.3f}s"
