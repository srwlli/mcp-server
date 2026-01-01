---
workorder_id: WO-PAPERTRAIL-FOUNDATION-DOCS-001
generated_by: coderef-docs v1.2.0
feature_id: foundation-docs
timestamp: 2025-12-30T00:00:00Z
title: Papertrail System Architecture
version: 1.0.0
status: APPROVED
doc_type: architecture
---

# Papertrail System Architecture

## Purpose

This document defines the system architecture of Papertrail, the Universal Documentation Standards (UDS) package for the CodeRef ecosystem. It explains how Papertrail integrates with MCP servers (coderef-docs, coderef-workflow) to provide automated document validation, health scoring, and template rendering with complete workorder traceability.

## Overview

Papertrail is a **Python library** (not a web service) that provides:

1. **UDS Data Structures** - YAML frontmatter (headers/footers) with workorder tracking
2. **Schema Validation** - JSON Schema-based validation for 5 document types
3. **Health Scoring** - 0-100 quality metrics (traceability, completeness, freshness, validation)
4. **Template Engine** - Jinja2 with UDS injection and CodeRef extensions
5. **MCP Integration** - Automatic UDS injection in coderef-docs MCP server

**Architecture Type:** Modular Python library with extension system

**Design Pattern:** Layered architecture with clean separation between data, validation, scoring, and rendering

---

## System Topology

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   CodeRef Ecosystem                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  coderef-    │  │  coderef-    │  │  coderef-    │      │
│  │  workflow    │  │    docs      │  │  context     │      │
│  │     MCP      │  │     MCP      │  │     MCP      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│                           ▼                                 │
│              ┌─────────────────────────┐                    │
│              │     Papertrail          │                    │
│              │  (UDS Provider)         │                    │
│              │                         │                    │
│              │  ┌─────────────────┐   │                    │
│              │  │  Public API     │   │                    │
│              │  │  (__init__.py)  │   │                    │
│              │  └────────┬────────┘   │                    │
│              │           │            │                    │
│              │  ┌────────┼────────┐  │                    │
│              │  │        │        │  │                    │
│              │  ▼        ▼        ▼  │                    │
│              │ UDS    Validator  Health│                    │
│              │         Engine          │                    │
│              │                         │                    │
│              │  ┌─────────────────┐   │                    │
│              │  │   Extensions    │   │                    │
│              │  │  (git, coderef, │   │                    │
│              │  │   workflow)     │   │                    │
│              │  └─────────────────┘   │                    │
│              └─────────────────────────┘                    │
│                           │                                 │
│                           ▼                                 │
│              ┌─────────────────────────┐                    │
│              │   5 Document Schemas    │                    │
│              │  (JSON Schema Draft 07) │                    │
│              └─────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

### Module Boundaries

```
papertrail/
│
├── __init__.py                 # Public API Layer
│   ├─> Exports: UDSHeader, UDSFooter, validate_uds, calculate_health, etc.
│   └─> Entry point for all external integrations
│
├── uds.py                      # Data Layer
│   ├─> UDSHeader, UDSFooter dataclasses
│   ├─> DocumentType, DocumentStatus enums
│   └─> create_uds_header(), create_uds_footer() factories
│
├── validator.py                # Validation Layer
│   ├─> UDSValidator (schema-based validation)
│   ├─> ValidationResult, ValidationError
│   └─> validate_workorder_id(), validate_feature_id()
│
├── health.py                   # Scoring Layer
│   ├─> HealthScorer (4-factor scoring: 40% + 30% + 20% + 10%)
│   ├─> HealthScore dataclass
│   └─> store_health_score(), load_health_score()
│
├── engine.py                   # Rendering Layer
│   ├─> TemplateEngine (Jinja2-based)
│   ├─> inject_uds(), render_with_uds()
│   └─> Extension registration system
│
├── extensions/                 # Integration Layer
│   ├── coderef_context.py     # Code intelligence (scan, query, impact)
│   ├── git_integration.py     # Git stats (commits, files, contributors)
│   └── workflow.py            # Workflow data (plan, tasks, progress)
│
└── schemas/                    # Schema Layer
    ├── plan.json              # 10-section implementation plan
    ├── deliverables.json      # Execution tracking & metrics
    ├── architecture.json      # POWER framework (architecture)
    ├── readme.json            # POWER framework (readme)
    └── api.json               # POWER framework (api)
```

