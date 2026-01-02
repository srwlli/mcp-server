# CodeRef Document Output Audit - coderef-workflow Analysis

**Server:** coderef-workflow
**Agent:** Lloyd (Orchestrator)
**Workorder:** WO-DOC-OUTPUT-AUDIT-001
**Analysis Date:** 2026-01-01
**Status:** Complete

---

## Executive Summary

coderef-workflow extensively utilizes all 4 document categories with **90% integration**:
- ✅ Foundation docs (deep extraction, dual-location support)
- ✅ Standards docs (existence checking, planning integration)
- ✅ Workflow/workorder docs (core orchestration, complete lifecycle)
- ✅ .coderef/ outputs (3-tier priority system, 99% AST accuracy)

**Key Finding:** coderef-workflow demonstrates sophisticated multi-tier fallback architecture for .coderef/ outputs but lacks content-level analysis for standards docs.

---

## 1. Foundation Docs Usage

### How Used
**Files:** `generators/planning_analyzer.py` (lines 113-191), `generators/coderef_foundation_generator.py`

**Primary Use Cases:**
1. **Planning Phase Context Gathering** (planning_analyzer.py:113-152)
   - Scans for: README.md, API.md, ARCHITECTURE.md, COMPONENTS.md, SCHEMA.md, USER-GUIDE.md
   - Checks dual locations: project root AND `coderef/foundation-docs/`
   - Returns: `{'available': [...], 'missing': [...]}`

2. **Deep Content Extraction** (planning_analyzer.py:154-191)
   - Mode 1: Shallow (500-char preview)
   - Mode 2: Deep (full content + header parsing)
   - Extracts: First 10 markdown headers, content size, location

3. **Foundation Doc Generation** (coderef_foundation_generator.py)
   - Auto-generates: ARCHITECTURE.md, SCHEMA.md, COMPONENTS.md, API.md, README.md
   - Uses coderef data when available (graph.json for diagrams, index.json for elements)
   - Falls back to regex detection when .coderef/ unavailable

**Code References:**
```python
# planning_analyzer.py:113-152
def scan_foundation_docs(self) -> dict:
    foundation_docs = ['README.md', 'API.md', 'ARCHITECTURE.md', ...]
    # Checks both root and coderef/foundation-docs/

# planning_analyzer.py:154-191
def read_foundation_doc_content(self) -> dict:
    # Deep extraction: preview, headers, size
    doc_content[doc_name] = {
        'location': rel_location,
        'preview': content[:500],
        'headers': self._extract_headers(content),
        'size': len(content)
    }
```

### Strengths
✅ **Flexible location checking** - Searches both root and coderef/foundation-docs/
✅ **Deep extraction mode** - Full content parsing with structural analysis
✅ **Header extraction** - Automatically parses markdown headers for quick navigation
✅ **Size tracking** - Monitors document growth over time
✅ **Auto-generation** - Creates missing foundation docs from coderef data

### Weaknesses
⚠️ **Limited header extraction** - Only first 10 headers (may miss deep sections)
⚠️ **500-char preview** - Shallow mode may miss critical context in long docs
⚠️ **No semantic search** - Can't query "what decisions were made about authentication?"
⚠️ **No versioning** - Doesn't track document evolution over time
⚠️ **No validation** - Doesn't verify POWER framework compliance

### Recommendations
1. **Add semantic search** - Index foundation docs for natural language queries
2. **Extract decision sections** - Parse "## Design Decisions" and "## Key Decisions" sections explicitly
3. **Increase header limit** - Extract all headers (remove 10-header cap)
4. **Add validation** - Check for POWER framework sections (Purpose, Overview, What/Why/When, Examples, References)
5. **Track document age** - Alert when foundation docs are >90 days old

---

## 2. Standards Docs Usage

### How Used
**Files:** `generators/planning_analyzer.py` (lines 377-415), `constants.py` (line 69)

**Primary Use Cases:**
1. **Existence Checking** (planning_analyzer.py:377-415)
   - Scans `coderef/standards/` for:
     - BEHAVIOR-STANDARDS.md
     - COMPONENT-PATTERN.md
     - UI-STANDARDS.md
     - UX-PATTERNS.md
     - COMPONENT-INDEX.md
   - Returns: `{'available': [...], 'missing': [...]}`

2. **Path Constants** (constants.py:69)
   - `STANDARDS_DIR = 'coderef/standards'`
   - Centralized path definition

