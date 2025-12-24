"""
Unit tests for workorder helper functions.

Tests workorder ID generation and timestamp formatting.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from handler_helpers import generate_workorder_id, get_workorder_timestamp
from datetime import datetime


class TestGenerateWorkorderID(unittest.TestCase):
    """Test generate_workorder_id() function."""

    def test_simple_feature_name(self):
        """Test workorder ID generation with simple feature name."""
        self.assertEqual(generate_workorder_id("auth-system"), "WO-AUTH-SYSTEM-001")

    def test_multi_word_feature_name(self):
        """Test workorder ID generation with multi-word feature name."""
        self.assertEqual(generate_workorder_id("deliverables-generator"), "WO-DELIVERABLES-GENERATOR-001")

    def test_single_word_feature(self):
        """Test workorder ID generation with single word."""
        self.assertEqual(generate_workorder_id("auth"), "WO-AUTH-001")

    def test_single_character_feature(self):
        """Test workorder ID generation with single character."""
        self.assertEqual(generate_workorder_id("a"), "WO-A-001")

    def test_feature_with_numbers(self):
        """Test workorder ID generation with numbers in name."""
        self.assertEqual(generate_workorder_id("feature-123"), "WO-FEATURE-123-001")

    def test_already_uppercase(self):
        """Test workorder ID generation with already uppercase name."""
        self.assertEqual(generate_workorder_id("ALREADY-UPPERCASE"), "WO-ALREADY-UPPERCASE-001")

    def test_mixed_case(self):
        """Test workorder ID generation with mixed case."""
        self.assertEqual(generate_workorder_id("Mixed-Case-Feature"), "WO-MIXED-CASE-FEATURE-001")

    def test_multiple_hyphens(self):
        """Test workorder ID generation with multiple hyphens."""
        self.assertEqual(generate_workorder_id("very-long-feature-name"), "WO-VERY-LONG-FEATURE-NAME-001")

    def test_underscores_preserved(self):
        """Test that underscores are preserved in workorder ID."""
        # Note: Feature names should use hyphens, but if underscores exist, they're preserved
        self.assertEqual(generate_workorder_id("feature_name"), "WO-FEATURE_NAME-001")


class TestGetWorkorderTimestamp(unittest.TestCase):
    """Test get_workorder_timestamp() function."""

    def test_timestamp_format(self):
        """Test that timestamp is in ISO 8601 format."""
        timestamp = get_workorder_timestamp()

        # Should be parseable as ISO 8601
        parsed = datetime.fromisoformat(timestamp)
        self.assertIsInstance(parsed, datetime)

    def test_timestamp_has_timezone(self):
        """Test that timestamp includes timezone information."""
        timestamp = get_workorder_timestamp()

        # ISO 8601 with timezone should contain '+' or 'Z'
        self.assertTrue('+' in timestamp or timestamp.endswith('Z'))

    def test_timestamp_is_recent(self):
        """Test that timestamp is current (within last second)."""
        timestamp = get_workorder_timestamp()
        parsed = datetime.fromisoformat(timestamp)
        now = datetime.now(parsed.tzinfo)

        # Should be within 1 second of now
        delta = abs((now - parsed).total_seconds())
        self.assertLess(delta, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
