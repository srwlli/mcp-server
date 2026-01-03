# Reference Sheets Documentation Index

**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001 Phase 3C (DOCS-001)
**Created:** 2026-01-03
**Purpose:** Navigation and hierarchy guide for project documentation

---

## Navigation - How to Find Documentation

### By Element Type

**UI Components:**
- Location: `coderef/reference-sheets/ui/`
- Examples: Buttons, modals, forms, widgets
- Search: `ls coderef/reference-sheets/ui/*.md`

**State Management:**
- Location: `coderef/reference-sheets/state/`
- Examples: Hooks (useAuth, useState wrappers), stores, context providers
- Search: `ls coderef/reference-sheets/state/*.md`

**API & Services:**
- Location: `coderef/reference-sheets/services/`
- Examples: API endpoints, API clients, data access layers
- Search: `ls coderef/reference-sheets/services/*.md`

**Utilities & Tools:**
- Location: `coderef/reference-sheets/tools/`
- Examples: Helper functions, CLI commands, scripts
- Search: `ls coderef/reference-sheets/tools/*.md`

**Data Structures:**
- Location: `coderef/reference-sheets/data/`
- Examples: Models, schemas, validators
- Search: `ls coderef/reference-sheets/data/*.md`

### By Search Method

**1. Find by Element Name:**
```bash
# Search all reference sheets
find coderef/reference-sheets -name "*AuthService*"

# Result: coderef/reference-sheets/services/AuthService.md
```

**2. Find by Topic (e.g., "authentication"):**
```bash
# Grep across all reference sheets
grep -r "authentication" coderef/reference-sheets/
```

**3. IDE Integration:**
```javascript
// In source code, JSDoc links to reference sheet
/**
 * @see {@link coderef/reference-sheets/services/AuthService.md}
 */
```

---

## Hierarchy - Where Resource Sheets Fit

### 4-Tier Documentation Structure

```
Project Documentation
│
├── Tier 1: Foundation Docs (Project-Wide)
│   ├── README.md (project overview)
│   ├── ARCHITECTURE.md (high-level patterns)
│   ├── SCHEMA.md (data models)
│   ├── API.md (API overview)
│   └── COMPONENTS.md (component overview)
│   └── Location: coderef/foundation-docs/
│
├── Tier 2: Reference Sheets (Element-Specific) ← YOU ARE HERE
│   ├── {element}.md (detailed docs)
│   ├── {element}.schema.json (type definitions)
│   └── {element}.jsdoc.txt (inline suggestions)
│   └── Location: coderef/reference-sheets/{category}/{element}/
│
├── Tier 3: Inline Documentation (Code-Level)
│   ├── JSDoc comments in source files
│   ├── TypeScript type definitions
│   └── Links to Tier 2 reference sheets
│   └── Location: Source files (*.ts, *.tsx, *.js, *.jsx)
│
└── Tier 4: Generated API Docs (Optional)
    ├── HTML/Markdown generated from JSDoc
    ├── TypeDoc or similar tool output
    └── Location: docs/api/ (if generated)
```

### Tier Responsibilities

| Tier | Scope | Authority | Update Frequency |
|------|-------|-----------|------------------|
| **Tier 1: Foundation** | Project-wide patterns, architecture | Canonical for project structure | On major changes |
| **Tier 2: Reference Sheets** | Individual code elements | Canonical for element behavior | On element changes |
| **Tier 3: Inline Docs** | Function/class signatures | Links to Tier 2 | With code commits |
| **Tier 4: Generated Docs** | Public API surface | Derived from Tiers 2 & 3 | On releases |

---

## Authority - What Takes Precedence

### When Documentation Conflicts

**Scenario 1: Foundation doc vs. Reference sheet**

```
ARCHITECTURE.md says: "Use Redux for state management"
AuthService.md says: "Uses React Context for auth state"

→ AuthService.md wins for AuthService specifics
→ ARCHITECTURE.md defines general pattern, exceptions documented
```

**Scenario 2: Reference sheet vs. Code**

```
AuthService.md says: "State persists to localStorage"
AuthService.ts says: "State stored in memory only"

→ Code wins (runtime truth)
→ Reference sheet must be updated
```

**Scenario 3: JSDoc vs. Reference sheet**

```
JSDoc says: "@param {string} token - Auth token"
AuthService.md says: "Token must be JWT format (Bearer {jwt})"

→ Reference sheet wins (more detailed)
→ JSDoc should link to reference sheet for details
```

**Authority Hierarchy:**

1. **Code** (runtime truth)
2. **Reference Sheets** (behavioral contracts)
3. **Foundation Docs** (architectural patterns)
4. **Inline JSDoc** (quick reference)
5. **Generated Docs** (derived documentation)

### Resolution Protocol

When conflicts arise:

1. **Identify authoritative source** (use hierarchy above)
2. **Update conflicting docs** to match authoritative source
3. **Add cross-references** explaining relationship
4. **Document exceptions** if deviation is intentional

---

## Maintenance - Keeping Docs Synchronized

### Synchronization Rules

**Rule 1: Code changes trigger Tier 2 updates**

