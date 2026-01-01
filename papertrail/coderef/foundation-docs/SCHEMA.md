---
workorder_id: WO-PAPERTRAIL-FOUNDATION-DOCS-001
generated_by: coderef-docs v1.2.0
feature_id: foundation-docs
timestamp: 2025-12-30T00:00:00Z
title: Papertrail Schema Reference
version: 1.0.0
status: APPROVED
doc_type: schema
---

# Papertrail Schema Reference

## Purpose

This document defines the complete data schemas for Papertrail's Universal Documentation Standards (UDS) system. It provides JSON schema definitions, data models, validation rules, and entity relationships for all 5 CodeRef document types and core UDS data structures.

## Overview

Papertrail uses JSON Schema (Draft 07) to validate documents and enforce quality standards across the CodeRef ecosystem. This document covers:

1. **UDS Data Models** - Core data structures (UDSHeader, UDSFooter, enums)
2. **Document Schemas** - JSON schemas for 5 document types (plan, deliverables, architecture, readme, api)
3. **Validation Rules** - Required/optional fields, patterns, and constraints
4. **Entity Relationships** - How UDS components relate across the ecosystem
5. **Schema Evolution** - Versioning and migration guidelines

---

## UDS Data Models

### 1. UDSHeader

**Purpose:** YAML frontmatter for complete document traceability.

**Python Dataclass:**

```python
@dataclass
class UDSHeader:
    # Required fields
    workorder_id: str       # Format: WO-{FEATURE}-{CATEGORY}-###
    generated_by: str       # Format: coderef-{server} v{version}
    feature_id: str         # Format: [a-z0-9_-]+
    timestamp: str          # ISO 8601: YYYY-MM-DDTHH:MM:SSZ

    # Optional fields
    title: Optional[str] = None
    version: Optional[str] = None
    status: Optional[DocumentStatus] = None
    classification: Optional[str] = None
    doc_type: Optional[DocumentType] = None
```

**JSON Schema:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["workorder_id", "generated_by", "feature_id", "timestamp"],
  "properties": {
    "workorder_id": {
      "type": "string",
      "pattern": "^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\\d{3}$",
      "description": "Workorder ID (requires at least 2 segments before final 3 digits)"
    },
    "generated_by": {
      "type": "string",
      "pattern": "^coderef-[a-z-]+ v[0-9]+\\.[0-9]+\\.[0-9]+$",
      "description": "MCP server attribution"
    },
    "feature_id": {
      "type": "string",
      "pattern": "^[a-z0-9_-]+$",
      "description": "Feature name (alphanumeric, hyphens, underscores only)"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
      "description": "ISO 8601 timestamp (UTC)"
    },
    "title": {
      "type": "string",
      "description": "Document title (optional)"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version (optional)"
    },
    "status": {
      "type": "string",
      "enum": ["DRAFT", "REVIEW", "APPROVED", "DEPRECATED"],
      "description": "Document lifecycle status (optional)"
    },
    "classification": {
      "type": "string",
      "enum": ["INTERNAL", "PUBLIC", "CONFIDENTIAL"],
      "description": "Security classification (optional)"
    },
    "doc_type": {
      "type": "string",
      "enum": ["plan", "deliverables", "architecture", "readme", "api", "changelog"],
      "description": "Document type (optional)"
    }
  }
}
```

**Field Constraints:**

| Field | Type | Pattern/Format | Required | Description |
|-------|------|----------------|----------|-------------|
| `workorder_id` | string | `^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\d{3}$` | Yes | Must have ≥2 segments before 3-digit ID |
| `generated_by` | string | `^coderef-[a-z-]+ v\d+\.\d+\.\d+$` | Yes | Must reference MCP server with version |
| `feature_id` | string | `^[a-z0-9_-]+$` | Yes | Lowercase alphanumeric with hyphens/underscores |
| `timestamp` | string | ISO 8601 (UTC) | Yes | Format: `YYYY-MM-DDTHH:MM:SSZ` |
| `version` | string | Semantic versioning | No | Format: `\d+.\d+.\d+` |

**Example:**

```yaml
---
workorder_id: WO-AUTH-SYSTEM-001
generated_by: coderef-docs v1.2.0
feature_id: auth-system
timestamp: 2025-12-30T10:15:00Z
title: Authentication System Architecture
version: 2.1.0
status: APPROVED
classification: INTERNAL
doc_type: architecture
---
```

---

### 2. UDSFooter

**Purpose:** YAML footer for attribution and tracking.

**Python Dataclass:**

```python
@dataclass
class UDSFooter:
    # Required fields
    copyright_year: int
    organization: str
    generated_by: str
    workorder_id: str
    feature_id: str
    last_updated: str       # Format: YYYY-MM-DD

    # Optional fields
    ai_assistance: bool = True
    status: Optional[DocumentStatus] = None
    next_review: Optional[str] = None
    contributors: Optional[list[str]] = None