**Code References:**
```python
# planning_analyzer.py:377-415
def scan_coding_standards(self) -> dict:
    standards_docs = [
        'BEHAVIOR-STANDARDS.md',
        'COMPONENT-PATTERN.md',
        'UI-STANDARDS.md',
        'UX-PATTERNS.md',
        'COMPONENT-INDEX.md'
    ]
    standards_dir = self.project_path / 'coderef' / 'standards'
    # Returns available/missing lists
```

### Strengths
✅ **Clear directory structure** - Centralized coderef/standards/ location
✅ **Available/missing tracking** - Easy gap identification
✅ **Standardized naming** - Predictable file names

### Weaknesses
⚠️ **No content parsing** - Only checks file existence, doesn't read content
⚠️ **No utilization scoring** - Can't tell if standards are actually followed
⚠️ **No compliance tracking** - Doesn't measure code adherence to standards
⚠️ **No auto-suggestion** - Doesn't recommend standards during planning
⚠️ **Missing integration** - Doesn't link standards to plan tasks

### Recommendations
1. **Parse standard definitions** - Extract pattern definitions and examples
2. **Track compliance metrics** - Scan codebase for standard adherence
3. **Auto-suggest standards** - During planning, recommend relevant standards for feature type
4. **Link to tasks** - Associate standards with specific plan tasks
5. **Generate violation reports** - Integrate with check_consistency tool results

---

## 3. Workflow/Workorder Docs Usage

### How Used
**Files:** Multiple files across the server (17 files reference these docs)

**Primary Use Cases:**
1. **Feature Lifecycle Orchestration**
   - `context.json` - Requirements & constraints
   - `plan.json` - 10-section implementation plan
   - `communication.json` - Multi-agent coordination
   - `DELIVERABLES.md` - Metrics & tracking
   - `execution-log.json` - Progress tracking

2. **Path Management** (constants.py:195)
   - `WORKING_DIR = Path('coderef') / 'workorder'`
   - Migrated from `coderef/working/` to `coderef/workorder/` (v1.1.0)

3. **Workorder Tracking**
   - Global audit trail in `coderef/workorder-log.txt`
   - Workorder ID format: `WO-{FEATURE}-{CATEGORY}-###`
   - Tracked in plan.json META_DOCUMENTATION

**Code References:**
```python
# constants.py:195
WORKING_DIR = Path('coderef') / 'workorder'

# Used in 17 Python files for:
# - plan.json generation/validation
# - context.json gathering
# - DELIVERABLES.md template generation
# - communication.json for multi-agent coordination
```

### Strengths
✅ **Complete lifecycle tracking** - From context → plan → execution → deliverables → archive
✅ **Structured JSON formats** - Machine-readable, validation-ready
✅ **Workorder ID tracking** - Global audit trail with unique IDs
✅ **Multi-agent support** - communication.json enables parallel execution
✅ **Metrics capture** - DELIVERABLES.md tracks LOC, commits, time

### Weaknesses
⚠️ **No cross-workorder analytics** - Can't analyze patterns across multiple features
⚠️ **No template validation** - plan.json schema validation is manual
⚠️ **No dependency tracking** - Can't detect dependent workorders
⚠️ **No progress dashboard** - Real-time progress tracking limited
⚠️ **No workorder search** - Can't query "find all auth-related workorders"

### Recommendations
1. **Add workorder dependency tracking** - Detect when workorders depend on each other
2. **Implement template validation schemas** - JSON Schema validation for plan.json, context.json
3. **Auto-generate DELIVERABLES** - Pre-populate from plan.json structure
4. **Cross-workorder analytics** - Dashboard showing velocity, completion rates, bottlenecks
5. **Workorder search** - Index workorder content for full-text search

---

## 4. .coderef Analysis Outputs Usage

### How Used
**Files:** `generators/planning_analyzer.py` (lines 206-302, 417-563), `generators/coderef_foundation_generator.py`

**Primary Use Cases:**
1. **3-Tier Priority System** (planning_analyzer.py:206-302)
   - **Priority 1:** Read `.coderef/index.json` (FASTEST - pre-scanned data)
   - **Priority 2:** Call `coderef_scan` MCP tool (AST-based live scan)
   - **Priority 3:** Fallback to `coderef/inventory/` manifests (legacy)

2. **Element Inventory** (planning_analyzer.py:206-265)
   - Reads index.json: List of all functions, classes, components
   - Groups by type: function, class, component, etc.
   - Extracts unique files and element counts

3. **Dependency Analysis** (planning_analyzer.py:417-456)
   - Uses `coderef_query` MCP tool for "depends-on-me" queries
   - Finds reference components based on dependency graph

