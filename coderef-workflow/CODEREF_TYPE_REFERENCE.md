# @coderef/core Type Reference for coderef-workflow

**Complete type definitions and data structure mappings**

---

## Core Data Structures

### ElementData (from @coderef/core scanner)

**TypeScript Definition** (source: `@coderef/core`):
```typescript
export interface ElementData {
  type: 'function' | 'class' | 'component' | 'hook' | 'method' | 'interface' | 'enum' | 'type' | 'unknown';
  name: string;
  file: string;
  line: number;
  exported?: boolean;
  parameters?: string[];
  calls?: string[];
}
```

**Python Type** (coderef-workflow):
```python
from typing import List, Dict, Literal

ElementType = Literal['function', 'class', 'component', 'hook', 'method', 'interface', 'enum', 'type', 'unknown']

class ElementData(TypedDict, total=False):
    type: ElementType
    name: str
    file: str
    line: int
    exported: bool
    parameters: List[str]
    calls: List[str]
```

**Example**:
```json
{
  "type": "function",
  "name": "authenticateUser",
  "file": "src/services/auth.ts",
  "line": 42,
  "exported": true,
  "parameters": ["username", "password"],
  "calls": ["validateCredentials", "hashPassword", "saveSession"]
}
```

**Field Descriptions**:
- `type` - Element kind detected by AST analyzer
- `name` - Identifier (function name, class name, etc.)
- `file` - Normalized file path relative to project root
- `line` - Line number where element is defined (1-based)
- `exported` - Whether element is exported from module
- `parameters` - Function/method parameter names
- `calls` - Functions/methods called by this element

---

### DependencyGraph (from @coderef/core analyzer)

**TypeScript Definition** (source: `@coderef/core`):
```typescript
export interface GraphNode {
  id: string;           // "src/file.ts:elementName"
  type: ElementType;
  file: string;
  line: number;
  metadata?: Record<string, any>;
}

export interface GraphEdge {
  source: string;       // Node ID
  target: string;       // Node ID
  type: 'import' | 'call' | 'dependency';
  metadata?: Record<string, any>;
}

export interface DependencyGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
```

**Python Type** (coderef-workflow):
```python
from typing import List, Dict, Literal

EdgeType = Literal['import', 'call', 'dependency']

class GraphNode(TypedDict, total=False):
    id: str
    type: ElementType
    file: str
    line: int
    metadata: Dict[str, Any]

class GraphEdge(TypedDict, total=False):
    source: str
    target: str
    type: EdgeType
    metadata: Dict[str, Any]

class DependencyGraph(TypedDict):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
```

**Example**:
```json
{
  "nodes": [
    {
      "id": "src/services/auth.ts:authenticateUser",
      "type": "function",
      "file": "src/services/auth.ts",
      "line": 42,
      "metadata": {"exported": true}
    },
    {
      "id": "src/utils/validation.ts:validateCredentials",
      "type": "function",
      "file": "src/utils/validation.ts",
      "line": 15,
      "metadata": {}
    }
  ],
  "edges": [
    {
      "source": "src/services/auth.ts:authenticateUser",
      "target": "src/utils/validation.ts:validateCredentials",
      "type": "call",
      "metadata": {"lineNumber": 45}
    }
  ]
}
```

---

### CoderefData (loaded by coderef-workflow)

**Python Type** (coderef-workflow):
```python
class CoderefData(TypedDict, total=False):
    elements: List[ElementData]
    graph: Optional[DependencyGraph]
```

**Source**: Loaded from `.coderef/index.json` and `.coderef/graph.json`

**Example**:
```python
coderef_data = {
    'elements': [
        {'type': 'function', 'name': 'auth', 'file': 'src/auth.ts', ...},
        {'type': 'class', 'name': 'User', 'file': 'src/models/User.ts', ...}
    ],
    'graph': {
        'nodes': [...],
        'edges': [...]
    }
}
```

---

### Project Context (AI Agent Input)

**Python Type** (coderef-workflow):
```python
class ProjectContext(TypedDict):
    api_context: Dict[str, Any]
    database: Dict[str, Any]
    dependencies: Dict[str, Any]
    activity: Dict[str, Any]
    patterns: Dict[str, Any]
    similar_features: List[Dict[str, Any]]
```

