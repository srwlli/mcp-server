---
agent: Lloyd (Planning Assistant)
date: 2026-01-10
task: DOCUMENT
---

# Emoji & Timestamp Enforcement Policy

## Overview

This document defines the universal emoji and timestamp policies for the CodeRef ecosystem and how they integrate with the UDS validation system.

## Emoji Policy

### Rule: Strict No-Emoji Enforcement

**Policy**: ALL generated documentation must be emoji-free.

**Exception**: `coderef/user/` documents MAY contain emojis (user-facing guides, tutorials).

**Enforcement**:
- BaseUDSValidator checks ALL documents for emojis
- Emojis trigger WARNINGS (not errors) to maintain flexibility
- Warning severity can be upgraded to MINOR/MAJOR in strict mode

**Script Ownership**:
- **Owner**: `coderef-docs` MCP server
- **Location**: `C:\Users\willh\Desktop\assistant\scripts\remove-emojis.py`
- **Usage**: Run post-generation to clean documents
- **Integration**: Called by coderef-docs generators before writing files

### Text Marker Replacements

Use these instead of emojis:

| Emoji | Text Marker | Use Case |
|-------|-------------|----------|
| ✅ | `[PASS]` | Test passing, validation success |
| ❌ | `[FAIL]` | Test failing, validation error |
| ⚠️ | `[WARN]` | Warnings, cautions |
| ℹ️ | `[INFO]` | Information, notes |
| 🔄 | `[IN PROGRESS]` | Work in progress |
| ⏳ | `[PENDING]` | Pending action |
| 📝 | `[NOTE]` | Important note |
| 🎯 | `[TARGET]` | Goal, objective |

### Implementation in Validators

**File**: `papertrail/validators/emoji_checker.py`

```python
def check_emojis(content: str, file_path: Optional[Path] = None) -> tuple[int, list[str]]:
    """
    Check content for emojis and return warnings.
    
    Returns:
        (emoji_count, warnings)
    """
    # User documents are exempt
    if is_user_document(file_path):
        return (0, [])
    
    # Detect emojis
    emojis_found = detect_emojis(content)
    
    if emojis_found:
        warnings.append(
            f"Document contains {len(emojis_found)} emoji(s). "
            f"Remove emojis for UDS compliance."
        )
    
    return (len(emojis_found), warnings)
```

**Integration**: BaseUDSValidator.validate_content() calls check_emojis()

---

## Timestamp Policy

### Rule: Universal Timestamp Utility

**Policy**: ALL timestamp generation MUST use `coderef-docs/utils/timestamp.py`

**Script Ownership**:
- **Owner**: `coderef-docs` MCP server
- **Location**: `C:\Users\willh\.mcp-servers\coderef-docs\utils\timestamp.py`
- **Standard**: ISO 8601 format with timezone
- **Usage**: Import in all generators (foundation, workorder, resource sheets)

### Timestamp Functions

```python
from utils.timestamp import get_date, get_timestamp, get_iso_timestamp

# For YAML front matter 'date' field (YYYY-MM-DD)
date: {get_date()}  # "2026-01-10"

# For YAML front matter 'timestamp' field (ISO 8601 with timezone)
timestamp: {get_timestamp()}  # "2026-01-10T14:30:45-05:00"

# For plan.json 'updated_at' field (ISO 8601 UTC)
updated_at: {get_iso_timestamp()}  # "2026-01-10T19:30:45Z"
```

### Schema Alignment

**All UDS schemas already support these formats:**

1. **Base Schema** (`base-frontmatter-schema.json`):
   ```json
   "date": {
     "type": "string",
     "pattern": "^\d{4}-\d{2}-\d{2}$"
   }
   ```

2. **Foundation Schema** (`foundation-doc-frontmatter-schema.json`):
   ```json
   "timestamp": {
     "type": "string",
     "pattern": "^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
   }
   ```

3. **Workorder Schema** (`workorder-doc-frontmatter-schema.json`):
   ```json
   "timestamp": {
     "type": "string",
     "pattern": "^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
   }
   ```

**Result**: Schema validation will PASS for all timestamp utility outputs.

---

## Integration Points

### 1. coderef-docs Generators

