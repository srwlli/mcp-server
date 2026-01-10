---
agent: coderef-docs v1.2.0
date: '2026-01-10'
task: DOCUMENT
workorder_id: WO-PAPERTRAIL-FOUNDATION-DOCS-001
generated_by: coderef-docs v1.2.0
feature_id: foundation-docs
timestamp: '2025-12-30T00:00:00Z'
title: Papertrail Component Library
version: 1.0.0
status: APPROVED
doc_type: components
---

# Papertrail Component Library

## Purpose

This document provides a complete inventory of Papertrail's reusable Python components, including modules, classes, functions, and extensions. It serves as a quick reference for developers integrating Papertrail into their projects or extending its functionality.

## Overview

Papertrail is structured as a modular Python package with 5 core modules and 3 extension modules:

**Core Modules:**

1. **papertrail.uds** - UDS data structures (headers, footers, enums)
2. **papertrail.validator** - Schema validation and metadata checking
3. **papertrail.health** - Document health scoring
4. **papertrail.engine** - Template engine with Jinja2
5. **papertrail.extensions** - CodeRef MCP integrations

**Project Type:** Python Library (not UI framework)

**Framework:** Python 3.8+ with dataclasses and type hints

---

## Component Hierarchy

```
papertrail/
├── __init__.py                 # Public API exports
├── uds.py                      # UDS data structures
│   ├── UDSHeader
│   ├── UDSFooter
│   ├── DocumentType (enum)
│   ├── DocumentStatus (enum)
│   ├── create_uds_header()
│   └── create_uds_footer()
├── validator.py                # Validation components
│   ├── UDSValidator
│   ├── ValidationResult
│   ├── ValidationError
│   ├── ValidationSeverity (enum)
│   ├── validate_uds()
│   ├── validate_workorder_id()
│   └── validate_feature_id()
├── health.py                   # Health scoring components
│   ├── HealthScorer
│   ├── HealthScore
│   ├── calculate_health()
│   ├── store_health_score()
│   └── load_health_score()
├── engine.py                   # Template engine components
│   ├── TemplateEngine
│   └── create_template_engine()
└── extensions/                 # CodeRef integrations
    ├── __init__.py
    ├── coderef_context.py     # CodeRefContextExtension
    ├── git_integration.py     # GitExtension
    └── workflow.py            # WorkflowExtension
```

---

## Core Components

### 1. UDS Data Structures (papertrail.uds)

#### UDSHeader

**Purpose:** YAML frontmatter for document traceability.

**Type:** Python dataclass

**Import:**

```python
from papertrail import UDSHeader, DocumentType, DocumentStatus
```

**Constructor:**

```python
header = UDSHeader(
    workorder_id: str,              # Required: WO-{FEATURE}-{CATEGORY}-###
    generated_by: str,              # Required: coderef-{server} v{version}
    feature_id: str,                # Required: Feature name (alphanumeric)
    timestamp: str,                 # Required: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
    title: Optional[str] = None,    # Optional: Document title
    version: Optional[str] = None,  # Optional: Semantic version
    status: Optional[DocumentStatus] = None,
    classification: Optional[str] = None,
    doc_type: Optional[DocumentType] = None
)
```

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `to_yaml()` | `str` | Generate YAML frontmatter with `---` delimiters |
| `from_dict(data: dict)` | `UDSHeader` | Create from dictionary (class method) |

**Example:**

```python
from papertrail import UDSHeader, DocumentStatus, DocumentType

header = UDSHeader(
    workorder_id="WO-AUTH-SYSTEM-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="auth-system",
    timestamp="2025-12-30T10:15:00Z",
    title="Authentication System",
    version="2.1.0",
    status=DocumentStatus.APPROVED,
    doc_type=DocumentType.ARCHITECTURE
)

yaml_output = header.to_yaml()
print(yaml_output)
```

**Output:**

```yaml
---
workorder_id: WO-AUTH-SYSTEM-001
generated_by: coderef-docs v1.2.0
feature_id: auth-system
timestamp: '2025-12-30T10:15:00Z'
title: Authentication System
version: 2.1.0
status: APPROVED
doc_type: architecture
---
```

---

