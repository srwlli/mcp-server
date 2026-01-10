"""
Tests for DocumentPostProcessor - Writing Standards Enforcement.

WO-RESOURCE-SHEET-MCP-TOOL-001 Phase 3C (PORT-TEST-001)

Tests cover all 5 writing guideline categories:
1. Voice & Tone (imperative, not conversational)
2. Precision (no hedging)
3. Active Voice (prefer active over passive)
4. Table Usage (structured data in tables)
5. Ambiguity ("must" vs "should")
"""

import pytest
from resource_sheet.processing.post_processor import (
    DocumentPostProcessor,
    Violation,
    ViolationSeverity
)


@pytest.fixture
def processor():
    """Fixture providing DocumentPostProcessor instance."""
    return DocumentPostProcessor()


class TestVoiceTone:
    """Test voice & tone guideline checks."""

    def test_detects_conversational_we(self, processor):
        """Test detection of conversational 'we' statements."""
        markdown = "We persist the state to localStorage."
        violations = processor.check_voice_tone(markdown)

        assert len(violations) == 1
        assert violations[0].category == "voice_tone"
        assert "we" in violations[0].text.lower()
        assert "imperative" in violations[0].message.lower()

    def test_detects_you_can(self, processor):
        """Test detection of 'you can' patterns."""
        markdown = "You can add custom handlers to the component."
        violations = processor.check_voice_tone(markdown)

        assert len(violations) == 1
        assert "you can" in violations[0].text.lower()

    def test_detects_lets(self, processor):
        """Test detection of conversational 'let's'."""
        markdown = "Let's start by configuring the service."
        violations = processor.check_voice_tone(markdown)

        assert len(violations) == 1
        assert "let's" in violations[0].text.lower()

    def test_skips_code_blocks(self, processor):
        """Test that code blocks are not checked for voice violations."""
        markdown = """
```javascript
// We persist state here
function save() { we.persist(); }
```
"""
        violations = processor.check_voice_tone(markdown)
        assert len(violations) == 0

    def test_skips_headers(self, processor):
        """Test that headers are not checked for voice violations."""
        markdown = "# We Persist State"
        violations = processor.check_voice_tone(markdown)
        assert len(violations) == 0


class TestPrecision:
    """Test precision guideline checks (no hedging)."""

    def test_detects_should_probably(self, processor):
        """Test detection of 'should probably' hedge."""
        markdown = "The component should probably validate inputs."
        violations = processor.check_precision(markdown)

        assert len(violations) == 1
        assert violations[0].category == "precision"
        assert "should probably" in violations[0].text.lower()

    def test_detects_might_want_to(self, processor):
        """Test detection of 'might want to' hedge."""
        markdown = "You might want to consider using Zod."
        violations = processor.check_precision(markdown)

        assert len(violations) >= 1
        assert any("might want to" in v.text.lower() for v in violations)

    def test_detects_perhaps(self, processor):
        """Test detection of 'perhaps' hedge."""
        markdown = "Perhaps we should add error handling."
        violations = processor.check_precision(markdown)

        # Should detect both "perhaps" and "we should"
        assert len(violations) >= 1
        hedge_violations = [v for v in violations if v.category == "precision"]
        assert any("perhaps" in v.text.lower() for v in hedge_violations)

    def test_detects_maybe(self, processor):
        """Test detection of 'maybe' hedge."""
        markdown = "Maybe add validation here."
        violations = processor.check_precision(markdown)

        assert len(violations) >= 1
        assert any("maybe" in v.text.lower() for v in violations)

    def test_detects_kind_of(self, processor):
        """Test detection of 'kind of' hedge."""
        markdown = "This is kind of how it works."
        violations = processor.check_precision(markdown)

        assert len(violations) >= 1
        assert any("kind of" in v.text.lower() for v in violations)