```
Developer modifies AuthService.ts
→ Re-run: generate_resource_sheet({element: "AuthService"})
→ Updates: AuthService.md, AuthService.schema.json, AuthService.jsdoc.txt
→ Commit all 4 files together (code + 3 docs)
```

**Rule 2: Reference sheets auto-update from code**

```
# Reverse-engineer mode (default)
generate_resource_sheet({
  element_name: "AuthService",
  mode: "reverse-engineer"  # Reads code, updates docs
})

# Output:
# - 60-80% auto-filled from code analysis
# - 20-40% manual sections preserved (rationale, pitfalls)
```

**Rule 3: Foundation docs update on architectural changes**

```
Major refactor: Switch from Redux to Zustand
→ Update: coderef/foundation-docs/ARCHITECTURE.md
→ Update: All affected reference sheets
→ Add: Migration guide in ARCHITECTURE.md
```

### Cross-Reference Patterns

**From Foundation Doc → Reference Sheet:**

```markdown
## State Management

The project uses **Zustand** for global state. For implementation examples, see:
- [AuthService.md](../reference-sheets/services/AuthService.md#state-management)
- [UserStore.md](../reference-sheets/state/UserStore.md)
```

**From Reference Sheet → Foundation Doc:**

```markdown
## Architecture

AuthService follows the [API Client pattern](../../foundation-docs/ARCHITECTURE.md#api-client-pattern)
documented in ARCHITECTURE.md.
```

**From Code (JSDoc) → Reference Sheet:**

```typescript
/**
 * AuthService manages authentication state and token lifecycle.
 *
 * @see {@link coderef/reference-sheets/services/AuthService.md} for detailed contracts
 */
export class AuthService {
  // ...
}
```

### Update Workflows

**Workflow 1: Feature Implementation**

```
1. Implement feature (modify code)
2. Run tests
3. Re-generate reference sheet: generate_resource_sheet()
4. Review auto-fill accuracy (should be 60-80%)
5. Manually fill rationale/pitfalls sections
6. Commit code + docs together
```

**Workflow 2: Documentation Refresh**

```
# Detect stale docs
coderef drift . --json

# If drift > 10%:
1. Re-run: generate_resource_sheet() for affected elements
2. Review changes
3. Update foundation docs if patterns changed
4. Commit refreshed docs
```

**Workflow 3: Bulk Regeneration**

```
# After major refactor, regenerate all reference sheets
for element in $(coderef scan . --json | jq -r '.[].name'); do
  generate_resource_sheet({element_name: $element, mode: "refresh"})
done
```

---

## Quick Reference

### Common Tasks

| Task | Command | Output |
|------|---------|--------|
| **Find element docs** | `find coderef/reference-sheets -name "*Element*"` | Path to reference sheet |
| **Generate new sheet** | `generate_resource_sheet({element: "Name"})` | 3 files (.md, .json, .txt) |
| **Refresh existing** | `generate_resource_sheet({element: "Name", mode: "refresh"})` | Updated docs |
| **Check doc drift** | `coderef drift . --json` | Staleness report |
| **Search all docs** | `grep -r "pattern" coderef/` | Matching lines |

### File Naming Conventions

- **Reference Sheets:** `{ElementName}.md` (PascalCase, e.g., AuthService.md)
- **JSON Schemas:** `{element-name}.schema.json` (kebab-case, e.g., auth-service.schema.json)
- **JSDoc Snippets:** `{element-name}.jsdoc.txt` (kebab-case, e.g., auth-service.jsdoc.txt)

### Directory Structure

```
coderef/
├── foundation-docs/           # Tier 1: Project-wide docs
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── SCHEMA.md
│   ├── API.md
│   └── COMPONENTS.md
│
├── reference-sheets/          # Tier 2: Element-specific docs
│   ├── INDEX.md               # This file
│   ├── ui/
│   │   └── Button.md
│   ├── services/
│   │   └── AuthService.md
│   ├── state/
│   │   └── useAuth.md
│   └── tools/
│       └── formatDate.md
│
└── schemas/                   # JSON schemas for elements
    ├── button.schema.json
    ├── auth-service.schema.json
    └── use-auth.schema.json
```

---

## Getting Help

### Questions?

- **"Where do I document X?"** → Check Tier Responsibilities table above
- **"Which doc is authoritative?"** → Check Authority Hierarchy section
- **"How do I update docs?"** → Check Maintenance workflows
- **"What if docs conflict?"** → Check Resolution Protocol

### Additional Resources

- [ARCHITECTURE.md](../foundation-docs/ARCHITECTURE.md) - Project architecture patterns
- [RESOURCE-SHEET-SYSTEM.md](../../modules/resource-sheet/RESOURCE-SHEET-SYSTEM.md) - Complete reference sheet guide
- [.claude/commands/create-resource-sheet.md](../../.claude/commands/create-resource-sheet.md) - Writing guidelines

---

**Generated by:** coderef-docs agent (WO-RESOURCE-SHEET-MCP-TOOL-001 Phase 3C)
**Last Updated:** 2026-01-03
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001
