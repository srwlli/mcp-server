---
agent: Claude Code
date: 2026-01-08
task: CREATE
subject: Papertrail MCP Server
parent_project: CodeRef Ecosystem
category: mcp-server
version: 1.0.0
related_files:
  - papertrail/validator.py
  - papertrail/health.py
  - papertrail/engine.py
  - papertrail/uds.py
  - schemas/documentation/resource-sheet-metadata-schema.json
  - validators/resource-sheets/validate.ps1
  - validators/scripts/validate.py
related_docs:
  - CLAUDE.md
  - README.md
  - standards/documentation/global-documentation-standards.md
  - standards/documentation/resource-sheet-standards.md
---

# Papertrail MCP Server - Resource Sheet

## Executive Summary

**Purpose:** Universal Documentation Standards (UDS) enforcement library and validation framework for the CodeRef ecosystem

**What It Does:**
- Provides UDS and RSMS (Resource Sheet Metadata Standards) for workorder-based and architectural documentation
- Validates document structure, metadata completeness, and compliance with global standards
- Calculates 0-100 health scores using 4-factor weighted scoring
- Powers Jinja2 template automation with CodeRef-specific extensions
- Enforces global documentation rules (headers, footers, no emojis)

**When To Use:**
- Validating implementation docs (plan.json, DELIVERABLES.md) against UDS
- Validating architectural docs (resource sheets) against RSMS v2.0
- Checking script/test frontmatter for triangular references
- Generating documentation from templates with CodeRef intelligence
- Enforcing global documentation standards across the ecosystem

**Key Constraints:**
- Python 3.10+ required
- Pydantic and jsonschema dependencies
- RSMS v2.0 uses snake_case fields (not camelCase)
- Global standards prohibit emojis in all documentation

---

## Audience & Intent

**Primary Audience:** CodeRef MCP servers (coderef-docs, coderef-workflow), AI agents implementing features

**Secondary Audience:** Developers creating documentation automation tools

**Assumptions:**
- Familiarity with YAML frontmatter
- Understanding of JSON Schema validation
- Basic knowledge of Jinja2 templating
- Working knowledge of CodeRef workorder system

**Not Covered:**
- MCP server implementation details (see server.py source)
- Template authoring beyond Jinja2 basics
- Git integration implementation (see extensions/git_integration.py)

---

## Quick Reference

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Validator** | `papertrail/validator.py` | UDS/RSMS schema validation |
| **Health Scorer** | `papertrail/health.py` | 4-factor document health scoring |
| **Template Engine** | `papertrail/engine.py` | Jinja2 rendering with CodeRef extensions |
| **UDS Utilities** | `papertrail/uds.py` | UDS header injection, workorder tracking |
| **RSMS Validator** | `validators/resource-sheets/validate.ps1` | PowerShell RSMS v2.0 compliance checker |
| **Script Validator** | `validators/scripts/validate.py` | Triangular reference validation |

### Metadata Standards

**UDS (Universal Documentation Standards)** - For workorder-based implementation docs
```yaml
---
workorder_id: WO-FEATURE-CATEGORY-001
feature_id: feature-name
mcp_server: coderef-workflow
generated_at: 2026-01-08T10:30:00Z
version: 1.0.0
---
```

**RSMS v2.0 (Resource Sheet Metadata Standards)** - For architectural reference docs
```yaml
---
agent: Claude Code
date: 2026-01-08
task: CREATE
subject: Component Name
parent_project: CodeRef Ecosystem
category: mcp-server
version: 1.0.0
related_files:
  - src/component.py
related_docs:
  - ARCHITECTURE.md
---
```

**Global Standards** - For all documents
```yaml
---
agent: Claude Code
date: YYYY-MM-DD
task: REVIEW | CONSOLIDATE | DOCUMENT | UPDATE | CREATE
---

# Document Title

[Content here]

---

**Last Updated:** YYYY-MM-DD
**Version:** X.Y.Z
**Maintained by:** CodeRef Ecosystem
```

### Health Scoring Formula

