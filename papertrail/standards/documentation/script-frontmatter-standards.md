# Script/Test Frontmatter Standards

**Purpose:** Define YAML frontmatter requirements for scripts and tests
**Scope:** All executable scripts (.py, .sh, .ps1, .ts, .js) and test files
**Enforcement:** `validators/scripts/validate.py`

---

## Overview

Scripts and tests use minimal YAML frontmatter in docstrings/comments to establish **triangular bidirectional references** with their resource sheets.

**Three-way relationship:**
- Resource Sheet ↔ Script (via `related_files`)
- Resource Sheet ↔ Test (via `related_files`)
- Script ↔ Test (via `related_test`/`related_script`)

---

## Field Naming Convention

**Standard:** All YAML field names use `snake_case` (consistent with RSMS v2.0)

---

## Required YAML Structure

### For Scripts

```python
"""
---
resource_sheet: docs/Component-RESOURCE-SHEET.md
related_test: tests/test_component.py
---
"""

# Script code here...
```

### For Tests

```python
"""
---
resource_sheet: docs/Component-RESOURCE-SHEET.md
related_script: src/component.py
---
"""

# Test code here...
```

---

## Required Fields

| Field | Type | Required In | Description | Format |
|-------|------|-------------|-------------|--------|
| `resource_sheet` | string | Scripts, Tests | Path to resource sheet documenting this code | Relative path ending in `.md` |
| `related_test` | string | Scripts only | Path to test file | Relative path ending in `.py`, `.ts`, or `.js` |
| `related_script` | string | Tests only | Path to script being tested | Relative path ending in `.py`, `.sh`, `.ps1`, `.ts`, `.js` |

---

## Validation Rules

### 1. File Existence
- `resource_sheet` file MUST exist
- `related_test` file MUST exist (for scripts)
- `related_script` file MUST exist (for tests)

### 2. Bidirectional Consistency

**Resource Sheet → Script:**
- Resource sheet's `related_files` MUST include script path

**Resource Sheet → Test:**
- Resource sheet's `related_files` MUST include test path

**Script → Test:**
- Script's `related_test` MUST point to test file
- Test's `related_script` MUST point back to script

### 3. Path Format
- All paths are relative to project root
- Use forward slashes `/` (cross-platform)
- No leading `/` or `./`

---

## Language-Specific Syntax

### Python

```python
"""
---
resource_sheet: docs/Validator-RESOURCE-SHEET.md
related_test: tests/test_validator.py
---
"""

def validate():
    pass
```

### Bash

```bash
#!/bin/bash
: '
---
resource_sheet: docs/Setup-RESOURCE-SHEET.md
related_test: tests/test_setup.sh
---
'

echo "Script code"
```

### PowerShell

```powershell
<#
---
resource_sheet: docs/Validator-RESOURCE-SHEET.md
related_test: tests/Validator.Tests.ps1
---
#>

Write-Host "Script code"
```

### TypeScript/JavaScript

```typescript
/**
 * ---
 * resource_sheet: docs/API-RESOURCE-SHEET.md
 * related_test: src/__tests__/api.test.ts
 * ---
 */

export function api() {}
```

---

## Complete Example

**Resource Sheet** (`docs/UDS-Validation-RESOURCE-SHEET.md`):
```yaml
---
agent: Claude
date: 2026-01-04
subject: UDS-Validation
parent_project: papertrail
category: validator
version: 1.0.0
related_files:
  - src/papertrail/validator.py
  - tests/test_validator.py
---
```

**Script** (`src/papertrail/validator.py`):
```python
"""
---
resource_sheet: docs/UDS-Validation-RESOURCE-SHEET.md
related_test: tests/test_validator.py
---
"""

class UDSValidator:
    pass
```

**Test** (`tests/test_validator.py`):
```python
"""
---
resource_sheet: docs/UDS-Validation-RESOURCE-SHEET.md
related_script: src/papertrail/validator.py
---
"""

def test_validator():
    assert True
```

---

## Validator Usage

```bash
# Validate all scripts/tests in project
python validators/scripts/validate.py /path/to/project

# Validate specific directory
python validators/scripts/validate.py /path/to/project --path src/

# Show detailed output
python validators/scripts/validate.py /path/to/project --verbose
```

---

## Benefits

1. **Single source of truth** - Resource sheet contains all metadata
2. **Minimal script overhead** - Only 2 fields in frontmatter
3. **Automatic validation** - Triangular references ensure consistency
4. **Traceability** - Easy to find related documentation and tests
5. **Auto-extraction** - Scripts can read metadata from resource sheet

---

**Version:** 1.0.0
**Last Updated:** 2026-01-04
**Maintained by:** Papertrail Standards Team