**Structure Generated**:
```json
{
  "api_context": {
    "endpoints": [
      {
        "method": "POST",
        "path": "/auth/login",
        "file": "src/handlers/auth.ts",
        "framework": "Express"
      }
    ],
    "count": 42,
    "frameworks_detected": ["Express", "Fastify"],
    "auth_method": "JWT",
    "error_format": "application/json"
  },
  "database": {
    "type": "postgres",
    "tables": ["users", "sessions", "tokens"],
    "relationships": [
      {"from": "users", "to": "sessions", "type": "one-to-many"}
    ]
  },
  "dependencies": {
    "count": 156,
    "outdated": ["lodash@3.0.0"],
    "vulnerabilities": []
  },
  "activity": {
    "recent_commits": ["feat: auth module", "fix: validation"],
    "active_files": ["src/services/auth.ts", "src/handlers/auth.ts"],
    "contributors": ["alice@example.com", "bob@example.com"]
  },
  "patterns": {
    "handlers": [
      {"name": "handle_auth", "file": "src/handlers/auth.py"}
    ],
    "decorators": [
      {"name": "app.post", "count": 12}
    ],
    "error_handling": ["AuthError", "ValidationError"]
  },
  "similar_features": [
    {
      "name": "user-profile",
      "workorder_id": "WO-USER-PROFILE-001",
      "goal": "Add user profile management"
    }
  ]
}
```

---

### Categorical Elements (from _categorize_elements)

**Python Type**:
```python
class CategorizedElements(TypedDict):
    handlers: List[ElementData]
    generators: List[ElementData]
    services: List[ElementData]
    middleware: List[ElementData]
    components: List[ElementData]
    utilities: List[ElementData]
    classes: List[ElementData]
    functions: List[ElementData]
    all: List[ElementData]
```

**Categorization Rules**:

| Category | Pattern | Example |
|----------|---------|---------|
| `handlers` | `handle_*`, `on_*` | `handle_auth`, `on_message` |
| `generators` | `*Generator` | `DataGenerator`, `ConfigGenerator` |
| `services` | `*Service` | `AuthService`, `UserService` |
| `middleware` | `*Middleware` | `AuthMiddleware`, `LoggingMiddleware` |
| `components` | `type='component'` (coderef detected) | `UserCard`, `LoginForm` |
| `utilities` | Remaining functions | `formatDate`, `parseJSON` |
| `classes` | Remaining classes | `DatabasePool`, `Logger` |

---

## CLI Interface

### Command

```bash
node <CODEREF_CLI_PATH>/dist/cli.js scan <PROJECT_PATH> \
  --lang <LANGUAGES> \
  --analyzer <TYPE> \
  --json
```

### Arguments

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `<PROJECT_PATH>` | Any valid path | N/A (required) | Project directory to scan |
| `--lang` | `ts,tsx,js,jsx,py` | Auto-detected | Comma-separated languages |
| `--analyzer` | `ast`, `regex` | `regex` | Analysis method (ast=99% accurate, regex=85%) |
| `--json` | Flag | N/A (required) | Return JSON format |

### Output Format

```json
{
  "elements": [ElementData, ...],
  "graph": {
    "nodes": [GraphNode, ...],
    "edges": [GraphEdge, ...]
  }
}
```

### Exit Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| 0 | Success | Use elements and graph |
| 1 | CLI error | Check path, permissions |
| 2 | No files found | Check --lang parameter |
| 127 | Node.js not found | Install Node.js |

---

## File Formats

### .coderef/index.json

**Content**: Array of `ElementData` objects

**Structure**:
```json
[
  {
    "type": "function",
    "name": "authenticateUser",
    "file": "src/services/auth.ts",
    "line": 42,
    "exported": true,
    "parameters": ["username", "password"],
    "calls": ["validateCredentials", "hashPassword"]
  },
  // ... more elements
]
```

**Generated by**: `coderef scan` CLI
**Size**: Typically 10-50 KB for medium projects
**Load time**: < 100 ms

---

### .coderef/graph.json

**Content**: `DependencyGraph` object

**Structure**:
```json
{
  "nodes": [
    {
      "id": "src/services/auth.ts:authenticateUser",
      "type": "function",
      "file": "src/services/auth.ts",
      "line": 42,
      "metadata": {"exported": true}
    }
  ],
  "edges": [
    {
      "source": "src/services/auth.ts:authenticateUser",
      "target": "src/utils/validation.ts:validateCredentials",
      "type": "call",
      "metadata": {"lineNumber": 45}
    }
  ]
}
```

**Generated by**: `coderef scan` CLI (optional, if graph analysis enabled)
**Size**: Typically 50-500 KB for medium projects
**Load time**: 100-500 ms

---

### project-context.json (Generated by coderef-workflow)

**Content**: Enhanced project context for AI agents

**Structure**: See "Project Context" section above

**Generated by**: `CoderefFoundationGenerator.generate()`
**Purpose**: Input for AI-based planning and code generation
**Format**: Optimized for LLM consumption (structured, concise)

---

## Type Conversions

### Coderef → Workflow

When loading coderef data, no conversion needed—Python dicts map directly:

```python
# TypeScript ElementData → Python dict
typescript_element = {
    'type': 'function',
    'name': 'getUser',
    'file': 'src/services/user.ts',
    'line': 10,
    'exported': True,
    'parameters': ['id'],
    'calls': ['db.query', 'cache.get']
}

# ↓ No conversion needed
python_element = typescript_element
```

### Element Type Mapping

