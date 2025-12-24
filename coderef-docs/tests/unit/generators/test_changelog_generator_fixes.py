"""
Unit tests for changelog_generator.py fixes (IMPL-001, IMPL-002, IMPL-003).

Tests cover:
- TEST-001: Semantic version comparison (IMPL-001)
- TEST-002: Migration validation for breaking changes (IMPL-002)
- TEST-003: Duplicate detection (IMPL-003)
"""

import pytest
import json
import tempfile
from pathlib import Path
from packaging.version import Version

from generators.changelog_generator import ChangelogGenerator


@pytest.fixture
def temp_changelog_dir():
    """Create a temporary directory with a valid CHANGELOG.json."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create CHANGELOG.json
        changelog_data = {
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
                            "severity": "minor",
                            "title": "Initial implementation",
                            "description": "First version of the tool",
                            "files": ["src/main.py"],
                            "reason": "Project kickoff",
                            "impact": "New tool released",
                            "breaking": False
                        }
                    ],
                    "contributors": ["test-user"]
                }
            ]
        }

        changelog_file = tmpdir_path / "CHANGELOG.json"
        with open(changelog_file, 'w') as f:
            json.dump(changelog_data, f)

        yield tmpdir_path


class TestSemanticVersionComparison:
    """TEST-001: Semantic version comparison fixes (IMPL-001)."""

    def test_simple_version_comparison(self):
        """Test simple version comparisons work correctly."""
        assert Version("1.0.0") < Version("2.0.0")
        assert Version("1.0.0") < Version("1.1.0")
        assert Version("1.0.0") < Version("1.0.1")

    def test_major_version_difference(self):
        """Test major version differences."""
        assert Version("2.0.0") > Version("1.9.9")
        assert Version("10.0.0") > Version("9.9.9")

    def test_double_digit_versions(self):
        """Test double-digit version numbers (the bug case)."""
        # This was the bug: string comparison "2.0.0" < "10.0.0" returns False
        # With Version objects, it correctly returns True
        assert Version("2.0.0") < Version("10.0.0")
        assert Version("2.10.0") < Version("2.100.0")
        assert Version("2.1.0") < Version("2.10.0")

    def test_version_comparison_in_changelog_update(self, temp_changelog_dir):
        """Test that semantic version comparison works in actual changelog update."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        # Add a version 10.0.0 (should update current_version since 10.0.0 > 1.0.0)
        generator.add_change(
            version="10.0.0",
            change_type="feature",
            severity="major",
            title="Major release",
            description="Significant changes",
            files=["src/main.py"],
            reason="Major update",
            impact="Breaking changes",
            breaking=False
        )

        # Verify current_version was updated
        data = generator.read_changelog()
        assert data["current_version"] == "10.0.0"

    def test_version_comparison_with_existing_version(self, temp_changelog_dir):
        """Test that newer version updates current_version."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        # Add version 2.0.0 (should update since 2.0.0 > 1.0.0)
        generator.add_change(
            version="2.0.0",
            change_type="feature",
            severity="minor",
            title="Version 2.0",
            description="Second major version",
            files=["src/main.py"],
            reason="Feature release",
            impact="New features"
        )

        data = generator.read_changelog()
        assert data["current_version"] == "2.0.0"

    def test_old_version_does_not_update_current(self, temp_changelog_dir):
        """Test that older version does NOT update current_version."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        # Try to add version 0.5.0 (should NOT update since 0.5.0 < 1.0.0)
        generator.add_change(
            version="0.5.0",
            change_type="feature",
            severity="patch",
            title="Old version",
            description="Backport fix",
            files=["src/old.py"],
            reason="Legacy support",
            impact="Old version updated"
        )

        data = generator.read_changelog()
        # current_version should still be 1.0.0
        assert data["current_version"] == "1.0.0"


