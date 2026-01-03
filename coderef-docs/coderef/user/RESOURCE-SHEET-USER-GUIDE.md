# Resource Sheet User Guide

**Version:** 1.0.0
**Last Updated:** 2026-01-03
**Workorder:** WO-RESOURCE-SHEET-CONSOLIDATION-001

---

## Purpose

Learn how to generate authoritative, refactor-safe technical documentation for code elements using the `/create-resource-sheet` command with 60-80% auto-fill from dependency graph analysis.

---

## Overview

The unified resource sheet system combines:
- **Tool 1's execution framework:** Writing standards, refactor safety, quality controls
- **Tool 2's element specialization:** 20 element type classifications with focused checklists
- **Graph integration:** Auto-fill from dependency analysis
- **Multi-format output:** Markdown + JSON Schema + JSDoc

**Key Innovation:** Detects element type automatically and generates specialized documentation with minimal manual input.

---

## Quick Start (3 Steps)

### Step 1: Invoke the Command

```bash
/create-resource-sheet <target> [element-type]
```

**Examples:**
```bash
/create-resource-sheet src/auth/AuthService.ts
/create-resource-sheet components/Button.tsx
/create-resource-sheet hooks/useLocalStorage.ts custom-hook
```

### Step 2: Review Auto-Generated Output

The system generates 3 synchronized outputs:

1. **Markdown** - Human-readable documentation (68%+ auto-filled)
2. **JSON Schema** - Machine-readable type contracts
3. **JSDoc** - Inline code comment suggestions

### Step 3: Fill Manual Sections & Validate

- Review sections flagged for manual input (typically 20-40%)
- Validate against 4-gate quality pipeline
- Save desired format(s)

**Total Time:** 5-15 minutes (vs 30-60 minutes manual)

---

## Element Type Classification

The system auto-detects one of **20 element types** based on filename, path, and code patterns:

### Critical Impact (Rank 1-5)
1. **Top-Level Widgets/Pages** - Entry components orchestrating workflows
2. **Stateful Containers** - Components managing and coordinating state
3. **Global State Layer** - Application-wide state (Redux/Zustand/Context)
4. **Custom Hooks** - Reusable hooks with side effects
5. **API Client Layer** - HTTP clients and API interaction

### High Impact (Rank 6-10)
6. **Data Models & Schemas** - Type definitions and validators
7. **Persistence Subsystem** - Storage, caching, data persistence
8. **Eventing/Messaging** - Event bus and cross-component messaging
9. **Routing & Navigation** - Router configuration
10. **File/Tree Primitives** - Tree data structures and path utilities

### Medium Impact (Rank 11-16)
11. **Context Menu/Commands** - Context menus and command registries
12. **Permission & AuthZ** - Authorization and permission management
13. **Error Handling** - Error boundaries and error handling
14. **Logging/Telemetry** - Analytics and telemetry systems
15. **Performance-Critical UI** - High-performance components
16. **Design System Components** - Reusable UI components

### Low Impact (Rank 17-20)
17. **Theming & Styling** - Theme configuration and styling
18. **Build Tooling** - Build scripts and developer tooling
19. **CI/CD Pipelines** - CI/CD configuration
20. **Testing Harness** - Test utilities, mocks, and fixtures

**See:** [ELEMENT-TYPE-CATALOG.md](../foundation-docs/ELEMENT-TYPE-CATALOG.md) for complete descriptions

---

## Invocation Modes

### Mode 1: Reverse-Engineer (Default)
**Use when:** Documenting existing code

```bash
/create-resource-sheet src/components/Modal.tsx
```

**Behavior:**
- Reads `.coderef/index.json` for code intelligence
- Auto-detects element type (85-95% confidence)
- Runs graph queries for imports/exports/consumers
- Auto-fills 60-80% of documentation
- Flags low-confidence sections for review

### Mode 2: Template (Scaffold New)
**Use when:** Creating documentation template before implementation

```bash
/create-resource-sheet components/NewFeature.tsx template
```

**Behavior:**
- Generates template with placeholders
- Skips graph queries (no code exists yet)
- Provides structure and checklists
- 0% auto-fill (all manual)

### Mode 3: Refresh (Update Existing)
**Use when:** Updating documentation after code changes

```bash
/create-resource-sheet src/auth/AuthService.ts refresh
```

**Behavior:**
- Reads existing resource sheet
- Re-runs graph queries for updated relationships
- Preserves manual sections
- Updates auto-fillable sections only

---

## Output Formats

### Markdown Output
**Location:** `coderef/workorder/{feature-name}/docs/`
**Use Case:** Human-readable documentation, architecture reference

**Sections Include:**
- Executive Summary (2-4 sentences)
- Architecture Overview (auto-filled from graph)
- State Ownership Table (semi-auto-filled)
- Event/Callback Contracts (auto-filled from TypeScript)
- Performance Considerations
- Testing Strategy
- Common Pitfalls

### JSON Schema Output
**Location:** `coderef/workorder/{feature-name}/schemas/`
**Use Case:** Validation, tooling, API contracts

**Contains:**
- Full TypeScript type definitions
- Props/event payload schemas
- Validation rules
- Default values

### JSDoc Output
**Location:** Inline in source code
**Use Case:** IDE autocomplete, inline documentation

