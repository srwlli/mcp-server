"""
End-to-end tests for Papertrail MCP tools.

Tests the validate_document and check_all_docs MCP tools.
"""

import pytest
from pathlib import Path


# Test data
VALID_FOUNDATION_DOC = """---
agent: 'Test Agent'
date: '2026-01-10'
task: CREATE
workorder_id: WO-TEST-001
generated_by: coderef-docs v1.0.0
feature_id: test-feature
doc_type: readme
---

# Test Document

This is a test foundation document.
"""

INVALID_DOC_MISSING_FIELDS = """---
agent: 'Test Agent'
date: '2026-01-10'
---

# Invalid Document

Missing required UDS fields.
"""


def test_validate_document_valid(tmp_path):
    """Test validate_document with a valid document."""
    # Create test file
    test_file = tmp_path / "TEST.md"
    test_file.write_text(VALID_FOUNDATION_DOC, encoding='utf-8')
    
    from papertrail.validators.factory import ValidatorFactory
    
    # Validate
    validator = ValidatorFactory.get_validator(test_file)
    result = validator.validate_file(test_file)
    
    # Assertions
    assert result.valid is True
    assert result.score >= 90
    assert len(result.errors) == 0


def test_validate_document_invalid(tmp_path):
    """Test validate_document with an invalid document."""
    # Create test file
    test_file = tmp_path / "INVALID.md"
    test_file.write_text(INVALID_DOC_MISSING_FIELDS, encoding='utf-8')
    
    from papertrail.validators.factory import ValidatorFactory
    
    # Validate
    validator = ValidatorFactory.get_validator(test_file)
    result = validator.validate_file(test_file)
    
    # Assertions
    assert result.valid is False
    assert result.score < 90
    assert len(result.errors) > 0


def test_check_all_docs(tmp_path):
    """Test check_all_docs with multiple documents."""
    # Create multiple test files
    valid_file = tmp_path / "valid.md"
    valid_file.write_text(VALID_FOUNDATION_DOC, encoding='utf-8')
    
    invalid_file = tmp_path / "invalid.md"
    invalid_file.write_text(INVALID_DOC_MISSING_FIELDS, encoding='utf-8')
    
    from papertrail.validators.factory import ValidatorFactory
    
    # Validate all files
    results = []
    for file_path in tmp_path.glob("*.md"):
        try:
            validator = ValidatorFactory.get_validator(file_path)
            result = validator.validate_file(file_path)
            results.append({
                "file": file_path.name,
                "valid": result.valid,
                "score": result.score
            })
        except Exception as e:
            results.append({
                "file": file_path.name,
                "error": str(e)
            })
    
    # Assertions
    assert len(results) == 2
    assert any(r["valid"] for r in results if "valid" in r)
    assert any(not r["valid"] for r in results if "valid" in r)


def test_schema_inheritance(tmp_path):
    """Test that schema inheritance works correctly (base → category)."""
    from papertrail.validators.foundation import FoundationDocValidator
    
    # Create test file
    test_file = tmp_path / "README.md"
    test_file.write_text(VALID_FOUNDATION_DOC, encoding='utf-8')
    
    # Validate
    validator = FoundationDocValidator()
    result = validator.validate_file(test_file)
    
    # Check that base schema fields are validated
    assert result.valid is True
    
    # Check that schema has both base and foundation fields
    assert validator.schema is not None
    assert 'agent' in validator.schema['required']
    assert 'date' in validator.schema['required']
    assert 'workorder_id' in validator.schema['required']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