#### UDSFooter

**Purpose:** YAML footer for attribution and tracking.

**Type:** Python dataclass

**Import:**

```python
from papertrail import UDSFooter, DocumentStatus
```

**Constructor:**

```python
footer = UDSFooter(
    copyright_year: int,             # Required: Copyright year (2020-2100)
    organization: str,               # Required: Organization name
    generated_by: str,               # Required: MCP server attribution
    workorder_id: str,               # Required: Workorder ID
    feature_id: str,                 # Required: Feature name
    last_updated: str,               # Required: YYYY-MM-DD
    ai_assistance: bool = True,      # Optional: AI assistance flag
    status: Optional[DocumentStatus] = None,
    next_review: Optional[str] = None,
    contributors: Optional[list[str]] = None
)
```

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `to_yaml()` | `str` | Generate YAML footer with `---` delimiters |
| `from_dict(data: dict)` | `UDSFooter` | Create from dictionary (class method) |

**Example:**

```python
from papertrail import UDSFooter, DocumentStatus

footer = UDSFooter(
    copyright_year=2025,
    organization="CodeRef Ecosystem",
    generated_by="coderef-docs v1.2.0",
    workorder_id="WO-AUTH-SYSTEM-001",
    feature_id="auth-system",
    last_updated="2025-12-30",
    status=DocumentStatus.APPROVED,
    contributors=["Agent1", "Agent2"]
)

print(footer.to_yaml())
```

---

#### Helper Functions

**`create_uds_header()`**

Auto-generate UDS header with current timestamp.

```python
from papertrail import create_uds_header, DocumentStatus

header = create_uds_header(
    workorder_id="WO-FEATURE-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="my-feature",
    title="My Feature",
    status=DocumentStatus.DRAFT
)

print(header.timestamp)  # Auto-generated: 2025-12-30T10:15:23Z
```

**`create_uds_footer()`**

Auto-generate UDS footer with current dates.

```python
from papertrail import create_uds_footer

footer = create_uds_footer(
    workorder_id="WO-FEATURE-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="my-feature"
)

print(footer.last_updated)  # Auto-generated: 2025-12-30
print(footer.next_review)   # Auto-generated: 2026-12-30
```

---

### 2. Validation Components (papertrail.validator)

#### UDSValidator

**Purpose:** Schema-based document validator.

**Type:** Python class

**Import:**

```python
from papertrail.validator import UDSValidator
```

**Constructor:**

```python
validator = UDSValidator(
    schemas_dir: Optional[Path] = None  # Optional: Custom schemas directory
)
```

**Methods:**

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `validate()` | `document: str, doc_type: str` | `ValidationResult` | Validate document against schema |

**Example:**

```python
from papertrail.validator import UDSValidator

validator = UDSValidator()  # Auto-loads from package schemas

doc_content = """
---
workorder_id: WO-AUTH-SYSTEM-001
generated_by: coderef-docs v1.2.0
feature_id: auth-system
timestamp: '2025-12-30T10:15:00Z'
---

# Architecture

## Purpose
...
"""

result = validator.validate(doc_content, "architecture")
print(f"Valid: {result.valid}")
print(f"Score: {result.score}/100")

for error in result.errors:
    print(f"[{error.severity.value}] {error.message}")
```

---

#### ValidationResult

**Purpose:** Validation result data structure.

**Type:** Python dataclass

**Fields:**

```python
@dataclass
class ValidationResult:
    valid: bool                    # True if passes all CRITICAL checks
    errors: list[ValidationError]  # All validation errors
    warnings: list[str]            # Warning messages
    score: int                     # Validation score (0-100)
```

**Example:**

```python
from papertrail import validate_uds

result = validate_uds(doc_content, "architecture")

if result.valid:
    print(f"✅ Document valid (score: {result.score}/100)")
else:
    print(f"❌ Document invalid (score: {result.score}/100)")
    for error in result.errors:
        print(f"  - {error.message}")
```

---

#### ValidationError

**Purpose:** Single validation error.

**Type:** Python dataclass

**Fields:**

