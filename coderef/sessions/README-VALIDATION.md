# Session Validation Guide

## Quick Start

**Validate all sessions:**
```powershell
.\validate-sessions.ps1
```

**Validate with verbose output:**
```powershell
.\validate-sessions.ps1 -Verbose
```

**Auto-fix common typos:**
```powershell
.\validate-sessions.ps1 -FixTypos
```

---

## What It Does

The validation script checks all `communication.json` files against the JSON schema to ensure:

✅ **Correct status values** - Only `not_started`, `in_progress`, `complete` (rejects typos like "completed")
✅ **Valid workorder IDs** - Must match pattern `WO-{CATEGORY}-{ID}`
✅ **Valid agent IDs** - Must be one of the 10 recognized agents
✅ **Proper file paths** - Absolute Windows paths with escaped backslashes
✅ **Required fields** - All mandatory fields present
✅ **Type safety** - Strings are strings, integers are integers, etc.

---

## Example Output

### ✅ All Valid
```
🔍 Session Validation Report
============================================================

Found 3 session(s) to validate

✅ coderef-core-dashboard-integration/communication.json
✅ document-effectiveness/communication.json
✅ ecosystem-resource-inventory/communication.json

============================================================

📊 Summary
   Total: 3
   ✅ Valid: 3
   ❌ Invalid: 0

✅ All sessions valid!
```

### ❌ Validation Errors
```
🔍 Session Validation Report
============================================================

Found 2 session(s) to validate

❌ coderef-core-dashboard-integration/communication.json
   instancePath: /status
   message: must be equal to one of the allowed values
   allowedValues: ["not_started","in_progress","complete"]

✅ ecosystem-resource-inventory/communication.json

============================================================

📊 Summary
   Total: 2
   ✅ Valid: 1
   ❌ Invalid: 1

⚠️  Validation failed for 1 file(s)
Run with -FixTypos to automatically fix common status typos
```

### 🔧 Auto-Fix Mode
```
🔍 Session Validation Report
============================================================

Found 2 session(s) to validate

🔧 coderef-core-dashboard-integration/communication.json
   Fixing: status 'completed' → 'complete'
✅ coderef-core-dashboard-integration/communication.json

✅ ecosystem-resource-inventory/communication.json

============================================================

📊 Summary
   Total: 2
   ✅ Valid: 2
   ❌ Invalid: 0
   🔧 Fixed: 1

✅ All sessions valid!
```

---

## Common Errors & Fixes

### ❌ Status Typo
**Error:**
```
instancePath: /status
message: must be equal to one of the allowed values
```

**Fix:**
Change `"completed"` → `"complete"` (or run with `-FixTypos`)

**Valid values:** `not_started`, `in_progress`, `complete`

---

### ❌ Invalid Workorder ID
**Error:**
```
instancePath: /workorder_id
message: must match pattern "^WO-[A-Z0-9-]+-\\d{3}$"
```

**Fix:**
Workorder IDs must follow pattern: `WO-CATEGORY-001`

**Examples:**
- ✅ `WO-CORE-DASHBOARD-INTEGRATION-001`
- ✅ `WO-DOCUMENT-EFFECTIVENESS-002`
- ❌ `WO-core-001` (lowercase not allowed)
- ❌ `WORK-001` (must start with "WO-")

---

### ❌ Invalid Agent ID
**Error:**
```
instancePath: /agents/0/agent_id
message: must be equal to one of the allowed values
```

**Fix:**
Agent ID must be one of:
- `coderef-assistant`
- `coderef-context`
- `coderef-workflow`
- `coderef-docs`
- `coderef-personas`
- `coderef-testing`
- `papertrail`
- `coderef-system`
- `coderef-dashboard`
- `coderef-packages`

---

### ❌ Missing Required Field
**Error:**
```
instancePath: ""
message: must have required property 'workorder_id'
```

**Fix:**
Add the missing field. Required fields:
- `workorder_id`
- `feature_name`
- `created`
- `status`
- `description`
- `instructions_file`
- `orchestrator`
- `agents`

**Note:** `aggregation` is **optional** (computed by orchestrator). Agents should NEVER update aggregation to avoid file locking conflicts.

---

## Auto-Fix Typos

The `-FixTypos` flag automatically corrects these common mistakes:

| Typo | Corrected To |
|------|--------------|
| `completed` | `complete` |
| `done` | `complete` |
| `finished` | `complete` |
| `started` | `in_progress` |
| `running` | `in_progress` |
| `pending` | `not_started` |

---

## Integration with Workflows

### Pre-Commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
cd C:/Users/willh/.mcp-servers/coderef/sessions
pwsh -File validate-sessions.ps1
if [ $? -ne 0 ]; then
  echo "❌ Session validation failed - fix errors before committing"
  exit 1
fi
```

### CI/CD Pipeline
Add to GitHub Actions:
```yaml
- name: Validate Sessions
  run: |
    cd sessions
    pwsh -File validate-sessions.ps1
```

### Manual Workflow
1. Agent updates `communication.json`
2. Run `.\validate-sessions.ps1`
3. If errors, fix manually or use `-FixTypos`
4. Verify all sessions pass
5. Commit changes

---

## Troubleshooting

### ajv-cli not installed
**Error:**
```
⚠️  ajv-cli not found. Installing...
```

**Action:** Script auto-installs via `npm install -g ajv-cli`. Requires Node.js.

### Invalid JSON Syntax
**Error:**
```
❌ coderef-core-dashboard-integration/communication.json
   ERROR: Invalid JSON syntax - Unexpected token } in JSON at position 142
```

**Action:** Fix syntax error in JSON file (missing comma, extra bracket, etc.)

### Schema not found
**Error:**
```
❌ Schema not found: C:\Users\willh\.mcp-servers\coderef\sessions\communication-schema.json
```

**Action:** Ensure `communication-schema.json` exists in sessions directory

---

## Files

- **communication-schema.json** - JSON Schema definition (source of truth)
- **validate-sessions.ps1** - Validation script (this tool)
- **README-VALIDATION.md** - This documentation

---

**Last Updated:** 2026-01-04
**Schema Version:** 1.0.0
**Maintained by:** coderef orchestrator