**Dependency Flow:**

```
┌───────────────┐
│ Public API    │  (External integrations call here)
└───────┬───────┘
        │
        ├──> UDS Data Layer (uds.py)
        ├──> Validation Layer (validator.py)
        ├──> Scoring Layer (health.py)
        ├──> Rendering Layer (engine.py)
        └──> Extensions Layer (extensions/)
                │
                └──> Schemas Layer (schemas/*.json)
```

---

## Stack Decisions

### Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Language** | Python 3.8+ | CodeRef ecosystem standard, type hints support |
| **Data Models** | `dataclasses` | Built-in, type-safe, zero dependencies |
| **Schema Validation** | JSON Schema Draft 07 | Industry standard, widely supported |
| **Template Engine** | Jinja2 | Mature, powerful, CodeRef ecosystem standard |
| **YAML Parsing** | `PyYAML` | Standard Python YAML library |
| **Testing** | `pytest` | CodeRef ecosystem standard |
| **Type Checking** | Type hints + `mypy` | Static analysis for reliability |
| **Package Management** | `setuptools` | Standard Python packaging |

### Key Design Decisions

#### 1. Dataclasses over Plain Dicts

**Decision:** Use Python `dataclasses` for UDSHeader, UDSFooter, ValidationResult, etc.

**Rationale:**

- ✅ Type safety with built-in type hints
- ✅ Auto-generated `__init__()`, `__repr__()`, `__eq__()`
- ✅ IDE autocomplete and validation
- ✅ Zero dependencies (built-in since Python 3.7)
- ❌ Alternative rejected: Plain dicts (no type safety, error-prone)

**Example:**

```python
@dataclass
class UDSHeader:
    workorder_id: str
    generated_by: str
    feature_id: str
    timestamp: str
```

#### 2. JSON Schema for Validation

**Decision:** Use JSON Schema Draft 07 for document validation.

**Rationale:**

- ✅ Declarative validation rules (no imperative code)
- ✅ Industry standard format
- ✅ Supports patterns, enums, required fields
- ✅ Extensible for future document types
- ❌ Alternative rejected: Custom validation code (harder to maintain, not portable)

**Example:**

```json
{
  "required_metadata": {
    "workorder_id": {
      "pattern": "^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\\d{3}$"
    }
  }
}
```

#### 3. Jinja2 for Templating

**Decision:** Use Jinja2 as the template engine.

**Rationale:**

- ✅ Already used by coderef-docs MCP server (consistency)
- ✅ Supports inheritance, includes, conditionals
- ✅ Extensible with custom filters/functions
- ✅ Mature, well-documented, widely adopted
- ❌ Alternative rejected: String formatting (no logic, limited features)

**Example:**

```jinja2
# {{ title }}

{% if status == "APPROVED" %}
✅ Approved
{% else %}
⏳ Pending approval
{% endif %}
```

#### 4. YAML for Headers/Footers

**Decision:** Use YAML frontmatter for UDS headers/footers (not JSON).

**Rationale:**

- ✅ Human-readable (better for markdown documents)
- ✅ Standard format for markdown metadata (e.g., Jekyll, Hugo)
- ✅ Supports comments (useful for documentation)
- ✅ Cleaner syntax than JSON
- ❌ Alternative rejected: JSON frontmatter (less readable, no comments)

**Example:**

```yaml
---
workorder_id: WO-AUTH-SYSTEM-001
generated_by: coderef-docs v1.2.0
feature_id: auth-system
timestamp: 2025-12-30T10:15:00Z
---
```

#### 5. Modular Package Structure

**Decision:** Separate modules for uds, validator, health, engine, extensions.

**Rationale:**

- ✅ Single Responsibility Principle (SRP)
- ✅ Easier testing (each module tested independently)
- ✅ Clear boundaries between concerns
- ✅ Easier to extend (add new validators, scorers, extensions)
- ❌ Alternative rejected: Monolithic module (harder to maintain, test, extend)

