---
agent: coderef-docs v1.2.0
date: 2026-01-10
task: DOCUMENT
workorder_id: WO-UDS-SYSTEM-001
generated_by: coderef-docs v1.2.0
feature_id: uds-comprehensive-system
timestamp: 2026-01-10T12:00:00Z
title: Papertrail - Universal Documentation Standards
version: 1.0.0
status: APPROVED
doc_type: readme
---

# Papertrail

**Version:** 1.0.0
**Type:** Python Library + MCP Server
**Purpose:** Universal Documentation Standards (UDS) enforcement for CodeRef ecosystem

---

## Purpose

Papertrail provides a comprehensive Python library and MCP server for enforcing Universal Documentation Standards (UDS) across the CodeRef ecosystem. It ensures every document has complete traceability, automated quality validation, health monitoring, and MCP attribution through standardized headers, footers, and schema-based validation.

---

## Overview

Papertrail solves the problem of inconsistent documentation by providing:

- **UDS Schema Validation** - Automated document structure validation with 0-100 scoring
- **Workorder Traceability** - Complete WO-ID linking for all generated documentation
- **Template Engine** - Jinja2-based rendering with CodeRef extensions (git, workflow, code intelligence)
- **Health Monitoring** - 4-factor scoring system (traceability 40%, completeness 30%, freshness 20%, validation 10%)
- **MCP Integration** - 6 MCP tools for validation, health checking, and workorder tracking

---

## Project Structure

```
papertrail/
├── papertrail/
│   ├── extensions/           # Jinja2 template extensions
│   │   ├── coderef_context.py   # CodeRef code intelligence integration
│   │   ├── git_integration.py    # Git statistics and contributor tracking
│   │   └── workflow.py          # Workflow plan and task integration
│   ├── engine.py             # Template rendering engine with UDS injection
│   ├── health.py             # Health scoring (0-100) for documents
│   ├── uds.py                # UDS header/footer data models
│   └── validator.py          # UDS schema validation
├── tests/                    # Comprehensive test suite
├── schemas/                  # JSON schemas for UDS validation
└── coderef/                  # Foundation documentation
```

---

## Key Components

### Core Modules

1. **TemplateEngine** (`engine.py:20`) - Jinja2-based template rendering with UDS injection
   - Renders templates with CodeRef extensions
   - Injects UDS headers and footers automatically
   - Supports template inheritance and includes

2. **UDSValidator** (`validator.py:51`) - Schema-based document validation
   - Validates document structure against UDS schema
   - Checks workorder ID and feature ID formats
   - Calculates validation scores (0-100)

3. **HealthScorer** (`health.py:50`) - 4-factor health scoring
   - Traceability (40%): workorder_id, feature_id, MCP attribution
   - Completeness (30%): required sections, examples, cross-references
   - Freshness (20%): document age (< 7 days = 100%, > 90 days = 0%)
   - Validation (10%): passes UDS schema validation

4. **UDSHeader** (`uds.py:34`) - Standardized document headers
   - Document metadata (title, type, version, status)
   - Workorder and feature tracking
   - Created/updated timestamps

5. **UDSFooter** (`uds.py:116`) - Standardized document footers
   - MCP attribution
   - Contributor tracking
   - Generation metadata

### Jinja2 Extensions

1. **GitExtension** (`extensions/git_integration.py:16`)
   - `git.stats()` - Repository statistics (commits, contributors, files)
   - `git.files()` - Recent file changes
   - `git.contributors()` - Contributor list with commit counts
   - `git.last_commit()` - Most recent commit metadata

2. **WorkflowExtension** (`extensions/workflow.py:15`)
   - `workflow.plan()` - Load implementation plan from plan.json
   - `workflow.tasks()` - Extract tasks by phase or status
   - `workflow.progress()` - Calculate completion percentage

3. **CodeRefContextExtension** (`extensions/coderef_context.py:15`)
   - `coderef.scan()` - Scan project for code elements
   - `coderef.query()` - Query code relationships (calls, imports, dependencies)
   - `coderef.impact()` - Analyze impact of code changes

---

## Getting Started

### Installation

```bash
# Install from source
cd papertrail
pip install -e .

# Install dependencies
pip install jinja2 pydantic jsonschema
```

### Basic Usage

```python
from papertrail import create_template_engine, validate_uds, calculate_health

# 1. Create template engine with extensions
engine = create_template_engine(
    template_dir="templates/",
    project_path="/path/to/project",
    extensions=["git", "workflow", "coderef"]
)

# 2. Render template with UDS
result = engine.render_file("plan.md.j2", {
    "workorder_id": "WO-FEATURE-001",
    "feature_name": "authentication"
})

# 3. Validate generated document
validation = validate_uds(result, doc_type="plan")
print(f"Validation Score: {validation.score}/100")

# 4. Calculate health score
health = calculate_health(result, doc_type="plan")
print(f"Health Score: {health.total_score}/100")
```

### MCP Integration

```python
# Available MCP tools:
# - validate_document(document_path, doc_type)
# - check_document_health(document_path, doc_type)
# - log_workorder(workorder_id, project_name, description)
# - get_workorder_log(project_path, filters)
# - inject_uds_headers(content, metadata)
# - generate_from_template(template_path, context)
```

---

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture, dependency diagrams, and design patterns.

See [API.md](./API.md) for complete API reference of all classes and functions.

---

## Key Features

- **Zero-Config UDS Compliance** - Automatic header/footer injection with standardized YAML format
- **4-Factor Health Scoring** - Weighted scoring across traceability, completeness, freshness, validation
- **Workorder Tracking** - Global audit trail for all documentation generation
- **Template Extensions** - Rich Jinja2 filters for git, workflow, and code intelligence data
- **Schema Validation** - JSON schema-based validation with detailed error reporting
- **MCP Server** - 6 tools for agent-driven documentation workflows

---

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_engine.py
pytest tests/test_health.py
pytest tests/test_validator.py
pytest tests/test_uds.py

# Run with coverage
pytest --cov=papertrail tests/
```

---

## Integration with CodeRef Ecosystem

**Used by:**
- **coderef-docs** - Document generation with UDS compliance
- **coderef-workflow** - Workorder logging and tracking
- **All MCP servers** - Documentation validation and health monitoring

**Provides:**
- Universal Documentation Standards (UDS) schema
- Automated validation and health scoring
- Template engine with CodeRef extensions
- Workorder traceability infrastructure

---

## Resources

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and design patterns
- **[API.md](./API.md)** - Complete API reference
- **[CLAUDE.md](../../CLAUDE.md)** - AI context documentation
- **[README.md](../../README.md)** - User-facing documentation

---

**Maintained by:** CodeRef Ecosystem
**License:** MIT
**Python Version:** 3.10+