**Total Score (0-100):**
- Traceability: 40% (workorder_id, feature_id, mcp_server present)
- Completeness: 30% (all required fields populated)
- Freshness: 20% (generated_at within 30 days)
- Validation: 10% (JSON schema compliance)

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Papertrail System                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Validator  │  │    Health    │  │   Template   │      │
│  │              │  │    Scorer    │  │    Engine    │      │
│  │  - UDS       │  │              │  │              │      │
│  │  - RSMS v2.0 │  │  - 4-factor  │  │  - Jinja2    │      │
│  │  - Schema    │  │  - Weighted  │  │  - CodeRef   │      │
│  │    check     │  │  - 0-100     │  │    filters   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │   UDS Core      │                        │
│                   │                 │                        │
│                   │  - Inject       │                        │
│                   │  - Log WO       │                        │
│                   │  - Query        │                        │
│                   └─────────────────┘                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
        Schemas         Standards      Validators
            │               │               │
    ┌───────▼────────┐  ┌──▼───────┐  ┌───▼────────┐
    │ documentation/ │  │ global-  │  │ resource-  │
    │ planning/      │  │ docs     │  │ sheets/    │
    │ mcp/           │  │ resource │  │ scripts/   │
    │ security/      │  │ scripts  │  │ plans/     │
    └────────────────┘  └──────────┘  └────────────┘
```

### Data Flow

**Validation Flow:**
```
Document (MD/JSON)
    ↓
Extract YAML frontmatter
    ↓
Check for UDS vs RSMS fields
    ↓
Load appropriate schema
    ↓
Validate against schema
    ↓
Calculate health score
    ↓
Return validation result (pass/fail + score)
```

**Template Generation Flow:**
```
Template file (Jinja2)
    ↓
Load CodeRef extensions
    ↓
Inject context (git, workflow, coderef data)
    ↓
Render template
    ↓
Inject UDS/RSMS headers
    ↓
Output document
```

---

## Core Concepts

### 1. Three Metadata Standards

**UDS (Universal Documentation Standards)**
- For: Implementation docs (plan.json, DELIVERABLES.md, execution logs)
- Required: workorder_id, feature_id, mcp_server, generated_at
- Traceability: Links docs to workorder tracking system
- Use Case: "Which workorder created this plan?"

**RSMS v2.0 (Resource Sheet Metadata Standards)**
- For: Architectural reference docs (resource sheets, component docs)
- Required: subject, parent_project, category, version
- Relationships: related_files, related_docs
- Use Case: "What files implement this architecture?"

**Global Documentation Standards**
- For: All documents in CodeRef ecosystem
- Required: agent, date, task frontmatter
- Required: Last Updated, Version, Maintained by footer
- Prohibited: Emojis (use text markers instead: [PASS], [FAIL], [WARN], [INFO])
- Use Case: Universal consistency across all docs

### 2. Health Scoring (4-Factor Weighted)

**Traceability (40%):**
- workorder_id present: +20 points
- feature_id present: +10 points
- mcp_server present: +10 points

**Completeness (30%):**
- All required fields populated: +30 points
- Partial: proportional score

**Freshness (20%):**
- generated_at within 30 days: +20 points
- 31-60 days: +10 points
- 60+ days: +0 points

**Validation (10%):**
- JSON schema passes: +10 points
- Schema fails: +0 points

**Total:** 0-100 scale (0=poor, 50=acceptable, 85+=excellent)

### 3. Validator Organization

**Standard:** Each validator type has its own dedicated folder

```
validators/
├── resource-sheets/     # RSMS v2.0 compliance
│   └── validate.ps1     # PowerShell script
├── scripts/             # Script/test frontmatter
│   └── validate.py      # Python script
├── plans/               # plan.json schema
│   ├── validate.py
│   ├── plan_format_validator.py
│   └── schema_validator.py
└── typescript/          # TypeScript-specific
    └── (6 files)
```

**Why Separate?**
- Different validation rules per document type
- Language-specific validators (PowerShell, Python, TypeScript)
- Easy to add new validator types
- Clear ownership and testing scope

### 4. Triangular Bidirectional Reference System

**Problem:** Scripts, tests, and resource sheets exist independently without explicit relationships

**Solution:** Triangular references enforced via frontmatter validation

```
Resource Sheet (Architecture Doc)
    ↓ lists in related_files
Script (Implementation)
    ↓ references in related_test
Test (Validation)
    ↓ references in related_script
    ↓ references in resource_sheet
    ↓ (closes the triangle)