**Module Breakdown:**

```
papertrail/
├── uds.py          # Data structures only
├── validator.py    # Validation logic only
├── health.py       # Scoring logic only
├── engine.py       # Rendering logic only
└── extensions/     # Integration logic only
```

---

## Data Flow

### Document Generation Flow

```
1. MCP Server (coderef-docs)
        │
        ├─ generate_individual_doc(workorder_id, feature_id, template_name)
        │
        ▼
2. Papertrail: create_uds_header()
        │
        ├─ workorder_id: WO-FEATURE-001
        ├─ generated_by: coderef-docs v1.2.0
        ├─ feature_id: my-feature
        └─ timestamp: 2025-12-30T10:15:00Z (auto-generated)
        │
        ▼
3. Papertrail: create_uds_footer()
        │
        ├─ last_updated: 2025-12-30 (auto-generated)
        └─ next_review: 2026-12-30 (auto-generated +1 year)
        │
        ▼
4. TemplateEngine: render_with_uds()
        │
        ├─ Load template (Jinja2)
        ├─ Inject context variables
        ├─ Render template
        ├─ Inject UDS header (YAML frontmatter)
        └─ Inject UDS footer (YAML footer)
        │
        ▼
5. Complete Document with UDS
        │
        ├─ UDS Header (---\nworkorder_id: ...\n---)
        ├─ Document Body (# Title\n## Purpose\n...)
        └─ UDS Footer (---\nCopyright © 2025...\n---)
        │
        ▼
6. Save to disk (coderef/foundation-docs/)
```

### Validation Flow

```
1. Document (markdown or JSON)
        │
        ▼
2. UDSValidator: validate(document, doc_type)
        │
        ├─ Extract YAML frontmatter (header)
        │   └─> _extract_header() → dict
        │
        ├─ Validate metadata
        │   ├─> Check required fields (workorder_id, generated_by, etc.)
        │   ├─> Check field patterns (regex validation)
        │   └─> Generate ValidationError objects
        │
        ├─ Validate sections
        │   ├─> Check required sections present (e.g., "Purpose", "Overview")
        │   ├─> Match section headings (markdown #, ##, ###)
        │   └─> Generate ValidationError objects
        │
        ├─ Calculate validation score
        │   ├─> CRITICAL error: -50 points
        │   ├─> MAJOR error: -20 points
        │   ├─> MINOR error: -10 points
        │   └─> WARNING: -5 points
        │
        ▼
3. ValidationResult
        │
        ├─ valid: bool (no CRITICAL errors)
        ├─ errors: list[ValidationError]
        ├─ warnings: list[str]
        └─ score: int (0-100)
```

### Health Scoring Flow

```
1. Document (markdown or JSON)
        │
        ▼
2. HealthScorer: calculate_health(document, doc_type)
        │
        ├─ Extract YAML frontmatter
        │   └─> _extract_header() → dict
        │
        ├─ Calculate Traceability (40 points max)
        │   ├─> Has workorder_id? +20
        │   ├─> Has feature_id? +10
        │   └─> Has MCP attribution (generated_by)? +10
        │
        ├─ Calculate Completeness (30 points max)
        │   ├─> All required sections present? +20
        │   └─> Has examples (code blocks or "Examples" heading)? +10
        │
        ├─ Calculate Freshness (20 points max)
        │   ├─> <7 days old: +20
        │   ├─> 7-30 days old: +10
        │   ├─> 30-90 days old: +5
        │   └─> >90 days old: 0
        │
        ├─ Calculate Validation (10 points max)
        │   └─> Passes schema validation? +10
        │
        ▼
3. HealthScore
        │
        ├─ score: int (0-100)
        ├─ traceability: int (0-40)
        ├─ completeness: int (0-30)
        ├─ freshness: int (0-20)
        ├─ validation: int (0-10)
        ├─ has_workorder_id: bool
        ├─ has_feature_id: bool
        ├─ has_mcp_attribution: bool
        ├─ age_days: int
        └─ passes_validation: bool
```

---

## Component Diagrams

### UDS Header/Footer Injection

