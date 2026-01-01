# Papertrail - AI Context Documentation

**Project:** Papertrail (Universal Documentation Standards)
**Version:** 1.0.0
**Status:** Production
**Type:** Python Library + MCP Server
**Purpose:** Universal Documentation Standards (UDS) enforcement for CodeRef ecosystem

---

## What is Papertrail?

Papertrail is a **Python library and MCP server** that provides Universal Documentation Standards (UDS) for the CodeRef ecosystem. It ensures every document has complete traceability, MCP attribution, quality validation, and health monitoring.

**Core Capabilities:**
- Complete workorder traceability (WO-ID linking)
- Automated UDS header/footer injection
- Schema-based validation (0-100 scoring)
- Health monitoring (4-factor scoring)
- Jinja2 template automation with CodeRef extensions

---

## Problem & Solution

### Problem
Documentation across CodeRef MCP servers was inconsistent, lacked traceability, and couldn't be validated automatically. No way to track which workorder generated which docs.

### Solution
Papertrail provides:
- **UDS Schema** - Standardized document structure
- **Workorder Traceability** - Every doc links to WO-ID
- **Automated Validation** - 0-100 health scores
- **MCP Attribution** - Auto-generated metadata
- **Template Engine** - Jinja2 with git/workflow/code intelligence

---

## Architecture

**Language:** Python 3.10+
**Dependencies:** Jinja2, Pydantic, jsonschema
**Integration:** MCP server + Python library

**Key Components:**
1. **UDS Schema Validator** - Validates document structure
2. **Health Scorer** - 4-factor scoring (traceability 40%, completeness 30%, freshness 20%, validation 10%)
3. **Template Engine** - Jinja2 with CodeRef extensions
4. **Workorder Logger** - Global workorder tracking
5. **MCP Tools** - 6 tools for validation and health checking

---

## MCP Tools

**Total:** 6 tools

1. **validate_document** - Validate against UDS schema
2. **check_document_health** - Calculate 0-100 health score
3. **log_workorder** - Log workorder to global log
4. **get_workorder_log** - Query workorder history
5. **inject_uds_headers** - Add UDS headers to documents
6. **generate_from_template** - Render Jinja2 templates with CodeRef extensions

---

## File Structure

```
papertrail/
├── CLAUDE.md                    # This file
├── README.md                    # User documentation
├── pyproject.toml              # Python package config
├── src/
│   └── papertrail/
│       ├── __init__.py
│       ├── validator.py        # UDS schema validation
│       ├── health.py           # Health scoring
│       ├── templates.py        # Jinja2 engine
│       └── logger.py           # Workorder logging
└── schemas/
    ├── uds-document.json       # Universal doc schema
    └── workorder-log.json      # Workorder log schema
```

---

## Integration with CodeRef Ecosystem

**Used by:**
- coderef-docs - Document generation with UDS compliance
- coderef-workflow - Workorder logging and tracking
- All MCP servers - Documentation validation

**Depends on:**
- None (foundational library)

---

## Design Decisions

**1. Python Library + MCP Server (Hybrid)**
- ✅ Chosen: Both library and MCP tools
- ❌ Rejected: MCP-only or library-only
- Reason: Library for programmatic use, MCP for agent integration

**2. 4-Factor Health Scoring**
- ✅ Chosen: Traceability (40%), Completeness (30%), Freshness (20%), Validation (10%)
- ❌ Rejected: Simple pass/fail validation
- Reason: Weighted scoring provides actionable quality metrics

**3. Jinja2 with CodeRef Extensions**
- ✅ Chosen: Extend Jinja2 with git/workflow/code intelligence filters
- ❌ Rejected: Custom template language
- Reason: Leverage existing ecosystem, add CodeRef-specific helpers

---

## Status

**Current Phase:** Production (Phase 4 Complete)
**Workorder:** WO-PAPERTRAIL-PYTHON-PACKAGE-001

**Completed:**
- ✅ UDS schema definition
- ✅ Validation engine
- ✅ Health scoring (0-100)
- ✅ Workorder logging
- ✅ MCP tool exposure
- ✅ Template engine with extensions

---

**Maintained by:** CodeRef Ecosystem
**Attribution:** Part of CodeRef v2 ecosystem