```python
@dataclass
class ValidationError:
    severity: ValidationSeverity  # CRITICAL, MAJOR, MINOR, WARNING
    message: str                  # Error message
    section: Optional[str]        # Section name (if applicable)
    field: Optional[str]          # Field name (if applicable)
```

---

#### Helper Functions

**`validate_uds()`**

Quick validation without creating validator instance.

```python
from papertrail import validate_uds

result = validate_uds(doc_content, "architecture")
print(f"Valid: {result.valid}, Score: {result.score}")
```

**`validate_workorder_id()`**

Validate workorder ID format.

```python
from papertrail.validator import validate_workorder_id

valid = validate_workorder_id("WO-AUTH-SYSTEM-001")  # True
valid = validate_workorder_id("WO-AUTH-001")         # False (missing category)
```

**`validate_feature_id()`**

Validate feature ID format.

```python
from papertrail.validator import validate_feature_id

valid = validate_feature_id("auth-system")    # True
valid = validate_feature_id("Auth System!")   # False
```

---

### 3. Health Scoring Components (papertrail.health)

#### HealthScorer

**Purpose:** Calculate document health scores.

**Type:** Python class

**Import:**

```python
from papertrail.health import HealthScorer
```

**Constructor:**

```python
scorer = HealthScorer()
```

**Methods:**

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `calculate_health()` | `document: str, doc_type: str` | `HealthScore` | Calculate health score |

**Example:**

```python
from papertrail.health import HealthScorer

scorer = HealthScorer()

health = scorer.calculate_health(doc_content, "architecture")
print(f"Health Score: {health.score}/100")
print(f"  Traceability: {health.traceability}/40")
print(f"  Completeness: {health.completeness}/30")
print(f"  Freshness: {health.freshness}/20")
print(f"  Validation: {health.validation}/10")
```

---

#### HealthScore

**Purpose:** Health score breakdown.

**Type:** Python dataclass

**Fields:**

```python
@dataclass
class HealthScore:
    score: int                   # Overall (0-100)
    traceability: int            # Traceability (0-40)
    completeness: int            # Completeness (0-30)
    freshness: int               # Freshness (0-20)
    validation: int              # Validation (0-10)
    has_workorder_id: bool
    has_feature_id: bool
    has_mcp_attribution: bool
    age_days: int
    passes_validation: bool
```

**Health Formula:**

| Component | Weight | Scoring Logic |
|-----------|--------|---------------|
| Traceability | 40% | `has_workorder_id` (20) + `has_feature_id` (10) + `has_mcp_attribution` (10) |
| Completeness | 30% | All required sections (20) + Has examples (10) |
| Freshness | 20% | <7 days (20), 7-30 days (10), 30-90 days (5), >90 days (0) |
| Validation | 10% | Passes schema validation (10) |

---

#### Helper Functions

**`calculate_health()`**

Quick health calculation.

```python
from papertrail import calculate_health

health = calculate_health(doc_content, "architecture")
print(f"Health: {health.score}/100")
```

**`store_health_score()`**

Store health score to JSON file.

```python
from papertrail.health import store_health_score
from pathlib import Path

store_health_score(
    feature_name="auth-system",
    doc_type="architecture",
    health_score=health,
    context_dir=Path("coderef/context/")
)
```

**`load_health_score()`**

Load health score from JSON file.

```python
from papertrail.health import load_health_score
from pathlib import Path

health = load_health_score(
    feature_name="auth-system",
    doc_type="architecture",
    context_dir=Path("coderef/context/")
)
```

---

### 4. Template Engine Components (papertrail.engine)

#### TemplateEngine

**Purpose:** Jinja2-based template engine with UDS injection.

**Type:** Python class

**Import:**

```python
from papertrail import TemplateEngine
```

**Constructor:**

```python
engine = TemplateEngine(
    template_dir: Optional[Path] = None  # Optional: Template directory
)
```

**Methods:**

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `register_extension()` | `name: str, extension: Any` | `None` | Register CodeRef extension |
| `render()` | `template_content: str, context: Dict[str, Any]` | `str` | Render template string |
| `render_file()` | `template_path: str, context: Dict[str, Any]` | `str` | Render template from file |
| `inject_uds()` | `content: str, header: UDSHeader, footer: Optional[UDSFooter]` | `str` | Inject UDS header/footer |
| `render_with_uds()` | `template_content: str, context: Dict, header: UDSHeader, footer: Optional[UDSFooter]` | `str` | Render and inject UDS |

