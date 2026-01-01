---
workorder_id: WO-PAPERTRAIL-FOUNDATION-DOCS-001
generated_by: coderef-docs v1.2.0
feature_id: foundation-docs
timestamp: 2025-12-30T00:00:00Z
title: Papertrail - Universal Documentation Standards
version: 1.0.0
status: APPROVED
doc_type: readme
---

# Papertrail - Universal Documentation Standards

**Version:** 1.0.0
**Status:** Production (Phase 4 Complete)
**Workorder:** WO-PAPERTRAIL-PYTHON-PACKAGE-001

## Purpose

Papertrail provides Universal Documentation Standards (UDS) for the CodeRef ecosystem with complete workorder traceability, automatic validation, and health tracking. It enables AI agents to generate high-quality, auditable documentation with automated UDS header/footer injection, schema validation, and quality scoring.

## Overview

Papertrail is a **Python library** that standardizes documentation across the CodeRef ecosystem (5 MCP servers). It ensures every document has:

- **Complete Traceability** - Workorder IDs linking docs to implementation tasks
- **MCP Attribution** - Auto-generated metadata showing which server created the doc
- **Quality Validation** - Schema-based validation with 0-100 scoring
- **Health Monitoring** - 4-factor health scoring (traceability 40%, completeness 30%, freshness 20%, validation 10%)
- **Template Automation** - Jinja2 engine with CodeRef extensions for git, workflow, and code intelligence

**Project Type:** Python Library (not web service)

**Integration:** Embedded in coderef-docs MCP server for automatic UDS injection

---

## What/Why/When

### What is Papertrail?

Papertrail is a **Universal Documentation Standards (UDS) enforcement system** that:

1. **Defines UDS Data Structures** - YAML headers/footers with workorder tracking
2. **Validates Documents** - JSON Schema-based validation for 5 doc types (plan, deliverables, architecture, readme, api)
3. **Scores Document Health** - 0-100 quality metrics across 4 dimensions
4. **Automates Template Rendering** - Jinja2 with UDS injection and CodeRef extensions
5. **Integrates with MCP Servers** - Automatic UDS injection in coderef-docs

### Why Papertrail?

**Problem:** Before Papertrail, CodeRef documentation lacked:

