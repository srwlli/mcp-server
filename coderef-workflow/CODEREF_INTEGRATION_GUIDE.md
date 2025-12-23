# @coderef/core Integration Guide

**How coderef-workflow MCPs consume @coderef/core for intelligent project analysis**

---

## Overview

The **coderef-workflow** system uses **@coderef/core** as its analytical backbone. The core library transforms raw codebases into semantic relationship graphs that power intelligent feature planning, context generation, and risk assessment.

### Architecture Diagram

```
User Request (e.g., /coderef-foundation-docs, /gather-context)
    ↓
coderef-workflow MCP (Python server)
    ↓
CoderefFoundationGenerator / PlanningAnalyzer
    ↓
subprocess call → coderef CLI (Node.js wrapper around @coderef/core)
    ↓
@coderef/core (TypeScript library)
    ├── Scanner (AST-based code discovery)
    ├── Analyzer (Dependency graph building)
    ├── Query Engine (Relationship queries)
    └── Context Generator (AI-friendly synthesis)
    ↓
.coderef/index.json + .coderef/graph.json (persisted results)
    ↓
coderef-workflow loads results → generates plans/docs
```

---

## Integration Points

### 1. **Code Discovery via CLI Subprocess**

**Location**: `generators/coderef_foundation_generator.py:343-432`

The workflow triggers coderef scanning by running the CLI as a subprocess:

```python
def _ensure_coderef_index(self) -> bool:
    """Ensure .coderef/index.json exists by running coderef CLI scan if needed."""

    cli_path = os.environ.get("CODEREF_CLI_PATH", DEFAULT_CODEREF_CLI_PATH)
    cli_bin = os.path.join(cli_path, "dist", "cli.js")

    # Build command with AST analyzer (99% accuracy)
    cmd = [
        'node',
        cli_bin,
        'scan',
        str(self.project_path),
        '--lang', lang_arg,           # e.g., "ts,tsx,js,jsx,py"
        '--analyzer', 'ast',          # Use AST (not regex) for precision
        '--json'                      # Return JSON format
    ]

    # Execute scan with 2-minute timeout
    result = subprocess.run(
        cmd,
        cwd=cli_path,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Parse JSON output and save to .coderef/index.json
    scan_result = json.loads(result.stdout)
    elements = scan_result.get('elements', [])
    index_path.write_text(json.dumps(elements, indent=2))

    # Also save relationship graph if available
    if scan_result.get('graph'):
        graph_path.write_text(json.dumps(scan_result['graph'], indent=2))
```

**What gets executed in @coderef/core**:

1. **Scanner module** discovers all code elements (functions, classes, components, hooks)
2. **Analyzer module** builds dependency graph (imports, calls, relationships)
3. **Exporter module** serializes to JSON for consumption

**Output Format**:

```json
{
  "elements": [
    {
      "type": "function|class|component|hook|method|interface|enum|type",
      "name": "elementName",
      "file": "src/services/auth.ts",
      "line": 42,
      "exported": true,
      "parameters": ["user", "password"],
      "calls": ["validateCredentials", "hashPassword"]
    },
    // ... more elements
  ],
  "graph": {
    "nodes": [
      {"id": "src/services/auth.ts:authenticateUser", "type": "function", ...}
    ],
    "edges": [
      {"source": "src/services/auth.ts:authenticateUser", "target": "src/utils/validation.ts:validateEmail"}
    ]
  }
}
```

---

### 2. **Persisted Index Loading**

**Location**: `generators/coderef_foundation_generator.py:304-341`

After initial scan, results are persisted and loaded from disk:

```python
def _load_coderef_data(self) -> Optional[Dict[str, Any]]:
    """Load .coderef/index.json and graph.json if available."""

    index_path = self.project_path / '.coderef' / 'index.json'
    graph_path = self.project_path / '.coderef' / 'graph.json'

    if not index_path.exists():
        return None  # Fallback to regex detection

    # Load element index (99% accurate, AST-derived)
    elements = json.loads(index_path.read_text())

    # Load relationship graph (optional, for analysis)
    graph = None
    if graph_path.exists():
        graph = json.loads(graph_path.read_text())

    return {
        'elements': elements,  # List of discovered code elements
        'graph': graph         # Dependency relationships
    }
```

**Key insight**: Once scanned, workflow doesn't need to re-run expensive analysis. Results are cached in `.coderef/` directory.

