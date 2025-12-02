````markdown
# Quick Start Slash Commands

## 🚀 Foundation Documentation

| Command | Description |
|----------|--------------|
| `/generate-docs` | Generate all foundation docs (README, ARCHITECTURE, API, COMPONENTS, SCHEMA) |
| `/generate-user-guide` | Generate user guide |
| `/generate-quickref` | Generate quick reference |
| `/list-templates` | View available templates |
| `/get-template` | Get specific template |

---

## 🧾 Changelog Commands

| Command | Description |
|----------|--------------|
| `/get-changelog` | View changelog |
| `/add-changelog` | Add entry (interactive) |
| `/update-changelog` | AI analyzes and documents changes |

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
| `/gather-context` | Gather feature requirements |
| `/analyze-for-planning` | Analyze project for planning |
| `/create-plan` | Create implementation plan |
| `/validate-plan` | Validate plan quality (0–100 score) |
| `/generate-plan-review` | Generate review report |

---

## 📂 Output Locations

| Output | Location |
|---------|-----------|
| **README.md** | Project root |
| **Other docs** | `coderef/foundation-docs/` |
| **Changelog** | `coderef/changelog/CHANGELOG.json` |
| **Standards** | `coderef/standards/` |
| **Plans** | `coderef/working/{feature}/` |
| **Reviews** | `coderef/reviews/` |

---

## ⚙️ MCP Tools (Direct Access)

### Templates
```python
mcp__docs-mcp__list_templates()
mcp__docs-mcp__get_template(template_name="readme")
````

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

```
```