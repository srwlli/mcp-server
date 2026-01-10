# Plan Review - CodeRef (Main MCP Server)

## Agent ID
coderef

## Timestamp
2026-01-02

## Plans Reviewed
1. `C:\Users\willh\Desktop\assistant\coderef\workorder\resource-sheet-system\plan.json`
2. `C:\Users\willh\.mcp-servers\coderef-docs\coderef\workorder\resource-sheet-reconciliation\plan.json`
3. `C:\Users\willh\Desktop\projects\coderef-system\coderef\workorder\resource-sheet-graph-integration\plan.json`

## Tools Analyzed

### Tool 1: create-resource-sheet.md (240 lines)
**Location:** `C:\Users\willh\Desktop\assistant\.claude\commands\create-resource-sheet.md`

**What it provides:**
- ✅ Agent execution framework (step-by-step instructions for generating docs)
- ✅ 13-section documentation template (Architecture, State, Events, Performance, etc.)
- ✅ Writing guidelines (voice, tone, precision rules)
- ✅ Refactor-safety validation checklist
- ✅ Maintenance protocol (versioning, deprecation)
- ✅ Output format specification

**What it's missing:**
- ❌ Element type classification (no awareness of "stateful container" vs "API client")
- ❌ Element-specific checklists (same template for all elements)
- ❌ Specialized templates per type

### Tool 2: resource-sheet-catalog.md (634 lines)
**Location:** `C:\Users\willh\Desktop\assistant\.claude\commands\resource-sheet-catalog.md`

**What it provides:**
- ✅ 20 element type classifications (top-level widgets, stateful containers, global state, hooks, API clients, etc.)
- ✅ Element-specific checklists per type
- ✅ Required sections per type
- ✅ Focus areas per element type
- ✅ Master checklist for all types

**What it's missing:**
- ❌ Agent execution framework (no instructions on HOW to generate)
- ❌ Writing quality standards (no voice/tone guidance)
- ❌ Output format specification
- ❌ Validation rules

---

## 🚨 CRITICAL DISCOVERY

**coderef-docs v3.4.0 ALREADY HAS a working MCP tool for resource sheets!**

### What Exists Today
- **MCP Tool:** `generate_resource_sheet` (operational since v3.4.0)
- **Location:** `coderef-docs/generators/resource_sheet_generator.py`
- **Status:** Phase 1 complete (17/22 tasks, 100% test coverage)

### What It Does
1. **Composable Module Architecture** - 4 universal modules + 11 conditional modules (planned)
2. **3-Step Workflow:**
   - **Detect** - CharacteristicsDetector maps 20+ code patterns from .coderef/index.json
   - **Select** - ModuleRegistry chooses appropriate modules based on characteristics
   - **Assemble** - DocumentComposer generates 3 synchronized outputs
3. **3 Output Formats:**
   - Markdown (human-readable documentation)
   - JSON Schema (machine-readable contracts)
   - JSDoc (inline code comments)
4. **Auto-Fill:** 50% in Phase 1 (architecture + integration modules fully auto-filled)
5. **Detection Accuracy:** ~85% baseline (target 90%+ in Phase 2)

### Implication
**We don't need to build from scratch. We need to RECONCILE the slash commands with the existing MCP tool.**

---

## Consolidation Design

### Strategy: RECONCILIATION (Not Rebuild)

**Core Insight:** Tool 1 + Tool 2 define WHAT to document. The MCP tool ALREADY does the HOW. We just need to connect them.

### Approach
1. **DEPRECATE** the two .md files (with notices pointing to MCP tool)
2. **ROUTE** `/create-resource-sheet` command to MCP tool `generate_resource_sheet`
3. **ENHANCE** MCP tool with missing features from Tool 1 and Tool 2

---

## Key Questions Answered

### Q1: How to structurally merge the two .md files?

**Answer:** Don't merge them - DEPRECATE them and route to the MCP tool.

**Rationale:**
- MCP tool has superior architecture (composable modules vs monolithic 874-line merged file)
- Merging .md files would duplicate existing working code
- Slash command abstraction layer hides backend implementation

**Implementation:**
```markdown
<!-- At top of create-resource-sheet.md -->
# ⚠️ DEPRECATED - Use MCP Tool Instead

This command now routes to `generate_resource_sheet` MCP tool (coderef-docs v3.4.0+).

For element type reference, see: resource-sheet-catalog.md
For implementation details, see: coderef-docs/generators/resource_sheet_generator.py

## Usage
/create-resource-sheet [target] [scope]

This command automatically detects element type and generates appropriate documentation.
```

### Q2: Where do the 20 element types from Tool 2 fit in the merged structure?

**Answer:** Map the 20 element types to conditional modules in the MCP tool.

**Mapping Strategy:**

