# Papertrail Validator Inventory

**Purpose:** Complete inventory of all validators and schemas in Papertrail (source of truth for CodeRef ecosystem)

**Last Updated:** 2026-01-10

---

## Validators (6 Total)

### 1. Resource Sheets Validator

**Location:** `validators/resource-sheets/validate.ps1`

**Purpose:** RSMS v2.0 compliance validation for resource/reference sheets

**Language:** PowerShell

**Validates:**
- YAML front matter presence (must start with `---`)
- Required UDS fields: `agent`, `date`, `task` (snake_case)
- Required RSMS fields: `subject`, `parent_project`, `category`
- Date format: `YYYY-MM-DD`
- Task enum: `REVIEW`, `CONSOLIDATE`, `DOCUMENT`, `UPDATE`, `CREATE`
- Category enum: `service`, `controller`, `model`, `utility`, `integration`, `component`, `middleware`, `validator`, `schema`, `config`, `other`
- Naming convention: `{ComponentName}-RESOURCE-SHEET.md`
- UDS section headers: `Executive Summary`, `Audience & Intent`, `Quick Reference`
- No emojis (text markers only: [PASS], [FAIL], [WARN], [INFO])

**Usage:**
```powershell
.\validators\resource-sheets\validate.ps1 -Path "docs/"
```

**Schema:** `schemas/documentation/resource-sheet-metadata-schema.json`

---

### 2. Script/Test Frontmatter Validator

**Location:** `validators/scripts/validate.py`

**Purpose:** Triangular bidirectional reference validation (resource sheet ↔ script ↔ test)

**Language:** Python

**Validates:**
- YAML frontmatter presence in scripts/tests
- Required field: `resource_sheet`
- Script has `related_test`, test has `related_script`
- Resource sheet exists and lists file in `related_files`
- Bidirectional consistency (script ↔ test references match)

**Supported Languages:** Python (.py), Bash (.sh), PowerShell (.ps1), TypeScript (.ts), JavaScript (.js)

**Usage:**
```bash
python validators/scripts/validate.py /path/to/project
python validators/scripts/validate.py /path/to/project --path src/
```

**Schema:** `schemas/documentation/script-frontmatter-schema.json`

---

### 3. Plan Validator (3 files)

**Location:** `validators/plans/`

**Files:**
- `validate.py` - Main validation entry point
- `plan_format_validator.py` - Format validation logic
- `schema_validator.py` - JSON schema validation

**Purpose:** plan.json schema validation for implementation plans

**Language:** Python

**Validates:**
- 10-section plan structure (META_DOCUMENTATION, 0_preparation, 1_executive_summary, etc.)
- Required metadata fields
- Task ID format
- Phase structure
- Testing strategy
- Success criteria

**Usage:**
```bash
python validators/plans/validate.py /path/to/plan.json
```

**Schemas:**
- `schemas/planning/plan.schema.json`
- `schemas/planning/plan-validator-schema.json`
- `schemas/planning/planning-analyzer-schema.json`
- `schemas/planning/planning-generator-schema.json`
- `schemas/planning/constants-schema.json`

---

### 4. Session Validator

**Location:** `validators/sessions/validate.ps1`

**Purpose:** Multi-agent session communication.json validation

**Language:** PowerShell

**Validates:**
- Workorder ID format: `WO-{CATEGORY}-{ID}-###`
- Feature name format: kebab-case
- Status enums: `not_started`, `in_progress`, `complete`
- Agent IDs: Valid CodeRef ecosystem agents
- File paths: Absolute Windows paths
- Required fields: workorder_id, feature_name, created, status, description, instructions_file, orchestrator, agents

**Auto-Fix Typos:**
- `completed` → `complete`
- `done` → `complete`
- `finished` → `complete`
- `started` → `in_progress`
- `running` → `in_progress`
- `pending` → `not_started`

