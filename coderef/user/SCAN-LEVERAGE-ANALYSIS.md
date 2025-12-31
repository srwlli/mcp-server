# Scan Result Leverage Analysis - How to Use coderef Intelligence

**Document Version:** 1.0.0
**Created:** 2025-12-31
**Purpose:** Analyze how to leverage coderef scan results across all 5 MCP servers
**Status:** Analysis Complete

---

## Executive Summary

**Current State:**
- coderef-context has 11 powerful tools (scan, query, impact, complexity, patterns, coverage, context, validate, drift, diagram, tag)
- Only coderef-docs has scan results (116,233 elements in .coderef/index.json + graph.json)
- Other servers (.coderef/ directories are empty)
- **THE GAP:** We have the tools, but workflows don't leverage them

**The Opportunity:**
Instead of "blind coding," agents can:
- Understand existing architecture before planning
- Discover patterns before reimplementing
- Assess impact before refactoring
- Estimate effort using complexity metrics
- Find reference components before building new

**This document:** Maps exactly how each server should leverage coderef scan results.

---

## Current Scan Capabilities (coderef-context)

### What We Have (11 Tools)

| Tool | What It Does | Output | Use Case |
|------|-------------|--------|----------|
| **scan** | Discover all code elements | JSON array of functions/classes/components | "What exists in this project?" |
| **query** | Trace relationships | Dependency graph | "What calls AuthService?" |
| **impact** | Assess change impact | Affected files + risk level | "What breaks if I refactor X?" |
| **complexity** | Calculate metrics | LOC, CC, dependencies, coverage % | "How complex is this feature?" |
| **patterns** | Find code patterns | Common patterns, anti-patterns | "What patterns exist here?" |
| **coverage** | Test coverage analysis | Coverage % by file | "What's untested?" |
| **context** | Full codebase context | Markdown/JSON comprehensive report | "Give me complete project overview" |
| **validate** | Validate CodeRef2 refs | Valid/invalid counts | "Are references still valid?" |
| **drift** | Detect index drift | Diff between cached and current | "Is my index stale?" |
| **diagram** | Generate diagrams | Mermaid/Graphviz dependency graphs | "Show me architecture visually" |
| **tag** | Add CodeRef2 tags | Tagging results | "Tag all functions/classes" |

### What Gets Saved

When you run `coderef scan`:
```
.coderef/
├── index.json         # 4MB - 116,233 code elements
├── graph.json         # 6.2MB - Dependency relationships
└── reports/           # Analysis reports (optional)
```

**Current Problem:** Only coderef-docs has this data. Other servers don't scan.

---

## Gap Analysis: What We're Missing

### Discovery Gap
**Problem:** Agents start tasks without understanding what exists
**Example:**
```
❌ Current workflow:
User: "Add dark mode toggle"
Agent: "I'll create ThemeProvider, ThemeContext, useTheme hook..."
      [Builds from scratch]
      [Later discovers ThemeProvider already exists]

✅ With scan leverage:
User: "Add dark mode toggle"
Agent: [Calls coderef_scan to see what exists]
      "I found existing ThemeProvider and useTheme hook"
      "I'll extend them instead of rebuilding"
```

### Architecture Gap
**Problem:** Planning happens without understanding existing patterns
**Example:**
```
❌ Current workflow:
/create-workorder → Analysis → Plan
[Analysis is manual - agent reads random files]
[Misses key patterns in other areas]

✅ With scan leverage:
/create-workorder
  → coderef_scan (discover components)
  → coderef_patterns (find existing patterns)
  → coderef_complexity (estimate effort)
  → Analysis with real data
  → Plan with informed decisions
```

### Impact Gap
**Problem:** Refactoring without knowing ripple effects
**Example:**
```
❌ Current workflow:
Agent: "Renaming AuthService..."
      [Breaks 12 files]
      [Discovers breakage during testing]

✅ With scan leverage:
Agent: [Calls coderef_impact before refactoring]
      "12 files depend on AuthService (MEDIUM risk)"
      "Here's the full list: login.ts, signup.ts, ..."
      [Plans comprehensive refactoring upfront]
```

### Pattern Gap
**Problem:** Reimplementing what already exists
**Example:**
```
❌ Current workflow:
Agent: "User wants data fetching. I'll use fetch API..."
      [Builds custom solution]
      [Project already uses React Query everywhere]

✅ With scan leverage:
Agent: [Calls coderef_patterns for "data-fetching"]
      "Found: React Query pattern (23 usages)"
      "I'll follow existing pattern for consistency"
```

