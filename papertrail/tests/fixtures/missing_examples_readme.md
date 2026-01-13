---
agent: Claude Sonnet 4.5
date: 2026-01-12
task: CREATE
workorder_id: WO-TEST-FIXTURE-002
generated_by: coderef-docs v1.0.0
feature_id: test-fixture-non-compliant
doc_type: readme
title: Test Fixture - Non-Compliant README (Missing Examples)
version: 1.0.0
status: DRAFT
---

# Test Fixture - Non-Compliant README

This is a sample README that is missing the Examples section to test validation failure.

## Purpose

This document serves as a test fixture for validating that the POWER framework validation correctly identifies documents missing required sections.

## Overview

The test fixture provides:
- Incomplete POWER framework structure
- Missing Examples section (intentional)
- Valid UDS frontmatter
- Used to test validation error detection

## What/Why/When

### What
This is a non-compliant test README fixture that intentionally omits the Examples section.

### Why
We need test fixtures that fail validation to ensure the validation system correctly identifies missing required sections and assigns appropriate error severity (MAJOR error, -20 points).

### When
Use this fixture when:
- Testing POWER framework section validation
- Verifying validation fails for non-compliant documents
- Testing error message clarity and severity levels

## References

- [POWER Framework Specification](../../../standards/documentation/global-documentation-standards.md)
- [Foundation Doc Schema](../../../schemas/documentation/foundation-doc-frontmatter-schema.json)
- [Validation Error Documentation](../README.md)

---

**Last Updated**: 2026-01-12
**Version**: 1.0.0
**Maintained by**: Papertrail Test Suite
**NOTE**: This document intentionally missing Examples section for testing purposes
