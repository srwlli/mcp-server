# Documentation Standards for Unified Resource Sheet System

**Agent:** coderef-docs
**Timestamp:** 2026-01-02
**Workorder:** WO-REFERENCE-SHEET-RECONCILIATION-001
**Plan Reviewed:** C:\Users\willh\.mcp-servers\coderef-docs\coderef\workorder\resource-sheet-reconciliation\plan.json

---

## Executive Summary

This document defines comprehensive documentation standards for the **unified resource sheet system** created by merging Tool 1 (execution framework) and Tool 2 (20 element types). The unified system preserves Tool 1's quality controls (exhaustiveness, refactor safety, voice guidelines) while integrating Tool 2's specialization (element type classification, focus areas, required sections). Documentation standards cover 4 core areas: user documentation structure, quality gate templates, maintenance workflows, and coderef-workflow integration.

**Key Achievement:** Defines how to document a composable module-based system that combines execution rigor with element-specific expertise.

---

## 1. User Documentation Structure

The unified resource sheet system requires **4-tier documentation hierarchy** to serve different audiences and use cases:

### 1.1 Core Documents

#### Tier 1: RESOURCE-SHEET-USER-GUIDE.md (Primary Entry Point)

- **Location:** `coderef/user/`
- **Purpose:** Primary user-facing guide for `/create-resource-sheet` command
- **Audience:** All developers using the resource sheet system
- **Sections:**
  1. **Quick Start** - 3-step workflow (detect → select → assemble)
  2. **Element Type Classification** - 20 types with examples
  3. **Invocation Modes** - reverse-engineer, template, refresh
  4. **Output Formats** - Markdown, JSON Schema, JSDoc
  5. **Auto-Fill Capabilities** - What's auto-populated vs manual
  6. **Advanced Usage** - Custom modules, overrides, extensions
  7. **Troubleshooting** - Common issues and solutions

**Why This Matters:** Users need single entry point. This guide walks them from "I want to document AuthService" to "Here's my complete resource sheet in 3 formats."

#### Tier 2: MODULE-REFERENCE.md (Technical Deep Dive)

- **Location:** `coderef/foundation-docs/`
- **Purpose:** Technical reference for all 15 modules (4 universal + 11 conditional)
- **Audience:** Advanced users, contributors, module developers
- **Sections:**
  1. **Universal Modules** - Architecture, Integration, Testing, Performance (always included)
  2. **Conditional Modules by Category** - UI, State, Network, Hooks (selected based on characteristics)
  3. **Module Selection Logic** - Triggers and detection characteristics
  4. **Module Content Schema** - Fields, auto-fill sources, placeholders
  5. **Composition Rules** - How modules combine (e.g., React component gets UI + State modules)
  6. **Extension Points** - Adding custom modules

**Why This Matters:** Power users need to understand module system internals for customization and troubleshooting.

#### Tier 3: ELEMENT-TYPE-CATALOG.md (Reference Lookup)

- **Location:** `coderef/foundation-docs/`
- **Purpose:** Comprehensive catalog of 20 element types from Tool 2
- **Audience:** All users needing element type reference
- **Sections:**
  1. **Classification Table** - All 20 types ranked by maintenance impact
  2. **Type Descriptions** - Purpose, focus areas, required sections (from Tool 2 templates)
  3. **Detection Patterns** - How element type is auto-detected from code
  4. **Module Mappings** - Which modules apply to which types
  5. **Examples** - Sample resource sheets for each type
  6. **Migration from Tool 2** - Mapping old catalog to new unified system

**Why This Matters:** Preserves Tool 2's 20 element type specializations. Users need quick lookup: "What's required for a Custom Hook?"

#### Tier 4: QUICK-REFERENCE-CARD.md (Cheat Sheet)

- **Location:** `coderef/user/`
- **Purpose:** One-page cheat sheet for common operations
- **Audience:** Quick reference during active development
- **Sections:**
  1. **Command Syntax** - `/create-resource-sheet [target] [options]`
  2. **Common Options** - mode, element-type, output-format
  3. **Element Type Quick Reference** - Top 10 types with examples
  4. **Module Selection Cheat Sheet** - Universal vs conditional
  5. **Auto-Fill Rates** - Expected completion % by element type
  6. **Quality Gate Checklist** - Pre-submission validation

