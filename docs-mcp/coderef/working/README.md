# Working Features Directory

**Purpose:** Active feature development and implementation planning
**Status:** Clean (no active features)
**Last Updated:** 2025-12-05

---

## Current State

The working directory is currently empty. All previous features have been archived to `coderef/archived/`.

To start a new feature, run `/start-feature`.

---

## Complete Feature Lifecycle

```
/start-feature ─┬─> /gather-context        → context.json
                ├─> /analyze-for-planning  → analysis.json
                ├─> /create-plan           → plan.json + DELIVERABLES.md
                └─> /validate-plan         → Score 0-100
                         │
                         ▼
                  /execute-plan            → TodoWrite task list
                         │
                         ▼
                   [implement]             → Write code
                         │
                         ▼
               /update-deliverables        → Git metrics (LOC, commits, time)
                         │
                         ▼
                   /update-docs            → Changelog, README, CLAUDE.md
                         │
                         ▼
             /update-foundation-docs       → API.md, user-guide.md (if needed)
                         │
                         ▼
                /archive-feature           → Move to coderef/archived/
```

---

## Available Commands

### Planning Phase
| Command | Description | Output |
|---------|-------------|--------|
| `/start-feature` | **Full automated workflow** | Runs all planning steps |
| `/gather-context` | Collect feature requirements | `context.json` |
| `/analyze-for-planning` | Discover docs, patterns | `analysis.json` |
| `/create-plan` | Generate implementation plan | `plan.json` + `DELIVERABLES.md` |
| `/validate-plan` | Score plan quality (0-100) | Validation report |

### Execution Phase
| Command | Description | Output |
|---------|-------------|--------|
| `/execute-plan` | Generate TodoWrite task list | Task checklist |

### Post-Implementation Phase
| Command | Description | Output |
|---------|-------------|--------|
| `/update-deliverables` | Capture git metrics | Updated `DELIVERABLES.md` |
| `/update-docs` | Update changelog + docs | `CHANGELOG.json`, `README.md`, `CLAUDE.md` |
| `/update-foundation-docs` | Update foundation docs | `API.md`, `user-guide.md`, etc. |
| `/archive-feature` | Archive completed feature | Move to `coderef/archived/` |

### Workorder Tracking
| Command | Description |
|---------|-------------|
| `/log-workorder` | Manually log workorder |
| `/get-workorder-log` | View workorder history |

---

## File Structure

When a feature is active, it contains:

```
coderef/working/{feature-name}/
├── context.json       ← Requirements (from /gather-context)
├── analysis.json      ← Project analysis (from /analyze-for-planning)
├── plan.json          ← Implementation plan (from /create-plan)
├── DELIVERABLES.md    ← Task tracking (auto-generated)
└── communication.json ← Multi-agent coordination (optional)
```

---

## Quick Start

### Start a New Feature
```bash
/start-feature
# Follow the interactive prompts
# Creates: context.json, analysis.json, plan.json, DELIVERABLES.md
```

### Resume Work on Existing Feature
```bash
# 1. Read the plan
cat coderef/working/{feature}/plan.json

# 2. Generate task list
/execute-plan

# 3. Implement following the plan phases

# 4. When complete:
/update-deliverables
/update-docs
/update-foundation-docs  # if API/docs changed
/archive-feature
```

---

## Workorder Activity Log

**Global Log:** `coderef/workorder-log.txt`

All workorder activity is tracked chronologically (latest first).

**View Activity:**
```bash
/get-workorder-log                    # All workorders
/get-workorder-log --project docs-mcp # Filter by project
/get-workorder-log --limit 10         # Latest 10
```

**Auto-Logging:** Tools automatically log when they complete:
- `/create-plan` - Logs plan creation
- `/archive-feature` - Logs feature archival
- And more...

---

## Related Resources

- **Archived Features:** `coderef/archived/` - Completed features
- **Standards:** `coderef/standards/` - UI/UX/behavior standards
- **Inventory:** `coderef/inventory/` - Project manifests
- **Templates:** `templates/` - Documentation templates

---

**Active Features:** 0
**Maintainer:** willh + Claude Code AI