```

**Validation Checks:**
1. Script has `related_test` → test file exists
2. Test has `related_script` → script file exists
3. Script has `resource_sheet` → resource sheet exists and lists script in `related_files`
4. Test has `resource_sheet` → resource sheet exists and lists test in `related_files`
5. Bidirectional consistency (script ↔ test references match)

**Benefits:**
- Traceability: Know which tests cover which scripts
- Impact analysis: Know which tests to run when script changes
- Documentation: Auto-generate architecture diagrams from references

---

## Implementation Details

### Validator API

**Function:** `validate_document(doc_path: str, schema_type: str) -> ValidationResult`

**Parameters:**
- `doc_path`: Absolute path to document
- `schema_type`: "uds" | "rsms" | "script_frontmatter" | "plan"

**Returns:**
```python
{
    "valid": bool,
    "errors": List[str],
    "health_score": int (0-100),
    "metadata": dict
}
```

**Example:**
```python
from papertrail import validate_document

result = validate_document(
    "coderef/workorder/feature/plan.json",
    "uds"
)

if result["valid"] and result["health_score"] >= 85:
    print("Document is excellent!")
```

### Health Scorer API

**Function:** `calculate_health_score(metadata: dict, doc_type: str) -> int`

**Parameters:**
- `metadata`: Extracted YAML frontmatter as dict
- `doc_type`: "uds" | "rsms" | "standard"

**Returns:** Integer 0-100

**Example:**
```python
from papertrail import calculate_health_score

metadata = {
    "workorder_id": "WO-AUTH-SYSTEM-001",
    "feature_id": "auth-system",
    "mcp_server": "coderef-workflow",
    "generated_at": "2026-01-08T10:00:00Z"
}

score = calculate_health_score(metadata, "uds")
# Returns: 100 (full traceability + completeness + fresh + valid)
```

### Template Engine API

**Function:** `render_template(template_path: str, context: dict) -> str`

**Parameters:**
- `template_path`: Path to Jinja2 template
- `context`: Dictionary of template variables

**Returns:** Rendered string

**Available Filters (CodeRef Extensions):**
- `git_log()`: Get recent commits
- `git_diff()`: Get uncommitted changes
- `workorder_log()`: Query global workorder log
- `coderef_scan()`: Get code intelligence data
- `find_related_features()`: Search archived features

**Example:**
```python
from papertrail import render_template

context = {
    "feature_name": "auth-system",
    "workorder_id": "WO-AUTH-SYSTEM-001"
}

output = render_template("templates/plan.md.j2", context)
```

### RSMS v2.0 Validation (PowerShell)

**Script:** `validators/resource-sheets/validate.ps1`

**Usage:**
```powershell
.\validators\resource-sheets\validate.ps1 -Path "docs/"
.\validators\resource-sheets\validate.ps1 -Path "docs/MyComponent-RESOURCE-SHEET.md"
```

**Checks:**
- [PASS] YAML front matter presence
- [PASS] Required UDS fields (agent, date, task)
- [PASS] Required RSMS fields (subject, parent_project, category, version)
- [PASS] Date format (YYYY-MM-DD)
- [PASS] Task enum (REVIEW, CONSOLIDATE, DOCUMENT, UPDATE, CREATE)
- [PASS] Naming convention (*-RESOURCE-SHEET.md)
- [PASS] No emojis
- [PASS] UDS section headers

**Output:**
```
[PASS] YAML Front Matter
[PASS] Required UDS Fields
[PASS] Required RSMS Fields
[PASS] Date Format
[PASS] Task Value
[PASS] Naming Convention
[PASS] No Emojis
[PASS] Section Headers

[PASS] docs/MyComponent-RESOURCE-SHEET.md
```

### Script Frontmatter Validation (Python)

**Script:** `validators/scripts/validate.py`

**Usage:**
```bash
python validators/scripts/validate.py /path/to/project
python validators/scripts/validate.py /path/to/project --path src/
```

**Checks:**
- [PASS] YAML frontmatter presence in scripts/tests
- [PASS] Required field: `resource_sheet`
- [PASS] Script has `related_test`, test has `related_script`
- [PASS] Resource sheet exists and lists file in `related_files`
- [PASS] Bidirectional consistency (script ↔ test references match)

**Supported Languages:** Python (.py), Bash (.sh), PowerShell (.ps1), TypeScript (.ts), JavaScript (.js)

**Output:**
```
[INFO] Validating project: /path/to/project
[INFO] Found 15 scripts, 12 tests

