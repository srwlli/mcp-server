---
agent: Claude Sonnet 4.5
date: 2026-01-12
task: CREATE
workorder_id: WO-TEST-FIXTURE-001
generated_by: coderef-docs v1.0.0
feature_id: test-fixture
doc_type: readme
title: Test Fixture - Compliant README
version: 1.0.0
status: APPROVED
---

# Test Fixture - Compliant README

This is a sample README that follows the POWER framework structure for testing validation.

## Purpose

This document serves as a test fixture for validating POWER framework compliance in README documents. It demonstrates the correct structure with all required sections present.

## Overview

The test fixture provides:
- Complete POWER framework structure
- All required sections (Purpose, Overview, What/Why/When, Examples, References)
- Valid UDS frontmatter with all required fields
- Proper markdown formatting

## What/Why/When

### What
This is a test README fixture used by the Papertrail validation system to verify that compliant documents pass validation checks.

### Why
We need test fixtures to ensure the validation system correctly identifies documents that meet all POWER framework requirements.

### When
Use this fixture when:
- Testing POWER framework validation
- Verifying README validation passes for compliant documents
- Creating new test cases for foundation doc validators

## Examples

### Example 1: Validation Usage
```python
from papertrail.validators.foundation import FoundationDocValidator

validator = FoundationDocValidator()
result = validator.validate_file("tests/fixtures/compliant_readme.md")

assert result.valid == True
assert result.score >= 98
```

### Example 2: Schema Validation
```python
# This document should pass all schema checks
assert "Purpose" in document_content
assert "Overview" in document_content
assert "Examples" in document_content
```

## References

- [POWER Framework Specification](../../../standards/documentation/global-documentation-standards.md)
- [Foundation Doc Schema](../../../schemas/documentation/foundation-doc-frontmatter-schema.json)
- [Test Validation Guide](../README.md)

---

**Last Updated**: 2026-01-12
**Version**: 1.0.0
**Maintained by**: Papertrail Test Suite