```
┌─────────────────────────────────────────────────────────┐
│  Template Content (Jinja2)                              │
│                                                          │
│  # {{ title }}                                           │
│                                                          │
│  ## Purpose                                              │
│  {{ purpose }}                                           │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼ render()
┌─────────────────────────────────────────────────────────┐
│  Rendered Content                                        │
│                                                          │
│  # Architecture                                          │
│                                                          │
│  ## Purpose                                              │
│  System architecture overview                            │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼ inject_uds()
┌─────────────────────────────────────────────────────────┐
│  Complete Document with UDS                              │
│                                                          │
│  ---                                                     │
│  workorder_id: WO-FEATURE-001                           │
│  generated_by: coderef-docs v1.2.0                      │
│  feature_id: my-feature                                 │
│  timestamp: 2025-12-30T10:15:00Z                        │
│  ---                                                     │
│                                                          │
│  # Architecture                                          │
│                                                          │
│  ## Purpose                                              │
│  System architecture overview                            │
│                                                          │
│  ---                                                     │
│  Copyright © 2025 | CodeRef Ecosystem                   │
│  Generated by: coderef-docs v1.2.0                      │
│  Workorder: WO-FEATURE-001                              │
│  Feature: my-feature                                    │
│  Last Updated: 2025-12-30                               │
│  AI Assistance: true                                    │
│  ---                                                     │
└─────────────────────────────────────────────────────────┘
```

### Extension System

```
┌────────────────────────────────────────┐
│      TemplateEngine                    │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │   Jinja2 Environment             │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │   Extension Registry             │ │
│  │                                  │ │
│  │   extensions = {                │ │
│  │     'git': GitExtension(),      │ │
│  │     'coderef': CodeRefExt(),    │ │
│  │     'workflow': WorkflowExt()   │ │
│  │   }                              │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
                │
                ├─ Template uses: {{ git.stats('feature') }}
                │                 {{ coderef.scan('/path') }}
                │                 {{ workflow.plan('feature') }}
                │
                ▼
┌────────────────────────────────────────┐
│     Extensions (Python Objects)        │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  GitExtension                    │ │
│  │  ├─ stats(feature_name)          │ │
│  │  ├─ files_changed(feature_name)  │ │
│  │  └─ contributors(feature_name)   │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  CodeRefContextExtension         │ │
│  │  ├─ scan(project_path)           │ │
│  │  ├─ query(target)                │ │
│  │  └─ impact(element)              │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  WorkflowExtension               │ │
│  │  ├─ plan(feature_name)           │ │
│  │  ├─ tasks(feature_name)          │ │
│  │  └─ progress(feature_name)       │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

---

## Security Considerations

### 1. Template Injection Prevention

**Risk:** Malicious template code execution via Jinja2.

**Mitigation:**

- ✅ Templates are controlled by coderef-docs MCP server (not user input)
- ✅ Jinja2 sandboxing enabled (no arbitrary Python code execution)
- ✅ No `eval()`, `exec()`, or `__import__()` in templates
- ✅ Extension methods are whitelisted (not dynamically loaded)

**Example Safe Template:**

```jinja2
# {{ title }}  ✅ Safe: Variable substitution only
```

**Example Unsafe Template (blocked):**

```jinja2
{{ ''.__class__.__mro__[1].__subclasses__() }}  ❌ Blocked: Sandbox prevents
```

### 2. Schema Validation Input

**Risk:** Malicious YAML input causing parsing errors or DoS.

**Mitigation:**

- ✅ Use `yaml.safe_load()` (not `yaml.load()` which executes Python)
- ✅ Validate YAML structure before processing
- ✅ Reject documents with invalid YAML frontmatter

**Example:**

```python
try:
    header = yaml.safe_load(frontmatter)  # ✅ Safe
except yaml.YAMLError:
    return ValidationResult(valid=False, ...)