[PASS] src/auth.py
  - resource_sheet: docs/Auth-RESOURCE-SHEET.md [EXISTS]
  - related_test: tests/test_auth.py [EXISTS, BIDIRECTIONAL OK]

[PASS] tests/test_auth.py
  - resource_sheet: docs/Auth-RESOURCE-SHEET.md [EXISTS]
  - related_script: src/auth.py [EXISTS, BIDIRECTIONAL OK]

[WARN] src/legacy.py
  - Missing resource_sheet field

[FAIL] src/broken.py
  - resource_sheet: docs/Nonexistent.md [NOT FOUND]

Summary: 13 passed, 1 warning, 1 failed
```

---

## Testing

### Test Coverage

**Total Coverage:** 98%

**Test Modules:**
- `test_validator.py`: Schema validation tests
- `test_health.py`: Health scoring tests
- `test_engine.py`: Template rendering tests
- `test_uds.py`: UDS utilities tests
- `test_coderef_context.py`: CodeRef extension tests
- `test_git_integration.py`: Git integration tests
- `test_workflow_filters.py`: Workflow filter tests

**Run Tests:**
```bash
# All tests
pytest

# With coverage
pytest --cov=papertrail --cov-report=html

# Specific module
pytest tests/test_validator.py -v
```

### Test Infrastructure

**Location:** `test-infrastructure/`

**Components:**
- `framework_detector.py`: Auto-detect test framework (pytest, unittest, jest, mocha)
- `test_runner.py`: Run tests with framework-specific commands
- `result_analyzer.py`: Parse test output, extract pass/fail/skip counts
- `test_aggregator.py`: Combine results from multiple test runs
- `models.py`: Data models for test results

**Supported Frameworks:**
- Python: pytest, unittest
- JavaScript/TypeScript: jest, mocha, vitest
- Go: go test
- Rust: cargo test

---

## Integration

### With coderef-workflow

**Use Case:** Validate plan.json after generation

```python
from papertrail import validate_document

# After generating plan.json
result = validate_document(
    "coderef/workorder/feature/plan.json",
    "plan"
)

if not result["valid"]:
    raise ValueError(f"Plan validation failed: {result['errors']}")

if result["health_score"] < 85:
    print(f"[WARN] Plan health score: {result['health_score']}/100")
```

### With coderef-docs

**Use Case:** Generate documentation with UDS headers

```python
from papertrail import render_template, inject_uds_headers

# Render template
content = render_template("templates/architecture.md.j2", context)

# Inject UDS headers
final_content = inject_uds_headers(
    content,
    workorder_id="WO-DOCS-GENERATE-001",
    feature_id="architecture-docs",
    mcp_server="coderef-docs"
)

# Write to file
with open("docs/ARCHITECTURE.md", "w") as f:
    f.write(final_content)
```

### With coderef-testing

**Use Case:** Validate test frontmatter before running tests

```bash
# Validate all test files
python validators/scripts/validate.py /path/to/project

# Run tests only if validation passes
if [ $? -eq 0 ]; then
    pytest
else
    echo "[FAIL] Test frontmatter validation failed"
    exit 1
fi
```

---

## Common Patterns

### Pattern 1: Validate and Score Document

```python
from papertrail import validate_document, calculate_health_score

# Validate document
result = validate_document("docs/plan.json", "uds")

if result["valid"]:
    score = calculate_health_score(result["metadata"], "uds")

    if score >= 85:
        print("[PASS] Excellent document health")
    elif score >= 50:
        print("[WARN] Acceptable document health")
    else:
        print("[FAIL] Poor document health")
else:
    print(f"[FAIL] Validation errors: {result['errors']}")
```

### Pattern 2: Generate Documentation with UDS

```python
from papertrail import render_template, inject_uds_headers

# Prepare context
context = {
    "feature_name": "auth-system",
    "components": ["AuthService", "TokenManager"],
    "endpoints": ["/login", "/logout"]
}

# Render template
content = render_template("templates/api.md.j2", context)

# Inject UDS headers
final = inject_uds_headers(
    content,
    workorder_id="WO-API-DOCS-001",
    feature_id="auth-system",
    mcp_server="coderef-docs",
    version="1.0.0"
)

# Save
with open("docs/API.md", "w") as f:
    f.write(final)
