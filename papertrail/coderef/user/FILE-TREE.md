---
agent: Claude Code
date: 2026-01-10
task: UPDATE
---

# Papertrail File Tree

```
papertrail/
│
├── Core Documentation
│   ├── CLAUDE.md                           # AI context documentation (this file)
│   ├── README.md                           # User-facing documentation
│   ├── WO-PAPERTRAIL-EXTENSIONS-001-SUMMARY.md
│   ├── DEMO_OUTPUT.md
│   └── document-io-inventory.json
│
├── Python Package
│   ├── setup.py                            # Package setup
│   ├── demo.py                             # Demo script
│   ├── papertrail/                         # Main package
│   │   ├── __init__.py
│   │   ├── validator.py                    # UDS/RSMS validation
│   │   ├── health.py                       # Health scoring
│   │   ├── engine.py                       # Jinja2 template engine
│   │   ├── uds.py                          # UDS utilities
│   │   ├── schemas/                        # Document schemas
│   │   │   ├── api.json
│   │   │   ├── architecture.json
│   │   │   ├── deliverables.json
│   │   │   ├── plan.json
│   │   │   └── readme.json
│   │   └── extensions/                     # Jinja2 extensions
│   │       ├── __init__.py
│   │       ├── coderef_context.py         # CodeRef integration
│   │       ├── coderef_context_part1.py
│   │       ├── git_integration.py         # Git helpers
│   │       └── workflow.py                # Workflow helpers
│   └── papertrail.egg-info/               # Package metadata
│
├── Schemas
│   ├── schemas/
│   │   ├── documentation/                  # Documentation schemas
│   │   │   ├── resource-sheet-metadata-schema.json  # RSMS v2.0
│   │   │   └── script-frontmatter-schema.json       # Script/test metadata
│   │   ├── mcp/                           # MCP server schemas
│   │   │   ├── error-responses-schema.json
│   │   │   ├── mcp-client-schema.json
│   │   │   ├── server-schema.json
│   │   │   ├── tool-handlers-schema.json
│   │   │   └── type-defs-schema.json
│   │   ├── planning/                      # Planning workflow schemas
│   │   │   ├── constants-schema.json
│   │   │   ├── plan.schema.json
│   │   │   ├── planning-analyzer-schema.json
│   │   │   ├── planning-generator-schema.json
│   │   │   └── plan-validator-schema.json
│   │   ├── security/                      # Security schemas
│   │   │   └── validation-schema.json
│   │   └── workflow/                      # Workflow artifact schemas (NEW)
│   │       ├── analysis-json-schema.json           # Project analysis validation
│   │       └── execution-log-json-schema.json      # Task execution log validation
│
├── Standards
│   └── standards/
│       └── documentation/
│           ├── global-documentation-standards.md    # Global rules (headers, footers, no emojis)
│           ├── resource-sheet-standards.md          # RSMS v2.0 standards
│           └── script-frontmatter-standards.md      # Script/test frontmatter standards
│
├── Validators
│   ├── validators/
│   │   ├── resource-sheets/               # RSMS validation
│   │   │   └── validate.ps1               # PowerShell validator
│   │   ├── scripts/                       # Script frontmatter validation
│   │   │   └── validate.py                # Python validator
│   │   ├── plans/                         # Plan.json validation
│   │   │   ├── validate.py
│   │   │   ├── plan_format_validator.py
│   │   │   └── schema_validator.py
│   │   └── typescript/                    # TypeScript validators
│   │       ├── breaking-change-detector.ts
│   │       ├── cli-validator.ts
│   │       ├── coderef-validator.ts
│   │       ├── drift-detector.ts
│   │       ├── path-validator.ts
│   │       └── tag-validator.ts
│   └── papertrail/validators/             # Python UDS validators (NEW)
│       ├── base.py                        # BaseUDSValidator
│       ├── factory.py                     # ValidatorFactory auto-detection
│       ├── foundation.py                  # FoundationDocValidator
│       ├── workorder.py                   # WorkorderDocValidator
│       ├── system.py                      # SystemDocValidator
│       ├── standards.py                   # StandardsDocValidator
│       ├── session.py                     # SessionDocValidator
│       ├── infrastructure.py              # InfrastructureDocValidator
│       ├── migration.py                   # MigrationDocValidator
│       ├── user_facing.py                 # UserFacingDocValidator
│       ├── general.py                     # GeneralMarkdownValidator
│       ├── analysis.py                    # AnalysisValidator (NEW - WO-001)
│       └── execution_log.py               # ExecutionLogValidator (NEW - WO-001)
│
├── Scripts
│   └── scripts/
│       └── remove-emojis.py               # Emoji removal utility
│
├── Tests
│   └── tests/
│       ├── __init__.py
│       ├── test_validator.py              # Validator tests
│       ├── test_health.py                 # Health scoring tests
│       ├── test_engine.py                 # Template engine tests
│       ├── test_uds.py                    # UDS tests
│       ├── test_coderef_context.py        # CodeRef extension tests
│       ├── test_git_integration.py        # Git integration tests
│       └── test_workflow_filters.py       # Workflow filter tests
│
├── Test Infrastructure
│   └── test-infrastructure/
│       ├── docs/
│       │   ├── ARCHITECTURE.md
│       │   ├── SCHEMA.md
│       │   ├── TESTING_GUIDE.md
│       │   └── USER-GUIDE.md
│       ├── framework_detector.py
│       ├── models.py
│       ├── result_analyzer.py
│       ├── test_aggregator.py
│       └── test_runner.py
│
├── CodeRef Integration
│   └── coderef/
│       ├── workorder-log.txt              # Global workorder tracking
│       ├── workorder/                     # Active workorders
│       │   ├── papertrail-extensions/
│       │   │   └── context.json
│       │   ├── resource-sheet-metadata/
│       │   │   ├── DELIVERABLES.md
│       │   │   └── plan.json
│       │   └── resource-sheet-validation/
│       │       ├── analysis.json
│       │       ├── context.json
│       │       └── plan.json
│       ├── archived/                      # Completed workorders
│       │   ├── index.json
│       │   └── papertrail-python-package/
│       │       ├── context.json
│       │       ├── execution-log.json
│       │       ├── plan.json
│       │       └── README.md
│       ├── context/                       # Context documents
│       │   ├── CODEREF_TAILORED_DESIGN.md
│       │   ├── context-v2.md
│       │   ├── SAFE_DEVELOPMENT_PLAN.md
│       │   └── stub-references.md
│       ├── foundation-docs/               # Foundation documentation
│       │   ├── API.md
│       │   ├── ARCHITECTURE.md
│       │   ├── COMPONENTS.md
│       │   ├── README.md
│       │   └── SCHEMA.md
│       └── standards/                     # Standards documentation
│           ├── BEHAVIOR-STANDARDS.md
│           ├── COMPONENT-INDEX.md
│           ├── UI-STANDARDS.md
│           └── UX-PATTERNS.md
│
├── Documentation
│   └── docs/
│       ├── QA-CONFIGURATION-STANDARDS.md
│       ├── RESOURCE-SHEET-SYSTEMS-COMPARISON.md
│       ├── UDS-IMPLEMENTATION-GUIDE.md    # Implementation guide (UPDATED - WO-001)
│       └── UDS-Validation-RESOURCE-SHEET.md
│
└── Coverage Reports
    └── htmlcov/                           # HTML coverage reports
        ├── index.html
        ├── coverage_html_cb_513c77fd.js
        ├── style_cb_ed8d5379.css
        ├── status.json
        └── [module coverage files]
```