---

## Server-by-Server Leverage Strategy

### 1. coderef-workflow (Planning & Orchestration)

**Current State:** Planning is manual, no code intelligence

**Where to Leverage:**

#### Phase 0: Preparation (analyze-for-planning)
```python
# CURRENT (tools/analyze-for-planning.py)
def analyze_project(project_path):
    """Manual file reading, grep, assumptions"""
    return {
        "existing_docs": find_markdown_files(),     # Just file list
        "coding_standards": find_config_files(),   # Just reads configs
        "reference_components": [],                # Empty (guessed)
        "patterns": []                             # Empty (guessed)
    }

# WITH SCAN LEVERAGE
async def analyze_project(project_path):
    """Use coderef intelligence for real analysis"""

    # 1. Discover all code elements
    scan_result = await mcp_client.call_tool("coderef_context", "coderef_scan", {
        "project_path": project_path,
        "use_ast": True
    })

    # 2. Find patterns
    patterns = await mcp_client.call_tool("coderef_context", "coderef_patterns", {
        "project_path": project_path,
        "limit": 10
    })

    # 3. Get architecture overview
    context = await mcp_client.call_tool("coderef_context", "coderef_context", {
        "project_path": project_path,
        "output_format": "json"
    })

    # 4. Identify reference components (most connected)
    # Query graph.json for high-dependency nodes
    reference_components = find_most_connected_components(scan_result, context)

    return {
        "total_elements": len(scan_result["elements"]),        # REAL count
        "components": filter_by_type(scan_result, "component"), # REAL components
        "patterns": patterns["patterns"],                       # REAL patterns
        "reference_components": reference_components,          # REAL references
        "complexity_overview": calculate_avg_complexity(scan_result)
    }
```

**Impact:**
- ✅ Preparation phase takes 30-60 seconds (automated scan) vs 30-60 minutes (manual)
- ✅ Analysis based on real code, not guesses
- ✅ Reference components discovered automatically

#### Section 3: Current State Analysis (in plan.json)
```json
// CURRENT (guessed)
{
  "3_CURRENT_STATE_ANALYSIS": {
    "architecture_summary": "Appears to be React app, not sure of patterns...",
    "key_components": "Unknown, need to investigate...",
    "patterns_in_use": "Will discover during implementation..."
  }
}

// WITH SCAN LEVERAGE (real data)
{
  "3_CURRENT_STATE_ANALYSIS": {
    "architecture_summary": "React app with 247 components, uses React Query for data fetching (23 usages), Redux for state (12 stores)",
    "key_components": [
      "ThemeProvider (imported by 45 components)",
      "AuthService (imported by 23 files)",
      "APIClient (base for all data fetching)"
    ],
    "patterns_in_use": [
      "React Query pattern (data fetching)",
      "HOC pattern (withAuth, withTheme)",
      "Context pattern (5 global contexts)"
    ],
    "complexity_metrics": {
      "average_component_complexity": 6.2,
      "highest_complexity": "CheckoutFlow (CC=15)",
      "test_coverage": "68%"
    }
  }
}
```

**Impact:**
- ✅ Risk assessment based on real data (not guesses)
- ✅ Effort estimation grounded in actual complexity
- ✅ Pattern consistency from day 1

#### Section 2: Risk Assessment (in plan.json)
```python
# WITH SCAN LEVERAGE
async def assess_risk(feature_name, files_to_modify):
    """Real risk assessment using impact analysis"""

    risk_factors = []

    for file in files_to_modify:
        # Get impact for each file
        impact = await mcp_client.call_tool("coderef_context", "coderef_impact", {
            "project_path": project_path,
            "element": extract_element_name(file),
            "operation": "modify"
        })

        if impact["affected_files"] > 10:
            risk_factors.append({
                "file": file,
                "risk": "HIGH",
                "reason": f"Affects {impact['affected_files']} files"
            })

    return {
        "overall_risk": calculate_overall(risk_factors),
        "breaking_changes_likelihood": assess_breaking(risk_factors),
        "mitigation_strategy": generate_mitigation(risk_factors)
    }
```

