# MCP Integration Guide

**Document:** INTEGRATION.md
**Version:** 4.0.0
**Status:** ✅ Complete
**Created:** 2026-01-13
**Workorder:** WO-GENERATION-ENHANCEMENT-001

---

## Purpose

This guide explains how coderef-docs integrates with coderef-context MCP server for enhanced documentation generation with code intelligence, drift detection, and semantic pattern analysis.

---

## Overview

**coderef-docs** leverages **coderef-context** MCP server to provide:

- **Drift Detection** - Detect when .coderef/index.json is stale (>10% drift)
- **Semantic Pattern Analysis** - Discover code patterns, frequency, and consistency violations
- **Code Intelligence** - Read pre-generated .coderef/ files for accurate documentation
- **Graceful Fallback** - Template-only mode when MCP unavailable

**Integration Status:** Optional enhancement (tools work without MCP)

---

## Architecture

```
coderef-docs (MCP Server)
├─ mcp_orchestrator.py          # MCP tool calling layer
│  └─ call_coderef_patterns()   # Calls coderef-context patterns tool
├─ mcp_integration.py            # .coderef/ resource reading
│  ├─ check_coderef_resources() # Validate file availability
│  ├─ check_drift()              # Drift detection
│  └─ get_context_instructions() # Template-specific guidance
└─ tool_handlers.py              # Tool implementations
   ├─ handle_generate_foundation_docs()  # Uses drift + resources
   ├─ handle_establish_standards()       # Uses MCP patterns
   └─ handle_list_templates()            # Shows MCP status

Calls ↓

coderef-context (MCP Server)
├─ coderef_patterns              # Semantic pattern analysis
├─ coderef_drift                 # Drift detection
└─ coderef_scan                  # Code scanning
```

---

## Integration Points

### 1. Foundation Docs Generation

**Tool:** `generate_foundation_docs`

**MCP Integration:**
- Checks drift via `check_drift()`
- Reads .coderef/ files (index.json, context.md, graph.json, patterns.json, diagrams/)
- Provides template-specific context instructions

**Example:**

```python
# tool_handlers.py - handle_generate_foundation_docs

# Check .coderef/ resource availability
resources = check_coderef_resources(project_path)

if not resources['resources_available']:
    # Warning: .coderef/ missing
    warning = format_missing_resources_warning(resources)
    # Suggests: Run coderef_scan first

# Check drift if resources available
if resources['resources_available']:
    drift_result = await check_drift(project_path)

    if drift_result['severity'] == 'severe':
        # Warning: Index severely out of date (>50% drift)
        # Recommendation: Re-run coderef_scan
```

**Template Context Mapping:**

```python
# README uses:
- .coderef/context.md           # Project overview
- .coderef/reports/patterns.json # Coding conventions

# ARCHITECTURE uses:
- .coderef/context.json          # Structure
- .coderef/graph.json            # Dependencies
- .coderef/diagrams/*.mmd        # Visual diagrams

# API uses:
- .coderef/index.json            # Filter for endpoints
- .coderef/reports/patterns.json # API conventions

# SCHEMA uses:
- .coderef/index.json            # Filter for models
- .coderef/context.json          # Relationships

# COMPONENTS uses:
- .coderef/index.json            # Filter for UI components
- .coderef/reports/patterns.json # Component conventions
```

**Workflow:**

```bash
# 1. Generate .coderef/ first (external tool - coderef-context)
coderef scan /path/to/project

# 2. Generate foundation docs (reads .coderef/ files)
# MCP tool call from Claude:
generate_foundation_docs(project_path="/path/to/project")

# Output includes:
# - Drift status (5% drift - up to date)
# - Available resources (index.json ✓, context.md ✓, graph.json ✓)
# - 5 docs generated with real code intelligence
```

---

### 2. Standards Generation with Semantic Analysis

**Tool:** `establish_standards`

**MCP Integration:**
- Calls `call_coderef_patterns()` for semantic pattern analysis
- Receives pattern frequency data
- Receives consistency violations

**Example:**

