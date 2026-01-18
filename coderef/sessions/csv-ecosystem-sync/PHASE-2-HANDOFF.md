# Phase 2 Handoff - CSV Integration

**Session:** WO-CSV-ECOSYSTEM-SYNC-001
**Phase:** 2 - CSV Integration & Updates
**Lead Agent:** coderef-docs
**Support Agent:** coderef-dashboard (for dashboard-specific resources only)
**Orchestrator Approval:** 2026-01-17

---

## Critical Decisions (User Approved)

✅ **Decision 1: Global Command Architecture**
- ALL 67 commands are global
- Update ALL command paths to: `C:\Users\willh\.claude\commands\{command}.md`
- No project-local commands exist (all migrated to global)

✅ **Decision 2: /archive-file Ownership**
- Move `/archive-file.md` from `coderef-workflow/.claude/commands/` to `~/.claude/commands/`
- Server attribution: coderef-workflow
- Add to CSV after moving file

✅ **Decision 3: Persona JSON Files**
- YES - Add ALL production persona files to CSV
- Total: 12 personas (exclude test fixtures and backups)
- Type: Persona, Server: coderef-personas, Category: Persona Definitions

✅ **Decision 4: UI Resource Granularity**
- NO - Do NOT add UI components, pages, API routes, contexts, hooks, widgets
- CSV tracks: "files, tools, scripts, logic, documents" - NOT UI components
- Dashboard UI resources remain undocumented in CSV (intentional)

---

## Phase 2 Execution Plan

### Step 1: Move /archive-file to Global (PREREQUISITE)

**Action:** Move file from project-local to global
```bash
# Current location
C:\Users\willh\.mcp-servers\coderef-workflow\.claude\commands\archive-file.md

# Target location
C:\Users\willh\.claude\commands\archive-file.md
```

**Verification:** File exists at global location, removed from coderef-workflow

---

### Step 2: Command Path Corrections (67 entries)

**Scope:** Update ALL command paths to global location

**CSV Updates:**
- coderef-docs commands (12 entries)
- coderef-workflow commands (26 entries) + /archive-file (1 new entry)
- coderef-personas commands (13 entries)
- coderef-testing commands (15 entries)

**New Path Format:** `C:\Users\willh\.claude\commands\{command}.md`

**Example:**
```csv
# BEFORE
Command,coderef-docs,Documentation,/create-resource-sheet,Create resource sheet,active,C:\Users\willh\.mcp-servers\coderef-docs\.claude\commands\create-resource-sheet.md,,

# AFTER
Command,coderef-docs,Documentation,/create-resource-sheet,Create resource sheet,active,C:\Users\willh\.claude\commands\create-resource-sheet.md,,
```

**Verification:** All 68 command paths use global location (67 existing + 1 new /archive-file)

---

### Step 3: MCP Tool Path Corrections (51 entries)

**Scope:** Remove `src\{server}\` prefix from all MCP tool paths

**Affected:**
- coderef-workflow: 37 tools
- coderef-testing: 14 tools

**Path Fix:**
```csv
# BEFORE
Tool,coderef-workflow,Planning,gather_context,Gather project context,active,C:\Users\willh\.mcp-servers\coderef-workflow\src\coderef_workflow\server.py,,

