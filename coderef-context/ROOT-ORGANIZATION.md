# coderef-context Root - File Organization Guide

**Date:** December 27, 2025
**Status:** Cleaned and organized

---

## Directory Structure

```
coderef-context/
├── README.md                     # Quick start (MASTER)
├── CLAUDE.md                     # Behavior definition (MASTER)
├── pyproject.toml                # Dependencies (MASTER)
├── communication.json            # Workorder tracking (MASTER)
│
├── src/                          # Python source files (CORE)
│   ├── server.py                 # MCP server entry
│   ├── tools.py                  # Tool implementations
│   ├── scanner.py                # Code scanning
│   ├── query_handler.py          # Query processing
│   └── [other modules as needed]
│
├── coderef/                      # CodeRef Ecosystem
│   ├── docs/                     # Documentation (ORGANIZED)
│   │   ├── guides/               # Implementation guides (2 files)
│   │   │   ├── ASYNC_CONVERSION_SUMMARY.md
│   │   │   └── IMPLEMENTATION_PLAN.md
│   │   ├── reports/              # Workorder & completion reports (1 file)
│   │   │   └── LLOYD_IMPLEMENTATION_WORKORDER.md
│   │   ├── integration/          # Integration documentation (empty)
│   │   └── reference/            # Reference documentation (1 file)
│   │       └── TOOLS_REFERENCE.md
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
├── generators/                   # Code generation modules (if applicable)
├── templates/                    # Template files (if applicable)
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

### 🟢 PYTHON SOURCE FILES (Keep in Root)

All Python source files remain in root for MCP server functionality.

### 📊 ORGANIZED DOCUMENTATION

#### `/coderef/docs/guides/` (2 files)
Implementation and conversion documentation:
- ASYNC_CONVERSION_SUMMARY.md - Async/await implementation details
- IMPLEMENTATION_PLAN.md - Server implementation plan

**Purpose:** Reference for developers implementing or extending the server

#### `/coderef/docs/reports/` (1 file)
Workorder and completion reports:
- LLOYD_IMPLEMENTATION_WORKORDER.md - Workorder tracking

**Purpose:** Quality assurance and workorder tracking

#### `/coderef/docs/integration/` (empty for now)
Reserved for future integration documentation.

#### `/coderef/docs/reference/` (1 file)
Reference documentation:
- TOOLS_REFERENCE.md - Complete tools reference

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

### When Adding Documentation
1. Determine category: guides, reports, integration, or reference
2. Add to appropriate `/coderef/docs/{category}/` folder
3. Update this file if adding new category

### When Implementing Features
1. Update `/coderef/docs/guides/` with implementation details
2. Create workorder in `/coderef/workorder/{feature-name}/`
3. Generate reports to `/coderef/docs/reports/` when complete

### When Maintaining Python Code
- Keep all .py files in root (do not move)
- Reference TOOLS_REFERENCE.md for tool specifications

---

## Root File Maintenance

### Master Files:
- **README.md** - Update when setup changes
- **CLAUDE.md** - Update when server behavior changes
- **pyproject.toml** - Update when dependencies change
- **communication.json** - Update for active workorders

---

## Quick Reference

**What's the entry point?**
→ server.py (in root)

**What tools are available?**
→ Read coderef/docs/reference/TOOLS_REFERENCE.md

**What's the implementation status?**
→ Check coderef/docs/guides/IMPLEMENTATION_PLAN.md

**What are the active workorders?**
→ Check coderef/workorder/ folder

---

*Generated: 2025-12-27*