- ❌ Workorder traceability (couldn't link docs to implementation tasks)
- ❌ MCP attribution (unknown which server generated which doc)
- ❌ Quality enforcement (no validation, inconsistent structure)
- ❌ Health monitoring (no way to detect stale/incomplete docs)

**Solution:** Papertrail provides:

- ✅ Complete audit trail (every doc linked to workorder ID)
- ✅ MCP attribution (auto-generated metadata: `generated_by: coderef-docs v1.2.0`)
- ✅ Schema validation (5 JSON schemas enforce structure)
- ✅ Health scoring (0-100 score with breakdown)

### When to Use Papertrail?

**Use Papertrail when:**

- ✅ Generating foundation docs (README, ARCHITECTURE, API, SCHEMA, COMPONENTS)
- ✅ Validating existing documentation
- ✅ Monitoring document health across a project
- ✅ Integrating UDS into custom MCP servers
- ✅ Building AI agents that generate documentation

**Don't use Papertrail for:**

- ❌ Non-CodeRef projects (designed for CodeRef ecosystem)
- ❌ Web service documentation (Papertrail is a library, not API server)
- ❌ Real-time validation (batch processing, not streaming)

---

## Features

### Core Features

1. **UDS Headers/Footers**
   - YAML frontmatter with `workorder_id`, `generated_by`, `feature_id`, `timestamp`
   - YAML footer with copyright, attribution, contributors
   - Auto-generated timestamps and dates

2. **Schema Validation**
   - 5 JSON Schema files for CodeRef doc types
   - Validates required sections (e.g., POWER framework: Purpose, Overview, What/Why/When, Examples, References)
   - Validates metadata patterns (workorder ID format, version numbers, timestamps)
   - Returns structured validation errors with severity levels

3. **Health Scoring**
   - 4-factor scoring: Traceability (40%), Completeness (30%), Freshness (20%), Validation (10%)
   - Auto-detects age from timestamp (<7 days = 20pt, 7-30 days = 10pt, etc.)
   - Identifies missing workorder IDs, feature IDs, MCP attribution

4. **Template Engine**
   - Jinja2-based with UDS injection
   - Extension system for git, coderef-context, workflow integrations
   - Template inheritance, conditionals, includes
   - Auto-injects UDS headers/footers

5. **coderef-docs Integration** (Phase 4)
   - Automatic UDS injection for all 5 doc types
   - Feature flag: `PAPERTRAIL_ENABLED=true` (default: enabled)
   - Backward compatible with legacy generation (set `PAPERTRAIL_ENABLED=false`)

### Supported Document Types

| Type | Description | Required Sections | Schema |
|------|-------------|-------------------|--------|
| **plan** | 10-section implementation plan | META_DOCUMENTATION, 0_preparation, 1_executive_summary, 2_risk_assessment, 3_current_state_analysis, 4_key_features, 5_task_id_system, 6_implementation_phases, 7_testing_strategy, 8_success_criteria, 9_implementation_checklist | `plan.json` |
| **deliverables** | Execution tracking & metrics | Overview, Completion Status, Implementation Metrics, Testing & Validation | `deliverables.json` |
| **architecture** | System architecture (POWER) | Purpose, Overview, What/Why/When, Examples, References | `architecture.json` |
| **readme** | Project overview (POWER) | Purpose, Overview, What/Why/When, Examples, References | `readme.json` |
| **api** | API reference (POWER) | Purpose, Overview, What/Why/When, Examples, References | `api.json` |

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install from Source

```bash
# Clone repository (or navigate to papertrail directory)
cd papertrail/

# Install in development mode
pip install -e .

# Install with dev dependencies (for testing)
pip install -e .[dev]
```

### Verify Installation

```bash
python -c "import papertrail; print(papertrail.__version__)"
# Output: 1.0.0
```

---

## Quick Start

### Example 1: Create UDS Header

```python
from papertrail import UDSHeader, DocumentType, DocumentStatus

header = UDSHeader(
    workorder_id="WO-AUTH-SYSTEM-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="auth-system",
    timestamp="2025-12-30T10:15:00Z",
    title="Authentication System Architecture",
    version="2.1.0",
    status=DocumentStatus.APPROVED,
    doc_type=DocumentType.ARCHITECTURE
)

# Generate YAML frontmatter
yaml_header = header.to_yaml()
print(yaml_header)
```

**Output:**

```yaml
---
workorder_id: WO-AUTH-SYSTEM-001
generated_by: coderef-docs v1.2.0
feature_id: auth-system
timestamp: 2025-12-30T10:15:00Z
title: Authentication System Architecture
version: 2.1.0
status: APPROVED
doc_type: architecture
---
```

### Example 2: Validate Document

```python
from papertrail import validate_uds

doc_content = """
---
workorder_id: WO-AUTH-SYSTEM-001
generated_by: coderef-docs v1.2.0
feature_id: auth-system
timestamp: 2025-12-30T10:15:00Z
---

# Architecture

## Purpose
System architecture overview

## Overview
...

## What/Why/When
...

## Examples
...

## References
...
"""

result = validate_uds(doc_content, "architecture")
print(f"Valid: {result.valid}, Score: {result.score}/100")
```

**Output:**

```
Valid: True, Score: 100/100
```

### Example 3: Calculate Health Score

```python
from papertrail import calculate_health

health = calculate_health(doc_content, "architecture")
print(f"Health Score: {health.score}/100")
print(f"  Traceability: {health.traceability}/40")
print(f"  Completeness: {health.completeness}/30")
print(f"  Freshness: {health.freshness}/20")
print(f"  Validation: {health.validation}/10")
```

**Output:**

```
Health Score: 100/100
  Traceability: 40/40
  Completeness: 30/30
  Freshness: 20/20
  Validation: 10/10
```

### Example 4: Render Template with UDS

```python
from papertrail import TemplateEngine, create_uds_header, create_uds_footer

# Create header and footer
header = create_uds_header(
    workorder_id="WO-FEATURE-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="my-feature",
    title="My Feature"
)

footer = create_uds_footer(
    workorder_id="WO-FEATURE-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="my-feature"
)

# Render template
engine = TemplateEngine()
template = """
# {{ title }}

## Purpose
{{ purpose }}
"""

context = {"title": "Architecture", "purpose": "System overview"}
doc = engine.render_with_uds(template, context, header, footer)

print(doc)
```

**Output:**

```markdown
---
workorder_id: WO-FEATURE-001
generated_by: coderef-docs v1.2.0
feature_id: my-feature
timestamp: 2025-12-30T10:15:23Z
title: My Feature
---

# Architecture

## Purpose
System overview

---
Copyright © 2025 | CodeRef Ecosystem
Generated by: coderef-docs v1.2.0
Workorder: WO-FEATURE-001
Feature: my-feature
Last Updated: 2025-12-30
AI Assistance: true
Next Review: 2026-12-30
---
```

---

## Examples

### Complete Workflow Example

```python
from papertrail import (
    create_uds_header,
    create_uds_footer,
    TemplateEngine,
    validate_uds,
    calculate_health,
    DocumentStatus,
    DocumentType
)

# 1. Create UDS header
header = create_uds_header(
    workorder_id="WO-AUTH-SYSTEM-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="auth-system",
    title="Authentication System Architecture",
    version="2.1.0",
    status=DocumentStatus.APPROVED,
    doc_type=DocumentType.ARCHITECTURE
)

# 2. Create UDS footer
footer = create_uds_footer(
    workorder_id="WO-AUTH-SYSTEM-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="auth-system",
    status=DocumentStatus.APPROVED,
    contributors=["Agent1", "Agent2"]
)

# 3. Render template with UDS
engine = TemplateEngine()

template = """
# {{ title }}

## Purpose
This document describes the authentication system architecture.

## Overview
- JWT-based authentication
- OAuth 2.0 integration
- Role-based access control

## What/Why/When
**What:** Secure authentication and authorization system
**Why:** Protect user data and control access to resources
**When:** Required for all authenticated endpoints

## Examples
```python
from auth import authenticate_user
user = authenticate_user(username, password)
```

## References
- [OAuth 2.0 Spec](https://oauth.net/2/)
- [JWT Best Practices](https://jwt.io/)
"""

context = {"title": "Authentication System Architecture"}
doc = engine.render_with_uds(template, context, header, footer)

# 4. Validate document
result = validate_uds(doc, "architecture")
print(f"Valid: {result.valid}, Score: {result.score}/100")

# 5. Calculate health score
health = calculate_health(doc, "architecture")
print(f"Health Score: {health.score}/100")
print(f"  Traceability: {health.traceability}/40")
print(f"  Completeness: {health.completeness}/30")
print(f"  Freshness: {health.freshness}/20")
print(f"  Validation: {health.validation}/10")

# 6. Save document
with open("ARCHITECTURE.md", "w") as f:
    f.write(doc)

print("✅ Document generated successfully!")
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PAPERTRAIL_ENABLED` | `true` | Enable UDS injection in coderef-docs MCP server |

**Enable UDS injection (default):**

```bash
export PAPERTRAIL_ENABLED=true
```

**Disable UDS injection (legacy mode):**

```bash
export PAPERTRAIL_ENABLED=false
```

---

## Integration with coderef-docs (Phase 4)

Papertrail is fully integrated into **coderef-docs** MCP server for automatic UDS injection:

### MCP Tool Usage

```python
# Generate document with UDS using MCP tool
{
  "tool": "generate_individual_doc",
  "arguments": {
    "project_path": "/path/to/project",
    "template_name": "readme",
    "workorder_id": "WO-FEATURE-001",  # Optional: enables UDS
    "feature_id": "my-feature",        # Optional: defaults to template_name
    "version": "1.0.0"                 # Optional: defaults to 1.0.0
  }
}
```

**Result:** Complete document with UDS headers/footers automatically injected.

### Supported Document Types

- README.md
- ARCHITECTURE.md
- API.md
- SCHEMA.md
- COMPONENTS.md

### Feature Flag

Set `PAPERTRAIL_ENABLED=false` to use legacy generation (backward compatible).

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=papertrail

# Run specific test file
pytest tests/test_uds.py

# Run Phase 4 integration tests (coderef-docs)
cd ../coderef-docs
python test_phase4_all_docs.py
```

### Test Status

- ✅ **Phase 1**: Core UDS (31/31 tests passing)
- ✅ **Phase 2**: Template Engine (44/44 tests passing)
- ✅ **Phase 3**: coderef-docs integration (6/6 tests passing)
- ✅ **Phase 4**: Gradual rollout (5/5 doc types passing)

**Total:** 86/86 tests passing | Status: **Production Ready**

### Code Formatting

```bash
# Format code with black
black papertrail/

# Type checking with mypy
mypy papertrail/
```

---

## Troubleshooting

### Issue 1: Missing UDS Header in Generated Documents

**Symptom:**

```markdown
# Architecture

## Purpose
...

<!-- ❌ Missing UDS header -->
```

**Cause:** `PAPERTRAIL_ENABLED=false` (legacy mode)

**Solution:**

```bash
# Enable Papertrail
export PAPERTRAIL_ENABLED=true

# Regenerate documents
cd coderef-docs
python -c "from server import generate_individual_doc; ..."
```

### Issue 2: Validation Errors for Workorder ID

**Symptom:**

```
ValidationResult(
    valid=False,
    errors=[ValidationError(message="Field 'workorder_id' does not match required pattern")]
)
```

**Cause:** Invalid workorder ID format (requires ≥2 segments before 3-digit ID)

**Solution:**

```python
# ❌ Invalid: WO-AUTH-001 (missing category)
# ✅ Valid: WO-AUTH-SYSTEM-001 (2 segments + 3 digits)

header = create_uds_header(
    workorder_id="WO-AUTH-SYSTEM-001",  # ✅ Correct format
    ...
)
```

### Issue 3: Low Health Score

**Symptom:**

```
Health Score: 50/100
  Traceability: 20/40  # ❌ Missing feature_id
  Freshness: 0/20      # ❌ Document >90 days old
```

**Solution:**

```python
# 1. Add missing metadata
header = create_uds_header(
    workorder_id="WO-FEATURE-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="my-feature",  # ✅ Add feature_id
    ...
)

# 2. Update timestamp to current date
# (auto-generated by create_uds_header())
```

### Issue 4: Schema Validation Failed

**Symptom:**

```
ValidationResult(
    valid=False,
    errors=[ValidationError(message="Missing required section: Examples")]
)
```

**Cause:** Document missing required section (POWER framework requires 5 sections)

**Solution:**

```markdown
# Architecture

## Purpose
...

## Overview
...

## What/Why/When
...

## Examples  ✅ Add missing section
...

## References
...
```

---

## Project Structure

```
papertrail/
├── papertrail/
│   ├── __init__.py           # Public API
│   ├── uds.py                # UDSHeader, UDSFooter classes
│   ├── validator.py          # Schema validation
│   ├── health.py             # Health scoring
│   ├── engine.py             # Template engine (Phase 2)
│   ├── extensions/           # CodeRef extensions (Phase 2)
│   │   ├── coderef_context.py
│   │   ├── git_integration.py
│   │   └── workflow.py
│   └── schemas/              # JSON schemas
│       ├── plan.json
│       ├── deliverables.json
│       ├── architecture.json
│       ├── readme.json
│       └── api.json
├── tests/                    # Unit tests (86 tests)
│   ├── test_uds.py
│   ├── test_validator.py
│   ├── test_health.py
│   └── test_engine.py
├── coderef/                  # Foundation docs (generated)
│   └── foundation-docs/
│       ├── API.md
│       ├── SCHEMA.md
│       ├── COMPONENTS.md
│       └── ARCHITECTURE.md
├── setup.py                  # Package configuration
└── README.md                 # This file
```

---

## References

- **[API Reference](coderef/foundation-docs/API.md)** - Complete API documentation
- **[Schema Reference](coderef/foundation-docs/SCHEMA.md)** - Data schemas and validation rules
- **[Component Library](coderef/foundation-docs/COMPONENTS.md)** - Reusable components
- **[Architecture](coderef/foundation-docs/ARCHITECTURE.md)** - System architecture
- **[coderef-docs Integration](../coderef-docs/CLAUDE.md)** - MCP server integration
- **[JSON Schema Spec](https://json-schema.org/draft-07/schema)** - Schema format
- **[Jinja2 Docs](https://jinja.palletsprojects.com/)** - Template engine

---

## License

MIT License

Copyright © 2025 CodeRef Ecosystem

---

Copyright © 2025 | CodeRef Ecosystem
Generated by: coderef-docs v1.2.0
Workorder: WO-PAPERTRAIL-FOUNDATION-DOCS-001
Feature: foundation-docs
Last Updated: 2025-12-30
AI Assistance: true
Status: APPROVED
