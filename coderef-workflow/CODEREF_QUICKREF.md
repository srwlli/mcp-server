# @coderef/core Quick Reference for coderef-workflow

**Fast lookup for common integration patterns**

---

## Quick Start: Running a Coderef Scan

```python
from generators.coderef_foundation_generator import CoderefFoundationGenerator
from pathlib import Path

project = Path("/path/to/project")

# Initialize generator
gen = CoderefFoundationGenerator(
    project_path=project,
    use_coderef=True,        # Enable coderef analysis
    deep_extraction=True,    # Deep extraction from docs
    force_regenerate=False   # Use cached results if available
)

# This will:
# 1. Run coderef CLI scan if .coderef/index.json doesn't exist
# 2. Generate ARCHITECTURE.md, SCHEMA.md, COMPONENTS.md, API.md
# 3. Create project-context.json for AI agents
result = gen.generate()

print(f"Generated {result['generated_count']} files")
print(f"Skipped {result['skipped_count']} (already exist)")
```

---

## Accessing Scanned Elements

```python
from generators.coderef_foundation_generator import CoderefFoundationGenerator
from pathlib import Path

gen = CoderefFoundationGenerator(Path("/path/to/project"))

# Load existing coderef data (from .coderef/index.json)
coderef_data = gen._load_coderef_data()

if coderef_data:
    elements = coderef_data['elements']
    graph = coderef_data.get('graph')

    # List all functions
    functions = [e for e in elements if e['type'] == 'function']

    # List all classes
    classes = [e for e in elements if e['type'] == 'class']

    # List React components
    components = [e for e in elements if e['type'] == 'component']

    # Find specific element
    auth_service = next((e for e in elements if e['name'] == 'AuthService'), None)
    if auth_service:
        print(f"Found {auth_service['name']} at {auth_service['file']}:{auth_service['line']}")
else:
    print("No coderef data - run scan first")
```

---

## Working with Discovered Elements

```python
# Structure of ElementData from coderef
element = {
    'type': 'function',           # or 'class', 'component', 'hook', etc.
    'name': 'authenticateUser',
    'file': 'src/services/auth.ts',
    'line': 42,
    'exported': True,
    'parameters': ['username', 'password'],
    'calls': ['validateCredentials', 'hashPassword', 'saveSession']
}

# Check what a function calls
if 'calls' in element:
    print(f"{element['name']} calls: {', '.join(element['calls'])}")

# Find all exported functions
exported_funcs = [e for e in elements if e.get('exported')]

# Find high-impact functions (called by many things)
call_counts = {}
for e in elements:
    for called in e.get('calls', []):
        call_counts[called] = call_counts.get(called, 0) + 1

high_impact = sorted(call_counts.items(), key=lambda x: x[1], reverse=True)[:10]
```

---

## Working with Dependency Graph

```python
# Structure of DependencyGraph (from .coderef/graph.json)
graph = coderef_data['graph']

# Nodes: individual code elements
nodes = graph['nodes']  # List of all discovered elements with positions

# Edges: relationships between elements
edges = graph['edges']  # List of all imports, calls, dependencies

# Find what imports a specific module
module_id = 'src/services/auth.ts'
importers = [e for e in edges
             if e['target'] == module_id and e['type'] == 'import']

# Find all functions called by a specific function
caller_id = 'src/services/auth.ts:authenticateUser'
called_functions = [e['target'] for e in edges
                    if e['source'] == caller_id and e['type'] == 'call']

# Find circular dependencies (performance indicator)
def find_cycles(edges, max_depth=5):
    cycles = []
    for edge in edges:
        # Simple cycle detection via DFS
        if _has_path(edges, edge['target'], edge['source'], max_depth):
            cycles.append((edge['source'], edge['target']))
    return cycles
```

---

## Categorizing Elements

```python
# Built-in categorization from CoderefFoundationGenerator
gen = CoderefFoundationGenerator(project_path)
categorized = gen._categorize_elements(elements)

# Access by category
handlers = categorized['handlers']           # handle_*, on_*
generators = categorized['generators']       # *Generator classes
services = categorized['services']           # *Service classes
middleware = categorized['middleware']       # *Middleware
components = categorized['components']       # React components
utilities = categorized['utilities']         # Helper functions
classes = categorized['classes']             # Remaining classes

# Add custom categorization
custom_categories = {
    'api_handlers': [e for e in elements if e['name'].startswith('api_')],
    'db_models': [e for e in elements if e['name'].endswith('Model')],
    'validators': [e for e in elements if 'validate' in e['name']]
}
```

---

## Pattern Detection

```python
# Code patterns detected by coderef-workflow
patterns = gen._detect_code_patterns()

# Returns dict with:
patterns = {
    'handlers': [{'name': 'handle_auth', 'file': 'src/handlers/auth.py'}, ...],
    'decorators': [{'name': 'app.route', 'count': 12}, ...],
    'error_handling': ['AuthenticationError', 'ValidationError', ...]
}

# Use patterns for documentation
def generate_handler_docs(patterns):
    docs = "# Handlers\n\n"
    for handler in patterns['handlers']:
        docs += f"- `{handler['name']}` ({handler['file']})\n"
    return docs
```

