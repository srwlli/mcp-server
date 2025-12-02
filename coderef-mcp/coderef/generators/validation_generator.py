"""Validation generator for CodeRef2 reference validation and batch processing.

This module provides comprehensive validation capabilities including:
- Reference format validation
- Element existence validation
- Relationship validation
- Metadata validation
- Batch validation with parallel processing
"""

import logging
import time
import asyncio
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from coderef.models import (
    TypeDesignator,
    MetadataCategory,
    RelationshipType,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Validation Result Types
# ============================================================================

class ValidationStatus(str, Enum):
    """Status of a validation check."""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    NOT_FOUND = "not_found"
    MALFORMED = "malformed"


class ValidationSeverity(str, Enum):
    """Severity level for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """A single validation issue."""
    severity: ValidationSeverity
    code: str
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validating a single reference."""
    reference: str
    status: ValidationStatus
    is_valid: bool
    issues: List[ValidationIssue]
    validation_time_ms: float
    metadata: Dict[str, Any]


@dataclass
class BatchValidationResult:
    """Result of batch validation."""
    total_items: int
    successful: int
    failed: int
    warnings: int
    results: List[ValidationResult]
    batch_execution_time_ms: float
    summary: Dict[str, Any]


# ============================================================================
# Reference Validator
# ============================================================================

class ReferenceValidator:
    """Validator for CodeRef2 references."""

    # CodeRef2 reference pattern
    REFERENCE_PATTERN = re.compile(
        r"^@(?P<type>[A-Za-z0-9_]+)/(?P<path>[^#:{}]+)(?:#(?P<element>[^:{}]+))?(?::(?P<line>\d+))?(?:\{(?P<metadata>[^}]*)\})?$"
    )

    # Valid path characters
    VALID_PATH_CHARS = re.compile(r"^[a-zA-Z0-9/_\.\-\+]+$")

    def __init__(self):
        """Initialize reference validator."""
        self.logger = logging.getLogger(f"{__name__}.ReferenceValidator")
        self._valid_types = {e.value for e in TypeDesignator}
        self._valid_metadata_categories = {e.value for e in MetadataCategory}

    def validate_format(self, reference: str) -> ValidationResult:
        """Validate reference format.

        Args:
            reference: Reference string to validate

        Returns:
            ValidationResult: Validation result
        """
        start_time = time.time()
        issues = []

        # Check for empty reference
        if not reference or not reference.strip():
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="EMPTY_REFERENCE",
                    message="Reference cannot be empty"
                )
            )
            return self._create_result(
                reference, ValidationStatus.INVALID, issues, start_time
            )

        # Check format with regex
        match = self.REFERENCE_PATTERN.match(reference)
        if not match:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="MALFORMED_REFERENCE",
                    message="Reference does not match CodeRef2 format",
                    suggestion="Expected format: @Type/path#element:line{metadata}"
                )
            )
            return self._create_result(
                reference, ValidationStatus.MALFORMED, issues, start_time
            )

        # Extract and validate components
        groups = match.groupdict()

        # Validate type designator
        type_des = groups.get("type", "")
        if type_des not in self._valid_types:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_TYPE",
                    message=f"Invalid type designator: {type_des}",
                    field="type",
                    suggestion=f"Valid types: {', '.join(sorted(self._valid_types)[:5])}..."
                )
            )

        # Validate path
        path = groups.get("path", "")
        if not path:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="EMPTY_PATH",
                    message="Path cannot be empty",
                    field="path"
                )
            )
        elif not self.VALID_PATH_CHARS.match(path):
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="INVALID_PATH_CHARS",
                    message="Path contains unusual characters",
                    field="path"
                )
            )

        # Validate line number if present
        line_str = groups.get("line")
        if line_str:
            try:
                line_num = int(line_str)
                if line_num < 0:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            code="NEGATIVE_LINE",
                            message="Line number cannot be negative",
                            field="line"
                        )
                    )
            except ValueError:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="INVALID_LINE_FORMAT",
                        message="Line number must be an integer",
                        field="line"
                    )
                )

        # Validate metadata if present
        metadata_str = groups.get("metadata")
        if metadata_str:
            self._validate_metadata(metadata_str, issues)

        # Determine status
        status = ValidationStatus.VALID
        has_error = any(i.severity == ValidationSeverity.ERROR for i in issues)
        if has_error:
            status = ValidationStatus.INVALID
        elif issues:
            status = ValidationStatus.WARNING

        return self._create_result(reference, status, issues, start_time)

    def _validate_metadata(
        self,
        metadata_str: str,
        issues: List[ValidationIssue]
    ) -> None:
        """Validate metadata portion of reference.

        Args:
            metadata_str: Metadata string
            issues: List to append issues to
        """
        items = metadata_str.split(",")
        for item in items:
            if not item.strip():
                continue
            if ":" not in item:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        code="INVALID_METADATA_FORMAT",
                        message=f"Metadata item missing colon: {item}",
                        field="metadata"
                    )
                )
                continue

            key, value = item.split(":", 1)
            key = key.strip()
            value = value.strip()

            # Check if key is a known category
            if key not in self._valid_metadata_categories:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        code="UNKNOWN_METADATA_CATEGORY",
                        message=f"Unknown metadata category: {key}",
                        field="metadata"
                    )
                )

    def validate_existence(
        self,
        reference: str,
        known_elements: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate that reference exists in known elements.

        Args:
            reference: Reference to validate
            known_elements: Dictionary of known elements

        Returns:
            ValidationResult: Validation result
        """
        start_time = time.time()
        issues = []

        if known_elements is None:
            known_elements = {}

        # If element not in known set, it's "not found"
        if reference not in known_elements and known_elements:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="ELEMENT_NOT_FOUND",
                    message=f"Element not found in known element set",
                    suggestion="Element may exist but not yet indexed"
                )
            )
            return self._create_result(
                reference, ValidationStatus.NOT_FOUND, issues, start_time
            )

        return self._create_result(
            reference, ValidationStatus.VALID, issues, start_time
        )

    def validate_relationships(
        self,
        source_reference: str,
        target_reference: str,
        relationship_type: str,
    ) -> ValidationResult:
        """Validate a relationship between two references.

        Args:
            source_reference: Source element reference
            target_reference: Target element reference
            relationship_type: Type of relationship

        Returns:
            ValidationResult: Validation result
        """
        start_time = time.time()
        issues = []

        # Validate both references
        source_valid = self.validate_format(source_reference)
        target_valid = self.validate_format(target_reference)

        if not source_valid.is_valid:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_SOURCE_REFERENCE",
                    message="Source reference is invalid",
                    field="source"
                )
            )

        if not target_valid.is_valid:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_TARGET_REFERENCE",
                    message="Target reference is invalid",
                    field="target"
                )
            )

        # Validate relationship type
        valid_types = {rt.value for rt in RelationshipType}
        if relationship_type not in valid_types:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_RELATIONSHIP_TYPE",
                    message=f"Invalid relationship type: {relationship_type}",
                    field="relationship_type",
                    suggestion=f"Valid types: {', '.join(sorted(valid_types))}"
                )
            )

        # Self-referencing warning
        if source_reference == target_reference:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="SELF_REFERENCE",
                    message="Element references itself",
                    suggestion="Verify this is intentional"
                )
            )

        status = ValidationStatus.VALID
        if any(i.severity == ValidationSeverity.ERROR for i in issues):
            status = ValidationStatus.INVALID
        elif issues:
            status = ValidationStatus.WARNING

        return self._create_result(reference, status, issues, start_time)

    def _create_result(
        self,
        reference: str,
        status: ValidationStatus,
        issues: List[ValidationIssue],
        start_time: float
    ) -> ValidationResult:
        """Create a validation result.

        Args:
            reference: Reference being validated
            status: Validation status
            issues: List of validation issues
            start_time: Start time of validation

        Returns:
            ValidationResult: Validation result
        """
        execution_time_ms = (time.time() - start_time) * 1000
        is_valid = status in (ValidationStatus.VALID, ValidationStatus.WARNING)

        return ValidationResult(
            reference=reference,
            status=status,
            is_valid=is_valid,
            issues=issues,
            validation_time_ms=execution_time_ms,
            metadata={
                "issue_count": len(issues),
                "error_count": sum(1 for i in issues if i.severity == ValidationSeverity.ERROR),
                "warning_count": sum(1 for i in issues if i.severity == ValidationSeverity.WARNING),
            }
        )


# ============================================================================
# Batch Validation Processor
# ============================================================================

class BatchValidationProcessor:
    """Processor for batch validation with parallel execution."""

    def __init__(self, validator: Optional[ReferenceValidator] = None):
        """Initialize batch processor.

        Args:
            validator: Optional reference validator instance
        """
        self.logger = logging.getLogger(f"{__name__}.BatchValidationProcessor")
        self.validator = validator or ReferenceValidator()

    async def validate_batch(
        self,
        references: List[str],
        parallel: bool = True,
        max_workers: int = 5,
        timeout_ms: int = 5000
    ) -> BatchValidationResult:
        """Validate multiple references.

        Args:
            references: List of references to validate
            parallel: Whether to process in parallel
            max_workers: Maximum number of parallel workers
            timeout_ms: Timeout for batch processing

        Returns:
            BatchValidationResult: Batch validation results
        """
        start_time = time.time()
        self.logger.info(f"Starting batch validation of {len(references)} references")

        if parallel:
            results = await self._validate_parallel(references, max_workers)
        else:
            results = await self._validate_sequential(references)

        # Calculate summary statistics
        successful = sum(1 for r in results if r.is_valid)
        failed = sum(1 for r in results if not r.is_valid)
        warnings = sum(1 for r in results if r.status == ValidationStatus.WARNING)

        batch_time_ms = (time.time() - start_time) * 1000

        return BatchValidationResult(
            total_items=len(references),
            successful=successful,
            failed=failed,
            warnings=warnings,
            results=results,
            batch_execution_time_ms=batch_time_ms,
            summary={
                "success_rate": (successful / len(references) * 100) if references else 0,
                "average_validation_time_ms": (
                    sum(r.validation_time_ms for r in results) / len(results)
                ) if results else 0,
                "total_issues": sum(len(r.issues) for r in results),
            }
        )

    async def _validate_sequential(
        self,
        references: List[str]
    ) -> List[ValidationResult]:
        """Validate references sequentially.

        Args:
            references: References to validate

        Returns:
            list: Validation results
        """
        results = []
        for reference in references:
            result = self.validator.validate_format(reference)
            results.append(result)
        return results

    async def _validate_parallel(
        self,
        references: List[str],
        max_workers: int
    ) -> List[ValidationResult]:
        """Validate references in parallel.

        Args:
            references: References to validate
            max_workers: Maximum concurrent validations

        Returns:
            list: Validation results
        """
        # Use semaphore to limit concurrent validations
        semaphore = asyncio.Semaphore(max_workers)

        async def validate_with_semaphore(ref: str) -> ValidationResult:
            async with semaphore:
                return self.validator.validate_format(ref)

        tasks = [validate_with_semaphore(ref) for ref in references]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return results

    def generate_report(self, batch_result: BatchValidationResult) -> str:
        """Generate human-readable validation report.

        Args:
            batch_result: Batch validation result

        Returns:
            str: Formatted report
        """
        report = []
        report.append("=" * 60)
        report.append("BATCH VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Total References: {batch_result.total_items}")
        report.append(f"Successful: {batch_result.successful}")
        report.append(f"Failed: {batch_result.failed}")
        report.append(f"Warnings: {batch_result.warnings}")
        report.append(f"Success Rate: {batch_result.summary['success_rate']:.1f}%")
        report.append(f"Execution Time: {batch_result.batch_execution_time_ms:.2f}ms")
        report.append("")

        if batch_result.failed > 0:
            report.append("FAILED REFERENCES:")
            for result in batch_result.results:
                if not result.is_valid:
                    report.append(f"  - {result.reference} ({result.status.value})")
                    for issue in result.issues:
                        report.append(f"      [{issue.severity.value}] {issue.code}: {issue.message}")

        return "\n".join(report)