class TestMigrationValidation:
    """TEST-002: Migration validation for breaking changes (IMPL-002)."""

    def test_breaking_without_migration_raises_error(self, temp_changelog_dir):
        """Test that breaking=true without migration guide raises ValueError."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        with pytest.raises(ValueError, match="Migration guide required"):
            generator.add_change(
                version="2.0.0",
                change_type="breaking_change",
                severity="major",
                title="Breaking API change",
                description="Removed deprecated endpoint",
                files=["src/api.py"],
                reason="Cleanup",
                impact="API compatibility broken",
                breaking=True,
                migration=None  # MISSING - should raise error
            )

    def test_breaking_with_migration_succeeds(self, temp_changelog_dir):
        """Test that breaking=true WITH migration guide succeeds."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        change_id = generator.add_change(
            version="2.0.0",
            change_type="breaking_change",
            severity="major",
            title="Breaking API change",
            description="Removed deprecated endpoint",
            files=["src/api.py"],
            reason="Cleanup",
            impact="API compatibility broken",
            breaking=True,
            migration="Update client to use new /v2/endpoint instead of /old/endpoint"
        )

        assert change_id.startswith("change-")

        # Verify entry was created
        data = generator.read_changelog()
        changes = data["entries"][0]["changes"]
        breaking_change = next(c for c in changes if c["title"] == "Breaking API change")
        assert breaking_change["breaking"] is True
        assert "Update client" in breaking_change["migration"]

    def test_non_breaking_with_migration_succeeds(self, temp_changelog_dir):
        """Test that non-breaking changes CAN have migration guide (optional)."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        change_id = generator.add_change(
            version="1.1.0",
            change_type="feature",
            severity="minor",
            title="Optional deprecation notice",
            description="Feature with optional migration",
            files=["src/main.py"],
            reason="New feature",
            impact="Users can migrate",
            breaking=False,
            migration="Optional: Consider using new feature instead"
        )

        assert change_id.startswith("change-")

    def test_non_breaking_without_migration_succeeds(self, temp_changelog_dir):
        """Test that non-breaking changes don't require migration."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        change_id = generator.add_change(
            version="1.1.0",
            change_type="feature",
            severity="minor",
            title="New feature",
            description="Non-breaking feature addition",
            files=["src/main.py"],
            reason="User request",
            impact="New functionality available",
            breaking=False,
            migration=None  # OK - not required for non-breaking
        )

        assert change_id.startswith("change-")