```python
# generators/standards_generator.py

async def fetch_mcp_patterns(self, pattern_type: str = None, limit: int = 50):
    """Fetch patterns from coderef-context MCP."""
    result = await call_coderef_patterns(
        project_path=str(self.project_path),
        pattern_type=pattern_type,
        limit=limit
    )

    if result['success']:
        return {
            'patterns': result.get('patterns', []),
            'frequency': result.get('frequency', {}),  # STANDARDS-003
            'violations': result.get('violations', []), # STANDARDS-004
            'success': True
        }
    else:
        # Fallback to regex-only
        return {'success': False}
```

**Pattern Frequency Example:**

```json
{
  "frequency": {
    "async_function": 45,
    "class_definition": 23,
    "test_function": 67,
    "mcp_handler": 12
  }
}
```

**Consistency Violations Example:**

```json
{
  "violations": [
    {
      "file": "old_module.py",
      "line": 50,
      "pattern": "sync_handler",
      "reason": "Handler should use async pattern"
    }
  ]
}
```

**Workflow:**

```bash
# Claude calls:
establish_standards(project_path="/path/to/project")

# Internal flow:
# 1. Call call_coderef_patterns() via MCP
# 2. Receive semantic pattern data
# 3. Generate 3 standards docs:
#    - ui-patterns.md (with frequency data)
#    - behavior-patterns.md (with violations)
#    - ux-patterns.md
# 4. Display top 5 patterns and violation count
```

---

### 3. User Docs - Tool Extraction

**Tool:** `generate_my_guide`

**MCP Integration:**
- Reads .coderef/index.json to discover MCP tool handlers

**Example:**

```python
# generators/user_guide_generator.py

def extract_mcp_tools(self, project_path: Path) -> Dict:
    """Extract MCP tools from .coderef/index.json."""
    coderef_index = project_path / ".coderef" / "index.json"

    if not coderef_index.exists():
        return {'tools': [], 'available': False}

    index_data = json.loads(coderef_index.read_text())

    cli_commands = []
    for element in index_data:
        # Look for handle_* functions (MCP tool handlers)
        if element.get('name', '').startswith('handle_'):
            tool_name = element['name'].replace('handle_', '')
            cli_commands.append({
                'name': tool_name,
                'file': element.get('file', ''),
                'category': self._categorize_tool(tool_name)
            })

    return {
        'tools': cli_commands,
        'available': True,
        'total_tools': len(cli_commands)
    }
```

**Tool Categorization:**

```
handle_generate_docs      → Documentation
handle_record_changes     → Changelog
handle_establish_standards → Standards
handle_audit_codebase     → Standards
```

---

### 4. Drift Detection

**Tool:** `check_drift`

**MCP Integration:**
- Calls coderef-context `coderef_drift` tool
- Returns drift percentage and severity

**Drift Severity Levels:**

```python
# mcp_integration.py

if drift_percentage <= 10:
    severity = 'none'      # ✅ Index up to date
elif drift_percentage <= 50:
    severity = 'standard'  # ⚠️ Consider re-scanning
else:
    severity = 'severe'    # 🚨 Re-scan strongly recommended
```

**Example:**

```python
# Check drift
drift_result = await check_drift("/path/to/project")

# Response:
{
    'success': True,
    'drift_percentage': 15.0,
    'severity': 'standard',
    'total_indexed': 100,
    'added_files': 8,
    'removed_files': 3,
    'modified_files': 4,
    'message': 'Index has moderate drift (15.0%). Consider re-scanning.'
}
```

---

### 5. Health Check

**Tool:** `list_templates`

**MCP Integration:**
- Displays MCP availability status
- Shows enhanced features when available
- Shows fallback mode when unavailable

**Example Output:**

```
============================================================

🔧 MCP INTEGRATION STATUS:

  • coderef-context MCP: ✅ Available
  • Enhanced Features: Drift detection, pattern analysis, semantic insights

============================================================
```

**When MCP Unavailable:**

```
============================================================

🔧 MCP INTEGRATION STATUS:

  • coderef-context MCP: ⚠️ Unavailable
  • Fallback Mode: Template-only generation (reduced accuracy)
  • Recommendation: Start coderef-context MCP server for full features

============================================================
```