```

**JSON Schema:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["copyright_year", "organization", "generated_by", "workorder_id", "feature_id", "last_updated"],
  "properties": {
    "copyright_year": {
      "type": "integer",
      "minimum": 2020,
      "maximum": 2100
    },
    "organization": {
      "type": "string",
      "default": "CodeRef Ecosystem"
    },
    "generated_by": {
      "type": "string",
      "pattern": "^coderef-[a-z-]+ v[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "workorder_id": {
      "type": "string",
      "pattern": "^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\\d{3}$"
    },
    "feature_id": {
      "type": "string",
      "pattern": "^[a-z0-9_-]+$"
    },
    "last_updated": {
      "type": "string",
      "format": "date",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    },
    "ai_assistance": {
      "type": "boolean",
      "default": true
    },
    "status": {
      "type": "string",
      "enum": ["DRAFT", "REVIEW", "APPROVED", "DEPRECATED"]
    },
    "next_review": {
      "type": "string",
      "format": "date",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    },
    "contributors": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

**Example:**

```yaml
---
Copyright © 2025 | CodeRef Ecosystem
Generated by: coderef-docs v1.2.0
Workorder: WO-AUTH-SYSTEM-001
Feature: auth-system
Last Updated: 2025-12-30
AI Assistance: true
Status: APPROVED
Next Review: 2026-12-30
Contributors:
  - Agent1
  - Agent2
---
```

---

### 3. Enums

#### DocumentType

```python
class DocumentType(Enum):
    PLAN = "plan"
    DELIVERABLES = "deliverables"
    ARCHITECTURE = "architecture"
    README = "readme"
    API = "api"
    CHANGELOG = "changelog"