class TestDuplicateDetection:
    """TEST-003: Duplicate detection (IMPL-003)."""

    def test_exact_duplicate_detected(self, temp_changelog_dir):
        """Test that exact duplicates (same version + title) are detected."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        # Add first entry
        change_id_1 = generator.add_change(
            version="2.0.0",
            change_type="feature",
            severity="minor",
            title="New feature",
            description="Feature description",
            files=["src/main.py"],
            reason="User request",
            impact="New functionality"
        )

        # Try to add exact duplicate (same version + title)
        change_id_2 = generator.add_change(
            version="2.0.0",
            change_type="feature",
            severity="minor",
            title="New feature",  # SAME TITLE
            description="Different description",  # Different content
            files=["src/other.py"],
            reason="Another reason",
            impact="Different impact"
        )

        # Should return same change_id (not create duplicate)
        assert change_id_1 == change_id_2

        # Verify only one entry exists
        data = generator.read_changelog()
        version_entry = next(e for e in data["entries"] if e["version"] == "2.0.0")
        matching_changes = [c for c in version_entry["changes"] if c["title"] == "New feature"]
        assert len(matching_changes) == 1

    def test_similar_titles_not_duplicates(self, temp_changelog_dir):
        """Test that similar but different titles are NOT considered duplicates."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        change_id_1 = generator.add_change(
            version="2.0.0",
            change_type="feature",
            severity="minor",
            title="New feature",
            description="Feature description",
            files=["src/main.py"],
            reason="User request",
            impact="New functionality"
        )

        change_id_2 = generator.add_change(
            version="2.0.0",
            change_type="feature",
            severity="minor",
            title="New feature improved",  # DIFFERENT TITLE
            description="Similar but different",
            files=["src/main.py"],
            reason="Enhancement",
            impact="Better functionality"
        )

        # Should create new entry (different titles)
        assert change_id_1 != change_id_2

    def test_same_title_different_versions_not_duplicates(self, temp_changelog_dir):
        """Test that same title in different versions are NOT duplicates."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        change_id_1 = generator.add_change(
            version="1.5.0",
            change_type="feature",
            severity="minor",
            title="New feature",
            description="Feature description",
            files=["src/main.py"],
            reason="User request",
            impact="New functionality"
        )

        change_id_2 = generator.add_change(
            version="2.0.0",  # DIFFERENT VERSION
            change_type="feature",
            severity="minor",
            title="New feature",  # SAME TITLE
            description="Feature description",
            files=["src/main.py"],
            reason="User request",
            impact="New functionality"
        )

        # Should create new entry (different versions)
        assert change_id_1 != change_id_2

    def test_duplicate_returns_existing_change_id(self, temp_changelog_dir):
        """Test that duplicate detection returns the existing change ID."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        # Add entry
        original_id = generator.add_change(
            version="2.0.0",
            change_type="feature",
            severity="minor",
            title="Feature X",
            description="Description",
            files=["src/main.py"],
            reason="Reason",
            impact="Impact"
        )

        # Add duplicate
        duplicate_id = generator.add_change(
            version="2.0.0",
            change_type="enhancement",  # Different type
            severity="patch",  # Different severity
            title="Feature X",  # SAME TITLE
            description="Different description",
            files=["src/other.py"],  # Different files
            reason="Different reason",
            impact="Different impact"
        )

        # Should return original ID
        assert original_id == duplicate_id

        # Verify change still has original properties (not overwritten)
        data = generator.read_changelog()
        version_entry = next(e for e in data["entries"] if e["version"] == "2.0.0")
        feature_x = next(c for c in version_entry["changes"] if c["title"] == "Feature X")
        assert feature_x["type"] == "feature"  # Not "enhancement"
        assert feature_x["severity"] == "minor"  # Not "patch"


class TestBackwardCompatibility:
    """TEST-005: Backward compatibility with existing changelog format."""

    def test_existing_changelog_entries_readable(self, temp_changelog_dir):
        """Test that existing changelog entries without metadata are readable."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        # Read existing entry (created in fixture)
        data = generator.read_changelog()
        assert len(data["entries"]) > 0

        existing_change = data["entries"][0]["changes"][0]
        assert existing_change["id"] == "change-001"
        assert existing_change["type"] == "feature"
        assert existing_change["title"] == "Initial implementation"

        # Verify no metadata fields in old entries
        assert "auto_detected" not in existing_change
        assert "agent_confirmed" not in existing_change
        assert "recorded_at" not in existing_change

    def test_add_with_metadata_to_existing_changelog(self, temp_changelog_dir):
        """Test adding new entries with metadata to existing changelog."""
        generator = ChangelogGenerator(temp_changelog_dir / "CHANGELOG.json")

        # Add entry WITH metadata
        change_id = generator.add_change(
            version="2.0.0",
            change_type="feature",
            severity="minor",
            title="New feature with metadata",
            description="Entry with agentic metadata",
            files=["src/main.py"],
            reason="Test metadata",
            impact="Testing",
            auto_detected={
                "files_from": "git diff --staged",
                "type_from": "commit msg: 'feat(...)'",
                "severity_from": "scope: 2 files = minor"
            },
            agent_confirmed=True,
            recorded_at="2025-12-23T18:32:15Z"
        )

        # Verify metadata was stored
        data = generator.read_changelog()
        new_entry = next(e for e in data["entries"] if e["version"] == "2.0.0")
        new_change = next(c for c in new_entry["changes"] if c["title"] == "New feature with metadata")

        assert "auto_detected" in new_change
        assert new_change["auto_detected"]["files_from"] == "git diff --staged"
        assert new_change["agent_confirmed"] is True
        assert new_change["recorded_at"] == "2025-12-23T18:32:15Z"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