**Example:**

```python
from papertrail import TemplateEngine, create_uds_header, create_uds_footer

engine = TemplateEngine()

header = create_uds_header(
    workorder_id="WO-FEATURE-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="my-feature"
)

footer = create_uds_footer(
    workorder_id="WO-FEATURE-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="my-feature"
)

template = """
# {{ title }}

## Purpose
{{ purpose }}
"""

context = {
    "title": "Architecture",
    "purpose": "System architecture overview"
}

doc = engine.render_with_uds(template, context, header, footer)
print(doc)
```

---

#### Helper Functions

**`create_template_engine()`**

Create engine with pre-registered extensions.

```python
from papertrail import create_template_engine
from papertrail.extensions import GitExtension

engine = create_template_engine(
    template_dir=Path("templates/"),
    extensions={
        'git': GitExtension()
    }
)

# Now can use: {{ git.stats() }} in templates
```

---

### 5. Extension Components (papertrail.extensions)

#### CodeRefContextExtension

**Purpose:** Code intelligence integration (scan, query, impact).

**Type:** Python class

**Import:**

```python
from papertrail.extensions import CodeRefContextExtension
```

**Usage:**

```python
from papertrail import create_template_engine
from papertrail.extensions import CodeRefContextExtension

engine = create_template_engine(
    extensions={'coderef': CodeRefContextExtension()}
)

template = """
Code Scan: {{ coderef.scan(project_path) }}
"""

result = engine.render(template, {"project_path": "/path/to/project"})
```

---

#### GitExtension

**Purpose:** Git statistics integration (stats, files, contributors).

**Type:** Python class

**Import:**

```python
from papertrail.extensions import GitExtension
```

**Usage:**

```python
from papertrail import create_template_engine
from papertrail.extensions import GitExtension

engine = create_template_engine(
    extensions={'git': GitExtension()}
)

template = """
Files changed: {{ git.files_changed('my-feature') }}
Contributors: {{ git.contributors('my-feature') }}
"""

result = engine.render(template, {})
```

---

#### WorkflowExtension

**Purpose:** Workflow data integration (plan, tasks, progress).

**Type:** Python class

**Import:**

```python
from papertrail.extensions import WorkflowExtension
```

**Usage:**

```python
from papertrail import create_template_engine
from papertrail.extensions import WorkflowExtension

engine = create_template_engine(
    extensions={'workflow': WorkflowExtension()}
)

template = """
Plan: {{ workflow.plan('my-feature') }}
Tasks: {{ workflow.tasks('my-feature') }}
"""

result = engine.render(template, {})
```

---

## Enums

### DocumentType

```python
from papertrail import DocumentType

# Values
DocumentType.PLAN           # "plan"
DocumentType.DELIVERABLES   # "deliverables"
DocumentType.ARCHITECTURE   # "architecture"
DocumentType.README         # "readme"
DocumentType.API            # "api"
DocumentType.CHANGELOG      # "changelog"
```

### DocumentStatus

```python
from papertrail import DocumentStatus

# Values
DocumentStatus.DRAFT        # "DRAFT"
DocumentStatus.REVIEW       # "REVIEW"
DocumentStatus.APPROVED     # "APPROVED"
DocumentStatus.DEPRECATED   # "DEPRECATED"
```

### ValidationSeverity

```python
from papertrail.validator import ValidationSeverity

# Values
ValidationSeverity.CRITICAL  # "CRITICAL" (-50 points)
ValidationSeverity.MAJOR     # "MAJOR" (-20 points)
ValidationSeverity.MINOR     # "MINOR" (-10 points)
ValidationSeverity.WARNING   # "WARNING" (-5 points)
```

---

## Usage Patterns

### Pattern 1: Complete Document Generation

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

# 1. Create header
header = create_uds_header(
    workorder_id="WO-AUTH-SYSTEM-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="auth-system",
    status=DocumentStatus.APPROVED,
    doc_type=DocumentType.ARCHITECTURE
)