---

## Checking if Coderef is Available

```python
# Safe check before using coderef data
project_path = Path("/path/to/project")
index_path = project_path / '.coderef' / 'index.json'

if index_path.exists():
    # Use AST-accurate data (99% accuracy)
    coderef_data = load_coderef_data()
    elements = coderef_data['elements']
else:
    # Fallback to regex (~85% accuracy)
    elements = detect_elements_with_regex()

# Always works, graceful degradation
```

---

## Common Queries

### Find all public APIs

```python
public_apis = [e for e in elements
               if e.get('exported') and e['type'] == 'function']

for api in public_apis:
    print(f"✓ {api['name']}({', '.join(api.get('parameters', []))})")
    print(f"  @ {api['file']}:{api['line']}")
```

### Find unused functions

```python
# Build reverse call map
called_by = {}
for e in elements:
    for called in e.get('calls', []):
        called_by[called] = called_by.get(called, 0) + 1

# Find functions never called
unused = [e for e in elements
          if e['type'] == 'function' and
          called_by.get(e['name'], 0) == 0]

print(f"Found {len(unused)} potentially unused functions")
```

### Find complex functions

```python
# Estimate complexity by parameter count + call count
def estimate_complexity(element):
    params = len(element.get('parameters', []))
    calls = len(element.get('calls', []))
    return params + calls

complex_funcs = sorted(
    [(e['name'], estimate_complexity(e)) for e in elements],
    key=lambda x: x[1],
    reverse=True
)[:10]

print("Most complex functions:")
for name, complexity in complex_funcs:
    print(f"  {name}: {complexity}")
```

### Find dependencies on external packages

```python
# Look for import statements to node_modules packages
external_deps = set()

for edge in graph['edges']:
    if edge['type'] == 'import' and 'node_modules' in edge.get('metadata', {}).get('source', ''):
        external_deps.add(edge['metadata']['package'])

print(f"Project depends on {len(external_deps)} external packages")
```

---

## Fallback Pattern (When Coderef Unavailable)

```python
def get_elements(project_path, prefer_coderef=True):
    """Get code elements, with automatic fallback."""

    if prefer_coderef:
        coderef_data = try_load_coderef_data(project_path)
        if coderef_data:
            return coderef_data['elements'], 'coderef'

    # Fallback to regex detection
    elements = detect_with_regex(project_path)
    return elements, 'regex'

# Usage
elements, source = get_elements(project_path)
print(f"Loaded {len(elements)} elements from {source}")

if source == 'regex':
    print("⚠ Using regex (~85% accuracy)")
else:
    print("✓ Using AST analysis (99% accuracy)")
```

---

## Configuration

### Enable/Disable Coderef in CoderefFoundationGenerator

```python
# Use coderef for analysis
gen = CoderefFoundationGenerator(
    project_path,
    use_coderef=True  # Enables coderef scanning + pattern detection
)

# Disable coderef (faster, less accurate)
gen = CoderefFoundationGenerator(
    project_path,
    use_coderef=False  # Skip coderef analysis, use regex only
)
```

### Set Coderef CLI Path

```python
import os

# Option 1: Environment variable
os.environ['CODEREF_CLI_PATH'] = r"C:\path\to\coderef\packages\cli"

# Option 2: Hardcoded (edit constants.py if needed)
# DEFAULT_CODEREF_CLI_PATH is in coderef_foundation_generator.py line 27
```

---

## Debugging

### Check if Coderef CLI Works

```bash
# Verify CLI is installed
node <CODEREF_CLI_PATH>/dist/cli.js scan /path/to/project --analyzer ast --json

# You should see JSON output with 'elements' key
```

### Enable Verbose Logging

```python
import logging
from logger_config import logger

logger.setLevel(logging.DEBUG)

# Now run generator - you'll see detailed logs
gen = CoderefFoundationGenerator(project_path)
result = gen.generate()
```

### Check Generated Data

```python
from pathlib import Path
import json

project = Path("/path/to/project")

# Check if index was created
index = project / '.coderef' / 'index.json'
if index.exists():
    data = json.loads(index.read_text())
    print(f"✓ Found {len(data)} elements in index")
else:
    print("✗ No index found - scan may have failed")

# Check graph
graph = project / '.coderef' / 'graph.json'
if graph.exists():
    data = json.loads(graph.read_text())
    print(f"✓ Graph has {len(data['nodes'])} nodes, {len(data['edges'])} edges")
else:
    print("✗ No graph - may not be generated by CLI")
```

---

## Performance Tips

1. **Cache results**: Don't re-run scan if `.coderef/index.json` exists
2. **Use element types**: Trust coderef's element type detection instead of guessing
3. **Lazy load graph**: Only load `graph.json` if you need dependency analysis
4. **Parallel processing**: Categorize elements in parallel if processing large codebases
5. **Incremental updates**: For changed projects, consider re-running scan with `--force-regenerate=True`

---

## See Also

- `CODEREF_INTEGRATION_GUIDE.md` - Detailed integration architecture
- `@coderef/core` guide - Full library documentation
- `.coderef/index.json` - Persisted element index format
- `.coderef/graph.json` - Persisted relationship graph format
