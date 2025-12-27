# coderef-personas Root - File Organization Guide

**Date:** December 27, 2025
**Status:** Cleaned and organized

---

## Directory Structure

```
coderef-personas/
├── README.md                     # Quick start (MASTER)
├── CLAUDE.md                     # Behavior definition (MASTER)
├── pyproject.toml                # Dependencies (MASTER)
├── communication.json            # Workorder tracking (MASTER)
├── CHANGELOG.json                # Change history
│
├── src/                          # Python source files (CORE)
│   ├── server.py                 # MCP server entry
│   ├── persona_manager.py        # Persona management
│   └── [other modules]
│
├── coderef/                      # CodeRef Ecosystem
│   ├── docs/                     # Documentation (ORGANIZED)
│   │   ├── guides/               # Customization & creation guides (3 files)
│   │   │   ├── CUSTOMIZATION-GUIDE.md
│   │   │   ├── persona-creation-form-v1.md
│   │   │   └── next5mcp.md
│   │   ├── reports/              # Status & synergy reports (2 files)
│   │   │   ├── PERSONAS-CREATED.md
│   │   │   └── MCP-SYNERGY-REPORT.md
│   │   ├── integration/          # Integration documentation (1 file)
│   │   │   └── WORKORDER-TRACKING-FLOW.md
│   │   └── reference/            # Developer guides (1 file)
│   │       └── my-guide.md
│   ├── foundation-docs/          # Generated foundation documentation
│   │   ├── API.md
│   │   ├── ARCHITECTURE.md
│   │   ├── SCHEMA.md
│   │   └── project-context.json
│   ├── schemas/                  # JSON schemas
│   ├── workorder/                # Active workorders
│   ├── working/                  # Feature ideas (stubs)
│   └── testing/                  # Test fixtures
│
├── generators/                   # Code generation modules
├── templates/                    # Template files
└── tests/                        # Test suite
```

---

## Root-Level Files Explained

### 🔵 MASTER CONFIGURATION FILES (Keep in Root)

- **README.md**
  - Quick start guide for developers
  - Entry point for new users

- **CLAUDE.md**
  - Server behavior definition
  - Core operating instructions

- **pyproject.toml**
  - Project dependencies and metadata
  - Entry point configuration

- **communication.json**
  - Server-level workorder tracking
  - Orchestration status

- **CHANGELOG.json**
  - Change history and versioning
  - Release notes in structured format

### 📊 ORGANIZED DOCUMENTATION

#### `/coderef/docs/guides/` (3 files)
Customization and creation guides:
- CUSTOMIZATION-GUIDE.md - How to customize personas
- persona-creation-form-v1.md - Persona creation form and process
- next5mcp.md - Next generation MCP integration guide

**Purpose:** Reference for developers creating and customizing personas

#### `/coderef/docs/reports/` (2 files)
Status and synergy reports:
- PERSONAS-CREATED.md - List of created personas and status
- MCP-SYNERGY-REPORT.md - MCP ecosystem synergy analysis

**Purpose:** Quality assurance and status tracking

#### `/coderef/docs/integration/` (1 file)
Integration documentation:
- WORKORDER-TRACKING-FLOW.md - Workorder tracking integration

**Purpose:** Understanding how personas integrate with workorder system

#### `/coderef/docs/reference/` (1 file)
Developer guides:
- my-guide.md - Developer guide for persona creation and usage

**Purpose:** Developer reference materials

### 🏗️ METADATA & WORKORDERS

- `/coderef/workorder/` - Active workorders
- `/coderef/working/` - Feature stubs (ideas)
- `/coderef/foundation-docs/` - Auto-generated documentation
- `/coderef/testing/` - Test fixtures

---

## Best Practices

### Daily Operations
1. Refer to **CLAUDE.md** for server behavior
2. Check **communication.json** for active workorders
3. Review **coderef/workorder/** for current features
4. Check **CHANGELOG.json** for recent changes

### When Adding Documentation
1. Determine category: guides, reports, integration, or reference
2. Add to appropriate `/coderef/docs/{category}/` folder
3. Update this file if adding new category

### When Creating New Personas
1. Follow process in coderef/docs/guides/persona-creation-form-v1.md
2. Document in coderef/docs/reports/PERSONAS-CREATED.md
3. Create workorder in `/coderef/workorder/{persona-name}/`

### When Implementing Features
1. Update `/coderef/docs/guides/` with implementation details
2. Create workorder in `/coderef/workorder/{feature-name}/`
3. Generate reports to `/coderef/docs/reports/` when complete

### When Maintaining Python Code
- Keep all .py files in root (do not move)
- Update guides/ when adding new features
- Update CHANGELOG.json when releasing changes

---

## Root File Maintenance

### Master Files:
- **README.md** - Update when setup changes
- **CLAUDE.md** - Update when server behavior changes
- **pyproject.toml** - Update when dependencies change
- **communication.json** - Update for active workorders
- **CHANGELOG.json** - Update with each release

---

## Quick Reference

**What's the entry point?**
→ server.py (in root)

**How do I create a new persona?**
→ Read coderef/docs/guides/persona-creation-form-v1.md

**How do I customize personas?**
→ Read coderef/docs/guides/CUSTOMIZATION-GUIDE.md

**What personas have been created?**
→ Check coderef/docs/reports/PERSONAS-CREATED.md

**How does this integrate with MCP?**
→ Read coderef/docs/reports/MCP-SYNERGY-REPORT.md

**What are the active workorders?**
→ Check coderef/workorder/ folder

---

*Generated: 2025-12-27*