**Why This Matters:** Developers need instant answers without reading full guide. "What options exist? What's the syntax?"

### 1.2 Documentation Hierarchy Flow

```
New User → RESOURCE-SHEET-USER-GUIDE.md (Quick Start)
         ↓ (needs advanced features)
Advanced User → MODULE-REFERENCE.md (Module internals)
         ↓ (lookup element type details)
Reference Lookup → ELEMENT-TYPE-CATALOG.md (20 type definitions)
         ↓ (need quick syntax reminder)
Active Dev → QUICK-REFERENCE-CARD.md (Cheat sheet)
```

**Design Principle:** Progressive disclosure. Start simple (user guide), go deep as needed (module reference), lookup specifics (catalog), get quick answers (cheat sheet).

---

## 2. Quality Gate Templates

Quality gates ensure generated resource sheets meet **Tool 1's rigor** (exhaustiveness, refactor safety) **plus Tool 2's specialization** (element-type requirements).

### 2.1 Validation Categories

5 validation categories with auto-verifiable and manual checks:

#### Category 1: Structural Validation (Critical)

**Purpose:** Ensure generated resource sheet has required sections from Tool 1 framework.

| Check ID | Name | Validation | Severity | Auto? |
|----------|------|------------|----------|-------|
| STRUCT-001 | Header Metadata Present | Resource sheet has agent/date/task header block | Critical | ✅ Yes |
| STRUCT-002 | Executive Summary Complete | 2-4 sentence summary covering what/role/position/intent | Critical | ❌ No |
| STRUCT-003 | Required Sections Present | All element-type-specific required sections exist | Major | ✅ Yes |
| STRUCT-004 | State Ownership Table Exists | If element is stateful, state ownership table present | Major | ✅ Yes |

**Why These Checks Matter:** Tool 1's structural requirements ensure consistency. Missing executive summary = unusable doc.

#### Category 2: Content Quality (Tool 1 Standards)

**Purpose:** Ensure documentation meets Tool 1's writing guidelines and exhaustiveness requirements.

| Check ID | Name | Validation | Severity | Auto? |
|----------|------|------------|----------|-------|
| QUAL-001 | No Placeholders in Critical Sections | No TODO or [PLACEHOLDER] in required sections | Major | ✅ Yes |
| QUAL-002 | Exhaustiveness Standard Met | All state keys, events, contracts documented | Major | ❌ No |
| QUAL-003 | Voice & Tone Compliance | Imperative voice, no hedging, active voice | Minor | ❌ No |
| QUAL-004 | Tables Over Prose | Structured data in tables, not paragraphs | Minor | ✅ Yes |

**Why These Checks Matter:** Tool 1's "Tables over prose" rule prevents vague documentation. Exhaustiveness ensures all state keys documented.

#### Category 3: Element-Specific Validation (Tool 2 Requirements)

**Purpose:** Element type requirements from Tool 2 catalog templates.

| Check ID | Name | Validation | Severity | Auto? |
|----------|------|------------|----------|-------|
| ELEM-001 | Focus Areas Checklist Complete | All element-type focus areas addressed (from Tool 2 template) | Major | ✅ Yes |
| ELEM-002 | Required Sections for Type Present | All required sections for element type exist (from Tool 2 template) | Critical | ✅ Yes |
| ELEM-003 | Element-Specific Tables Complete | Type-specific tables (props, events, endpoints, etc.) populated | Major | ❌ No |

**Why These Checks Matter:** Tool 2 defines what matters per element type. Custom Hook MUST document side effects and cleanup.

#### Category 4: Refactor Safety (Tool 1 Core Value)

