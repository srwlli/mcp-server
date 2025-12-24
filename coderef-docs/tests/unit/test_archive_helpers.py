"""
Unit tests for archive helper functions (ARCHIVE-008).

Tests update_archive_index() and parse_deliverables_status() functions.
"""

import unittest
import sys
import json
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from handler_helpers import update_archive_index, parse_deliverables_status


class TestUpdateArchiveIndex(unittest.TestCase):
    """Test update_archive_index() function."""

    def setUp(self):
        """Create temporary directory for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_create_new_index(self):
        """Test creating index.json when it doesn't exist."""
        update_archive_index(
            self.project_path,
            'Test Feature',
            'test-feature',
            '2025-10-18T15:30:00+00:00'
        )

        index_path = self.project_path / 'coderef' / 'archived' / 'index.json'
        self.assertTrue(index_path.exists())

        # Verify content
        content = json.loads(index_path.read_text())
        self.assertEqual(content['total_archived'], 1)
        self.assertEqual(len(content['archived_features']), 1)
        self.assertEqual(content['archived_features'][0]['feature_name'], 'Test Feature')
        self.assertEqual(content['archived_features'][0]['folder_name'], 'test-feature')

    def test_append_to_existing_index(self):
        """Test appending to existing index.json."""
        # Create initial entry
        update_archive_index(
            self.project_path,
            'First Feature',
            'first-feature',
            '2025-10-18T15:00:00+00:00'
        )

        # Add second entry
        update_archive_index(
            self.project_path,
            'Second Feature',
            'second-feature',
            '2025-10-18T16:00:00+00:00'
        )

        index_path = self.project_path / 'coderef' / 'archived' / 'index.json'
        content = json.loads(index_path.read_text())

        self.assertEqual(content['total_archived'], 2)
        self.assertEqual(len(content['archived_features']), 2)
        self.assertEqual(content['archived_features'][0]['feature_name'], 'First Feature')
        self.assertEqual(content['archived_features'][1]['feature_name'], 'Second Feature')

    def test_update_timestamps(self):
        """Test that last_updated is updated correctly."""
        timestamp1 = '2025-10-18T15:00:00+00:00'
        timestamp2 = '2025-10-18T16:00:00+00:00'

        update_archive_index(self.project_path, 'Feature 1', 'feature-1', timestamp1)

        index_path = self.project_path / 'coderef' / 'archived' / 'index.json'
        content1 = json.loads(index_path.read_text())
        self.assertEqual(content1['last_updated'], timestamp1)

        # Add second entry with later timestamp
        update_archive_index(self.project_path, 'Feature 2', 'feature-2', timestamp2)

        content2 = json.loads(index_path.read_text())
        self.assertEqual(content2['last_updated'], timestamp2)

    def test_corrupted_index_raises_error(self):
        """Test that corrupted index.json raises ValueError."""
        # Create corrupted index.json
        archived_dir = self.project_path / 'coderef' / 'archived'
        archived_dir.mkdir(parents=True)
        index_path = archived_dir / 'index.json'
        index_path.write_text('{ invalid json')

        with self.assertRaises(ValueError) as context:
            update_archive_index(
                self.project_path,
                'Test Feature',
                'test-feature',
                '2025-10-18T15:30:00+00:00'
            )
        self.assertIn('Corrupted index.json', str(context.exception))

    def test_invalid_structure_raises_error(self):
        """Test that invalid index structure raises ValueError."""
        # Create index with wrong structure
        archived_dir = self.project_path / 'coderef' / 'archived'
        archived_dir.mkdir(parents=True)
        index_path = archived_dir / 'index.json'
        index_path.write_text(json.dumps({'archived_features': 'not an array'}))

        with self.assertRaises(ValueError) as context:
            update_archive_index(
                self.project_path,
                'Test Feature',
                'test-feature',
                '2025-10-18T15:30:00+00:00'
            )
        self.assertIn('must be an array', str(context.exception))

    def test_feature_name_formatting(self):
        """Test that feature names are preserved as-is."""
        update_archive_index(
            self.project_path,
            'Archive Feature Tool',  # Capitalized display name
            'archive-feature',       # Lowercase folder name
            '2025-10-18T15:30:00+00:00'
        )

        index_path = self.project_path / 'coderef' / 'archived' / 'index.json'
        content = json.loads(index_path.read_text())

        self.assertEqual(content['archived_features'][0]['feature_name'], 'Archive Feature Tool')
        self.assertEqual(content['archived_features'][0]['folder_name'], 'archive-feature')