**Files to update:**
- `coderef-docs/generators/foundation_generator.py`
- `coderef-docs/generators/resource_sheet_generator.py`
- `coderef-docs/tool_handlers.py`

**Changes:**
```python
from utils.timestamp import get_date, get_timestamp
from scripts.remove_emojis import remove_emojis

# In template rendering
frontmatter = {
    'agent': 'coderef-docs v1.2.0',
    'date': get_date(),
    'timestamp': get_timestamp(),
    # ... other fields
}

# After rendering
rendered_content, emoji_count = remove_emojis(rendered_content)
```

### 2. coderef-workflow Generators

**Files to update:**
- `coderef-workflow/generators/plan_generator.py`
- `coderef-workflow/generators/deliverables_generator.py`
- `coderef-workflow/generators/planning_analyzer.py`

**Note**: coderef-workflow should import timestamp utility from coderef-docs:
```python
import sys
sys.path.append(str(Path.home() / ".mcp-servers" / "coderef-docs"))
from utils.timestamp import get_date, get_iso_timestamp
```

### 3. Papertrail Validators

**Already implemented:**
- `papertrail/validators/emoji_checker.py` - Emoji detection
- `papertrail/validators/base.py` - Calls emoji checker (pending integration)

**Timestamp validation:**
- Schemas already validate timestamp patterns
- No additional code needed (regex patterns handle it)

---

## Future Tasks

### Task 1: Own plan_validator.py
**File**: `C:\Users\willh\.mcp-servers\coderef-workflow\generators\plan_validator.py`
**Action**: Move to Papertrail as PlanDocValidator
**Reason**: Centralize all validation in Papertrail

**Steps:**
1. Create `papertrail/validators/plan.py` (PlanDocValidator)
2. Extend workorder-doc-frontmatter-schema.json for plan-specific fields
3. Update coderef-workflow to import from Papertrail
4. Deprecate old plan_validator.py

### Task 2: Complete Emoji Integration
**File**: `papertrail/validators/base.py`
**Action**: Add emoji checking to validate_content()
**Status**: Drafted but not committed

### Task 3: Copy Timestamp Utility to Papertrail
**Consideration**: Should Papertrail have its own copy or import from coderef-docs?
**Decision needed**: Dependency direction (likely coderef-docs → Papertrail)

---

## Validation Examples

### Example 1: Valid Document (No Emojis, Valid Timestamp)

```markdown
---
agent: coderef-docs v1.2.0
date: 2026-01-10
task: DOCUMENT
workorder_id: WO-AUTH-SYSTEM-001
generated_by: coderef-docs v1.2.0
feature_id: auth-system
timestamp: 2026-01-10T14:30:45Z
doc_type: architecture
---

# Architecture

[PASS] All tests passing
[INFO] See API.md for details
```

**Validation**: ✅ PASS (no emojis, valid timestamps)

### Example 2: Invalid Document (Contains Emojis)

```markdown
---
agent: coderef-docs v1.2.0
date: 2026-01-10
task: DOCUMENT
---

# Architecture

✅ All tests passing
❌ Known issue with auth
```

**Validation**: ⚠️ WARNINGS
- "Document contains 2 emoji(s): ✅, ❌. Remove emojis for UDS compliance."
- "Line 7: '✅' in 'All tests passing'"
- "Line 8: '❌' in 'Known issue with auth'"

### Example 3: User Document (Emojis Allowed)

```markdown
---
agent: manual
date: 2026-01-10
task: CREATE
---

# User Guide 🎯

Welcome to the guide! 👋

- Step 1: Install ✅
- Step 2: Configure ⚙️
```

**File**: `coderef/user/USER-GUIDE.md`
**Validation**: ✅ PASS (user documents exempt from emoji policy)

---

## Summary

**Emoji Policy**: Strict no-emoji enforcement via validators + removal script
**Timestamp Policy**: Universal timestamp utility ensures schema compliance
**Validation**: Automated warnings for emojis, automated validation for timestamps
**Ownership**: coderef-docs owns both scripts, Papertrail enforces policies

**Next Steps**:
1. Complete emoji checker integration in base.py
2. Update coderef-docs generators to use timestamp utility
3. Update coderef-workflow generators to import timestamp utility
4. Migrate plan_validator.py to Papertrail (future task)