**Impact:**
- ✅ Risk assessment based on actual dependency graph
- ✅ Breaking change detection before implementation
- ✅ Mitigation strategies tailored to real impact

---

### 2. coderef-docs (Documentation)

**Current State:** Generates docs from templates, not from code

**Where to Leverage:**

#### ARCHITECTURE.md Generation
```python
# CURRENT (generators/foundation_generator.py)
def generate_architecture(project_path):
    """Template-based, requires manual editing"""
    return """
    # Architecture

    ## Components
    [TODO: List main components]

    ## Patterns
    [TODO: Describe patterns]
    """

# WITH SCAN LEVERAGE
async def generate_architecture(project_path):
    """Auto-generate from scan results"""

    # 1. Get all components
    scan = await call_tool("coderef_scan", {"project_path": project_path})

    # 2. Get dependency diagram
    diagram = await call_tool("coderef_diagram", {
        "project_path": project_path,
        "diagram_type": "dependencies",
        "format": "mermaid"
    })

    # 3. Get patterns
    patterns = await call_tool("coderef_patterns", {"project_path": project_path})

    return f"""
    # Architecture

    ## System Overview
    - Total Components: {count_components(scan)}
    - Total Functions: {count_functions(scan)}
    - Test Coverage: {get_coverage()}%

    ## Key Components
    {generate_component_list(scan, top_n=10)}

    ## Dependency Graph
    ```mermaid
    {diagram["mermaid_code"]}
    ```

    ## Patterns in Use
    {format_patterns(patterns)}
    """
```

**Impact:**
- ✅ ARCHITECTURE.md auto-generated from real code
- ✅ Dependency diagrams included automatically
- ✅ Updates reflect actual codebase (not stale docs)

#### SCHEMA.md Generation
```python
# WITH SCAN LEVERAGE
async def generate_schema(project_path):
    """Extract schema from code, not manual entry"""

    # Scan for schema definitions
    scan = await call_tool("coderef_scan", {
        "project_path": project_path,
        "pattern": "**/schema.ts"  # Target schema files
    })

    # Query relationships between schemas
    for schema in extract_schemas(scan):
        relationships = await call_tool("coderef_query", {
            "query_type": "depends-on",
            "target": schema["name"]
        })
        schema["relationships"] = relationships

    return generate_schema_markdown(schemas_with_relationships)
```

**Impact:**
- ✅ Schema docs auto-generated from TypeScript/Zod/etc definitions
- ✅ Relationships discovered automatically
- ✅ Single source of truth (code, not docs)

---

### 3. coderef-personas (Expert Agents)

**Current State:** Personas give advice, but don't have code context

**Where to Leverage:**

#### Ava (Frontend Specialist)
```python
# CURRENT
@persona("ava")
def activate_ava():
    """Frontend expert, but doesn't know project specifics"""
    return {
        "expertise": ["React", "CSS", "UI/UX"],
        "advice": "Use React best practices..."  # Generic
    }

# WITH SCAN LEVERAGE
@persona("ava")
async def activate_ava(project_path):
    """Frontend expert WITH project context"""

    # Scan for UI components
    scan = await call_tool("coderef_scan", {
        "project_path": project_path,
        "languages": ["tsx", "jsx"]
    })

    # Find UI patterns
    patterns = await call_tool("coderef_patterns", {
        "project_path": project_path,
        "pattern_type": "ui_components"
    })

    return {
        "expertise": ["React", "CSS", "UI/UX"],
        "project_context": {
            "total_components": count_components(scan),
            "ui_library": detect_ui_library(patterns),  # "Material-UI" or "Tailwind"
            "state_management": detect_state(patterns), # "Redux" or "Context"
            "patterns_to_follow": extract_patterns(patterns)
        },
        "advice": f"This project uses {ui_library}. Follow the {pattern} pattern for consistency."
    }
```

**Impact:**
- ✅ Ava gives project-specific advice (not generic)
- ✅ Follows existing patterns automatically
- ✅ Recommends consistent styling approach

