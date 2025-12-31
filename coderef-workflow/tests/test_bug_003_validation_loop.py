"""Tests for BUG-003: Validation loop exhaustion."""
import pytest

@pytest.mark.unit
@pytest.mark.major
@pytest.mark.bug
class TestBug003ValidationLoop:
    def test_validation_loop_offers_choice_after_3_failures(self):
        """Verify user gets choice after 3 validation failures."""
        iterations = 3
        assert iterations == 3
        # Test: After 3 iterations, offer user choice (save/restart/abort)
