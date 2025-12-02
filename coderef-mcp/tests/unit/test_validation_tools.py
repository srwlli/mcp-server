"""Unit tests for validation tools (reference validation and batch processing)."""

import pytest
import asyncio
from coderef.generators.validation_generator import (
    ReferenceValidator,
    BatchValidationProcessor,
    ValidationStatus,
    ValidationSeverity,
)


# ============================================================================
# Reference Validator Tests
# ============================================================================

class TestReferenceValidator:
    """Tests for reference format validation."""

    @pytest.fixture
    def validator(self):
        """Create a reference validator instance."""
        return ReferenceValidator()

    def test_validate_complete_reference(self, validator):
        """Test validating a complete reference."""
        ref = "@Fn/src/utils#calculate_total:42{complexity:high,status:active}"
        result = validator.validate_format(ref)

        assert result.is_valid
        assert result.status == ValidationStatus.VALID
        assert len(result.issues) == 0

    def test_validate_reference_without_metadata(self, validator):
        """Test validating reference without metadata."""
        ref = "@C/src/models#MyClass:10"
        result = validator.validate_format(ref)

        assert result.is_valid
        assert result.status == ValidationStatus.VALID

    def test_validate_reference_path_only(self, validator):
        """Test validating reference with path only."""
        ref = "@F/src/config.py"
        result = validator.validate_format(ref)

        assert result.is_valid
        assert result.status == ValidationStatus.VALID

    def test_validate_empty_reference(self, validator):
        """Test validating empty reference."""
        result = validator.validate_format("")

        assert not result.is_valid
        assert result.status == ValidationStatus.INVALID
        assert len(result.issues) > 0

    def test_validate_malformed_reference(self, validator):
        """Test validating malformed reference."""
        result = validator.validate_format("invalid_reference")

        assert not result.is_valid
        assert result.status == ValidationStatus.MALFORMED

    def test_validate_invalid_type(self, validator):
        """Test validating reference with invalid type."""
        ref = "@InvalidType/src/file.py"
        result = validator.validate_format(ref)

        assert not result.is_valid
        assert result.status == ValidationStatus.INVALID
        assert any(i.code == "INVALID_TYPE" for i in result.issues)

    def test_validate_negative_line_number(self, validator):
        """Test validating reference with negative line number."""
        ref = "@Fn/src/utils#func:-1"
        result = validator.validate_format(ref)

        assert not result.is_valid
        assert any(i.code == "NEGATIVE_LINE" for i in result.issues)

    def test_validate_non_numeric_line(self, validator):
        """Test validating reference with non-numeric line number."""
        ref = "@Fn/src/utils#func:abc"
        result = validator.validate_format(ref)

        assert not result.is_valid
        assert any(i.code == "INVALID_LINE_FORMAT" for i in result.issues)

    def test_validate_metadata_format(self, validator):
        """Test validating metadata format."""
        ref = "@Fn/src/test#func:1{status:active,complexity:high}"
        result = validator.validate_format(ref)

        # Should be valid - metadata properly formatted
        assert result.status in (ValidationStatus.VALID, ValidationStatus.WARNING)

    def test_validate_relationship_self_reference(self, validator):
        """Test validating self-referencing relationship."""
        ref = "@Fn/src/utils#func:10"
        result = validator.validate_relationships(ref, ref, "calls")

        assert any(i.code == "SELF_REFERENCE" for i in result.issues)

    def test_validate_relationship_invalid_type(self, validator):
        """Test validating relationship with invalid type."""
        result = validator.validate_relationships(
            "@Fn/src/a#func",
            "@Fn/src/b#func",
            "invalid_type"
        )

        assert not result.is_valid
        assert any(i.code == "INVALID_RELATIONSHIP_TYPE" for i in result.issues)

    def test_validation_timing(self, validator):
        """Test that validation timing is recorded."""
        result = validator.validate_format("@Fn/src/test#func")

        assert result.validation_time_ms >= 0
        assert result.validation_time_ms < 100  # Should be fast

    def test_validation_metadata_contains_counts(self, validator):
        """Test that validation metadata contains issue counts."""
        result = validator.validate_format("@Fn/src/test#func:100")

        assert "issue_count" in result.metadata
        assert "error_count" in result.metadata
        assert "warning_count" in result.metadata


# ============================================================================
# Batch Validation Processor Tests
# ============================================================================