```

### Pattern 3: Batch Validate Resource Sheets

```powershell
# Validate all resource sheets in docs/
.\validators\resource-sheets\validate.ps1 -Path "docs/"

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] All resource sheets valid"
} else {
    Write-Host "[FAIL] Some resource sheets have errors"
    exit 1
}
```

### Pattern 4: Triangular Reference Validation

```python
# Validate script/test references
import subprocess

result = subprocess.run(
    ["python", "validators/scripts/validate.py", "/path/to/project"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("[PASS] All triangular references valid")
else:
    print(f"[FAIL] Reference validation failed:\n{result.stdout}")
```

---

## Best Practices

### Documentation Standards

**DO:**
- Use YAML frontmatter for all metadata
- Include all required UDS/RSMS fields
- Use snake_case for RSMS v2.0 fields
- Add Last Updated footer to all docs
- Use text markers ([PASS], [FAIL], [WARN], [INFO])

**DON'T:**
- Don't use emojis anywhere in documentation
- Don't mix camelCase and snake_case in same document
- Don't skip validation before committing docs
- Don't use relative dates ("yesterday", "last week")

### Validation Workflow

**Before Committing:**
1. Run appropriate validator for document type
2. Check health score (aim for 85+)
3. Fix any validation errors
4. Re-validate after fixes
5. Commit with validated docs

**Example Pre-Commit Hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate resource sheets
./validators/resource-sheets/validate.ps1 -Path "docs/"
if [ $? -ne 0 ]; then
    echo "[FAIL] Resource sheet validation failed"
    exit 1
fi

# Validate script frontmatter
python validators/scripts/validate.py .
if [ $? -ne 0 ]; then
    echo "[FAIL] Script frontmatter validation failed"
    exit 1
fi

echo "[PASS] All validations passed"
exit 0
```

### Template Authoring

**Structure:**
```jinja2
{# templates/my-doc.md.j2 #}
---
agent: {{ agent | default('Claude Code') }}
date: {{ date | default(now().strftime('%Y-%m-%d')) }}
task: {{ task | default('CREATE') }}
---

# {{ title }}

## Recent Changes
{{ git_log(limit=5) }}

## Related Features
{{ find_related_features(category='auth') }}

---

**Last Updated:** {{ now().strftime('%Y-%m-%d') }}
**Version:** {{ version }}
**Maintained by:** CodeRef Ecosystem
```

**Usage:**
```python
context = {
    "title": "Authentication System",
    "task": "DOCUMENT",
    "version": "1.0.0"
}

output = render_template("templates/my-doc.md.j2", context)
```

### Health Score Optimization

**To Achieve 85+ Score:**
1. **Traceability (40%):** Include workorder_id, feature_id, mcp_server
2. **Completeness (30%):** Fill all required fields (no empty strings)
3. **Freshness (20%):** Generate within 30 days (auto if using templates)
4. **Validation (10%):** Ensure JSON schema compliance

**Quick Wins:**
- Add workorder_id to existing docs: +20 points
- Populate empty optional fields: +10-15 points
- Regenerate old docs: +20 points (if 30+ days old)

---

## Troubleshooting

### Issue: Validation Fails with "Missing required field"

**Symptom:** Validator reports missing field but field exists in frontmatter

**Cause:** Incorrect field naming (camelCase vs snake_case)

**Fix:**
```yaml
# ❌ WRONG (RSMS v1.0 camelCase)
---
parentProject: CodeRef Ecosystem
relatedFiles:
  - src/component.py
---

# ✅ CORRECT (RSMS v2.0 snake_case)
---
parent_project: CodeRef Ecosystem
related_files:
  - src/component.py
---
```

### Issue: Health Score Lower Than Expected

**Symptom:** Document passes validation but score is 60-70

**Diagnosis:**
```python
from papertrail import validate_document

result = validate_document("docs/plan.json", "uds")
print(f"Health Score: {result['health_score']}/100")
print(f"Breakdown: {result.get('score_breakdown')}")
```

**Common Causes:**
- Missing optional fields (completeness penalty)
- Document older than 30 days (freshness penalty)
- Partially filled arrays (completeness penalty)

**Fix:** Regenerate document or manually populate missing fields

### Issue: Emoji Validation False Positives

**Symptom:** Validator reports emoji when none visible

**Cause:** Hidden Unicode emoji characters (Zero Width Joiner, etc)

**Fix:**
```bash
# Remove all emojis from file
python scripts/remove-emojis.py docs/MyDoc.md

# Re-validate
.\validators\resource-sheets\validate.ps1 -Path "docs/MyDoc.md"
```

### Issue: Triangular Reference Mismatch

**Symptom:** Script references test, but test doesn't reference script back

**Diagnosis:**
```bash
python validators/scripts/validate.py . --verbose
```

**Fix:**
```yaml
# In src/auth.py
---
resource_sheet: docs/Auth-RESOURCE-SHEET.md
related_test: tests/test_auth.py
---

# In tests/test_auth.py
---
resource_sheet: docs/Auth-RESOURCE-SHEET.md
related_script: src/auth.py  # ← Add this
---

# In docs/Auth-RESOURCE-SHEET.md
---
related_files:
  - src/auth.py
  - tests/test_auth.py  # ← Add this
---
```

---

## Migration Guide

### Migrating from RSMS v1.0 to v2.0

**Changes:**
- camelCase → snake_case for all fields
- `parentProject` → `parent_project`
- `relatedFiles` → `related_files`
- `relatedDocs` → `related_docs`

**Script:**
```python
# migrate_rsms.py
import re

def migrate_frontmatter(content):
    replacements = {
        'parentProject': 'parent_project',
        'relatedFiles': 'related_files',
        'relatedDocs': 'related_docs',
        'resourceSheet': 'resource_sheet',
        'relatedTest': 'related_test',
        'relatedScript': 'related_script'
    }

    for old, new in replacements.items():
        content = re.sub(f'{old}:', f'{new}:', content)

    return content

# Usage
with open('docs/MyDoc.md', 'r') as f:
    content = f.read()

migrated = migrate_frontmatter(content)

with open('docs/MyDoc.md', 'w') as f:
    f.write(migrated)
```

### Adding UDS to Existing Docs

**Before:**
```markdown
# My Feature Plan

Implementation details...
```

**After:**
```markdown
---
workorder_id: WO-FEATURE-IMPL-001
feature_id: my-feature
mcp_server: coderef-workflow
generated_at: 2026-01-08T10:00:00Z
version: 1.0.0
---

# My Feature Plan

Implementation details...

---

**Last Updated:** 2026-01-08
**Version:** 1.0.0
**Maintained by:** CodeRef Ecosystem
```

**Script:**
```python
from papertrail import inject_uds_headers

with open('docs/plan.md', 'r') as f:
    content = f.read()

updated = inject_uds_headers(
    content,
    workorder_id="WO-FEATURE-IMPL-001",
    feature_id="my-feature",
    mcp_server="coderef-workflow"
)

with open('docs/plan.md', 'w') as f:
    f.write(updated)
```

---

## API Reference

### Validator Module (`papertrail/validator.py`)

```python
def validate_document(doc_path: str, schema_type: str) -> dict:
    """
    Validate document against schema.

    Args:
        doc_path: Absolute path to document
        schema_type: "uds" | "rsms" | "script_frontmatter" | "plan"

    Returns:
        {
            "valid": bool,
            "errors": List[str],
            "health_score": int,
            "metadata": dict,
            "score_breakdown": dict
        }
    """
```

### Health Module (`papertrail/health.py`)

```python
def calculate_health_score(metadata: dict, doc_type: str) -> int:
    """
    Calculate 0-100 health score.

    Args:
        metadata: Extracted YAML frontmatter
        doc_type: "uds" | "rsms" | "standard"

    Returns:
        int: 0-100 score
    """

def get_score_breakdown(metadata: dict, doc_type: str) -> dict:
    """
    Get detailed score breakdown.

    Returns:
        {
            "traceability": int (0-40),
            "completeness": int (0-30),
            "freshness": int (0-20),
            "validation": int (0-10),
            "total": int (0-100)
        }
    """
```

### Template Engine Module (`papertrail/engine.py`)

```python
def render_template(template_path: str, context: dict) -> str:
    """
    Render Jinja2 template with CodeRef extensions.

    Args:
        template_path: Path to .j2 template
        context: Template variables

    Returns:
        str: Rendered content
    """

def load_extensions() -> list:
    """
    Load CodeRef Jinja2 extensions.

    Returns:
        List of extension instances
    """
```

### UDS Module (`papertrail/uds.py`)

```python
def inject_uds_headers(
    content: str,
    workorder_id: str,
    feature_id: str,
    mcp_server: str,
    version: str = "1.0.0"
) -> str:
    """
    Inject UDS YAML frontmatter into document.

    Returns:
        str: Content with UDS headers
    """

def log_workorder(workorder_id: str, description: str, project: str) -> None:
    """
    Log workorder to global workorder-log.txt.
    """

def query_workorder_log(
    workorder_pattern: str = None,
    project: str = None,
    limit: int = None
) -> list:
    """
    Query global workorder log.

    Returns:
        List of workorder entries
    """
```

---

## Schema Reference

### UDS Schema (`papertrail/schemas/uds-document.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["workorder_id", "feature_id", "mcp_server", "generated_at"],
  "properties": {
    "workorder_id": {
      "type": "string",
      "pattern": "^WO-[A-Z0-9-]+-\\d{3}$"
    },
    "feature_id": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$"
    },
    "mcp_server": {
      "type": "string",
      "enum": ["coderef-workflow", "coderef-docs", "coderef-context", "coderef-personas", "coderef-testing"]
    },
    "generated_at": {
      "type": "string",
      "format": "date-time"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    }
  }
}
```

### RSMS v2.0 Schema (`schemas/documentation/resource-sheet-metadata-schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["subject", "parent_project", "category", "version"],
  "properties": {
    "subject": {
      "type": "string",
      "minLength": 1
    },
    "parent_project": {
      "type": "string",
      "minLength": 1
    },
    "category": {
      "type": "string",
      "enum": ["mcp-server", "library", "tool", "framework", "service"]
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "related_files": {
      "type": "array",
      "items": {"type": "string"}
    },
    "related_docs": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "\\.md$"
      }
    }
  }
}
```

---

## Glossary

**UDS (Universal Documentation Standards)** - Metadata standard for workorder-based implementation docs (plan.json, DELIVERABLES.md)

**RSMS (Resource Sheet Metadata Standards)** - Metadata standard for architectural reference docs (resource sheets, component docs)

**Health Score** - 0-100 weighted score measuring document quality across 4 factors

**Traceability** - Ability to link document back to workorder/feature/server that created it

**Triangular Reference** - Bidirectional reference system between resource sheet, script, and test

**Frontmatter** - YAML metadata block at top of markdown file (between `---` delimiters)

**Snake Case** - Naming convention using underscores (e.g., `parent_project`, `related_files`)

**Text Markers** - Emoji-free status indicators ([PASS], [FAIL], [WARN], [INFO])

---

## Related Resources

**Documentation:**
- [Global Documentation Standards](../standards/documentation/global-documentation-standards.md) - Universal rules for all docs
- [Resource Sheet Standards](../standards/documentation/resource-sheet-standards.md) - RSMS v2.0 specification
- [Script Frontmatter Standards](../standards/documentation/script-frontmatter-standards.md) - Triangular reference rules
- [CLAUDE.md](../CLAUDE.md) - AI context documentation for Papertrail
- [README.md](../README.md) - User-facing documentation

**Schemas:**
- [Resource Sheet Metadata Schema](../schemas/documentation/resource-sheet-metadata-schema.json) - RSMS v2.0 JSON schema
- [Script Frontmatter Schema](../schemas/documentation/script-frontmatter-schema.json) - Script/test metadata schema
- [Plan Schema](../papertrail/schemas/plan.json) - plan.json schema

**Validators:**
- [Resource Sheet Validator](../validators/resource-sheets/validate.ps1) - PowerShell RSMS validator
- [Script Validator](../validators/scripts/validate.py) - Python triangular reference validator
- [Plan Validator](../validators/plans/validate.py) - Python plan.json validator

**CodeRef Ecosystem:**
- coderef-workflow: Planning and orchestration (uses UDS for plan.json)
- coderef-docs: Documentation generation (uses RSMS for resource sheets)
- coderef-context: Code intelligence (uses script frontmatter for traceability)
- coderef-personas: Expert agents (uses standards for consistency)
- coderef-testing: Test automation (uses script frontmatter for test discovery)

---

**Last Updated:** 2026-01-08
**Version:** 1.0.0
**Maintained by:** CodeRef Ecosystem