class TestParseDeliverablesStatus(unittest.TestCase):
    """Test parse_deliverables_status() function."""

    def setUp(self):
        """Create temporary directory for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_complete_status(self):
        """Test parsing Complete status."""
        deliverables_path = self.temp_path / 'DELIVERABLES.md'
        deliverables_path.write_text('**Status**: ✅ Complete\n', encoding='utf-8')

        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'Complete')

    def test_in_progress_status(self):
        """Test parsing In Progress status."""
        deliverables_path = self.temp_path / 'DELIVERABLES.md'
        deliverables_path.write_text('**Status**: 🚧 In Progress\n', encoding='utf-8')

        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'In Progress')

    def test_not_started_status(self):
        """Test parsing Not Started status."""
        deliverables_path = self.temp_path / 'DELIVERABLES.md'
        deliverables_path.write_text('**Status**: 🚧 Not Started\n', encoding='utf-8')

        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'Not Started')

    def test_status_without_markdown_bold(self):
        """Test parsing status without markdown bold markers."""
        deliverables_path = self.temp_path / 'DELIVERABLES.md'
        deliverables_path.write_text('Status: ✅ Complete\n', encoding='utf-8')

        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'Complete')

    def test_status_without_emoji(self):
        """Test parsing status without emoji."""
        deliverables_path = self.temp_path / 'DELIVERABLES.md'
        deliverables_path.write_text('**Status**: Complete\n', encoding='utf-8')

        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'Complete')

    def test_case_insensitive_matching(self):
        """Test case-insensitive status matching."""
        deliverables_path = self.temp_path / 'DELIVERABLES.md'
        deliverables_path.write_text('**status**: ✅ COMPLETE\n', encoding='utf-8')

        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'Complete')

    def test_missing_file_returns_unknown(self):
        """Test that missing file returns UNKNOWN."""
        deliverables_path = self.temp_path / 'nonexistent.md'

        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'UNKNOWN')

    def test_file_without_status_returns_unknown(self):
        """Test that file without status line returns UNKNOWN."""
        deliverables_path = self.temp_path / 'DELIVERABLES.md'
        deliverables_path.write_text('# Deliverables\n\nNo status line here.\n', encoding='utf-8')

        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'UNKNOWN')

    def test_hyphenated_status_formats(self):
        """Test status with hyphens (in-progress, not-started)."""
        # Test in-progress
        deliverables_path = self.temp_path / 'DELIVERABLES.md'
        deliverables_path.write_text('**Status**: in-progress\n', encoding='utf-8')
        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'In Progress')

        # Test not-started
        deliverables_path.write_text('**Status**: not-started\n', encoding='utf-8')
        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'Not Started')

    def test_status_in_middle_of_file(self):
        """Test finding status line in middle of file."""
        deliverables_path = self.temp_path / 'DELIVERABLES.md'
        content = """# Deliverables

## Overview

**Status**: ✅ Complete

## Phases
"""
        deliverables_path.write_text(content, encoding='utf-8')

        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'Complete')

    def test_multiple_status_lines(self):
        """Test that first status line is matched."""
        deliverables_path = self.temp_path / 'DELIVERABLES.md'
        content = """**Status**: ✅ Complete

Some text here

**Status**: 🚧 In Progress
"""
        deliverables_path.write_text(content, encoding='utf-8')

        # Should match first occurrence
        status = parse_deliverables_status(deliverables_path)
        self.assertEqual(status, 'Complete')


if __name__ == "__main__":
    unittest.main(verbosity=2)