```

**JSON Schema:**

```json
{
  "type": "string",
  "enum": ["plan", "deliverables", "architecture", "readme", "api", "changelog"]
}
```

#### DocumentStatus

```python
class DocumentStatus(Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    DEPRECATED = "DEPRECATED"
```

**JSON Schema:**

```json
{
  "type": "string",
  "enum": ["DRAFT", "REVIEW", "APPROVED", "DEPRECATED"]
}
```

#### ValidationSeverity

```python
class ValidationSeverity(Enum):
    CRITICAL = "CRITICAL"  # -50 points
    MAJOR = "MAJOR"        # -20 points
    MINOR = "MINOR"        # -10 points
    WARNING = "WARNING"    # -5 points
```

---

### 4. Validation Result Models

#### ValidationResult

```python
@dataclass
class ValidationResult:
    valid: bool                    # True if passes all CRITICAL checks
    errors: list[ValidationError]  # All validation errors
    warnings: list[str]            # Warning messages
    score: int                     # Validation score (0-100)
```

#### ValidationError

```python
@dataclass
class ValidationError:
    severity: ValidationSeverity  # CRITICAL, MAJOR, MINOR, WARNING
    message: str                  # Error message
    section: Optional[str]        # Section name (if applicable)
    field: Optional[str]          # Field name (if applicable)
```

---

### 5. Health Score Models

#### HealthScore

```python
@dataclass
class HealthScore:
    score: int                   # Overall health score (0-100)
    traceability: int            # Traceability score (0-40)
    completeness: int            # Completeness score (0-30)
    freshness: int               # Freshness score (0-20)
    validation: int              # Validation score (0-10)
    has_workorder_id: bool       # Has workorder ID
    has_feature_id: bool         # Has feature ID
    has_mcp_attribution: bool    # Has MCP attribution
    age_days: int                # Age of document in days
    passes_validation: bool      # Passes schema validation
```

**Scoring Formula:**

| Component | Weight | Scoring Logic |
|-----------|--------|---------------|
| **Traceability** | 40% | `has_workorder_id` (20pt) + `has_feature_id` (10pt) + `has_mcp_attribution` (10pt) |
| **Completeness** | 30% | All required sections (20pt) + Has examples (10pt) |
| **Freshness** | 20% | <7 days (20pt), 7-30 days (10pt), 30-90 days (5pt), >90 days (0pt) |
| **Validation** | 10% | Passes schema validation (10pt) |

---

## Document Schemas

### 1. Plan Schema (plan.json)

**Document Type:** `plan`

**Purpose:** 10-section implementation plan structure for feature development.

**File Location:** `papertrail/schemas/plan.json`

**Required Sections:**

```json
{
  "required_sections": [
    "META_DOCUMENTATION",
    "0_preparation",
    "1_executive_summary",
    "2_risk_assessment",
    "3_current_state_analysis",
    "4_key_features",
    "5_task_id_system",
    "6_implementation_phases",
    "7_testing_strategy",
    "8_success_criteria",
    "9_implementation_checklist"
  ]
}
```

**Required Metadata:**

| Field | Pattern | Description |
|-------|---------|-------------|
| `workorder_id` | `^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\d{3}$` | Workorder ID (≥2 segments) |
| `feature_name` | `^[a-z0-9_-]+$` | Feature name |
| `generated_by` | `^coderef-workflow v.*$` | Must be coderef-workflow |
| `version` | `^\d+\.\d+\.\d+$` | Semantic version |
| `status` | `planning \| in_progress \| completed \| archived` | Plan status |

**Validation Rules:**

```json
{
  "validation_rules": {
    "critical": [
      "Must have workorder_id in META_DOCUMENTATION",
      "Must have all 10 required sections",
      "Must have at least 1 implementation phase",
      "Must have testing strategy defined",
      "Must have success criteria defined"
    ],
    "warnings": [
      "Should have task_id_system with naming convention",
      "Should have pre-implementation preparation steps",
      "Should have risk assessment with dependencies"
    ]
  }
}
```

---

### 2. Deliverables Schema (deliverables.json)

**Document Type:** `deliverables`

**Purpose:** Execution tracking and metrics for completed features.

**File Location:** `papertrail/schemas/deliverables.json`

**Required Sections:**

```json
{
  "required_sections": [
    "Overview",
    "Completion Status",
    "Implementation Metrics",
    "Testing & Validation"
  ]
}
```

**Required Metadata:**

| Field | Pattern/Enum | Description |
|-------|--------------|-------------|
| `workorder_id` | `^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\d{3}$` | Workorder ID |
| `feature_id` | `^[a-z0-9_-]+$` | Feature name |
| `status` | `NOT_STARTED \| IN_PROGRESS \| COMPLETE` | Completion status |
| `generated_by` | `^coderef-(workflow\|docs) v.*$` | Generator attribution |

**Required Metrics:**

```json
{
  "required_metrics": {
    "lines_of_code": {
      "added": "number",
      "removed": "number",
      "modified": "number"
    },
    "commits": {
      "count": "number"
    },
    "time_spent": {
      "first_commit": "ISO 8601 timestamp",
      "last_commit": "ISO 8601 timestamp",
      "duration": "string (e.g., '3 hours 45 minutes')"
    },
    "contributors": {
      "type": "array",
      "items": "string"
    }
  }
}
```

**Validation Rules:**

```json
{
  "validation_rules": {
    "critical": [
      "Must have workorder_id",
      "Must have completion status",
      "Must have implementation metrics section",
      "Must have LOC metrics if status is COMPLETE"
    ],
    "warnings": [
      "Should have git commit metrics",
      "Should have testing results",
      "Should track contributors"
    ]
  }
}
```

---

### 3. Architecture Schema (architecture.json)

**Document Type:** `architecture`

**Purpose:** System architecture following POWER framework.

**File Location:** `papertrail/schemas/architecture.json`

**Required Sections (POWER Framework):**

```json
{
  "required_sections": [
    "Purpose",
    "Overview",
    "What/Why/When",
    "Examples",
    "References"
  ]
}
```

**Optional Sections:**

```json
{
  "optional_sections": [
    "Component Diagram",
    "Data Flow",
    "API Contracts",
    "Security Considerations",
    "Performance Considerations",
    "Deployment Architecture"
  ]
}
```

**Required Metadata:**

| Field | Pattern | Description |
|-------|---------|-------------|
| `workorder_id` | `^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\d{3}$` | Workorder ID |
| `generated_by` | `^coderef-docs v.*$` | Must be coderef-docs |
| `version` | `^\d+\.\d+\.\d+$` | Document version |

**Validation Rules:**

```json
{
  "validation_rules": {
    "critical": [
      "Must follow POWER framework (all 5 sections)",
      "Must have workorder_id",
      "Must have MCP attribution (generated_by)",
      "Purpose section must explain why architecture exists"
    ],
    "warnings": [
      "Should include component diagrams or references",
      "Should document key architectural decisions",
      "Should link to related documents"
    ]
  }
}
```

---

### 4. README Schema (readme.json)

**Document Type:** `readme`

**Purpose:** Project overview following POWER framework.

**File Location:** `papertrail/schemas/readme.json`

**Required Sections (POWER Framework):**

```json
{
  "required_sections": [
    "Purpose",
    "Overview",
    "What/Why/When",
    "Examples",
    "References"
  ]
}
```

**Optional Sections:**

```json
{
  "optional_sections": [
    "Installation",
    "Quick Start",
    "Configuration",
    "Usage",
    "API Documentation",
    "Contributing",
    "License",
    "Changelog"
  ]
}
```

**Required Metadata:**

| Field | Pattern | Description |
|-------|---------|-------------|
| `workorder_id` | `^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\d{3}$` | Workorder ID |
| `generated_by` | `^coderef-docs v.*$` | Must be coderef-docs |
| `version` | `^\d+\.\d+\.\d+$` | Project version |

**Validation Rules:**

```json
{
  "validation_rules": {
    "critical": [
      "Must follow POWER framework",
      "Must have workorder_id",
      "Must have version number",
      "Must have project purpose clearly stated"
    ],
    "warnings": [
      "Should include installation instructions",
      "Should include usage examples",
      "Should link to other documentation"
    ]
  }
}
```

---

### 5. API Schema (api.json)

**Document Type:** `api`

**Purpose:** API reference following POWER framework.

**File Location:** `papertrail/schemas/api.json`

**Required Sections (POWER Framework):**

```json
{
  "required_sections": [
    "Purpose",
    "Overview",
    "What/Why/When",
    "Examples",
    "References"
  ]
}
```

**Optional Sections:**

```json
{
  "optional_sections": [
    "Authentication",
    "Endpoints",
    "Request/Response Formats",
    "Error Codes",
    "Rate Limiting",
    "Versioning",
    "SDKs & Client Libraries"
  ]
}
```

**Required Metadata:**

| Field | Pattern | Description |
|-------|---------|-------------|
| `workorder_id` | `^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\d{3}$` | Workorder ID |
| `generated_by` | `^coderef-docs v.*$` | Must be coderef-docs |
| `api_version` | `^v\d+(\.\d+)?$` | API version (e.g., v1, v2.1) |

**Validation Rules:**

```json
{
  "validation_rules": {
    "critical": [
      "Must follow POWER framework",
      "Must have workorder_id",
      "Must have API version",
      "Must document all public endpoints"
    ],
    "warnings": [
      "Should include authentication examples",
      "Should document error responses",
      "Should include request/response examples"
    ]
  }
}
```

---

## Entity Relationships

### UDS Ecosystem Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                      CodeRef Ecosystem                       │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │ Workflow │  │   Docs   │  │ Context  │
         │   MCP    │  │   MCP    │  │   MCP    │
         └──────────┘  └──────────┘  └──────────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Papertrail     │
                    │  (UDS Provider)  │
                    └──────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │ UDSHeader│  │ Validator│  │  Health  │
         └──────────┘  └──────────┘  └──────────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   5 Document     │
                    │    Schemas       │
                    └──────────────────┘
```

### Document Lifecycle

```
1. Feature Request
         │
         ▼
2. coderef-workflow: gather_context()
         │
         ├─> context.json (user requirements)
         │
         ▼
3. coderef-workflow: create_plan()
         │
         ├─> plan.json (UDSHeader injected)
         │   └─ workorder_id: WO-FEATURE-001
         │
         ▼
4. coderef-workflow: execute_plan()
         │
         ├─> DELIVERABLES.md (UDSHeader injected)
         │   └─ workorder_id: WO-FEATURE-001
         │   └─ status: IN_PROGRESS → COMPLETE
         │
         ▼
5. coderef-docs: generate_foundation_docs()
         │
         ├─> README.md (UDSHeader + UDSFooter)
         ├─> ARCHITECTURE.md (UDSHeader + UDSFooter)
         ├─> API.md (UDSHeader + UDSFooter)
         ├─> SCHEMA.md (UDSHeader + UDSFooter)
         └─> COMPONENTS.md (UDSHeader + UDSFooter)
             │
             └─ All link to: workorder_id: WO-FEATURE-001
```

### Cross-Document References

| Document | References | Referenced By |
|----------|-----------|---------------|
| **plan.json** | context.json, analysis.json | DELIVERABLES.md, README.md |
| **DELIVERABLES.md** | plan.json, git history | CHANGELOG.json, README.md |
| **README.md** | All foundation docs | External users, search engines |
| **ARCHITECTURE.md** | README.md, API.md | SCHEMA.md, COMPONENTS.md |
| **API.md** | README.md, ARCHITECTURE.md | Client developers, SDK generators |
| **SCHEMA.md** | ARCHITECTURE.md, API.md | Validators, code generators |

---

## Schema Evolution

### Versioning Guidelines

**Schema Version Format:** `{major}.{minor}.{patch}`

- **Major** (1.x.x) - Breaking changes (remove required fields, change patterns)
- **Minor** (x.1.x) - New optional fields, additional constraints
- **Patch** (x.x.1) - Bug fixes, clarifications

**Current Versions:**

| Schema | Version | File |
|--------|---------|------|
| plan | 1.0.0 | `papertrail/schemas/plan.json` |
| deliverables | 1.0.0 | `papertrail/schemas/deliverables.json` |
| architecture | 1.0.0 | `papertrail/schemas/architecture.json` |
| readme | 1.0.0 | `papertrail/schemas/readme.json` |
| api | 1.0.0 | `papertrail/schemas/api.json` |

### Migration Strategy

**Adding Optional Fields:**

1. Add field to schema with `"required": false`
2. Update `UDSHeader` or `UDSFooter` dataclass
3. Bump minor version (1.0.0 → 1.1.0)
4. Existing documents remain valid

**Changing Required Fields (Breaking):**

1. Create new schema version (e.g., `plan_v2.json`)
2. Update `UDSValidator` to support both versions
3. Bump major version (1.0.0 → 2.0.0)
4. Provide migration tool

**Example Migration:**

```python
# Migrate plan.json from v1 to v2
from papertrail.migration import migrate_plan

with open("plan.json", "r") as f:
    plan_v1 = json.load(f)

plan_v2 = migrate_plan(plan_v1, from_version="1.0.0", to_version="2.0.0")

with open("plan.json", "w") as f:
    json.dump(plan_v2, f, indent=2)
```

---

## Validation Examples

### Example 1: Valid UDSHeader

```yaml
---
workorder_id: WO-AUTH-SYSTEM-001
generated_by: coderef-docs v1.2.0
feature_id: auth-system
timestamp: 2025-12-30T10:15:00Z
title: Authentication System Architecture
version: 2.1.0
status: APPROVED
---
```

**Validation Result:**

```python
ValidationResult(
    valid=True,
    errors=[],
    warnings=[],
    score=100
)
```

### Example 2: Invalid Workorder ID

```yaml
---
workorder_id: WO-AUTH-001  # ❌ Missing category segment
generated_by: coderef-docs v1.2.0
feature_id: auth-system
timestamp: 2025-12-30T10:15:00Z
---
```

**Validation Result:**

```python
ValidationResult(
    valid=False,
    errors=[
        ValidationError(
            severity=ValidationSeverity.MAJOR,
            message="Field 'workorder_id' does not match required pattern: ^WO-[A-Z0-9]+(-[A-Z0-9]+)+-\d{3}$",
            field="workorder_id"
        )
    ],
    warnings=[],
    score=80  # -20 for MAJOR error
)
```

### Example 3: Missing Required Section

```markdown
---
workorder_id: WO-AUTH-SYSTEM-001
generated_by: coderef-docs v1.2.0
feature_id: auth-system
timestamp: 2025-12-30T10:15:00Z
---

# Architecture

## Purpose
...

## Overview
...

<!-- ❌ Missing: What/Why/When, Examples, References -->
```

**Validation Result:**

```python
ValidationResult(
    valid=True,  # No CRITICAL errors
    errors=[
        ValidationError(severity=ValidationSeverity.MAJOR, message="Missing required section: What/Why/When", section="What/Why/When"),
        ValidationError(severity=ValidationSeverity.MAJOR, message="Missing required section: Examples", section="Examples"),
        ValidationError(severity=ValidationSeverity.MAJOR, message="Missing required section: References", section="References")
    ],
    warnings=[],
    score=40  # -60 for 3 MAJOR errors
)
```

---

## References

- [Papertrail API Reference](./API.md) - Complete API documentation
- [Papertrail README](../../README.md) - Project overview and installation
- [JSON Schema Draft 07 Specification](https://json-schema.org/draft-07/schema) - Schema format reference
- [coderef-workflow Planning Standard](../../../coderef-workflow/templates/feature-implementation-planning-standard.json) - 10-section plan structure
- [POWER Framework](../../../coderef-docs/templates/power/) - Documentation templates

---

Copyright © 2025 | CodeRef Ecosystem
Generated by: coderef-docs v1.2.0
Workorder: WO-PAPERTRAIL-FOUNDATION-DOCS-001
Feature: foundation-docs
Last Updated: 2025-12-30
AI Assistance: true
Status: APPROVED