**Usage:**
```powershell
pwsh validators/sessions/validate.ps1
pwsh validators/sessions/validate.ps1 -Verbose
pwsh validators/sessions/validate.ps1 -FixTypos
```

**Schema:** `schemas/sessions/communication-schema.json`

---

## Schemas (14 Total)

### Documentation Schemas (2)

1. **`schemas/documentation/resource-sheet-metadata-schema.json`**
   - RSMS v2.0 schema
   - Validates resource sheet YAML front matter
   - Required fields: agent, date, task, subject, parent_project, category

2. **`schemas/documentation/script-frontmatter-schema.json`**
   - Script/test frontmatter schema
   - Validates resource_sheet, related_test, related_script fields

---

### Planning Schemas (5)

1. **`schemas/planning/plan.schema.json`**
   - Main plan.json schema
   - 10-section structure validation

2. **`schemas/planning/plan-validator-schema.json`**
   - Plan validation rules

3. **`schemas/planning/planning-analyzer-schema.json`**
   - Planning analyzer configuration

4. **`schemas/planning/planning-generator-schema.json`**
   - Planning generator configuration

5. **`schemas/planning/constants-schema.json`**
   - Planning constants and defaults

---

### Session Schemas (1)

1. **`schemas/sessions/communication-schema.json`**
   - Multi-agent session communication file
   - Agent roster and status tracking
   - Orchestrator coordination

---

### MCP Schemas (5)

1. **`schemas/mcp/server-schema.json`**
   - MCP server configuration

2. **`schemas/mcp/mcp-client-schema.json`**
   - MCP client configuration

3. **`schemas/mcp/tool-handlers-schema.json`**
   - MCP tool handler definitions

4. **`schemas/mcp/type-defs-schema.json`**
   - MCP type definitions

5. **`schemas/mcp/error-responses-schema.json`**
   - MCP error response formats

---

### Security Schemas (1)

1. **`schemas/security/validation-schema.json`**
   - Security validation rules

---

## Validator Summary by Type

| Type | Count | Files |
|------|-------|-------|
| **PowerShell** | 2 | resource-sheets, sessions |
| **Python** | 4 | scripts, plans (3 files) |
| **Total Validators** | 6 | 6 validator scripts |
| **Total Schemas** | 14 | 14 JSON schemas |

---

## Schema Summary by Category

| Category | Count | Purpose |
|----------|-------|---------|
| **Documentation** | 2 | Resource sheets, script frontmatter |
| **Planning** | 5 | Implementation plans, analyzers, generators |
| **Sessions** | 1 | Multi-agent coordination |
| **MCP** | 5 | MCP server/client configuration |
| **Security** | 1 | Security validation |

---

## Integration Points

### coderef-workflow
- Uses: `validators/plans/` for plan.json validation
- Schemas: `schemas/planning/*.json`

### coderef-docs
- Uses: `validators/resource-sheets/` for RSMS compliance
- Schemas: `schemas/documentation/resource-sheet-metadata-schema.json`

### coderef (orchestrator)
- Uses: `validators/sessions/` for communication.json validation
- Schemas: `schemas/sessions/communication-schema.json`

### All Projects
- Uses: `validators/scripts/` for script/test frontmatter validation
- Schemas: `schemas/documentation/script-frontmatter-schema.json`

---

## Running All Validators

```powershell
# Resource sheets (PowerShell)
pwsh validators/resource-sheets/validate.ps1 -Path "docs/"

# Scripts/tests (Python)
python validators/scripts/validate.py /path/to/project

# Plans (Python)
python validators/plans/validate.py /path/to/plan.json

# Sessions (PowerShell)
pwsh validators/sessions/validate.ps1
```

---

## Next Steps

**Potential Additions:**
- TypeScript validators (currently in `validators/typescript/` - 6 files)
- Python library validators
- MCP server validators
- Schema cross-validation (ensure consistency across related schemas)

---

**Maintained by:** Papertrail
**Source of Truth:** C:\Users\willh\.mcp-servers\papertrail\validators\