# AFTER
Tool,coderef-workflow,Planning,gather_context,Gather project context,active,C:\Users\willh\.mcp-servers\coderef-workflow\server.py,,
```

**Verification:** All tool paths point to `{server}\server.py` (no src subdirectory)

---

### Step 4: Add Papertrail Resources (16 new entries)

**4 MCP Tools:**
```csv
Tool,papertrail,UDS Validation,validate_stub,"Validate a stub.json file against stub-schema.json. Checks required fields, format validation (stub_id, feature_name, dates), and optionally auto-fills missing fields with defaults.",active,C:\Users\willh\.mcp-servers\papertrail\papertrail\server.py,,
Tool,papertrail,UDS Validation,validate_schema_completeness,"Validate that a JSON schema has required_sections defined for all doc_types. Reports completeness, issues, and section counts per doc_type.",active,C:\Users\willh\.mcp-servers\papertrail\papertrail\server.py,,
Tool,papertrail,UDS Validation,validate_all_schemas,"Validate all JSON schemas in schemas/documentation/ directory. Returns summary report with pass/fail counts and lists issues for each schema.",active,C:\Users\willh\.mcp-servers\papertrail\papertrail\server.py,,
Tool,papertrail,UDS Validation,validate_communication,"Validate a communication.json file against communication-schema.json. Checks required fields, agent structure, outputs validation.",active,C:\Users\willh\.mcp-servers\papertrail\papertrail\server.py,,
```

**2 Schemas:**
```csv
Schema,papertrail,Sessions,communication-schema.json,"Agent roster and status tracking for multi-agent sessions in the CodeRef ecosystem. Supports 1-N agents (flexible agent count, not fixed roster).",active,C:\Users\willh\.mcp-servers\papertrail\schemas\communication-schema.json,,
Schema,papertrail,Planning,plan.schema.json,"JSON schema for plan.json structure - validates 10-section implementation plan format with META_DOCUMENTATION, PREPARATION, EXECUTIVE_SUMMARY, etc.",active,C:\Users\willh\.mcp-servers\papertrail\schemas\planning\plan.schema.json,,
```

**10 Validators:**
```csv
Validator,papertrail,Session,CommunicationValidator,"Validates communication.json files for multi-agent sessions. Checks agent structure, status enums, and workorder tracking.",active,C:\Users\willh\.mcp-servers\papertrail\papertrail\validators\communication.py,,
Validator,papertrail,Core,EmojiChecker,"Detects and reports emoji usage in documentation. Enforces no-emoji policy across CodeRef ecosystem per global standards.",active,C:\Users\willh\.mcp-servers\papertrail\papertrail\validators\emoji_checker.py,,
Validator,papertrail,Core,ValidatorFactory,"Auto-detects document type and returns appropriate validator. Uses 30+ path patterns and frontmatter analysis for automatic validator selection.",active,C:\Users\willh\.mcp-servers\papertrail\papertrail\validators\factory.py,,
Validator,papertrail,Documentation,Resource Sheet PowerShell Validator,"RSMS v2.0 compliance validation for resource sheets. Checks snake_case frontmatter, required fields, naming conventions, and UDS section headers.",active,C:\Users\willh\.mcp-servers\papertrail\validators\resource-sheets\validate.ps1,,
Validator,papertrail,Session,Session PowerShell Validator,"Validates multi-agent session communication files against JSON schema. Auto-fixes common status typos (completed → complete, etc.).",active,C:\Users\willh\.mcp-servers\papertrail\validators\sessions\validate.ps1,,
Validator,papertrail,Session,Agent Resources Validator,"Validates agent resource allocation and tracking in multi-agent session files. Ensures proper agent workspace structure.",active,C:\Users\willh\.mcp-servers\papertrail\validators\sessions\validate-agent-resources.ps1,,
Validator,papertrail,Workflow,Plan Validator Script,"Command-line validator for plan.json files. Provides standalone validation outside MCP server context.",active,C:\Users\willh\.mcp-servers\papertrail\validators\plans\validate.py,,
Validator,papertrail,Workflow,PlanFormatValidator,"Format validation for plan.json structure. Checks required sections, task structure, and complexity field (no time estimates).",active,C:\Users\willh\.mcp-servers\papertrail\validators\plans\plan_format_validator.py,,
Validator,papertrail,Workflow,PlanSchemaValidator,"JSON schema validation for plan.json against plan.schema.json. Validates metadata, phase structure, and task definitions.",active,C:\Users\willh\.mcp-servers\papertrail\validators\plans\schema_validator.py,,
Validator,papertrail,Documentation,Script Frontmatter Validator,"Triangular bidirectional reference validation. Ensures resource sheet ↔ script ↔ test references are consistent and all files exist.",active,C:\Users\willh\.mcp-servers\papertrail\validators\scripts\validate.py,,
```

---

### Step 5: Add Dashboard Python Scripts (3 new entries)

```csv
Script,coderef-dashboard,Scanners,build-source-of-truth.py,"Scans dashboard project for all resources (tools, commands, scripts, etc.) and generates comprehensive inventory CSV.",active,C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\resources\coderef\build-source-of-truth.py,,
Script,coderef-dashboard,Utilities,merge-and-dedupe.py,"Merges multiple CSV files and removes duplicate entries based on Type+Name+Server composite key.",active,C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\resources\coderef\merge-and-dedupe.py,,
Script,coderef-dashboard,Validators,validate-csv.py,"Validates tools-and-commands.csv for schema compliance, data quality, and referential integrity.",active,C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\resources\coderef\validate-csv.py,,
```

---

### Step 6: Add coderef-core Scripts (3 new entries)

```csv
Script,coderef-core,Setup,setup_coderef_dirs.py,"Creates .coderef/ directory structure with Phase 0 initialization (directories, schemas, templates). Creates 8 directories (.coderef/reports, .coderef/diagrams, etc.). Used via CLI: py setup_coderef_dirs.py <project_path>",active,C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core\scripts\setup-coderef-dir\setup_coderef_dirs.py,,
Script,coderef-core,Testing,test_setup_coderef_dirs.py,"Unit tests for setup_coderef_dirs.py with 100% test coverage. Tests all 8 directories creation, validation logic, and error handling.",active,C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core\scripts\setup-coderef-dir\test_setup_coderef_dirs.py,,
Script,coderef-core,Scanners,scan.cjs,"CLI scanner implementation for CodeRef analysis (CommonJS). Standalone CLI tool for running CodeRef scans. Uses TypeScript scanner engine (src/scanner/scanner.ts).",active,C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core\scripts\scan-cli\scan.cjs,,
```

---

### Step 7: Add coderef-docs Resources (6 new entries)

**2 Commands:**
```csv
Command,coderef-docs,Documentation,/coderef-foundation-docs,"Generate foundation documentation using deprecated tool (use /generate-docs instead)",deprecated,C:\Users\willh\.claude\commands\coderef-foundation-docs.md,,
Command,coderef-docs,Documentation,/features-inventory,"Generate FEATURES.md inventory with workorder tracking",active,C:\Users\willh\.claude\commands\features-inventory.md,,
```

**4 Scripts:**
```csv
Script,coderef-docs,Utilities,consistency_checker.py,"Consistency checking module for standards enforcement",active,C:\Users\willh\.mcp-servers\coderef-docs\generators\consistency_checker.py,,
Script,coderef-docs,Utilities,validation_pipeline.py,"Validation pipeline for document health checks",active,C:\Users\willh\.mcp-servers\coderef-docs\generators\validation_pipeline.py,,
Script,coderef-docs,Utilities,user_guide_generator.py,"Generator for comprehensive USER-GUIDE.md documentation",active,C:\Users\willh\.mcp-servers\coderef-docs\generators\user_guide_generator.py,,
Script,coderef-docs,Utilities,remove-emojis.py,"Utility script to remove emoji characters from documentation",active,C:\Users\willh\.mcp-servers\coderef-docs\scripts\remove-emojis.py,,
```

---

### Step 8: Add Persona Files (12 new entries)

```csv
Persona,coderef-personas,Persona Definitions,ava.json,"Ava persona definition (Frontend Specialist)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\base\ava.json,,
Persona,coderef-personas,Persona Definitions,coderef-assistant.json,"CodeRef Assistant persona definition (Orchestrator)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\base\coderef-assistant.json,,
Persona,coderef-personas,Persona Definitions,lloyd.json,"Lloyd persona definition (Multi-Agent Coordinator)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\base\lloyd.json,,
Persona,coderef-personas,Persona Definitions,marcus.json,"Marcus persona definition (Backend Specialist)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\base\marcus.json,,
Persona,coderef-personas,Persona Definitions,quinn.json,"Quinn persona definition (Testing Specialist)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\base\quinn.json,,
Persona,coderef-personas,Persona Definitions,taylor.json,"Taylor persona definition (General Purpose Agent)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\base\taylor.json,,
Persona,coderef-personas,Persona Definitions,coderef-context-agent.json,"CodeRef Context Agent persona definition (Code Intelligence Specialist)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\coderef-personas\coderef-context-agent.json,,
Persona,coderef-personas,Persona Definitions,coderef-docs-agent.json,"CodeRef Docs Agent persona definition (Documentation Specialist)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\coderef-personas\coderef-docs-agent.json,,
Persona,coderef-personas,Persona Definitions,coderef-mcp-lead.json,"CodeRef MCP Lead persona definition (Lead System Architect)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\coderef-personas\coderef-mcp-lead.json,,
Persona,coderef-personas,Persona Definitions,coderef-personas-agent.json,"CodeRef Personas Agent persona definition (Personas Specialist)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\coderef-personas\coderef-personas-agent.json,,
Persona,coderef-personas,Persona Definitions,coderef-testing-agent.json,"CodeRef Testing Agent persona definition (Testing Specialist)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\coderef-personas\coderef-testing-agent.json,,
Persona,coderef-personas,Persona Definitions,research-scout.json,"Research Scout persona definition (Research & Discovery Specialist)",active,C:\Users\willh\.mcp-servers\coderef-personas\personas\custom\research-scout.json,,
```

**Exclude:** integration-test.json (test fixture), nfl-scraper-expert-*.json (backups)

---

### Step 9: Fix CSV Description Truncations (5 entries)

**coderef-context tools with truncated descriptions:**

```csv
# BEFORE
Tool,coderef-context,Code Intelligence,coderef_context,"Generate comprehensive codebase context with visual architecture diagram. Returns project metadata",active,C:\Users\willh\.mcp-servers\coderef-context\server.py,,