# 2. Create footer
footer = create_uds_footer(
    workorder_id="WO-AUTH-SYSTEM-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="auth-system"
)

# 3. Render template
engine = TemplateEngine()
template = "# {{ title }}\n\n{{ content }}"
context = {"title": "Architecture", "content": "System overview"}

doc = engine.render_with_uds(template, context, header, footer)

# 4. Validate
result = validate_uds(doc, "architecture")
print(f"Valid: {result.valid}, Score: {result.score}")

# 5. Check health
health = calculate_health(doc, "architecture")
print(f"Health: {health.score}/100")
```

### Pattern 2: Validation-Only Workflow

```python
from papertrail import validate_uds, ValidationSeverity

# Read existing document
with open("ARCHITECTURE.md", "r") as f:
    doc = f.read()

# Validate
result = validate_uds(doc, "architecture")

# Handle errors
if not result.valid:
    critical_errors = [e for e in result.errors if e.severity == ValidationSeverity.CRITICAL]
    print(f"❌ {len(critical_errors)} CRITICAL errors:")
    for error in critical_errors:
        print(f"  - {error.message}")
else:
    print(f"✅ Document valid (score: {result.score}/100)")
```

### Pattern 3: Health Monitoring

```python
from papertrail import calculate_health
from pathlib import Path

# Calculate health for all documents
docs = {
    "README.md": "readme",
    "ARCHITECTURE.md": "architecture",
    "API.md": "api"
}

for doc_path, doc_type in docs.items():
    with open(doc_path, "r") as f:
        doc = f.read()

    health = calculate_health(doc, doc_type)
    print(f"{doc_path}: {health.score}/100")

    if health.score < 70:
        print(f"  ⚠️ Low health score!")
        print(f"    Traceability: {health.traceability}/40")
        print(f"    Completeness: {health.completeness}/30")
        print(f"    Freshness: {health.freshness}/20 (age: {health.age_days} days)")
```

---

## Copy-Paste Examples

### Example 1: Basic UDS Header

```python
from papertrail import create_uds_header, DocumentStatus

header = create_uds_header(
    workorder_id="WO-MY-FEATURE-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="my-feature",
    title="My Feature Documentation",
    status=DocumentStatus.DRAFT
)

print(header.to_yaml())
```

### Example 2: Validate Document

```python
from papertrail import validate_uds

doc_content = """
---
workorder_id: WO-MY-FEATURE-001
generated_by: coderef-docs v1.2.0
feature_id: my-feature
timestamp: '2025-12-30T10:00:00Z'
---

# Architecture

## Purpose
My architecture purpose...

## Overview
System overview...

## What/Why/When
Details...

## Examples
Code examples...

## References
- [Link](url)
"""

result = validate_uds(doc_content, "architecture")
print(f"Valid: {result.valid}, Score: {result.score}/100")
```

### Example 3: Health Check

```python
from papertrail import calculate_health

health = calculate_health(doc_content, "architecture")

print(f"Overall Health: {health.score}/100")
print(f"Components:")
print(f"  Traceability: {health.traceability}/40")
print(f"  Completeness: {health.completeness}/30")
print(f"  Freshness: {health.freshness}/20")
print(f"  Validation: {health.validation}/10")
print(f"\nDetails:")
print(f"  Has workorder ID: {health.has_workorder_id}")
print(f"  Has feature ID: {health.has_feature_id}")
print(f"  Has MCP attribution: {health.has_mcp_attribution}")
print(f"  Age: {health.age_days} days")
print(f"  Passes validation: {health.passes_validation}")
```

---

## References

- [Papertrail API Reference](./API.md) - Complete API documentation
- [Papertrail Schema Reference](./SCHEMA.md) - Data schemas and validation rules
- [Papertrail README](../../README.md) - Project overview and installation
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html) - Dataclass documentation
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Template engine reference

---

Copyright © 2025 | CodeRef Ecosystem
Generated by: coderef-docs v1.2.0
Workorder: WO-PAPERTRAIL-FOUNDATION-DOCS-001
Feature: foundation-docs
Last Updated: 2025-12-30
AI Assistance: true
Status: APPROVED