---

### 3. **Element Categorization**

**Location**: `generators/coderef_foundation_generator.py:462-520`

The workflow categorizes discovered elements by pattern matching:

```python
def _categorize_elements(self, elements: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize elements from coderef index by architectural role."""

    categories = {
        'handlers': [],      # Functions matching handle_*, on_*
        'generators': [],    # Classes matching *Generator
        'services': [],      # Classes matching *Service
        'middleware': [],    # Classes/functions matching *Middleware
        'components': [],    # React components (from coderef type='component')
        'utilities': [],     # Remaining functions
        'classes': [],       # Remaining classes
    }

    for elem in elements:
        name = elem.get('name', '')
        elem_type = elem.get('type', '')

        # Smart categorization based on naming conventions + coderef type detection
        if name.startswith('handle_') or name.startswith('on_'):
            categories['handlers'].append(elem)
        elif elem_type == 'component':  # Already detected by coderef AST
            categories['components'].append(elem)
        elif name.endswith('Service'):
            categories['services'].append(elem)
        # ... more patterns
```

**Why this matters**: The workflow builds on coderef's accurate element detection (99% from AST) rather than re-implementing its own pattern matching.

---

### 4. **Context Generation for AI Agents**

**Location**: `generators/coderef_foundation_generator.py:222-231`

Coderef data is passed to documentation generators:

```python
def generate(self) -> Dict[str, Any]:
    """Main generation method - orchestrates all operations."""

    # Load coderef data (AST-derived, 99% accurate)
    coderef_data = self._load_coderef_data()
    has_coderef = coderef_data is not None

    # Phase 4: Code pattern detection
    patterns = self._detect_code_patterns() if self.use_coderef else {}

    # Generate docs with coderef context
    content = self._generate_architecture_md(
        project_context,
        existing_docs,
        coderef_data  # ← Pass AST data to generator
    )
```

The generators use coderef element data to:
- Identify critical functions (for ARCHITECTURE.md)
- Detect module boundaries and dependencies
- Generate accurate component hierarchies (COMPONENTS.md)
- Build module dependency diagrams

---

### 5. **Planning Analyzer Integration**

**Location**: `generators/planning_analyzer.py:46-100`

The planning analyzer discovers project structure for implementation plan context:

```python
def analyze(self) -> PreparationSummaryDict:
    """Analyze project for implementation planning preparation."""

    # These scans prepare section 0 of implementation plans
    foundation_docs = self.scan_foundation_docs()
    coding_standards = self.scan_coding_standards()
    reference_components = self.find_reference_components()
    key_patterns = self.identify_patterns()
    technology_stack = self.detect_technology_stack()
    project_structure = self.analyze_project_structure()
    gaps_and_risks = self.identify_gaps_and_risks()

    return PreparationSummaryDict(
        foundation_docs=foundation_docs,
        coding_standards=coding_standards,
        reference_components=reference_components,
        key_patterns_identified=key_patterns,
        technology_stack=technology_stack,
        project_structure=project_structure,
        gaps_and_risks=gaps_and_risks
    )
```

While this analyzer does its own pattern detection (for compatibility with projects without coderef), it's **enhanced** when coderef data is available:
- More accurate component detection
- Better dependency understanding
- Fewer false positives

---

### 6. **Similar Feature Discovery**

**Location**: `generators/coderef_foundation_generator.py:1060-1082`

When planning new features, the workflow discovers similar completed features:

```python
def _discover_similar_features(self) -> List[Dict[str, Any]]:
    """Discover similar features from coderef/archived/."""

    archived_dir = self.project_path / 'coderef' / 'archived'

    for feature_dir in archived_dir.iterdir():
        plan_file = feature_dir / 'plan.json'
        if plan_file.exists():
            data = json.loads(plan_file.read_text())
            similar.append({
                'name': feature_dir.name,
                'workorder_id': data.get('META_DOCUMENTATION', {}).get('workorder_id'),
                'goal': data.get('goal', '')
            })
```

Combined with coderef's relationship analysis, this enables:
- Learning from similar past implementations
- Identifying reusable patterns
- Avoiding duplicate work

---

## Data Flow Diagram

### Scenario: Generate Foundation Docs for Planning