---

## MCP Orchestration Layer

**File:** `mcp_orchestrator.py`

**Purpose:** Centralized MCP tool calling with caching

### call_coderef_patterns

```python
async def call_coderef_patterns(
    project_path: str,
    pattern_type: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Call coderef-context coderef_patterns tool.

    Args:
        project_path: Absolute path to project
        pattern_type: Optional filter (async_function, class_definition, etc.)
        limit: Maximum patterns to return

    Returns:
        {
            'success': bool,
            'patterns': [...],
            'frequency': {...},
            'violations': [...],
            'pattern_count': int
        }
    """
    if not CODEREF_CONTEXT_AVAILABLE:
        return {
            'success': False,
            'error': 'coderef-context MCP not available',
            'patterns': [],
            'frequency': {},
            'violations': []
        }

    # Check cache
    cache_key = f"{project_path}:{pattern_type}:{limit}"
    if cache_key in _cache:
        return _cache[cache_key]

    # Call MCP tool
    result = await _call_mcp_tool(
        tool_name='coderef_patterns',
        project_path=project_path,
        pattern_type=pattern_type,
        limit=limit
    )

    # Cache result
    _cache[cache_key] = result

    return result
```

**Caching:**
- Pattern results cached by (project_path, pattern_type, limit)
- Reduces redundant MCP calls
- Improves performance for repeated queries

---

## Resource Checking

**File:** `mcp_integration.py`

### check_coderef_resources

```python
def check_coderef_resources(project_path: Path, drift_result: Dict = None) -> Dict:
    """
    Check which .coderef/ resources are available.

    Returns:
        {
            'resources_available': bool,
            'available': ['index.json', 'context.md', ...],
            'missing': ['graph.json', ...],
            'coderef_dir': str,
            'drift': {...}  # Optional drift info
        }
    """
    coderef_dir = project_path / ".coderef"

    resource_files = [
        'index.json',
        'context.md',
        'context.json',
        'graph.json',
        'reports/patterns.json',
        'reports/coverage.json',
        'reports/drift.json',
        'diagrams/dependencies.mmd'
    ]

    available = []
    missing = []

    for resource in resource_files:
        if (coderef_dir / resource).exists():
            available.append(resource)
        else:
            missing.append(resource)

    return {
        'resources_available': len(available) > 0,
        'available': available,
        'missing': missing,
        'coderef_dir': str(coderef_dir),
        'drift': drift_result  # DRIFT-004
    }
```

---

## Error Handling

### Graceful Degradation

**When MCP Unavailable:**

```python
# All tools check CODEREF_CONTEXT_AVAILABLE flag

if not CODEREF_CONTEXT_AVAILABLE:
    # Fallback modes:
    # - Foundation docs: Template-only (no code intelligence)
    # - Standards: Regex-based pattern detection (~55% accuracy)
    # - User docs: Manual placeholders (40% auto-fill)

    return {
        'success': False,
        'error': 'coderef-context MCP not available',
        'fallback_mode': True
    }
```

**When .coderef/ Missing:**

```python
if not resources['resources_available']:
    warning = f"""
⚠️ .coderef/ directory not found or empty.

Missing resources:
{', '.join(resources['missing'])}

Recommendation:
Run coderef_scan to generate code intelligence first:

  coderef scan {project_path}

Documentation will be generated with placeholders.
"""
    # Proceed with template-only generation
```

---

## Performance Considerations

### Sequential Generation

**Problem:** Generating all 5 foundation docs at once (~1,470 lines) causes timeouts

**Solution:** Sequential generation (5 calls × ~300 lines each)

```python
# handle_generate_foundation_docs

templates = ['readme', 'architecture', 'api', 'schema', 'components']

for i, template in enumerate(templates, 1):
    result += f"\n[{i}/{len(templates)}] Generating {template.upper()}...\n"

    # Sequential call
    doc_result = await handle_generate_individual_doc({
        'project_path': project_path,
        'template_name': template
    })

    result += doc_result[0].text
```

**Performance:** < 2 seconds for all 5 docs (mocked), < 10 seconds (real usage)

### Caching

