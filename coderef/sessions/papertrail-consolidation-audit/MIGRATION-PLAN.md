# Papertrail Migration Plan

**Status:** Ready for Execution
**Mode:** Copy files first, wire up later (safe migration)
**Total Files:** ~25 core files (Phase 1, 3, 4, 6, 7)

---

## Directory Structure to Create

```
papertrail/
├── schemas/
│   ├── security/
│   │   └── validation-schema.json
│   ├── mcp/
│   │   ├── error-responses-schema.json
│   │   ├── server-schema.json
│   │   ├── tool-handlers-schema.json
│   │   ├── mcp-client-schema.json
│   │   └── type-defs-schema.json
│   └── planning/
│       ├── plan.schema.json
│       ├── planning-analyzer-schema.json
│       ├── planning-generator-schema.json
│       ├── plan-validator-schema.json
│       └── constants-schema.json
├── validators/
│   └── planning/
│       ├── plan_validator.py
│       ├── plan_format_validator.py
│       └── schema_validator.py
└── test-infrastructure/
    ├── models.py
    ├── result_analyzer.py
    ├── test_runner.py
    ├── test_aggregator.py
    ├── framework_detector.py
    └── docs/
        ├── TESTING_GUIDE.md
        ├── USER-GUIDE.md
        ├── ARCHITECTURE.md
        └── SCHEMA.md
```

---

## Phase 1: Security Validation Schema (1 file)

**Source:** `C:\Users\willh\.mcp-servers\coderef-workflow\coderef\schemas\validation-schema.json`
**Destination:** `C:\Users\willh\.mcp-servers\papertrail\schemas\security\validation-schema.json`

**Purpose:** Security boundary - path traversal prevention

---

## Phase 3: Core MCP Schemas (5 files)

**Source Root:** `C:\Users\willh\.mcp-servers\coderef-workflow\coderef\schemas\`
**Destination:** `C:\Users\willh\.mcp-servers\papertrail\schemas\mcp\`

| File | Purpose |
|------|---------|
| error-responses-schema.json | Standard error structure |
| server-schema.json | MCP server configuration |
| tool-handlers-schema.json | MCP tool handler implementations |
| mcp-client-schema.json | MCP client-to-server communication |
| type-defs-schema.json | TypedDict structures |

---

## Phase 4: Test Infrastructure (9 files)

**Source Root:** `C:\Users\willh\.mcp-servers\coderef-testing\`
**Destination:** `C:\Users\willh\.mcp-servers\papertrail\test-infrastructure\`

| Source File | Destination |
|-------------|-------------|
| src/models.py | models.py |
| src/result_analyzer.py | result_analyzer.py |
| src/test_runner.py | test_runner.py |
| src/test_aggregator.py | test_aggregator.py |
| src/framework_detector.py | framework_detector.py |
| TESTING_GUIDE.md | docs/TESTING_GUIDE.md |
| coderef/user/USER-GUIDE.md | docs/USER-GUIDE.md |
| coderef/foundation-docs/ARCHITECTURE.md | docs/ARCHITECTURE.md |
| coderef/foundation-docs/SCHEMA.md | docs/SCHEMA.md |

---

## Phase 6: Planning Schemas (5 files)

**Source Root:** `C:\Users\willh\.mcp-servers\coderef-workflow\coderef\schemas\`
**Destination:** `C:\Users\willh\.mcp-servers\papertrail\schemas\planning\`

| File | Purpose |
|------|---------|
| plan.schema.json | Validates plan.json structure - 10-section format |
| planning-analyzer-schema.json | analysis.json output format |
| planning-generator-schema.json | Plan generation logic |
| plan-validator-schema.json | Validation results (0-100 score) |
| constants-schema.json | Naming conventions, value constraints |

**⚠️ CONFLICT-001:** `plan.schema.json` conflicts with existing `papertrail/schemas/plan.json`. MUST resolve before migration.

---

## Phase 7: Plan Validators (3 files)

**Source Root:** `C:\Users\willh\.mcp-servers\coderef-workflow\`
**Destination:** `C:\Users\willh\.mcp-servers\papertrail\validators\planning\`

| Source File | Purpose | LOC |
|-------------|---------|-----|
| generators/plan_validator.py | Validates plans (0-100 scoring) | ~500 |
| plan_format_validator.py | Enforces plan.json format | ~100 |
| schema_validator.py | Generic schema validation utilities | ~200 |

**Dependencies:** MUST migrate Phase 6 (planning schemas) BEFORE Phase 7

---

## Execution Commands

### Dry Run (Validate Paths)
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\willh\.mcp-servers\coderef\sessions\papertrail-consolidation-audit\migrate-to-papertrail.ps1" -DryRun
```

### Actual Migration
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\willh\.mcp-servers\coderef\sessions\papertrail-consolidation-audit\migrate-to-papertrail.ps1"
```

---

## Post-Migration Wiring Tasks

1. **Import Path Updates** - Update 50-100 imports across coderef-workflow
2. **Test Suite** - Run full test suite in papertrail (100% pass required)
3. **Schema Loader** - Update validator.py in papertrail to load all new schemas
4. **Documentation** - Update README, ARCHITECTURE, CLAUDE.md

---

## Critical Blocker

**CONFLICT-001:** Resolve plan.json vs plan.schema.json conflict
**Action Required:** Read and compare both files before Phase 6 migration

---

**Script Location:** `C:\Users\willh\.mcp-servers\coderef\sessions\papertrail-consolidation-audit\migrate-to-papertrail.ps1`
**Manifest:** `orchestrator-migration-manifest.json`