class TestActiveVoice:
    """Test active voice guideline checks."""

    def test_detects_is_managed_by(self, processor):
        """Test detection of 'is managed by' passive voice."""
        markdown = "State is managed by the parent component."
        violations = processor.check_active_voice(markdown)

        assert len(violations) == 1
        assert violations[0].category == "active_voice"
        assert "is" in violations[0].text.lower() and "by" in violations[0].text.lower()

    def test_detects_was_created_by(self, processor):
        """Test detection of 'was created by' passive voice."""
        markdown = "The token was created by the authentication service."
        violations = processor.check_active_voice(markdown)

        assert len(violations) == 1
        assert "was" in violations[0].text.lower() and "by" in violations[0].text.lower()

    def test_detects_are_processed_by(self, processor):
        """Test detection of 'are processed by' passive voice."""
        markdown = "Requests are processed by the backend."
        violations = processor.check_active_voice(markdown)

        assert len(violations) == 1
        assert "are" in violations[0].text.lower() and "by" in violations[0].text.lower()

    def test_detects_been_validated(self, processor):
        """Test detection of 'been validated' passive voice."""
        markdown = "The input has been validated."
        violations = processor.check_active_voice(markdown)

        assert len(violations) == 1
        assert "been" in violations[0].text.lower()

    def test_skips_tables(self, processor):
        """Test that table rows are not checked for passive voice."""
        markdown = """
| State | Owner | Managed By |
|-------|-------|------------|
| value | Component | is managed by parent |
"""
        violations = processor.check_active_voice(markdown)
        # Should skip table rows
        assert len(violations) == 0


class TestTableUsage:
    """Test table usage guideline checks."""

    def test_detects_structured_list(self, processor):
        """Test detection of structured lists that should be tables."""
        markdown = """
- State: active, Owner: Component, Type: boolean
- State: value, Owner: Component, Type: string
- State: error, Owner: Component, Type: Error | null
"""
        violations = processor.check_table_usage(markdown)

        assert len(violations) == 1
        assert violations[0].category == "table_usage"
        assert "table" in violations[0].message.lower()

    def test_detects_bold_key_value_list(self, processor):
        """Test detection of bold key-value lists."""
        markdown = """
- **Name:** AuthService
- **Type:** Class
- **Module:** auth
- **Exports:** login, logout
"""
        violations = processor.check_table_usage(markdown)

        assert len(violations) == 1
        assert "table" in violations[0].message.lower()

    def test_skips_short_lists(self, processor):
        """Test that short lists (< 3 items) are not flagged."""
        markdown = """
- State: active, Owner: Component
- State: value, Owner: Component
"""
        violations = processor.check_table_usage(markdown)
        # Less than 3 items, should not flag
        assert len(violations) == 0

    def test_skips_unstructured_lists(self, processor):
        """Test that unstructured lists are not flagged."""
        markdown = """
- First item
- Second item
- Third item
- Fourth item
"""
        violations = processor.check_table_usage(markdown)
        assert len(violations) == 0


class TestAmbiguity:
    """Test ambiguity guideline checks (should vs must/may)."""

    def test_detects_should_statement(self, processor):
        """Test detection of ambiguous 'should' statements."""
        markdown = "Components should validate props."
        violations = processor.check_ambiguity(markdown)

        assert len(violations) == 1
        assert violations[0].category == "ambiguity"
        assert "should" in violations[0].text.lower()
        assert "must" in violations[0].suggestion.lower() or "may" in violations[0].suggestion.lower()

    def test_detects_multiple_shoulds(self, processor):
        """Test detection of multiple 'should' statements."""
        markdown = """
Components should validate props. They should also handle errors.
State should be immutable.
"""
        violations = processor.check_ambiguity(markdown)
        assert len(violations) == 3

    def test_skips_code_blocks_for_should(self, processor):
        """Test that code blocks are not checked for 'should'."""
        markdown = """
```typescript
// Should validate here
function validate() { }
```
"""
        violations = processor.check_ambiguity(markdown)
        assert len(violations) == 0

    def test_skips_quotes_for_should(self, processor):
        """Test that quoted text is not checked for 'should'."""
        markdown = "> This should be considered"
        violations = processor.check_ambiguity(markdown)
        assert len(violations) == 0


class TestCheckAll:
    """Test check_all method that runs all checks."""

    def test_check_all_combines_violations(self, processor):
        """Test that check_all combines violations from all checkers."""
        markdown = """
# Test Document

We persist state. You can add handlers. Maybe use validation.
State is managed by the parent component. The component should handle errors.

- State: active, Owner: Component, Type: boolean
- State: value, Owner: Component, Type: string
- State: error, Owner: Component, Type: Error | null
"""
        violations = processor.check_all(markdown)

        # Should have violations from multiple categories
        categories = {v.category for v in violations}
        assert "voice_tone" in categories  # "We persist", "You can"
        assert "precision" in categories   # "Maybe"
        assert "active_voice" in categories  # "is managed by"
        assert "ambiguity" in categories   # "should"
        assert "table_usage" in categories  # Structured list

    def test_violations_sorted_by_line(self, processor):
        """Test that violations are sorted by line number."""
        markdown = """
Line 1: Components should validate.
Line 2: We persist state.
Line 3: Maybe add error handling.
"""
        violations = processor.check_all(markdown)

        # Verify sorted
        for i in range(len(violations) - 1):
            assert violations[i].line_number <= violations[i + 1].line_number