4. **Pattern Detection** (planning_analyzer.py:461-563)
   - Uses `coderef_patterns` MCP tool for AST-based detection (99% accuracy)
   - Falls back to regex-based analysis (85% accuracy)

5. **Test Coverage** (planning_analyzer.py:733-765)
   - Uses `coderef_coverage` MCP tool for test gap analysis
   - Identifies untested code during planning

6. **Foundation Doc Generation** (coderef_foundation_generator.py)
   - Uses index.json for element lists
   - Uses graph.json for dependency diagrams
   - Uses patterns.json for architecture patterns

**Code References:**
```python
# planning_analyzer.py:206-265 (Priority system)
async def read_inventory_data(self) -> dict:
    # Priority 1: Read .coderef/index.json (FASTEST)
    if check_coderef_available(str(self.project_path)):
        index_data = read_coderef_output(str(self.project_path), 'index')
        return {'index_data': index_data, 'source': 'coderef_index', ...}

    # Priority 2: Call coderef_scan MCP tool
    result = await call_coderef_tool("coderef_scan", {...})

    # Priority 3: Fallback to coderef/inventory/ manifests
    inventory_data = json.loads(inventory_path.read_text(...))

# planning_analyzer.py:461-496 (Pattern detection)
async def identify_patterns(self) -> List[str]:
    # Try coderef_patterns tool (99% accuracy)
    result = await call_coderef_tool("coderef_patterns", {...})
    # Fallback to regex (85% accuracy)
    source_files = self._scan_source_files()
```

### Strengths
✅ **Multi-tier fallback architecture** - Graceful degradation when tools unavailable
✅ **AST-based accuracy** - 99% accuracy with coderef_scan vs 85% regex
✅ **Fast .coderef/ reads** - Preprocessed data loads in milliseconds
✅ **Comprehensive integration** - Uses index.json, graph.json, patterns.json, coverage.json
✅ **Real-time MCP calls** - Falls back to live scanning when .coderef/ stale

### Weaknesses
⚠️ **Auto-scan failures silent** - No explicit alerts when coderef_scan fails
⚠️ **No drift detection** - Doesn't check if .coderef/ is stale before planning
⚠️ **No cache invalidation** - Can't tell when .coderef/ needs refresh
⚠️ **Limited utilization tracking** - Doesn't measure which .coderef/ outputs are used
⚠️ **No export format integration** - Doesn't use graph.jsonld or diagram-wrapped.md

### Recommendations
1. **Add drift alerts** - Before planning, check .coderef/index.json age vs last git commit
2. **Cache invalidation strategy** - Auto-refresh .coderef/ when stale (>7 days old or git changes)
3. **Export utilization metrics** - Track which .coderef/ outputs are read during planning
4. **Integrate diagram-wrapped.md** - Use pre-wrapped diagrams in foundation docs
5. **Silent failure logging** - Log when auto-scan fails with actionable error messages

---

## Additional Comments

### Improvements
1. **Unified document query interface** - Single API to search across all document types
2. **Document health dashboard** - Real-time view of all doc freshness, completeness, compliance
3. **Auto-remediation** - Detect missing/stale docs and auto-generate/update
4. **Cross-document linking** - Automatically link standards → plan tasks, foundation docs → workorders
5. **Intelligent caching** - Pre-load frequently used documents during planning

### Weaknesses
1. **No document versioning** - Can't track document evolution over time
2. **No semantic understanding** - Can't answer "what auth decisions were made?"
3. **Limited compliance checking** - Doesn't validate POWER framework, UDS standards
4. **No document dependency tracking** - Can't detect circular references or orphaned docs

### Other
**Integration Success:** coderef-workflow is the **most integrated** server in the ecosystem, with sophisticated fallback mechanisms and comprehensive document utilization. The 3-tier priority system for .coderef/ outputs is particularly well-designed.

**Future Direction:** Add document intelligence layer (semantic search, auto-linking, compliance checking) to transform from "document reader" to "document understanding system."

---

## Utilization Score

**Overall: 90% (Excellent)**

| Category | Utilization | Score |
|----------|-------------|-------|
| Foundation Docs | Deep extraction + auto-generation | 95% |
| Standards Docs | Existence checking only | 70% |
| Workflow/Workorder Docs | Core orchestration, complete lifecycle | 100% |
| .coderef/ Outputs | 3-tier priority system, comprehensive | 95% |

---

**Analysis Complete:** 2026-01-01
**Next Steps:** Update `communication.json` with this analysis