**Purpose:** Verify documentation supports safe refactoring (Tool 1's primary goal).

| Check ID | Name | Validation | Severity | Auto? |
|----------|------|------------|----------|-------|
| SAFE-001 | State Ownership Unambiguous | Clear ownership rules, no conflicts | Critical | ❌ No |
| SAFE-002 | Failure Modes Documented | All failure modes have recovery paths | Major | ❌ No |
| SAFE-003 | Non-Goals Explicit | Out-of-scope items listed to prevent scope creep | Minor | ✅ Yes |
| SAFE-004 | Contracts Defined | All external integration contracts documented | Critical | ❌ No |

**Why These Checks Matter:** Tool 1's refactor-safety checklist prevents breaking changes. Ambiguous state ownership = bugs during refactor.

#### Category 5: Auto-Fill Validation (Phase 2 Target)

**Purpose:** Verify auto-population from graph integration meets 60%+ target.

| Check ID | Name | Validation | Severity | Auto? |
|----------|------|------------|----------|-------|
| AUTO-001 | Auto-Fill Rate Meets Target | Generated content >= 60% auto-filled (Phase 2 target) | Major | ✅ Yes |
| AUTO-002 | Manual Review Flags Present | Low auto-fill sections flagged for human review | Minor | ✅ Yes |
| AUTO-003 | Graph Data Citations | Auto-filled data cites source (imports, exports, dependencies) | Minor | ✅ Yes |

**Why These Checks Matter:** 60%+ auto-fill = time savings. Flagging low auto-fill sections guides manual review effort.

### 2.2 Validation Workflow

7-step validation pipeline:

```
Step 1: Run structural validation (STRUCT-* checks)
  → Ensures basic template compliance (Tool 1 framework)

Step 2: Run element-specific validation (ELEM-* checks)
  → Ensures type-specific requirements met (Tool 2 templates)

Step 3: Run content quality checks (QUAL-* checks)
  → Ensures writing standards (Tool 1 guidelines)

Step 4: Run refactor safety checks (SAFE-* checks)
  → Ensures documentation supports safe changes (Tool 1 core value)

Step 5: Run auto-fill validation (AUTO-* checks)
  → Measures auto-population success (Phase 2 goal)

Step 6: Generate validation report
  → Counts: pass/fail/warning by category

Step 7: Flag critical failures for manual review
  → CRITICAL = blocking issue, MAJOR = warning, MINOR = informational
```

### 2.3 Scoring System

Validation outcomes:

- **REJECT:** Any critical check fails → Resource sheet not usable
- **PASS with Warnings:** ≤2 major failures → Acceptable but needs improvement
- **PASS:** ≤5 minor failures → Good quality
- **APPROVED:** All checks pass → Perfect resource sheet

**Example:**

```
Validation Report for AuthService-resource-sheet.md
=====================================================
Structural: 4/4 PASS ✅
Content Quality: 3/4 PASS ⚠️ (QUAL-003 failed: hedging detected "should probably")
Element-Specific: 3/3 PASS ✅
Refactor Safety: 3/4 PASS ⚠️ (SAFE-002 failed: network timeout failure mode missing recovery)
Auto-Fill: 3/3 PASS ✅ (62% auto-filled)

Overall: PASS with Warnings (2 major failures)
Action: Review QUAL-003 and SAFE-002 issues before finalizing
```

---

## 3. Maintenance Workflow

### 3.1 Update Triggers

When to update unified system documentation:

1. **New element type added** - 20 → 21+ types (update ELEMENT-TYPE-CATALOG.md)
2. **New conditional module created** - 11 → 12+ modules (update MODULE-REFERENCE.md)
3. **Detection characteristics enhanced** - New code patterns detected (update detection logic docs)
4. **Auto-fill capabilities improved** - New graph queries (update auto-fill rates in RESOURCE-SHEET-USER-GUIDE.md)
5. **Template structure changed** - New required sections (update templates, quality gates)
6. **Quality gate rules updated** - New validation checks (update validation docs)

### 3.2 Update Process (6 Steps)

#### Step 1: Identify Change Type

Classify the change:
- Element type addition
- Module addition/modification
- Detection enhancement
- Auto-fill improvement
- Template structure change
- Quality gate update

#### Step 2: Update Primary Documentation

Update the main affected doc:
- **Element type** → ELEMENT-TYPE-CATALOG.md
- **Module** → MODULE-REFERENCE.md
- **Detection/Auto-fill** → RESOURCE-SHEET-USER-GUIDE.md
- **Quality gate** → Quality gate templates (internal)

#### Step 3: Update Dependent Docs

Cascade changes to cross-references:
- Update examples that use the changed element type/module
- Update QUICK-REFERENCE-CARD.md if command syntax changed
- Update cross-references in other docs

#### Step 4: Version Control

Apply semantic versioning:
- **MAJOR bump** - Breaking changes (element types removed, required sections changed)
- **MINOR bump** - New element types, new modules, new features (backward compatible)
- **PATCH bump** - Bug fixes, clarifications, examples added (no behavior change)

Add CHANGELOG entry documenting the change.

#### Step 5: Validation

Run quality gates on updated docs:
- Verify examples work
- Check cross-references resolve
- Test command syntax (if changed)

#### Step 6: Announcement

Update RESOURCE-SHEET-USER-GUIDE.md with "What's New" section at top.

### 3.3 Deprecation Protocol

When removing or changing functionality:

1. **Mark Deprecated:** Add `⚠️ DEPRECATED` header to old section
2. **Migration Notes:** Provide migration path to new approach
3. **Archive Timeline:** Keep deprecated content for 1 version, then move to appendix
4. **Breaking Changes:** Bump major version, document prominently in CHANGELOG

**Example:**

```markdown
## ⚠️ DEPRECATED: Single Monolithic Template Approach

**Deprecated in:** v2.0.0
**Removed in:** v3.0.0
**Migration:** Use modular approach with universal + conditional modules

The old single-template approach has been replaced by the composable module system.

### Migration Guide
1. Identify your element type from ELEMENT-TYPE-CATALOG.md
2. Run /create-resource-sheet with auto-detection
3. System will select appropriate modules automatically
```

### 3.4 Versioning Strategy

Semantic versioning aligned with tool changes:

- **v1.0.0** - Initial unified system (Tool 1 + Tool 2 merged)
- **v1.1.0** - Added 21st element type (minor bump, backward compatible)
- **v2.0.0** - Changed required sections for API Client type (major bump, breaking)
- **v2.0.1** - Fixed typo in Custom Hook example (patch bump)

---

## 4. Coderef-Workflow Integration

### 4.1 Planning Workflow Hooks

The unified resource sheet system integrates into coderef-workflow at **3 phases**:

#### Phase 0: Preparation (Reference Component Documentation)

**When:** Before planning begins
**Purpose:** Document reference components to understand existing patterns
**Tool Call:** `generate_resource_sheet`
**Input:** Reference component from `analysis.json`
**Output:** Resource sheet for reference component (used as template in planning)
**Trigger:** Manual - Agent calls `/create-resource-sheet` during analysis

**Example:**
```
Agent analyzing project for dark-mode-toggle feature
→ Identifies ThemeProvider as reference component
→ Runs /create-resource-sheet ThemeProvider
→ Gets resource sheet documenting current state management pattern
→ Uses pattern in plan.json as "follow this approach"
```

#### Phase 3: Current State Analysis (Baseline Documentation)

**When:** After identifying affected files
**Purpose:** Document existing components before making changes (baseline)
**Tool Call:** `generate_resource_sheet`
**Input:** Affected files from current state analysis
**Output:** Resource sheets for existing components (baseline documentation)
**Trigger:** Manual - Agent documents current state before implementation

**Example:**
```
Agent planning auth-system feature
→ Current state analysis identifies UserManager, SessionStore affected
→ Runs /create-resource-sheet UserManager
→ Runs /create-resource-sheet SessionStore
→ Documents current state ownership, event contracts
→ Plans refactoring aware of existing contracts (refactor-safe)
```

#### Post-Implementation: Documentation (Final Artifacts)

**When:** After feature implementation complete
**Purpose:** Document newly created components
**Tool Call:** `generate_resource_sheet`
**Input:** New components from implementation
**Output:** Resource sheets for new components (final documentation)
**Trigger:** Manual - Agent runs `/create-resource-sheet` after feature complete

**Example:**
```
Agent completed auth-system feature
→ Created new AuthService, TokenManager components
→ Runs /create-resource-sheet AuthService
→ Runs /create-resource-sheet TokenManager
→ Resource sheets saved to coderef/workorder/auth-system/docs/
→ Referenced in DELIVERABLES.md as documentation artifacts
```

### 4.2 Output Format Expectations

3 output formats, each with specific use case:

#### Markdown Output

- **Location:** `coderef/workorder/{feature-name}/docs/`
- **Filename:** `{component-name}-resource-sheet.md`
- **Use Case:** Human-readable component documentation
- **Integration:** Referenced in DELIVERABLES.md as documentation artifact

#### JSON Schema Output

- **Location:** `coderef/workorder/{feature-name}/schemas/`
- **Filename:** `{component-name}-schema.json`
- **Use Case:** Validation, tooling, API contracts
- **Integration:** Used by coderef-workflow for type validation

#### JSDoc Output

- **Location:** Inline in source code
- **Filename:** N/A (embedded in `.ts`/`.tsx` files)
- **Use Case:** IDE autocomplete, inline documentation
- **Integration:** Agent adds JSDoc comments during implementation

### 4.3 Slash Command Recommendations

**New Command:** `/document-component`

- **Purpose:** Shorthand for `/create-resource-sheet` focused on components
- **Syntax:** `/document-component {ComponentName}`
- **Behavior:**
  1. Auto-detects element type (likely "Design System Component" or "Top-Level Widget")
  2. Generates all 3 formats (markdown, JSON schema, JSDoc)
  3. Saves to current workorder docs directory
  4. Returns summary of auto-fill rate and manual review sections
- **Integration:** Calls `generate_resource_sheet` MCP tool with component-focused defaults

**Example:**
```
Agent: /document-component AuthService

System:
→ Detected element type: API Client Layer (Template 5)
→ Selected modules: Architecture, Integration, Network (Endpoints, Auth, Retry, Errors)
→ Auto-fill rate: 68% (imports, exports, endpoint detection via graph)
→ Generated 3 outputs:
  - coderef/workorder/auth-system/docs/AuthService-resource-sheet.md
  - coderef/workorder/auth-system/schemas/AuthService-schema.json
  - JSDoc comments added to src/auth/AuthService.ts
→ Manual review needed: Error taxonomy table (32% auto-filled, needs human input)
```

### 4.4 Agent Guidance

**When to Generate Resource Sheets:**

1. **Before refactoring** - Document current state (baseline)
2. **After major feature** - Document new components (final artifacts)
3. **During code review** - Verify documentation exists
4. **When onboarding** - Create resource sheets for complex systems

**Quality Expectations:**

1. Resource sheet **passes all critical quality gates** (STRUCT-*, ELEM-*, SAFE-*)
2. **Auto-fill rate >= 60%** for most element types (use graph integration)
3. **Manual sections flagged** for review (don't leave TODOs unmarked)
4. **Examples provided** for complex behaviors (state transitions, error recovery)

---

## 5. Ecosystem Alignment

### 5.1 MCP Tool Patterns

**Alignment Score: 9/10**

✅ **Strengths:**
- Modular architecture (4 universal + 11 conditional modules) aligns with coderef-workflow composability
- 3-output generation (markdown, JSON schema, JSDoc) matches coderef-docs multi-format pattern
- Quality gates follow coderef-workflow validation approach (0-100 scoring)

⚠️ **Minor Gap:**
- No direct REST API wrapper yet (aligns with ecosystem-wide limitation)

### 5.2 Documentation Standards

**Alignment Score: 10/10**

✅ **Perfect Alignment:**
- 4-tier documentation hierarchy follows POWER framework (Purpose, Overview, What/Why/When, Examples, References)
- Semantic versioning matches ecosystem standard (MAJOR.MINOR.PATCH)
- Deprecation protocol matches ecosystem-wide approach (⚠️ DEPRECATED headers, migration notes)

### 5.3 Workflow Integration

**Alignment Score: 8/10**

✅ **Strengths:**
- Hooks into coderef-workflow at 3 natural phases (preparation, current state, post-implementation)
- Output formats align with workorder structure (docs/, schemas/)
- `/document-component` shorthand follows ecosystem command conventions

⚠️ **Gap:**
- Auto-trigger not implemented (requires manual `/create-resource-sheet` calls)
- Could integrate with `update_deliverables` tool for automatic post-implementation docs

---

## 6. Key Features to Preserve

From **Tool 1 (Execution Framework):**

1. ✅ **Exhaustiveness Requirements** - "Document ALL state keys, events, contracts"
2. ✅ **Refactor Safety Checks** - Pre-submission checklist (state ownership, failure modes, contracts)
3. ✅ **Voice & Tone Guidelines** - Imperative, no hedging, active voice
4. ✅ **Tables Over Prose** - Structured data in tables (state, events, contracts)
5. ✅ **Maintenance Protocol** - Deprecation, versioning, migration notes

From **Tool 2 (Element Specialization):**

1. ✅ **20 Element Types** - High-ROI classification (top-level widgets → testing harness)
2. ✅ **Focus Areas Checklists** - Element-specific priorities (hooks: side effects, cleanup)
3. ✅ **Required Sections Per Type** - Type-specific templates (API client: endpoint catalog, retry logic)
4. ✅ **Maintenance Impact Ranking** - Critical → High → Medium → Low prioritization
5. ✅ **Element Type Detection** - Auto-detect from code patterns

---

## 7. Concerns

1. **Documentation Maintenance Burden:**
   - **Issue:** 4-tier documentation hierarchy (user guide, module reference, catalog, quick ref) requires consistent updates
   - **Mitigation:** Implement automated cross-reference checking, update checklist in maintenance workflow

2. **Quality Gate Complexity:**
   - **Issue:** 5 categories × ~4 checks each = 20+ validation rules, some manual
   - **Mitigation:** Automate what's possible (12/20 checks auto-verifiable), prioritize critical checks

3. **Auto-Fill Rate Variance:**
   - **Issue:** 60%+ target achievable for some element types (API Client), harder for others (Design System Component)
   - **Mitigation:** Document expected auto-fill rates per element type, flag low auto-fill sections

4. **Workflow Integration Friction:**
   - **Issue:** Manual `/create-resource-sheet` calls at 3 phases may be forgotten
   - **Mitigation:** Add reminders in coderef-workflow plan templates, consider auto-trigger in future

---

## 8. Recommendations

### High Priority (Implement in Phase 1)

1. **Create 4-tier documentation hierarchy** (user guide → module reference → catalog → quick ref)
   - Rationale: Different audiences need different entry points

2. **Implement 5-category validation pipeline** (structural, content, element-specific, refactor-safety, auto-fill)
   - Rationale: Combines Tool 1's rigor with Tool 2's specialization

3. **Define semantic versioning strategy** (MAJOR.MINOR.PATCH aligned with changes)
   - Rationale: Clear expectations for breaking vs non-breaking changes

4. **Add `/document-component` shorthand command**
   - Rationale: Common use case, reduces friction

### Medium Priority (Implement in Phase 2)

5. **Auto-trigger resource sheet generation** post-implementation
   - Rationale: Reduces manual steps, ensures docs always exist

6. **Cross-reference validation tool**
   - Rationale: Prevents broken links in 4-tier documentation

7. **Auto-fill rate reporting dashboard**
   - Rationale: Tracks Phase 2 60%+ target per element type

### Low Priority (Future Enhancement)

8. **Visual diff tool for resource sheet updates**
   - Rationale: Helps review changes during refactoring

9. **Resource sheet templates in IDE**
   - Rationale: Generate docs directly from code editor

10. **AI-powered quality gate auto-fixes**
    - Rationale: Automatically fix voice/tone issues, missing sections

---

## Conclusion

This documentation standards guide defines how to document the unified resource sheet system (Tool 1 + Tool 2 merged). The system preserves:

- **Tool 1's execution rigor** - Exhaustiveness, refactor safety, quality controls
- **Tool 2's element specialization** - 20 types, focus areas, type-specific requirements

The 4-tier documentation hierarchy (user guide → module reference → catalog → quick ref) serves different audiences. The 5-category validation pipeline (20+ checks) ensures quality. The 6-step maintenance workflow supports evolution. Integration with coderef-workflow at 3 phases (preparation, current state, post-implementation) completes the feature lifecycle.

**Next Steps:**
1. Review this standards guide with coderef (synthesizer) output
2. Validate alignment with papertrail (template generator) schema
3. Create final workorder using approved consolidation approach

---

**Agent Status:** COMPLETE
**Output Files:**
- `coderef-docs-output.json` (structured standards data)
- `coderef-docs-output.md` (this narrative guide)
