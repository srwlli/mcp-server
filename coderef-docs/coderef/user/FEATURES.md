# coderef-docs Features

**What can coderef-docs do for you?**

A comprehensive overview of capabilities organized by feature category.

---

## Documentation Generation

### Foundation Docs (5 Documents)

Generate complete technical documentation suite using the POWER framework:

- **README.md** - Project overview, installation, quick start
- **API.md** - Complete MCP tool reference with schemas
- **SCHEMA.md** - Data models and validation rules
- **COMPONENTS.md** - Module architecture and dependencies
- **ARCHITECTURE.md** - System design and patterns

**Use Case:** "I built an MCP server and need professional docs"
**Time:** 2-5 minutes
**Command:** `/generate-docs`

---

### User-Facing Docs (4 Documents)

Generate end-user documentation for non-technical audiences:

- **my-guide.md** - Concise tool reference (60-80 lines)
- **USER-GUIDE.md** - Comprehensive tutorial with examples
- **FEATURES.md** - Feature overview (this document!)
- **quickref.md** - Scannable quick reference (150-250 lines)

**Use Case:** "I need user-friendly docs for my team"
**Time:** 3-7 minutes
**Command:** `/generate-user-docs`

---

## Resource Sheets (NEW in v3.4.0)

### Composable Module-Based Documentation

Revolutionary documentation system:

- Auto-detects code characteristics
- Generates 3 outputs: Markdown + JSON Schema + JSDoc
- 50% auto-fill rate (architecture + integration modules)

**Use Case:** "Document this AuthService class"
**Time:** < 5 seconds
**Tool:** `generate_resource_sheet`

---

## Changelog Management

### Smart Change Recording

- Git auto-detection
- Change type suggestion
- Workorder tracking

**Command:** `/record-changes`

---

## Standards & Compliance

### Standards Extraction

Discover codebase patterns:
- With `.coderef/`: ~50ms
- Without: ~5-60 seconds

**Command:** `/establish-standards`

### Codebase Auditing

Compliance scoring (0-100) with fix suggestions

**Command:** `/audit-codebase`

### Pre-Commit Checks

Quality gate for modified files only

**Command:** `/check-consistency`

---

## Key Features

✅ **13 MCP Tools** (up from 11)
✅ **POWER Framework** - Consistent doc structure
✅ **UDS Integration** - Workorder tracking
✅ **MCP Orchestration** - Works with coderef-context
✅ **10x Faster** - With `.coderef/` data

---

**Version:** 3.4.0 | **Status:** Production Ready