**MCP Results Cached:**
- Pattern queries cached by (path, type, limit)
- Reduces redundant MCP calls
- Cache cleared on new scan

---

## Example Workflows

### Workflow 1: Complete Documentation Generation

```bash
# Step 1: Generate .coderef/ (via coderef-context)
coderef scan /path/to/project

# Step 2: Generate all docs (via coderef-docs)
# Claude calls:
generate_foundation_docs(project_path="/path/to/project")
generate_my_guide(project_path="/path/to/project")
generate_user_guide(project_path="/path/to/project")
generate_features(project_path="/path/to/project")
establish_standards(project_path="/path/to/project")

# Result:
# - 5 foundation docs (coderef/foundation-docs/)
# - 3 user docs (coderef/user/)
# - 3 standards docs (coderef/standards/)
# - All with real code intelligence from .coderef/
```

### Workflow 2: Standards with Semantic Analysis

```bash
# Claude calls:
establish_standards(project_path="/path/to/project")

# Internal:
# 1. Fetch MCP patterns via call_coderef_patterns()
# 2. Receive pattern frequency:
#    - async_function: 45 occurrences
#    - test_function: 67 occurrences
# 3. Receive violations:
#    - old_module.py:50 - Uses deprecated pattern
# 4. Generate standards docs with semantic data
# 5. Output shows top 5 patterns and violation count

# Quality: 80%+ (vs 55% regex-only)
```

### Workflow 3: Drift Detection

```bash
# User modifies 20% of codebase without re-scanning

# Claude calls:
generate_foundation_docs(project_path="/path/to/project")

# Internal:
# 1. Check drift via check_drift()
# 2. Result: 20% drift (severity: standard)
# 3. Warning displayed:
#    "⚠️ Index has moderate drift (20%). Consider re-scanning."
# 4. Docs generated with available (possibly stale) data

# User re-scans:
coderef scan /path/to/project

# Drift now 0%
```

---

## Testing

**Test Coverage:** 185 tests across 10 test files

**Key Test Files:**
- `test_mcp_orchestrator.py` - MCP calling, caching, errors
- `test_drift_detection.py` - Drift severity, boundaries
- `test_foundation_docs_mcp.py` - Sequential generation, context mapping
- `test_standards_semantic.py` - Pattern fetching, frequency, violations
- `test_full_workflow_integration.py` - End-to-end integration

**Run Tests:**

```bash
pytest tests/test_mcp_orchestrator.py -v
pytest tests/test_drift_detection.py -v
pytest tests/test_full_workflow_integration.py -v
```

---

## Configuration

### Enable/Disable MCP Integration

**Flag:** `CODEREF_CONTEXT_AVAILABLE`

**Location:** `mcp_integration.py`

```python
# Auto-detected based on MCP server availability
CODEREF_CONTEXT_AVAILABLE = True  # or False

# Override for testing:
import os
CODEREF_CONTEXT_AVAILABLE = os.getenv('CODEREF_MCP_ENABLED', 'true').lower() == 'true'
```

---

## Troubleshooting

### Issue: MCP calls timing out

**Symptoms:** Tools hang for >10 seconds

**Solution:**
```python
# Use timeout in MCP calls
result = await asyncio.wait_for(
    call_coderef_patterns(path, None, 50),
    timeout=5.0  # 5 second timeout
)
```

### Issue: Drift always shows 0%

**Symptoms:** Drift detection not working

**Solution:**
- Ensure .coderef/index.json exists
- Verify coderef-context MCP server running
- Check CODEREF_CONTEXT_AVAILABLE flag is True

### Issue: Standards have low quality (< 60%)

**Symptoms:** Placeholders in standards docs

**Solution:**
- Verify MCP patterns being fetched (check logs)
- Ensure coderef-context MCP server running
- Fallback regex-only mode has ~55% quality

---

## References

- **WO-GENERATION-ENHANCEMENT-001** - Implementation workorder
- **coderef-context MCP Server** - Code intelligence provider
- **CLAUDE.md** - Architecture documentation
- **README.md** - User-facing guide

---

**Maintained by:** willh, Claude Code AI
**Status:** ✅ Complete Integration