# AFTER
Tool,coderef-context,Code Intelligence,coderef_context,"Generate comprehensive codebase context with visual architecture diagram. Returns project metadata, stats, and ready-to-render Mermaid diagram in single call.",active,C:\Users\willh\.mcp-servers\coderef-context\server.py,,
```

**Fix descriptions for:**
1. coderef_context
2. coderef_export
3. coderef_incremental_scan
4. coderef_query
5. coderef_scan

**Solution:** Properly escape commas or use double-quotes for entire description field.

---

### Step 10: Timestamp Population (174 entries)

**Scope:** Auto-fill empty Created/LastUpdated fields using git log

**Method:**
```bash
# For each resource with empty timestamps:
git log --follow --format=%aI --diff-filter=A -- <file_path> | tail -1  # Created
git log --follow --format=%aI -1 -- <file_path>  # LastUpdated
```

**Affected:** 174/306 resources (57%)

**Output Format:** ISO 8601 (e.g., `2026-01-17T10:30:00-05:00`) or CSV-friendly (`2026-01-17`)

**Verification:** All 306 resources have non-empty Created and LastUpdated timestamps after update

---

### Step 11: Server Re-attribution (1 entry)

**Change:**
```csv
# BEFORE
Command,coderef-docs,Documentation,/audit-plans,Audit implementation plans,active,C:\Users\willh\.claude\commands\audit-plans.md,,