**Adds:**
- Function/method documentation comments
- Parameter descriptions
- Return type descriptions
- Usage examples

---

## Auto-Fill Capabilities

**What Gets Auto-Filled (60-80% of documentation):**

| Section | Auto-Fill Source | Completion % |
|---------|------------------|--------------|
| Header Metadata | System context (agent, date, task) | 100% |
| Architecture Overview | Graph imports/exports/hierarchy | 70-90% |
| State Ownership | Code analysis (useState, useReducer) | 40-60% |
| Event Contracts | TypeScript signatures, handlers | 60-80% |
| Dependencies | Graph imports | 90% |
| Public API | Graph exports | 95% |
| Usage Examples | Graph consumers | 70% |
| Testing Scenarios | Test file parsing | 20-40% |

**What Requires Manual Input (20-40%):**

- Executive Summary (synthesis required)
- Non-Goals (human decision)
- Performance Limits (requires profiling data)
- Common Pitfalls (requires experience)
- Failure Recovery (requires design knowledge)

---

## Advanced Usage

### Override Element Type Detection

```bash
/create-resource-sheet components/CustomWidget.tsx top-level-widget
```

Use when auto-detection is ambiguous or incorrect.

### Specify Output Formats

```bash
# Generate only markdown
/create-resource-sheet src/api.ts --format markdown

# Generate markdown + schema
/create-resource-sheet src/api.ts --format markdown,schema
```

### Custom Module Selection

```bash
# Force inclusion of specific modules
/create-resource-sheet hooks/useData.ts --modules hooks,network
```

---

## Quality Validation (4-Gate Pipeline)

Resource sheets automatically run through 4 validation gates:

### Gate 1: Structural Validation
- Header metadata present
- Executive summary complete (2-4 sentences)
- Required sections for element type present
- State ownership table exists (if stateful)

### Gate 2: Content Quality
- No placeholders in critical sections
- Exhaustiveness standard met (all state/events/contracts)
- Voice/tone compliance (imperative, no hedging)
- Tables used for structured data

### Gate 3: Element-Specific Validation
- Element-type focus areas addressed
- Required sections for type present
- Element-specific tables complete

### Gate 4: Auto-Fill Threshold
- >= 60% completion rate
- Manual review sections flagged
- Low auto-fill sections identified

**Validation Results:**
- **APPROVED:** All gates pass
- **APPROVED_WITH_WARNINGS:** ≤2 major issues
- **REJECTED:** Critical validation failures

---

## Troubleshooting

### "Element type detection failed"
**Cause:** Ambiguous filename/path patterns
**Solution:** Manually specify element type:
```bash
/create-resource-sheet file.ts custom-hook
```

### "Auto-fill rate < 60%"
**Cause:** `.coderef/index.json` missing or stale
**Solution:** Regenerate coderef structure:
```bash
python scripts/populate-coderef.py /path/to/project
```

### "Validation gate failed: Missing state ownership table"
**Cause:** Stateful component without ownership documentation
**Solution:** Add state ownership table manually:
```markdown
| State | Owner | Type | Persistence | Source of Truth |
|-------|-------|------|-------------|-----------------|
| selectedItem | FileTree | UI | none | Component |
```

### "Graph queries slow (>1 second)"
**Cause:** Large codebase with complex dependency graph
**Solution:** Optimize `.coderef/exports/graph.json` regeneration or use partial scans

---

## Best Practices

### When to Generate Resource Sheets

✅ **Do Generate:**
- Before refactoring complex components
- After major feature implementation
- During code review (verify documentation exists)
- For onboarding new team members

❌ **Don't Generate:**
- For trivial utilities (<50 lines)
- For simple pure functions
- For test files (use testing-harness type instead)

### Maintenance

**Update frequency:**
- **Breaking changes:** Regenerate immediately
- **New features:** Refresh after implementation
- **Bug fixes:** Usually no update needed
- **Refactoring:** Refresh to update dependencies

**Version control:**
- Commit resource sheets with code changes
- Include in PR documentation requirements
- Archive when components deprecated

---

## Integration with Workflows

### Planning Workflow (Phase 0: Preparation)
Generate resource sheets for reference components before planning:
```bash
/create-resource-sheet src/components/ExamplePattern.tsx
# Use output to understand existing patterns
```

### Implementation Workflow (Post-Feature)
Document newly created components:
```bash
/create-resource-sheet src/new-feature/NewComponent.tsx
# Save to coderef/workorder/{feature}/docs/
```

### Code Review Workflow
Verify documentation completeness:
```bash
# Check if resource sheet exists and is up-to-date
ls coderef/workorder/{feature}/docs/*-resource-sheet.md
```

---

## Next Steps

- **Element Type Details:** [ELEMENT-TYPE-CATALOG.md](../foundation-docs/ELEMENT-TYPE-CATALOG.md)
- **Module System:** [MODULE-REFERENCE.md](../foundation-docs/MODULE-REFERENCE.md)
- **Quick Reference:** [QUICK-REFERENCE-CARD.md](QUICK-REFERENCE-CARD.md)

---

**Questions or Issues?**
See troubleshooting section above or consult [MODULE-REFERENCE.md](../foundation-docs/MODULE-REFERENCE.md) for advanced topics.
