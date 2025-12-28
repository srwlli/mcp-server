# coderef-docs Root - File Organization Guide

**Date:** December 27, 2025
**Status:** Cleaned and organized

---

## Directory Structure

```
coderef-docs/
├── README.md                     # Quick start (MASTER)
├── CLAUDE.md                     # Behavior definition (MASTER)
├── pyproject.toml                # Dependencies (MASTER)
├── communication.json            # Workorder tracking (MASTER)
├── claude.json                   # MCP configuration
├── railway.json                  # Deployment configuration
├── requirements.txt              # Python dependencies
├── runtime.txt                   # Runtime configuration
│
├── src/                          # Python source files (CORE)
│   ├── server.py                 # MCP server entry
│   ├── tool_handlers.py          # Tool implementations
│   └── [other modules]
│
├── coderef/                      # CodeRef Ecosystem
│   ├── docs/                     # Documentation (ORGANIZED)
│   │   ├── guides/               # Setup & implementation guides (3 files)
│   │   │   ├── MCP-SETUP-GUIDE.md
│   │   │   ├── QUICK-START.md
│   │   │   └── WORKFLOW-SEPARATION.md
│   │   ├── reports/              # Review & workorder reports (3 files)
│   │   │   ├── COMPREHENSIVE-review.md
│   │   │   ├── RELEASE_NOTES.md
│   │   │   └── WORKORDER_SUMMARY.md
│   │   ├── integration/          # Integration documentation (empty)
│   │   └── reference/            # User guides & reference (2 files)
│   │       ├── user-guide.md
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

### 🟢 ENVIRONMENT & DEPLOYMENT FILES (Keep in Root)

- **claude.json**
  - MCP server configuration
  - Tool definitions

- **railway.json**
  - Railway deployment configuration
  - Required for production deployment

- **requirements.txt** & **runtime.txt**
  - Python environment configuration
  - Required for deployment

- **uv.lock**
  - Dependency lock file
  - Auto-generated

### 📊 ORGANIZED DOCUMENTATION

#### `/coderef/docs/guides/` (3 files)
Setup and implementation guides:
- MCP-SETUP-GUIDE.md - How to set up the MCP server
- QUICK-START.md - Quick start guide
- WORKFLOW-SEPARATION.md - Workflow separation documentation

**Purpose:** Reference for developers setting up or implementing the server

#### `/coderef/docs/reports/` (3 files)
Review and workorder reports:
- COMPREHENSIVE-review.md - Comprehensive review findings
- RELEASE_NOTES.md - Release notes and changes
- WORKORDER_SUMMARY.md - Workorder tracking and summary

**Purpose:** Quality assurance and workorder tracking

#### `/coderef/docs/integration/` (empty for now)
Reserved for future integration documentation.

#### `/coderef/user/` (4 files)
User-facing guides and reference documentation:
- USER-GUIDE.md - Complete user guide
- my-guide.md - Quick tool reference
- FEATURES.md - Feature overview
- quickref.md - Scannable quick reference

**Purpose:** End-user and developer reference materials

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
- Update guides/ when adding new features

### When Deploying
- Keep railway.json in root (required for Railway)
- Keep requirements.txt and runtime.txt in root (required for deployment)

---

## Root File Maintenance

### Master Files:
- **README.md** - Update when setup changes
- **CLAUDE.md** - Update when server behavior changes
- **pyproject.toml** - Update when dependencies change
- **communication.json** - Update for active workorders

### Configuration Files (Do Not Move):
- **claude.json** - MCP server configuration
- **railway.json** - Railway deployment
- **requirements.txt** & **runtime.txt** - Python environment
- **uv.lock** - Dependency lock (auto-generated)

---

## Quick Reference

**What's the entry point?**
→ server.py (in root)

**How do I get started?**
→ Read coderef/docs/guides/QUICK-START.md

**How do I set up the MCP server?**
→ Read coderef/docs/guides/MCP-SETUP-GUIDE.md

**What's included in this release?**
→ Check coderef/docs/reports/RELEASE_NOTES.md

**What are the active workorders?**
→ Check coderef/workorder/ folder

---

*Generated: 2025-12-27*
