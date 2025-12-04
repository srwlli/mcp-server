# Quick Start Slash Commands

## ⭐ Recommended Entry Points

| Command | Description |
|----------|--------------|
| `/start-feature` | **RECOMMENDED** - Full planning workflow (gather → analyze → plan → validate) |
| `/quick-inventory` | **RECOMMENDED** - Run all 7 inventory tools at once |
| `/generate-docs` | Generate all foundation docs |

---

## 🚀 Foundation Documentation

| Command | Description |
|----------|--------------|
| `/generate-docs` | Generate all foundation docs (README, ARCHITECTURE, API, COMPONENTS, SCHEMA) |
| `/generate-user-guide` | Generate user guide |
| `/generate-quickref` | Generate quick reference |
| `/generate-my-guide` | Generate compact tool reference |

---

## 🧾 Changelog Commands

| Command | Description |
|----------|--------------|
| `/get-changelog` | View changelog |
| `/add-changelog` | Add entry (interactive) |
| `/update-changelog` | AI analyzes and documents changes |
| `/update-docs` | Update README, CLAUDE, CHANGELOG after feature |

---

## 🧩 Standards & Consistency

| Command | Description |
|----------|--------------|
| `/establish-standards` | Extract coding standards from project |
| `/audit-codebase` | Full codebase compliance audit |
| `/check-consistency` | Quick check on modified files (fast) |

---

## 🧠 Planning Workflow

| Command | Description |
|----------|--------------|
| `/start-feature` ⭐ | **RECOMMENDED** - Complete planning pipeline |
| `/gather-context` | Gather feature requirements |
| `/analyze-for-planning` | Analyze project for planning (Advanced) |
| `/create-plan` | Create implementation plan (Advanced) |
| `/validate-plan` | Validate plan quality (0-100 score) |
| `/execute-plan` | Generate TodoWrite task list |
| `/generate-plan-review` | Generate review report |

**Recommended Workflow:**
```
/start-feature → /execute-plan → implement → /update-deliverables → /archive-feature
```

---

## 📦 Inventory Commands

| Command | Description |
|----------|--------------|
| `/quick-inventory` ⭐ | **RECOMMENDED** - Run all 7 inventory tools |
| `/inventory-manifest` | File catalog |
| `/dependency-inventory` | Dependencies + security scanning |
| `/api-inventory` | API endpoints |
| `/database-inventory` | Database schemas |
| `/config-inventory` | Configuration files |
| `/test-inventory` | Test infrastructure |
| `/documentation-inventory` | Documentation files |

---

## 📋 Reference Commands

| Command | Description |
|----------|--------------|
| `/list-tools` | Show all 53 MCP tools across 3 servers |
| `/list-commands` | Show all 40 slash commands by category |

---

## 📂 Output Locations

| Output | Location |
|---------|-----------|
| **README.md** | Project root |
| **Other docs** | `coderef/foundation-docs/` |
| **Changelog** | `coderef/changelog/CHANGELOG.json` |
| **Standards** | `coderef/standards/` |
| **Plans** | `coderef/working/{feature}/` |
| **Inventory** | `coderef/inventory/` |
| **Reviews** | `coderef/reviews/` |

---

## ⚙️ MCP Tools (Direct Access)

### Templates
```python
mcp__docs-mcp__list_templates()
mcp__docs-mcp__get_template(template_name="readme")
```

### Changelog
```python
mcp__docs-mcp__get_changelog(project_path="/path")
mcp__docs-mcp__add_changelog_entry(project_path="/path", ...)
```

### Standards
```python
mcp__docs-mcp__establish_standards(project_path="/path")
mcp__docs-mcp__audit_codebase(project_path="/path")
mcp__docs-mcp__check_consistency(project_path="/path")
```

### Inventory
```python
mcp__docs-mcp__inventory_manifest(project_path="/path")
mcp__docs-mcp__dependency_inventory(project_path="/path")
```

---

**Total: 37 MCP Tools | 40 Slash Commands**