class TestApplyFixes:
    """Test apply_fixes method for auto-fixing violations."""

    def test_removes_basically(self, processor):
        """Test that 'basically' is removed."""
        markdown = "Basically, this is how it works."
        violations = processor.check_precision(markdown)
        fixed = processor.apply_fixes(markdown, violations)

        assert "basically" not in fixed.lower()

    def test_removes_perhaps(self, processor):
        """Test that 'perhaps' is removed."""
        markdown = "Perhaps we should add validation."
        violations = processor.check_precision(markdown)
        fixed = processor.apply_fixes(markdown, violations)

        assert "perhaps" not in fixed.lower()

    def test_removes_maybe(self, processor):Test that 'maybe' is removed."""
        markdown = "Maybe add error handling here."
        violations = processor.check_precision(markdown)
        fixed = processor.apply_fixes(markdown, violations)

        assert "maybe" not in fixed.lower()

    def test_preserves_non_auto_fixable(self, processor):
        """Test that non-auto-fixable violations don't break the document."""
        markdown = "We persist state to localStorage."
        violations = processor.check_voice_tone(markdown)
        fixed = processor.apply_fixes(markdown, violations)

        # Should preserve original (can't auto-fix "we")
        assert "we persist" in fixed.lower()


class TestGetReport:
    """Test get_report method for human-readable output."""

    def test_report_shows_violation_count(self, processor):
        """Test that report shows total violation count."""
        markdown = "We persist state. Maybe add validation."
        violations = processor.check_all(markdown)
        report = processor.get_report(violations)

        assert f"{len(violations)} writing guideline violations" in report.lower()

    def test_report_groups_by_category(self, processor):
        """Test that report groups violations by category."""
        markdown = "We persist state. Maybe add validation. Should handle errors."
        violations = processor.check_all(markdown)
        report = processor.get_report(violations)

        # Should have category headers
        assert "voice" in report.lower() or "tone" in report.lower()
        assert "precision" in report.lower()
        assert "ambiguity" in report.lower()

    def test_report_shows_suggestions(self, processor):
        """Test that report includes fix suggestions."""
        markdown = "Components should validate props."
        violations = processor.check_all(markdown)
        report = processor.get_report(violations)

        assert "suggestion" in report.lower()
        assert "must" in report.lower() or "may" in report.lower()

    def test_empty_report(self, processor):
        """Test report for document with no violations."""
        markdown = """
# Clean Document

## State Ownership

| State | Owner | Type |
|-------|-------|------|
| active | Component | boolean |

Component manages state directly. Users must provide valid props.
"""
        violations = processor.check_all(markdown)
        report = processor.get_report(violations)

        assert "no" in report.lower() and "violations" in report.lower()


class TestSeverityLevels:
    """Test that violations have appropriate severity levels."""

    def test_voice_tone_is_warning(self, processor):
        """Test that voice/tone violations are warnings."""
        markdown = "We persist state."
        violations = processor.check_voice_tone(markdown)

        assert violations[0].severity == ViolationSeverity.WARNING

    def test_precision_is_warning(self, processor):
        """Test that precision violations are warnings."""
        markdown = "Maybe add validation."
        violations = processor.check_precision(markdown)

        assert violations[0].severity == ViolationSeverity.WARNING

    def test_active_voice_is_info(self, processor):
        """Test that active voice violations are info level."""
        markdown = "State is managed by the component."
        violations = processor.check_active_voice(markdown)

        assert violations[0].severity == ViolationSeverity.INFO

    def test_table_usage_is_info(self, processor):
        """Test that table usage violations are info level."""
        markdown = """
- State: active, Owner: Component, Type: boolean
- State: value, Owner: Component, Type: string
- State: error, Owner: Component, Type: Error | null
"""
        violations = processor.check_table_usage(markdown)

        assert violations[0].severity == ViolationSeverity.INFO

    def test_ambiguity_is_warning(self, processor):
        """Test that ambiguity violations are warnings."""
        markdown = "Components should validate props."
        violations = processor.check_ambiguity(markdown)

        assert violations[0].severity == ViolationSeverity.WARNING


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