class TestBatchValidationProcessor:
    """Tests for batch validation processing."""

    @pytest.fixture
    def processor(self):
        """Create a batch validation processor."""
        return BatchValidationProcessor()

    @pytest.mark.asyncio
    async def test_batch_validation_sequential(self, processor):
        """Test batch validation in sequential mode."""
        references = [
            "@Fn/src/a#func:1",
            "@C/src/b#Class",
            "@F/src/c.py",
            "invalid_ref",
        ]

        result = await processor.validate_batch(references, parallel=False)

        assert result.total_items == 4
        assert result.successful == 3
        assert result.failed == 1
        assert len(result.results) == 4

    @pytest.mark.asyncio
    async def test_batch_validation_parallel(self, processor):
        """Test batch validation in parallel mode."""
        references = [
            "@Fn/src/a#func:1",
            "@C/src/b#Class",
            "@F/src/c.py",
            "@M/src/d#method",
        ]

        result = await processor.validate_batch(references, parallel=True, max_workers=2)

        assert result.total_items == 4
        assert result.successful == 4
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_batch_validation_mixed(self, processor):
        """Test batch validation with mixed valid/invalid references."""
        references = [
            "@Fn/src/valid#func",
            "invalid",
            "@C/src/class#MyClass",
            "@InvalidType/src/file",
            "@F/src/file.py",
        ]

        result = await processor.validate_batch(references, parallel=False)

        assert result.total_items == 5
        assert result.successful >= 3
        assert result.failed >= 2

    @pytest.mark.asyncio
    async def test_batch_summary_calculations(self, processor):
        """Test that batch summary calculations are correct."""
        references = [
            "@Fn/src/a#func:1",
            "@Fn/src/b#func:2",
            "invalid",
        ]

        result = await processor.validate_batch(references)

        assert result.summary["success_rate"] > 0
        assert result.summary["average_validation_time_ms"] >= 0
        assert result.summary["total_issues"] >= 0

    @pytest.mark.asyncio
    async def test_batch_empty_list(self, processor):
        """Test batch validation with empty list."""
        result = await processor.validate_batch([])

        assert result.total_items == 0
        assert result.successful == 0
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_batch_performance(self, processor):
        """Test batch validation performance."""
        # Create 100 valid references
        references = [f"@Fn/src/module_{i}#func_{i}" for i in range(100)]

        result = await processor.validate_batch(references, parallel=True, max_workers=10)

        assert result.total_items == 100
        assert result.successful == 100
        # Should complete reasonably fast with parallelization
        assert result.batch_execution_time_ms < 5000

    def test_generate_report(self, processor):
        """Test report generation."""
        references = [
            "@Fn/src/a#func",
            "invalid_ref",
            "@C/src/class#Class",
        ]

        # Create batch result through synchronous validation
        import asyncio
        result = asyncio.run(processor.validate_batch(references, parallel=False))

        report = processor.generate_report(result)

        assert "BATCH VALIDATION REPORT" in report
        assert "Total References:" in report
        assert "Success Rate:" in report
        assert "Execution Time:" in report


# ============================================================================
# Integration Tests
# ============================================================================

class TestValidationIntegration:
    """Integration tests for validation tools."""

    @pytest.mark.asyncio
    async def test_complete_validation_workflow(self):
        """Test complete validation workflow."""
        processor = BatchValidationProcessor()

        # Mixed batch of references
        references = [
            "@Fn/src/handlers#process_request:100",
            "@C/src/models#User",
            "@F/src/config.py",
            "not a valid reference",
            "@M/src/service#execute:200",
            "@InvalidType/src/file",
        ]

        result = await processor.validate_batch(references)

        # Should have found issues
        assert result.failed > 0
        assert result.successful > 0

        # Generate report
        report = processor.generate_report(result)
        assert "FAILED REFERENCES:" in report or "Success Rate: 100" in report

    @pytest.mark.asyncio
    async def test_validation_accuracy(self):
        """Test validation accuracy."""
        validator = ReferenceValidator()

        # Test known valid formats
        valid_refs = [
            "@Fn/src/utils#calculate:42",
            "@C/src/models#User:10",
            "@F/src/config.py",
            "@M/src/service#execute",
        ]

        for ref in valid_refs:
            result = validator.validate_format(ref)
            assert result.is_valid, f"Should be valid: {ref}"

        # Test known invalid formats
        invalid_refs = [
            "no_at_symbol/path",
            "@NoSlash",
            "@/nopath",
            "@@double/at#sym",
        ]

        for ref in invalid_refs:
            result = validator.validate_format(ref)
            assert not result.is_valid, f"Should be invalid: {ref}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