#### Marcus (Backend Specialist)
```python
# WITH SCAN LEVERAGE
@persona("marcus")
async def activate_marcus(project_path):
    """Backend expert WITH project context"""

    # Scan for API patterns
    patterns = await call_tool("coderef_patterns", {
        "project_path": project_path,
        "pattern_type": "api_endpoints"
    })

    # Find database patterns
    db_patterns = await call_tool("coderef_patterns", {
        "pattern_type": "database"
    })

    return {
        "expertise": ["Node.js", "APIs", "Databases"],
        "project_context": {
            "api_framework": detect_framework(patterns),    # "Express" or "Fastify"
            "database": detect_database(db_patterns),       # "PostgreSQL" or "MongoDB"
            "orm": detect_orm(db_patterns),                 # "Prisma" or "TypeORM"
            "auth_pattern": detect_auth(patterns)           # "JWT" or "Session"
        },
        "advice": f"Use {orm} for database access (project standard). Follow REST pattern for consistency."
    }
```

**Impact:**
- ✅ Marcus recommends tools already in use
- ✅ API design matches existing endpoints
- ✅ Database queries follow project patterns

---

### 4. coderef-testing (Test Automation)

**Current State:** Runs tests, but doesn't guide what to test

**Where to Leverage:**

#### Test Discovery & Prioritization
```python
# CURRENT (just runs pytest)
def run_tests(project_path):
    """Run all tests, no intelligence"""
    subprocess.run(["pytest", project_path])

# WITH SCAN LEVERAGE
async def run_tests_intelligently(project_path, feature_changed):
    """Run tests based on impact analysis"""

    # 1. Find what changed
    affected = await call_tool("coderef_impact", {
        "project_path": project_path,
        "element": feature_changed,
        "operation": "modify"
    })

    # 2. Find related tests
    test_files = find_tests_for_files(affected["affected_files"])

    # 3. Prioritize by risk
    high_risk_tests = [t for t in test_files if is_high_risk(t, affected)]

    # 4. Run high-risk first
    print(f"Running {len(high_risk_tests)} high-risk tests first...")
    subprocess.run(["pytest"] + high_risk_tests)
```

**Impact:**
- ✅ Test only what's affected (faster CI/CD)
- ✅ Prioritize high-risk tests
- ✅ Skip unaffected tests

#### Coverage Gap Detection
```python
# WITH SCAN LEVERAGE
async def detect_coverage_gaps(project_path):
    """Find untested code areas"""

    # 1. Get test coverage
    coverage = await call_tool("coderef_coverage", {
        "project_path": project_path,
        "format": "detailed"
    })

    # 2. Get complexity metrics
    scan = await call_tool("coderef_scan", {"project_path": project_path})

    # 3. Find high-complexity, low-coverage areas (DANGER ZONES)
    gaps = []
    for element in scan["elements"]:
        complexity_result = await call_tool("coderef_complexity", {
            "element": element["name"]
        })

        if complexity_result["cyclomatic_complexity"] > 10 and \
           coverage[element["file"]] < 0.5:
            gaps.append({
                "file": element["file"],
                "function": element["name"],
                "complexity": complexity_result["cyclomatic_complexity"],
                "coverage": coverage[element["file"]],
                "priority": "HIGH"  # High complexity + low coverage = RISK
            })

    return gaps
```

**Impact:**
- ✅ Identify high-risk untested areas
- ✅ Prioritize test writing (highest impact first)
- ✅ Prevent bugs in complex code

---

### 5. coderef-context (Code Intelligence)

**Current State:** Has all the tools, but they're underutilized

**Where to Leverage:**

#### Self-Improvement: Cache & Organize
```python
# NEW: processors/scan_organizer.py
async def organize_scan_results(project_path):
    """Run scan and organize results for easy access"""

    # 1. Run comprehensive scan
    scan = await call_tool("coderef_scan", {
        "project_path": project_path,
        "use_ast": True
    })

    # 2. Copy .coderef/ to visible location
    source = f"{project_path}/.coderef/"
    dest = f"coderef/scans/{project_name}/"

    shutil.copytree(source, dest)

    # 3. Split by domain
    organize_by_domain(dest, scan)
    # Creates:
    #   coderef/scans/{project}/
    #   ├── by-type/
    #   │   ├── functions.json
    #   │   ├── classes.json
    #   │   └── components.json
    #   ├── by-server/
    #   │   ├── coderef-docs/
    #   │   ├── coderef-workflow/
    #   │   └── ...
    #   └── indexes/
    #       ├── by-name.json
    #       └── by-complexity.json

    # 4. Generate quick-reference indexes
    generate_indexes(dest, scan)
```