## Key Directories

**Core Package (`papertrail/`)** - Python library with validator, health scorer, template engine, and Jinja2 extensions

**Schemas (`schemas/`)** - JSON schemas for documentation, MCP servers, planning, security, and workflow validation

**Standards (`standards/documentation/`)** - Markdown standards for global docs, resource sheets, and script frontmatter

**Validators (`validators/` & `papertrail/validators/`)** - 6 validator types: resource-sheets (PowerShell), scripts (Python), plans (Python), typescript (TypeScript), workflow JSON (Python - NEW), markdown UDS (Python - NEW)

**Tests (`tests/`)** - 7 test modules with 98% coverage

**Test Infrastructure (`test-infrastructure/`)** - Framework detector, test runner, result analyzer, aggregator

**CodeRef Integration (`coderef/`)** - Workorder tracking, archived features, foundation docs, standards

**Documentation (`docs/`)** - QA standards, system comparisons, resource sheets

**Coverage (`htmlcov/`)** - HTML test coverage reports

---

## Recent Changes (WO-PAPERTRAIL-SCHEMA-ADDITIONS-001)

**Added:**
- `schemas/workflow/` directory with 2 new JSON schemas
- `analysis-json-schema.json` - Project analysis validation
- `execution-log-json-schema.json` - Task execution log validation
- `papertrail/validators/analysis.py` - AnalysisValidator class
- `papertrail/validators/execution_log.py` - ExecutionLogValidator class
- JSON validator documentation in UDS-IMPLEMENTATION-GUIDE.md

**Modified:**
- `papertrail/validators/factory.py` - Added auto-detection for new validators
- `docs/UDS-IMPLEMENTATION-GUIDE.md` - Added JSON validators section (+173 lines)

**Total:** +1,100 LOC across 5 new files, 2 modified files

---

**Last Updated:** 2026-01-10
**Version:** 1.1.0
**Maintained by:** CodeRef Ecosystem