```
[User] → /coderef-foundation-docs
         ↓
    [coderef-workflow MCP]
         ↓
    CoderefFoundationGenerator.generate()
         ├─ Step 1: Check if .coderef/index.json exists
         │  └─ If not, run: node coderef/cli.js scan <path> --analyzer ast --json
         │     ↓
         │     @coderef/core (Scanner + Analyzer modules)
         │     ├─ Discovers elements via AST (99% accuracy)
         │     └─ Builds dependency graph
         │  └─ Save results to .coderef/index.json, .coderef/graph.json
         │
         ├─ Step 2: Load persisted coderef data
         │  └─ elements = index.json
         │  └─ graph = graph.json
         │
         ├─ Step 3: Deep extraction from existing docs
         ├─ Step 4: Auto-detect APIs, Database, Dependencies
         ├─ Step 5: Analyze git activity
         ├─ Step 6: Detect code patterns (handlers, decorators, errors)
         ├─ Step 7: Discover similar features from coderef/archived/
         │
         └─ Step 8: Synthesize project-context.json
            ├─ api_context (from detection + coderef graph)
            ├─ database (entities, relationships)
            ├─ dependencies (count, vulnerabilities)
            ├─ activity (recent commits, active files)
            ├─ patterns (handlers, decorators from AST data)
            ├─ code_patterns (from coderef categorization)
            └─ similar_features (from coderef/archived/)

    [Output] → ARCHITECTURE.md
            → SCHEMA.md
            → COMPONENTS.md (if UI project)
            → project-context.json
            → API.md
```

---

## Type Mappings

### @coderef/core → coderef-workflow