| Element Type (Tool 2) | Conditional Modules (MCP) | Detection Characteristics |
|----------------------|---------------------------|---------------------------|
| Top-level widgets/pages | ui/composition, ui/events, ui/accessibility | is_component, has_jsx, is_entry_point |
| Stateful containers | state/management, state/lifecycle | has_state, manages_children |
| Global state layer | state/management, state/persistence | is_store, has_actions |
| Custom hooks | hooks/signature, hooks/side_effects | is_hook, has_use_effect |
| API client layer | network/endpoints, network/auth, network/retry | has_fetch, has_axios |
| Data models & schemas | - (universal architecture module) | has_interface, has_type |
| Persistence subsystem | state/persistence | has_storage, has_cache |
| Eventing/messaging | ui/events | has_event_emitter |
| ... (12 more mappings) | ... | ... |

**Implementation:**
- Create `element-type-mapping.json` in MCP tool
- Enhance CharacteristicsDetector with Tool 2's classification logic
- ModuleRegistry uses mapping to select appropriate conditional modules

### Q3: How does element type detection/selection work?

**Answer:** CharacteristicsDetector already exists with 20+ detection patterns.

**Current Implementation (Phase 1):**
```python
# coderef-docs/modules/resource-sheet/detection/characteristics.py
class CharacteristicsDetector:
    def detect(self, element_data):
        return {
            "is_component": self._check_component(element_data),
            "has_state": self._check_state(element_data),
            "has_lifecycle": self._check_lifecycle(element_data),
            # ... 17+ more characteristics
        }
```

**Enhancement Needed:**
- Add Tool 2's element type classifications as higher-level detection
- Map combinations of characteristics → element types
- Use element types to drive module selection

**Example:**
```python
def classify_element_type(characteristics):
    if characteristics["is_component"] and characteristics["is_entry_point"]:
        return "top-level-widget"
    elif characteristics["has_state"] and characteristics["manages_children"]:
        return "stateful-container"
    elif characteristics["is_hook"] and characteristics["has_use_effect"]:
        return "custom-hook"
    # ... 17 more classifications
```

### Q4: How does `/create-resource-sheet` command route to element types?

**Answer:** Slash command calls MCP tool with optional `element_type` parameter.

**Implementation Flow:**
```
User: /create-resource-sheet AuthService
       ↓
Slash Command Handler:
  - Parses target: "AuthService"
  - Calls MCP tool: generate_resource_sheet(target="AuthService", mode="reverse-engineer")
       ↓
MCP Tool:
  1. Reads .coderef/index.json to find AuthService
  2. CharacteristicsDetector analyzes code
  3. classify_element_type() → "api-client-layer" (from Tool 2's 20 types)
  4. ModuleRegistry selects: [architecture, integration, network/endpoints, network/auth, network/retry]
  5. DocumentComposer assembles 3 outputs
       ↓
Output: Markdown + JSON Schema + JSDoc for AuthService
```

**With Manual Override:**
```
User: /create-resource-sheet Button.tsx --type design-system-component
       ↓
MCP Tool skips auto-detection, uses specified type directly
```

### Q5: What's the migration path from old to new?

**Answer:** 3-phase migration: Deprecate → Route → Enhance