**Impact:**
- ✅ Scan results visible and organized
- ✅ Easy to query without re-running scan
- ✅ Pre-computed indexes for common queries

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
**Goal:** Get scan results organized and accessible

1. ✅ Document current capabilities (this file)
2. ⏳ Create `processors/scan_organizer.py` in coderef-context
3. ⏳ Create `scripts/organize-scan.py` CLI tool
4. ⏳ Run scan on all 5 servers
5. ⏳ Organize results into `coderef/scans/` structure

**Deliverable:** All 5 servers have organized scan data

### Phase 2: Workflow Integration (Week 2)
**Goal:** Planning uses real code intelligence

1. ⏳ Update `coderef-workflow/generators/analysis_generator.py`
2. ⏳ Add MCP client to call coderef_scan during preparation
3. ⏳ Integrate scan results into Section 3 (Current State Analysis)
4. ⏳ Add impact analysis to Section 2 (Risk Assessment)
5. ⏳ Update plan validation to check for scan usage

**Deliverable:** Plans include real architecture analysis

### Phase 3: Documentation Automation (Week 3)
**Goal:** Docs auto-generate from code

1. ⏳ Update `coderef-docs/generators/foundation_generator.py`
2. ⏳ ARCHITECTURE.md auto-generation from scan
3. ⏳ SCHEMA.md auto-generation from scan
4. ⏳ Dependency diagram inclusion
5. ⏳ Pattern documentation from coderef_patterns

**Deliverable:** Foundation docs generate from real code

### Phase 4: Persona Enhancement (Week 4)
**Goal:** Personas give project-specific advice

1. ⏳ Update all 9 personas with scan integration
2. ⏳ Ava uses UI pattern detection
3. ⏳ Marcus uses API pattern detection
4. ⏳ Quinn uses test coverage analysis
5. ⏳ Each persona activates with project context

**Deliverable:** Personas provide context-aware guidance

### Phase 5: Testing Intelligence (Week 5)
**Goal:** Smart test execution and gap detection

1. ⏳ Update `coderef-testing/runners/pytest_runner.py`
2. ⏳ Impact-based test selection
3. ⏳ Coverage gap detection with complexity
4. ⏳ Test prioritization by risk
5. ⏳ Automated test generation for gaps

**Deliverable:** Test suite runs intelligently

---

## Expected Benefits

### For Planning
- ✅ 30-60 minutes → 30-60 seconds (preparation time)
- ✅ 95%+ accuracy in risk assessment (vs 60% guess-based)
- ✅ Real complexity estimates (vs "probably 2-3 days")

### For Implementation
- ✅ Pattern consistency from day 1
- ✅ Reference components discovered automatically
- ✅ Impact-aware refactoring (no surprise breakage)

### For Documentation
- ✅ Docs auto-generated from code
- ✅ Always up-to-date (generated on demand)
- ✅ Dependency diagrams included

### For Testing
- ✅ Test only what's affected (faster CI)
- ✅ High-risk areas identified automatically
- ✅ Coverage gaps prioritized by complexity

---

## Success Metrics

### Quantitative
- **Scan utilization rate:** 0% → 80%+ (calls per task)
- **Preparation time:** 30-60 min → 30-60 sec
- **Risk assessment accuracy:** 60% → 95%+
- **Doc generation time:** 2-3 hours → 5 minutes
- **Test execution time:** 100% → 30% (impact-based)

### Qualitative
- ✅ Agents discover existing patterns before building new
- ✅ Refactoring happens with full impact awareness
- ✅ Documentation stays synchronized with code
- ✅ Tests focus on high-risk areas

---

## Next Steps

1. **Immediate:** Implement Phase 1 (scan organization)
2. **This Week:** Integrate with coderef-workflow planning
3. **This Month:** Full ecosystem integration
4. **Long Term:** Self-improving scan intelligence

---

## Conclusion

**The Gap:** We built powerful code intelligence tools but don't leverage them in workflows.

**The Solution:** Integrate coderef scan results into every phase:
- Planning → Understand architecture before designing
- Implementation → Follow existing patterns automatically
- Documentation → Generate from real code
- Testing → Test what matters based on impact

**The Impact:** Agents go from "blind coding" to "informed implementation" - reducing rework, increasing consistency, and shipping faster.

---

**Document Status:** ✅ Complete
**Next Step:** Implement Phase 1 (scan organization system)