# AFTER
Command,coderef-workflow,Planning,/audit-plans,Audit implementation plans,active,C:\Users\willh\.claude\commands\audit-plans.md,,
```

**Reason:** Planning audit belongs to workflow server, not docs server.

---

### Step 12: Duplicate Resource Sheet Cleanup (2 entries)

**Remove from CSV:**
- `C:\Users\willh\Desktop\coderef-dashboard\coderef\resource-sheets\Electron-IPC-Analysis-RESOURCE-SHEET.md` (root level)
- `C:\Users\willh\Desktop\coderef-dashboard\coderef\resource-sheets\Notifications-UX-Review-RESOURCE-SHEET.md` (root level)

**Keep in CSV:**
- `C:\Users\willh\Desktop\coderef-dashboard\coderef\resource-sheets\analysis\Electron-IPC-Analysis-RESOURCE-SHEET.md`
- `C:\Users\willh\Desktop\coderef-dashboard\coderef\resource-sheets\analysis\Notifications-UX-Review-RESOURCE-SHEET.md`

**Verification:** Only 1 entry per resource sheet, canonical path in subdirectory

---

### Step 13: Stale Command Verification (43 entries)

**Scope:** Verify if 43 commands were deleted or moved to global

**Affected:**
- coderef-workflow: 26 commands (likely moved to global - covered in Step 2)
- coderef-personas: 13 commands (likely moved to global - covered in Step 2)
- coderef-testing: 15 commands (likely moved to global - covered in Step 2)

**Action:**
1. Verify each command exists in `~/.claude/commands/`
2. If YES: Already covered in Step 2 (path correction)
3. If NO: Remove from CSV (command was deleted)

**Expected:** All 43 commands exist globally, so Step 2 resolves this entirely.

---

## Phase 2 Validation Checklist

After all updates complete:

- [ ] **Move /archive-file:** File relocated to global commands directory
- [ ] **Command Paths:** All 68 commands use global path (67 existing + 1 new)
- [ ] **Tool Paths:** All 51 tools have correct path (no src/ prefix)
- [ ] **Papertrail:** 16 new resources added (4 tools, 2 schemas, 10 validators)
- [ ] **Dashboard Scripts:** 3 scripts added
- [ ] **coderef-core Scripts:** 3 scripts added
- [ ] **coderef-docs Resources:** 6 resources added (2 commands, 4 scripts)
- [ ] **Persona Files:** 12 personas added
- [ ] **Descriptions:** 5 truncated descriptions fixed
- [ ] **Timestamps:** 174 empty timestamps populated from git log
- [ ] **Re-attribution:** /audit-plans moved to coderef-workflow server
- [ ] **Duplicates:** 2 duplicate resource sheets removed
- [ ] **Stale Commands:** 43 commands verified (likely all covered in command path updates)
- [ ] **Run validate-csv.py:** 100% data quality, no errors
- [ ] **CSV Change Log:** Created with before/after metrics

---

## Expected Metrics (After Phase 2)

**Before Phase 2:**
- Total Resources: 306
- Resource Types: 9
- Empty Timestamps: 174 (57%)
- Incorrect Paths: 119 (67 commands + 51 tools + 1 /archive-file)

**After Phase 2:**
- Total Resources: 346 (306 + 40 new resources)
- Resource Types: 10 (added "Persona")
- Empty Timestamps: 0 (0%)
- Incorrect Paths: 0 (0%)
- Data Quality: 100%

**New Resources Breakdown:**
- Papertrail: +16 (4 tools, 2 schemas, 10 validators)
- Dashboard: +3 (scripts)
- coderef-core: +3 (scripts)
- coderef-docs: +6 (2 commands, 4 scripts)
- coderef-personas: +12 (persona JSON files)
- coderef-workflow: +1 (/archive-file command)
- **Total: +40** (NOT +123, UI components excluded per decision #4)

---

## Handoff Instructions for coderef-docs Agent

**Your Role:** CSV Integration Lead

**Tasks:**
1. Move /archive-file to global directory (prerequisite)
2. Execute Steps 2-13 (all CSV updates)
3. Run validate-csv.py
4. Create CSV change log
5. Update Phase 2 communication.json status

**Working Directory:** `C:\Users\willh\.mcp-servers\coderef-docs`

**CSV Location:** `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\resources\coderef\tools-and-commands.csv`

**Audit Reports:** `C:\Users\willh\.mcp-servers\coderef\sessions\csv-ecosystem-sync\{agent-id}\outputs\`

**Success Criteria:**
- All 40 new resources added
- All 119 path corrections applied
- All 174 timestamps populated
- validate-csv.py passes with 100% data quality
- CSV change log documents all changes

**Estimated Duration:** 2-3 hours

---

**Phase 2 Status:** READY TO START
**Awaiting:** coderef-docs agent activation to begin CSV integration
