"""
Test suite for csv_manager.py

Tests CSV automation utilities for Phase 3 Task 2.
"""

import pytest
from pathlib import Path
import csv
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from csv_manager import (
    add_csv_entry,
    update_csv_status,
    check_csv_exists,
    find_csv_entry,
    get_csv_stats,
    CSV_PATH
)


@pytest.fixture
def backup_csv():
    """Backup and restore CSV for tests"""
    import shutil

    backup_path = CSV_PATH.parent / f"{CSV_PATH.stem}.test_backup{CSV_PATH.suffix}"

    # Backup
    if CSV_PATH.exists():
        shutil.copy2(CSV_PATH, backup_path)

    yield

    # Restore
    if backup_path.exists():
        shutil.copy2(backup_path, CSV_PATH)
        backup_path.unlink()


class TestCSVManager:
    """Test CSV manager functions"""

    def test_csv_path_exists(self):
        """Test that CSV path is accessible"""
        assert CSV_PATH.exists(), f"CSV not found at {CSV_PATH}"

    def test_check_csv_exists(self):
        """Test checking if resource exists in CSV"""
        # Should find existing resource
        exists = check_csv_exists("/create-workorder", "coderef-workflow")
        assert exists, "Expected to find /create-workorder in CSV"

        # Should not find non-existent resource
        not_exists = check_csv_exists("non-existent-resource-xyz")
        assert not not_exists, "Should not find non-existent resource"

    def test_find_csv_entry(self):
        """Test finding specific CSV entry"""
        entry = find_csv_entry("/create-workorder", "coderef-workflow")

        assert entry is not None, "Expected to find /create-workorder"
        assert entry['Type'] == 'Command', "Expected type=Command"
        assert entry['Server'] == 'coderef-workflow', "Expected server=coderef-workflow"

    def test_get_csv_stats(self):
        """Test getting CSV statistics"""
        stats = get_csv_stats()

        assert 'total' in stats, "Stats should have total count"
        assert stats['total'] > 0, "Should have resources in CSV"
        assert 'by_type' in stats, "Stats should have type breakdown"
        assert 'by_server' in stats, "Stats should have server breakdown"
        assert 'by_status' in stats, "Stats should have status breakdown"

        # Check specific counts
        assert 'Tool' in stats['by_type'], "Should have Tool type"
        assert 'Command' in stats['by_type'], "Should have Command type"
        assert 'coderef-workflow' in stats['by_server'], "Should have coderef-workflow server"

    def test_update_csv_status_requires_backup(self, backup_csv):
        """Test updating CSV status (requires backup)"""
        # Find a coderef-workflow resource to update
        entry = find_csv_entry("/archive-feature", "coderef-workflow")

        if entry:
            original_status = entry['Status']

            # Update to test status
            updated_count = update_csv_status("/archive-feature", "test_status", "coderef-workflow")

            assert updated_count == 1, "Should update 1 entry"

            # Verify update
            updated_entry = find_csv_entry("/archive-feature", "coderef-workflow")
            assert updated_entry['Status'] == "test_status", "Status should be updated"

            # Restore will happen via fixture

    def test_add_csv_entry_requires_backup(self, backup_csv):
        """Test adding new CSV entry (requires backup)"""
        test_resource_name = f"/test-resource-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Add entry
        entry = add_csv_entry(
            type="Command",
            server="coderef-workflow",
            category="Testing",
            name=test_resource_name,
            description="Test resource for unit tests",
            status="active",
            path="tests/test_resource.md"
        )

        assert entry['Name'] == test_resource_name, "Entry should have correct name"
        assert entry['Type'] == "Command", "Entry should have correct type"

        # Verify it was added
        exists = check_csv_exists(test_resource_name, "coderef-workflow")
        assert exists, "Resource should exist in CSV after adding"

        # Test duplicate prevention
        with pytest.raises(ValueError, match="Entry already exists"):
            add_csv_entry(
                type="Command",
                server="coderef-workflow",
                category="Testing",
                name=test_resource_name,
                description="Duplicate",
                status="active"
            )

    def test_csv_entry_validation(self):
        """Test that CSV entry validation works"""
        with pytest.raises(ValueError, match="Missing required fields"):
            add_csv_entry(
                type="Command",
                server="",  # Missing server
                category="Testing",
                name="/test",
                description="Test"
            )

    def test_thread_safety(self):
        """Test thread-safe operations"""
        import threading

        results = []

        def check_resource():
            exists = check_csv_exists("/create-workorder", "coderef-workflow")
            results.append(exists)

        # Run 10 concurrent checks
        threads = [threading.Thread(target=check_resource) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed
        assert len(results) == 10, "All threads should complete"
        assert all(results), "All checks should find resource"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
