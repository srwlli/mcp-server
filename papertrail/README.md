# Papertrail

**Universal Documentation Standards (UDS) & Resource Sheet Metadata Standards (RSMS v2.0)**

## Purpose

Papertrail enforces documentation quality across the CodeRef ecosystem through validation, schema-based quality scoring, and automated enforcement via MCP tools.

## Overview

A Python library and MCP server providing:
- **7 MCP Tools** for document validation
- **13 Validators** covering 18 document types
- **100% Validation Coverage** across all CodeRef docs
- **Score-Based Quality** (0-100) with actionable metrics
- **RSMS v2.0** resource sheet compliance

## What

### Key Features
- Auto-detect document type from path/frontmatter
- POWER framework enforcement (foundation docs)
- Completeness metrics (section coverage 0-100%)
- Code example validation (API/COMPONENTS docs)
- Pre-commit hooks & CI/CD integration
- Batch validation for directories

### Supported Document Types (18)
- Foundation (5): readme, architecture, api, schema, components
- Workorder (4): plan, deliverables, analysis, tasks  
- User-Facing (6): guide, tutorial, faq, quickstart, reference, troubleshooting
- System, Standards, Migration, Infrastructure, Session, Plan, Resource Sheet, General

## Why

**Problem:** Inconsistent documentation across CodeRef servers, no quality enforcement, manual validation.

**Solution:** Automated validation with real-time feedback, schema-based standards, MCP integration for agents.

**Impact:**
- 72% → 100% validation coverage
- Eliminated schema-template drift
- Real-time quality gates for agents
- Pre-commit enforcement

## When

### Installation
```bash
pip install -e .
```

### Quick Start
```python
from papertrail.validators.factory import ValidatorFactory

validator = ValidatorFactory.get_validator(Path("README.md"))
result = validator.validate_file(Path("README.md"))

print(f"Score: {result.score}/100")
print(f"Completeness: {result.completeness}%")
```

### MCP Usage
```json
{
  "tool": "validate_document",
  "arguments": {
    "file_path": "C:/project/README.md"
  }
}
```

## Examples

### Example 1: Validate Foundation Doc
```python
from papertrail.validators.foundation import FoundationDocValidator

validator = FoundationDocValidator()
result = validator.validate_file(Path("README.md"))

if result.valid:
    print("✅ Document validates successfully!")
else:
    print(f"❌ Validation failed ({result.score}/100)")
    for error in result.errors:
        print(f"  - {error.message}")
```

### Example 2: Batch Validation
```python
from papertrail.server import check_all_docs

result = await check_all_docs({
    "directory": "C:/project/docs",
    "pattern": "**/*.md"
})
```

### Example 3: Pre-Commit Hook
```bash
# .git/hooks/pre-commit
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$')
for FILE in $FILES; do
  mcp call validate_document --file_path "$FILE" || exit 1
done
```

## References

- [CLAUDE.md](CLAUDE.md) - System architecture & AI context
- [API.md](coderef/foundation-docs/API.md) - MCP API endpoints
- [SCHEMA.md](coderef/foundation-docs/SCHEMA.md) - Validation schemas
- [COMPONENTS.md](coderef/foundation-docs/COMPONENTS.md) - Validator classes
- [ARCHITECTURE.md](coderef/foundation-docs/ARCHITECTURE.md) - System design

---

**Version:** 1.0.0  
**Status:** Production  
**Last Updated:** 2026-01-13  
**Maintained by:** CodeRef Ecosystem