| @coderef/core | coderef-workflow | Usage |
|---------------|------------------|-------|
| `ElementData` | dict with keys `type`, `name`, `file`, `line`, `exported`, `parameters`, `calls` | Discovered code elements |
| `DependencyGraph` | `.coderef/graph.json` structure with `nodes` and `edges` | Relationship analysis |
| `QueryResult` | Not directly used (CLI doesn't expose query API) | Query engine available for future integration |
| `AnalysisResult` | Elements + Graph combined | Full analysis output |

### Scanner Output Format

```typescript
// @coderef/core scanner emits this format:
export interface ElementData {
  type: 'function' | 'class' | 'component' | 'hook' | 'method' | 'interface' | 'enum' | 'type';
  name: string;
  file: string;        // Normalized path
  line: number;        // 1-based
  exported?: boolean;
  parameters?: string[];
  calls?: string[];
}
```

### Graph Output Format

```typescript
// Dependency graph from analyzer:
export interface DependencyGraph {
  nodes: Array<{
    id: string;           // "src/file.ts:functionName"
    type: string;         // Element type
    file: string;
    line: number;
    metadata?: Record<string, any>;
  }>;
  edges: Array<{
    source: string;       // Source node id
    target: string;       // Target node id
    type: 'import' | 'call' | 'dependency';
    metadata?: Record<string, any>;
  }>;
}
```

---

## Key Integration Points for Developers

### When Adding New Tools/Generators to coderef-workflow

1. **Always check for coderef data first**
   ```python
   coderef_data = self._load_coderef_data()
   if coderef_data:
       # Use AST-accurate elements from coderef
       elements = coderef_data['elements']
   else:
       # Fallback to regex detection
       elements = self._detect_elements_with_regex()
   ```

2. **Use coderef element types for categorization**
   ```python
   # Don't guess element type with regex - use what coderef discovered
   if elem.get('type') == 'component':  # Already detected by AST
       categories['components'].append(elem)
   ```

3. **Leverage the dependency graph for impact analysis**
   ```python
   graph = coderef_data.get('graph')
   if graph:
       # Analyze impact of changes using dependency edges
       affected_files = find_dependents(element_id, graph)
   ```

4. **Cache results to avoid re-scanning**
   ```python
   # Check .coderef/ before running subprocess
   if (project_path / '.coderef' / 'index.json').exists():
       # Use cached results (fast, accurate)
       pass
   else:
       # Run expensive CLI scan only if needed
       self._ensure_coderef_index()
   ```

---

## Configuration

### Environment Variable

The CLI path can be configured via environment variable:

```bash
export CODEREF_CLI_PATH="C:\Users\willh\Desktop\projects\coderef-system\packages\cli"
```

Default fallback (hardcoded in `coderef_foundation_generator.py`):
```python
DEFAULT_CODEREF_CLI_PATH = r"C:\Users\willh\Desktop\projects\coderef-system\packages\cli"
```

### Scanner Options

When running coderef CLI scan, the workflow uses:

- `--analyzer ast` - Use AST-based analysis (99% accuracy, slower)
- `--lang ts,tsx,js,jsx,py` - Languages to scan (auto-detected from project)
- `--json` - Return JSON format (required for parsing)

For projects without Node.js, the workflow gracefully falls back to regex detection (~85% accuracy).

---

## Performance Characteristics

### Time Complexity

| Operation | Time | Notes |
|-----------|------|-------|
| Initial scan (CLI) | 10-60s | Depends on project size (per language) |
| Load cached index | <1s | Fast disk read |
| Categorize elements | <100ms | Simple pattern matching on memory data |
| Generate docs | 1-5s | Includes extraction, detection, synthesis |

### Accuracy

| Metric | Regex | AST (@coderef/core) |
|--------|-------|---------------------|
| Element detection | ~85% | 99% |
| False positives | High | Low |
| Type detection | Manual patterns | Automatic from syntax |
| Complex syntax support | Poor | Excellent |

---

## Troubleshooting

### Coderef Index Not Created

**Problem**: `.coderef/index.json` is not created after running `/coderef-foundation-docs`

**Causes**:
1. Node.js not installed (required by coderef CLI)
2. CODEREF_CLI_PATH points to wrong directory
3. Project language not supported (AST fallback to regex)
4. Permission issues writing to `.coderef/`

**Solution**:
```bash
# Verify Node.js installed
node --version

# Verify CLI path
export CODEREF_CLI_PATH="<correct-path>"

# Manually test CLI scan
node <CODEREF_CLI_PATH>/dist/cli.js scan <project> --analyzer ast --json
```

### Low Confidence Scores in Generated Context

**Problem**: Generated `project-context.json` has low confidence scores (e.g., 0.24)

**Reason**: Pattern detection is limited without proper coderef data. Use `--analyzer ast` for better accuracy.

### Regex Fallback Being Used

**Problem**: Logs show "No coderef data found, falling back to regex detection"

**Causes**:
1. CLI scan failed (check logs for error)
2. Project has no Node.js runtime
3. AST analysis not supported for project language

**Mitigation**: System continues with regex (~85% accuracy). Coderef data will be used if available.

---

## Future Integration Opportunities

### 1. **Direct Library Import** (Instead of CLI Subprocess)

Currently, @coderef/core is accessed via CLI subprocess. Future optimization:

```python
# Instead of subprocess.run(cli_bin), directly import and use:
from coderef_core import ContextGenerator, QueryExecutor

context = ContextGenerator()
result = await context.generate(project_path)
```

**Requirements**:
- Bridge module (Python wrapper over Node.js library)
- Type definitions for Python
- Async/await support

### 2. **Real-time Query Engine**

Currently only index/graph are persisted. Future:

```python
query_executor = QueryExecutor(analyzer)

# Real-time relationship queries
callers = query_executor.execute({
    'type': 'what-calls',
    'target': 'authenticateUser'
})

paths = query_executor.execute({
    'type': 'shortest-path',
    'source': 'userLogin',
    'target': 'database.query'
})
```

**Use case**: Risk assessment, impact analysis during planning.

### 3. **Semantic Search with Vector DB**

Integrate ChromaDB/Pinecone support (already in @coderef/core dependencies):

```python
# Find similar functions by semantics, not just name matching
similar = semantic_search(
    query="user authentication",
    embedding_model="openai",
    top_k=5
)
```

**Use case**: Learning from similar past implementations.

### 4. **Drift Detection**

Monitor reference accuracy as code evolves:

```python
drift_report = drift_detector.analyze(
    coderef_tags=['@Fn/auth/login#authenticate:42'],
    current_codebase=project_path
)
# Output: { coderef: "@Fn/...", status: "moved", currentLine: 47 }
```

---

## Summary

**@coderef/core** powers intelligent project understanding in **coderef-workflow** through:

1. **AST-based scanning** - Accurate code element discovery (99%)
2. **Dependency graph analysis** - Understanding relationships and impact
3. **Pattern-based categorization** - Intelligent element grouping
4. **Persistent caching** - Fast subsequent operations
5. **Fallback mechanisms** - Graceful degradation when unavailable

The integration is **subprocess-based** currently but **designed for direct library consumption** in future versions when Python/Node.js interop is improved.