| @coderef/core | Description | Usage |
|---------------|-------------|-------|
| `function` | Regular function or arrow function | Utility, handler |
| `class` | Class declaration | Service, model |
| `component` | React/Vue component (detected from naming) | UI element |
| `hook` | React hook (detected from `use*` pattern) | React hook |
| `method` | Class method | Service method |
| `interface` | TypeScript interface | Type definition |
| `enum` | TypeScript enum | Constants |
| `type` | TypeScript type alias | Type definition |
| `unknown` | Unable to determine | Error case |

### Edge Type Mapping

| Type | Meaning | Example |
|------|---------|---------|
| `import` | ES6/CommonJS import or require | `import { auth } from './auth.ts'` |
| `call` | Function/method call | `authenticate(user)` |
| `dependency` | Transitive dependency | B depends on A through C |

---

## Query Types (Available from @coderef/core, not yet integrated)

**Note**: Currently not exposed through CLI, but available in @coderef/core library:

```typescript
type QueryType =
  | 'what-calls'          // What calls this element?
  | 'what-calls-me'       // What does this element call?
  | 'what-imports'        // What does this element import?
  | 'what-imports-me'     // What imports this element?
  | 'what-depends-on'     // What does this element depend on?
  | 'what-depends-on-me'  // What depends on this element?
  | 'shortest-path'       // Find shortest path between elements
  | 'all-paths';          // Find all paths between elements
```

**Future integration**: These queries will be exposed for real-time analysis during planning.

---

## Common Type Patterns

### Element Filtering

```python
# Find all exported functions
exported_functions = [
    e for e in elements
    if e['type'] == 'function' and e.get('exported', False)
]

# Find all React components
components = [
    e for e in elements
    if e['type'] == 'component'
]

# Find elements in specific file
auth_elements = [
    e for e in elements
    if e['file'] == 'src/services/auth.ts'
]
```

### Graph Traversal

```python
# Find all calls made by a function
def find_calls(element_id: str, edges: List[GraphEdge]) -> List[str]:
    return [e['target'] for e in edges
            if e['source'] == element_id and e['type'] == 'call']

# Find all functions that import this element
def find_importers(element_file: str, edges: List[GraphEdge]) -> List[str]:
    return [e['source'] for e in edges
            if element_file in e['target'] and e['type'] == 'import']

# Build reverse dependency map
def build_reverse_deps(edges: List[GraphEdge]) -> Dict[str, List[str]]:
    deps = {}
    for edge in edges:
        if edge['type'] in ['call', 'import']:
            target = edge['target']
            deps[target] = deps.get(target, []) + [edge['source']]
    return deps
```

---

## Error Handling

### CLI Errors

```python
import subprocess
import json

try:
    result = subprocess.run(
        ['node', cli_bin, 'scan', str(project_path), '--analyzer', 'ast', '--json'],
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        # Log error
        logger.warning(f"Coderef scan failed: {result.stderr[:200]}")
        # Fallback to regex or empty
        elements = []
    else:
        data = json.loads(result.stdout)
        elements = data.get('elements', [])

except subprocess.TimeoutExpired:
    logger.warning("Coderef scan timed out")
    elements = []
except json.JSONDecodeError:
    logger.warning("Failed to parse coderef output")
    elements = []
except FileNotFoundError:
    logger.warning("Node.js not found")
    elements = []
```

### Data Validation

```python
def validate_element(elem: Dict) -> bool:
    """Validate ElementData structure."""
    required = ['type', 'name', 'file', 'line']
    return all(key in elem for key in required)

def validate_graph(graph: Dict) -> bool:
    """Validate DependencyGraph structure."""
    return 'nodes' in graph and 'edges' in graph

# Usage
for elem in elements:
    if not validate_element(elem):
        logger.warning(f"Invalid element: {elem}")
        continue
```

---

## Performance Characteristics

### Data Sizes

| Metric | Small Project | Medium Project | Large Project |
|--------|---------------|----------------|---------------|
| Element count | 50-200 | 200-2000 | 2000-50000+ |
| index.json size | 5 KB | 20 KB | 200+ KB |
| graph.json size | 10 KB | 100 KB | 1+ MB |
| Load time | < 10 ms | 50-200 ms | 500+ ms |
| Scan time (AST) | 1-5 s | 10-30 s | 60+ s |

### Memory Usage

```python
# Rough estimation for Python dicts
import sys

# Single element
elem = {'type': 'function', 'name': 'test', 'file': 'src/main.ts', 'line': 1}
print(sys.getsizeof(elem))  # ~300 bytes

# For 1000 elements
elements = [elem] * 1000
print(sys.getsizeof(elements) / 1024 / 1024)  # ~0.3 MB
```

---

## See Also

- `CODEREF_INTEGRATION_GUIDE.md` - Architecture and integration flow
- `CODEREF_QUICKREF.md` - Quick examples and patterns
- `@coderef/core` types.ts - Original TypeScript definitions
- `@coderef/core` guide-to-coderef-core.md - Detailed core documentation