#### Phase 1: DEPRECATE (Immediate - 15 min)
- Add deprecation notices to both .md files
- Point users to MCP tool documentation
- Keep files for backward compatibility (don't delete)

#### Phase 2: ROUTE (Short-term - 1-2 hours)
- Update `/create-resource-sheet` command implementation
- Change from "expand .md file" to "call MCP tool"
- Maintain same user interface (command signature unchanged)

#### Phase 3: ENHANCE (Long-term - Deferred to MCP Tool Phase 2)
- Port Tool 1's writing guidelines into MCP tool post-processing
- Port Tool 2's 20 element type checklists into conditional modules
- Integrate validation rules from Tool 1's refactor-safety checklist

**Timeline:**
- Phase 1: Today (deprecation)
- Phase 2: This week (routing)
- Phase 3: Next sprint (enhancements as part of existing MCP tool Phase 2 workorder)

---

## Unified System Architecture

### Entry Point
```
/create-resource-sheet [target] [--type element_type]
```

### Backend Flow
```
Slash Command Wrapper
    ↓
MCP Tool Handler (generate_resource_sheet)
    ↓
Detection Engine (CharacteristicsDetector + Element Type Classifier)
    ↓
Module Selection (ModuleRegistry with Tool 2's 20-type mapping)
    ↓
Assembly (DocumentComposer with Tool 1's writing guidelines)
    ↓
3 Outputs: Markdown + JSON Schema + JSDoc
```

### File Changes Required

#### Deprecate
- `.claude/commands/create-resource-sheet.md` - Add deprecation notice at top
- `.claude/commands/resource-sheet-catalog.md` - Add deprecation notice at top

#### Modify
- `.claude/commands/create-resource-sheet.md` - Route to MCP tool (keep for backward compat)
- `coderef-docs/generators/resource_sheet_generator.py` - Enhance with Tool 1 + Tool 2 features

#### New
- `coderef-docs/modules/resource-sheet/mapping/element-type-mapping.json` - Map Tool 2's 20 types
- `coderef-docs/modules/resource-sheet/guidelines/writing-standards.py` - Port Tool 1's guidelines
- `coderef-docs/modules/resource-sheet/validation/refactor-safety.py` - Port Tool 1's validation

---

## Feature Preservation Matrix

### From Tool 1 (create-resource-sheet.md)

| Feature | Preservation Strategy | Implementation |
|---------|----------------------|----------------|
| Writing guidelines (voice, tone, precision) | Port to MCP tool post-processing | Create writing-standards.py module |
| Refactor-safety checklist | Port to MCP tool validation | Create refactor-safety.py validator |
| 13-section template | Already exists in MCP tool | No action needed (architecture module) |
| Maintenance protocol | Document in MCP tool usage guide | Update coderef-docs/CLAUDE.md |
| Output format specification | Already exists in MCP tool | No action needed (3 outputs: MD/JSON/JSDoc) |

### From Tool 2 (resource-sheet-catalog.md)

| Feature | Preservation Strategy | Implementation |
|---------|----------------------|----------------|
| 20 element type classifications | Map to conditional modules + detection | Create element-type-mapping.json |
| Element-specific checklists | Integrate into ModuleRegistry | Add checklist metadata to modules |
| Required sections per type | Define in module metadata | Each module declares sections it provides |
| Focus areas per element type | Convert to detection characteristics | Enhance CharacteristicsDetector |
| Master checklist | Convert to validation rules | Port to refactor-safety.py |

---

## Validation Results

### Completeness Check
- ✅ All Tool 1 features preserved
- ✅ All Tool 2 features preserved
- ✅ `/create-resource-sheet` command continues working
- ✅ Zero functionality loss
- ✅ Backward compatibility maintained

### Technical Feasibility
- ✅ MCP tool exists and is operational
- ✅ Routing mechanism is straightforward (slash command → MCP tool call)
- ✅ Enhancement path is clear (Phase 2 work already scoped)
- ✅ No architectural conflicts with ecosystem

### Alignment with CodeRef Ecosystem
- ✅ Follows MCP tool pattern (consistent with coderef-docs architecture)
- ✅ Consistent with global deployment rule (no local copies)
- ✅ Integrates with coderef-workflow planning workflows
- ✅ Leverages existing .coderef/ intelligence infrastructure

---

## Recommendations

### Immediate Actions (Today)
1. **Add deprecation notices** to both .md files (15 min)
   - Clear messaging: "This command now uses MCP tool generate_resource_sheet"
   - Link to coderef-docs documentation

### Short-Term Actions (This Week)
2. **Update `/create-resource-sheet` command** to route to MCP tool (1-2 hours)
   - Change implementation from "expand .md file" to "call MCP tool"
   - Test backward compatibility

3. **Create element type mapping** (2-3 hours)
   - Map Tool 2's 20 types → MCP conditional modules
   - Document mapping in element-type-mapping.json

### Medium-Term Actions (Next Sprint)
4. **Port writing guidelines** into MCP tool (deferred to Phase 2)
   - Create writing-standards.py post-processor
   - Apply Tool 1's voice/tone rules to generated output

5. **Port validation checklist** into MCP tool (deferred to Phase 2)
   - Create refactor-safety.py validator
   - Run validation before finalizing output

### Long-Term Integration
6. **Leverage Plan 3's graph integration** (separate workorder)
   - Integrate DependencyGraph queries for auto-fill improvement
   - Target: 60-80% auto-fill rate (up from current 50%)

---

## Next Steps

### User Decision Required
1. **Confirm deprecation approach**
   - Option A: Keep .md files with warnings (recommended for backward compatibility)
   - Option B: Delete .md files entirely (cleaner but breaks old references)

2. **Decide on Phase 2 timeline**
   - When to port writing guidelines and validation?
   - Integrate with existing MCP tool Phase 2 workorder or separate?

3. **Approve element type mapping design**
   - Review 20-type → module mapping table
   - Confirm detection characteristics are sufficient

### Ready to Implement
- ✅ Deprecation notices can be added immediately
- ✅ Slash command routing can be implemented today
- ✅ Mapping table can be created this week

---

## Conclusion

**The consolidation path is clear:** We don't need to merge 874 lines of markdown into a monolithic file. Instead, we **deprecate the old slash command implementations** and **route to the existing MCP tool** that already has superior architecture.

**Key Insight:** Tool 1 (HOW to write) + Tool 2 (WHAT to write) = Perfect input for the MCP tool's Phase 2 enhancement. The MCP tool provides the execution engine. Tool 1 provides quality standards. Tool 2 provides specialization. Together, they create the complete system.

**Recommended Approach:**
1. ✅ Deprecate old .md files (keep for reference)
2. ✅ Route `/create-resource-sheet` to MCP tool
3. ✅ Create 20-type → module mapping
4. ✅ Defer enhancements to MCP tool Phase 2 (already scoped)

This approach:
- ✅ Preserves all functionality
- ✅ Maintains backward compatibility
- ✅ Leverages existing working code
- ✅ Aligns with ecosystem architecture
- ✅ Provides clear migration path

**Total Effort:** ~5-6 hours for complete consolidation (vs ~40-60 hours to rebuild from scratch)

---

**Agent:** coderef (Main MCP Server)
**Session:** WO-REFERENCE-SHEET-RECONCILIATION-001
**Role:** Synthesizer - Compare all three plans and design unified approach