```

### 3. File System Access

**Risk:** Path traversal or unauthorized file access.

**Mitigation:**

- ✅ Papertrail does NOT read/write files directly
- ✅ MCP servers (coderef-docs, coderef-workflow) handle file I/O
- ✅ All paths are validated by MCP servers before passing to Papertrail

**Responsibility:**

- Papertrail: Data processing only (no file I/O)
- MCP servers: File I/O with path validation

### 4. Workorder ID Validation

**Risk:** Invalid workorder IDs causing audit trail corruption.

**Mitigation:**

- ✅ Strict regex validation: `^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\d{3}$`
- ✅ Requires ≥2 segments before final 3 digits
- ✅ Validated before storing in UDSHeader

**Example:**

```python
validate_workorder_id("WO-AUTH-SYSTEM-001")  # ✅ Valid
validate_workorder_id("WO-AUTH-001")         # ❌ Invalid (missing category)
validate_workorder_id("DROP TABLE users")    # ❌ Invalid (no match)
```

---

## Performance Considerations

### 1. Schema Loading

**Challenge:** Loading 5 JSON schemas on every validation call.

**Optimization:**

- ✅ Schemas loaded once during `UDSValidator` initialization
- ✅ Cached in `self.schemas` dict for reuse
- ✅ No disk I/O on subsequent validations

**Impact:** ~10ms (first call) → <1ms (subsequent calls)

### 2. YAML Parsing

**Challenge:** Parsing YAML frontmatter on every validation/health check.

**Optimization:**

- ✅ Use `re.match()` to extract frontmatter (no full document parse)
- ✅ Parse only the frontmatter section (typically <20 lines)
- ✅ Cache parsed header in memory for multi-step processing

**Impact:** ~5ms per document (acceptable for typical use case)

### 3. Template Rendering

**Challenge:** Jinja2 template compilation overhead.

**Optimization:**

- ✅ Jinja2 auto-caches compiled templates
- ✅ Use `Environment.from_string()` for simple templates
- ✅ Use `Environment.get_template()` for file-based templates (cached)

**Impact:** ~20ms (first render) → <5ms (subsequent renders)

### 4. Health Score Calculation

**Challenge:** Multiple passes over document (validation + health scoring).

**Optimization:**

- ✅ Validation result cached and reused in health calculation
- ✅ Single regex scan for section headings (not per-section)
- ✅ Lazy evaluation for optional fields (skip if not needed)

**Impact:** ~15ms per document (combined validation + health)

---

## Deployment Architecture

### Integration with coderef-docs MCP Server

**Deployment Model:** Embedded library (not standalone service)

```
┌────────────────────────────────────────────────────────┐
│             coderef-docs MCP Server                    │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  MCP Tools (generate_individual_doc, etc.)       │ │
│  └──────────────────────────────────────────────────┘ │
│                         │                              │
│                         ▼                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Papertrail (imported as library)                │ │
│  │                                                  │ │
│  │  import papertrail                               │ │
│  │  header = papertrail.create_uds_header(...)      │ │
│  │  doc = engine.render_with_uds(...)               │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   File System        │
              │                      │
              │  coderef/            │
              │  └─ foundation-docs/ │
              │     ├─ README.md     │
              │     ├─ ARCHITECTURE.md│
              │     └─ API.md        │
              └──────────────────────┘
```

**Installation:**

```bash
# Install Papertrail as dependency
cd papertrail/
pip install -e .

# coderef-docs imports Papertrail
cd ../coderef-docs/
python server.py
```

**Feature Flag:**

```bash
# Enable UDS injection in coderef-docs
export PAPERTRAIL_ENABLED=true

# Disable UDS injection (legacy mode)
export PAPERTRAIL_ENABLED=false
```

---

## References

- [Papertrail API Reference](./API.md) - Complete API documentation
- [Papertrail Schema Reference](./SCHEMA.md) - Data schemas and validation rules
- [Papertrail Component Library](./COMPONENTS.md) - Reusable components
- [Papertrail README](../../README.md) - Project overview and installation
- [JSON Schema Specification](https://json-schema.org/draft-07/schema) - Schema format
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Template engine
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html) - Data structures

---

Copyright © 2025 | CodeRef Ecosystem
Generated by: coderef-docs v1.2.0
Workorder: WO-PAPERTRAIL-FOUNDATION-DOCS-001
Feature: foundation-docs
Last Updated: 2025-12-30
AI Assistance: true
Status: APPROVED
