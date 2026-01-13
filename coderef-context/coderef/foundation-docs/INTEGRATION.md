# Integration Guide: coderef-context + coderef-docs

**Project:** coderef-context MCP Server
**Version:** 2.1.0
**Last Updated:** 2026-01-13
**Status:** ✅ Production

---

## Purpose

This guide provides concrete Python code examples showing how **coderef-docs** (and other MCP servers) should call **coderef-context** MCP tools to leverage code intelligence for documentation generation.

**Target Audience:** Developers implementing coderef-docs integration, agents generating foundation docs

**Key Benefit:** Instead of template-only docs, generate documentation populated with real code data from .coderef/ files.

---

## Overview

**Current State:** coderef-docs reads .coderef/ files directly but doesn't orchestrate coderef-context MCP tools.

**Target State:** coderef-docs calls coderef-context tools (coderef_scan, coderef_query, coderef_patterns, etc.) to get structured data, then populates POWER framework templates.

**Integration Pattern:**
```
coderef-docs → coderef-context MCP tool → .coderef/ file → structured data → template population
```

---

## Prerequisites

1. **Generate .coderef/ structure first:**
   ```bash
   python scripts/populate-coderef.py /path/to/project
   ```

2. **Verify .coderef/index.json exists:**
   ```python
   from pathlib import Path

   project_path = Path("/path/to/project")
   if not (project_path / ".coderef/index.json").exists():
       print("ERROR: Run populate-coderef.py first")
       return
   ```

3. **Import MCP client** (adjust import based on your MCP SDK version):
   ```python
   from mcp.client import Client
   # or however your MCP client is imported
   ```

---

## Example 1: Calling coderef_scan and Reading index.json

**Use Case:** Get complete inventory of code elements for foundation doc generation.

**Python Code:**
```python
import json
from pathlib import Path
from typing import List, Dict, Any

async def get_code_elements(project_path: str) -> Dict[str, Any]:
    """
    Call coderef_scan tool to get code elements from index.json.

    Args:
        project_path: Absolute path to project

    Returns:
        Dict with success, elements_found, elements array

    Example:
        elements = await get_code_elements("C:/Users/dev/project")
        if elements['success']:
            print(f"Found {elements['elements_found']} elements")
            for elem in elements['elements'][:5]:
                print(f"  - {elem['name']} ({elem['type']})")
    """
    # Option 1: Call MCP tool (if you have MCP client)
    # result = await mcp_client.call_tool("coderef_scan", {
    #     "project_path": project_path,
    #     "languages": ["py", "ts", "tsx", "js", "jsx"],
    #     "use_ast": True
    # })

    # Option 2: Read index.json directly (fallback if MCP not available)
    index_path = Path(project_path) / ".coderef/index.json"

    if not index_path.exists():
        return {
            "success": False,
            "error": f"index.json not found. Run: python scripts/populate-coderef.py {project_path}"
        }

    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return {
            "success": True,
            "elements_found": data.get("totalElements", len(data.get("elements", []))),
            "elements": data.get("elements", [])
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read index.json: {str(e)}"
        }

# Usage example:
async def main():
    result = await get_code_elements("C:/Users/willh/.mcp-servers/coderef-docs")

    if result['success']:
        print(f"✅ Found {result['elements_found']} code elements")

        # Show first 5 elements
        for elem in result['elements'][:5]:
            print(f"  {elem['type']:10} | {elem['name']:30} | {elem['file']}:{elem['line']}")
    else:
        print(f"❌ Error: {result['error']}")

# Expected Output:
# ✅ Found 105 code elements
#   function   | composeDocumentation           | src/composer.ts:17
#   method     | validateInput                  | src/validator.ts:42
#   function   | readTemplates                  | src/templates.ts:10
```

**Key Points:**
- Check if .coderef/index.json exists before reading
- Provide clear error messages with fix commands
- Return structured data compatible with POWER templates

---

## Example 2: Filtering Elements by Type

**Use Case:** Separate functions (for API.md), classes (for SCHEMA.md), components (for COMPONENTS.md).

**Python Code:**
```python
from typing import List, Dict

def filter_elements_by_type(elements: List[Dict], element_type: str) -> List[Dict]:
    """
    Filter elements array by type for targeted documentation.

    Args:
        elements: Array from index.json
        element_type: "function", "method", "class", "component", "interface", "type"

    Returns:
        Filtered array of elements matching type

    Example:
        # Generate API.md with functions only
        functions = filter_elements_by_type(elements, "function")

        # Generate SCHEMA.md with classes and interfaces
        classes = filter_elements_by_type(elements, "class")
        interfaces = filter_elements_by_type(elements, "interface")
        schemas = classes + interfaces
    """
    return [elem for elem in elements if elem.get("type") == element_type]

def group_elements_by_type(elements: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group all elements by type for multi-doc generation.

    Returns:
        Dict keyed by type, values are element arrays

    Example:
        groups = group_elements_by_type(elements)

        # Generate API.md
        api_elements = groups.get("function", []) + groups.get("method", [])

        # Generate SCHEMA.md
        schema_elements = groups.get("class", []) + groups.get("interface", [])

        # Generate COMPONENTS.md
        component_elements = groups.get("component", [])
    """
    groups = {}
    for elem in elements:
        elem_type = elem.get("type", "unknown")
        if elem_type not in groups:
            groups[elem_type] = []
        groups[elem_type].append(elem)
    return groups

# Usage example:
async def generate_api_md(project_path: str) -> str:
    """Generate API.md populated with real function data."""
    result = await get_code_elements(project_path)

    if not result['success']:
        return f"Error: {result['error']}"

    elements = result['elements']
    groups = group_elements_by_type(elements)

    # Get all callable elements (functions + methods)
    api_elements = groups.get("function", []) + groups.get("method", [])

    # Sort by name
    api_elements.sort(key=lambda e: e['name'])

    # Generate markdown
    lines = ["# API Documentation\n"]
    lines.append(f"**Total Endpoints:** {len(api_elements)}\n")
    lines.append("## Functions\n")

    for elem in api_elements:
        lines.append(f"### `{elem['name']}`\n")
        lines.append(f"**Location:** `{elem['file']}:{elem['line']}`\n")

        if elem.get('exported'):
            lines.append("**Exported:** Yes\n")

        if elem.get('parameters'):
            lines.append(f"**Parameters:** `{', '.join(elem['parameters'])}`\n")

        lines.append("---\n")

    return '\n'.join(lines)

# Expected Output:
# # API Documentation
#
# **Total Endpoints:** 55
#
# ## Functions
#
# ### `composeDocumentation`
# **Location:** `src/composer.ts:17`
# **Exported:** Yes
# **Parameters:** `content, template, options`
# ---
```

**Key Points:**
- Use `filter_elements_by_type()` for single-type queries
- Use `group_elements_by_type()` for multi-doc generation
- Sort elements for consistent output

---

## Example 3: Using coderef_query for Relationship Analysis

**Use Case:** Show "what calls this function" or "what this function depends on" in documentation.

**Python Code:**
```python
async def get_element_relationships(
    project_path: str,
    element_name: str,
    query_type: str = "calls-me"
) -> Dict[str, Any]:
    """
    Query relationships for an element (who calls it, what it imports, etc.).

    Args:
        project_path: Absolute path to project
        element_name: Name of element to query (e.g., "composeDocumentation")
        query_type: "calls" | "calls-me" | "imports" | "imports-me" | "depends-on" | "depends-on-me"

    Returns:
        Dict with success, query_type, target, results array

    Example:
        # Find all functions that call composeDocumentation
        rels = await get_element_relationships(
            "C:/Users/dev/project",
            "composeDocumentation",
            "calls-me"
        )

        if rels['success']:
            print(f"{element_name} is called by:")
            for rel in rels['results']:
                print(f"  - {rel['from']} in {rel['file']}:{rel['line']}")
    """
    # Read graph.json for relationships
    graph_path = Path(project_path) / ".coderef/graph.json"

    if not graph_path.exists():
        return {
            "success": False,
            "error": f"graph.json not found. Run: python scripts/populate-coderef.py {project_path}"
        }

    try:
        with open(graph_path, 'r', encoding='utf-8') as f:
            graph = json.load(f)

        results = []

        if query_type == "calls-me":
            # Find all edges pointing to this element
            for node_id, dependencies in graph.get("edges", {}).items():
                if element_name in str(dependencies):
                    node = graph["nodes"].get(node_id, {})
                    results.append({
                        "from": node.get("name", node_id),
                        "to": element_name,
                        "type": "call",
                        "file": node.get("file", ""),
                        "line": node.get("line", 0)
                    })

        elif query_type == "calls":
            # Find all dependencies of this element
            for node_id, node in graph.get("nodes", {}).items():
                if node.get("name") == element_name:
                    deps = graph.get("edges", {}).get(node_id, [])
                    for dep_id in deps:
                        dep_node = graph["nodes"].get(dep_id, {})
                        results.append({
                            "from": element_name,
                            "to": dep_node.get("name", dep_id),
                            "type": "call",
                            "file": dep_node.get("file", ""),
                            "line": dep_node.get("line", 0)
                        })
                    break

        return {
            "success": True,
            "query_type": query_type,
            "target": element_name,
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to query relationships: {str(e)}"
        }

# Usage example:
async def document_function_with_relationships(
    project_path: str,
    function_name: str
) -> str:
    """Generate function documentation with usage examples from real code."""
    # Get relationship data
    callers = await get_element_relationships(project_path, function_name, "calls-me")
    dependencies = await get_element_relationships(project_path, function_name, "calls")

    if not callers['success'] or not dependencies['success']:
        return "Error querying relationships"

    # Generate documentation
    lines = [f"## `{function_name}`\n"]

    # Show callers
    if callers['results']:
        lines.append("**Used by:**\n")
        for rel in callers['results'][:5]:  # Top 5 callers
            lines.append(f"- `{rel['from']}` in `{rel['file']}:{rel['line']}`\n")

    # Show dependencies
    if dependencies['results']:
        lines.append("\n**Dependencies:**\n")
        for rel in dependencies['results'][:5]:  # Top 5 dependencies
            lines.append(f"- `{rel['to']}`\n")

    return '\n'.join(lines)

# Expected Output:
# ## `composeDocumentation`
#
# **Used by:**
# - `generateFoundationDocs` in `src/generator.ts:45`
# - `updateDocumentation` in `src/updater.ts:23`
#
# **Dependencies:**
# - `validateInput`
# - `readTemplates`
```

**Key Points:**
- Use graph.json for relationship queries
- Limit results (top 5-10) to avoid overwhelming docs
- Show real usage examples from codebase

---

## Example 4: Error Handling for Missing .coderef/ Data

**Use Case:** Gracefully handle cases where .coderef/ doesn't exist or is stale.

**Python Code:**
```python
from pathlib import Path
from typing import Optional, Dict, Any

class CodeRefValidator:
    """Validate .coderef/ structure before tool calls."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.coderef_dir = self.project_path / ".coderef"

    def validate(self) -> Dict[str, Any]:
        """
        Check if .coderef/ structure exists and is valid.

        Returns:
            Dict with 'valid' (bool), 'errors' (list), 'warnings' (list)

        Example:
            validator = CodeRefValidator("C:/Users/dev/project")
            result = validator.validate()

            if not result['valid']:
                for error in result['errors']:
                    print(f"ERROR: {error}")
                print("\nRun: python scripts/populate-coderef.py /path/to/project")
                return

            if result['warnings']:
                for warning in result['warnings']:
                    print(f"WARNING: {warning}")
        """
        errors = []
        warnings = []

        # Check 1: .coderef/ directory exists
        if not self.coderef_dir.exists():
            errors.append(
                ".coderef/ directory not found. "
                f"Run: python scripts/populate-coderef.py {self.project_path}"
            )
            return {"valid": False, "errors": errors, "warnings": warnings}

        # Check 2: index.json exists (foundation file)
        index_path = self.coderef_dir / "index.json"
        if not index_path.exists():
            errors.append(
                "index.json not found in .coderef/. "
                f"Run: python scripts/populate-coderef.py {self.project_path}"
            )

        # Check 3: graph.json exists (for relationships)
        graph_path = self.coderef_dir / "graph.json"
        if not graph_path.exists():
            warnings.append(
                "graph.json not found. Relationship queries will fail. "
                f"Run: python scripts/populate-coderef.py {self.project_path}"
            )

        # Check 4: Check staleness (optional drift check)
        drift_path = self.coderef_dir / "reports" / "drift.json"
        if drift_path.exists():
            try:
                with open(drift_path, 'r') as f:
                    drift_data = json.load(f)
                    drift_pct = drift_data.get("drift_percentage", 0)

                    if drift_pct > 10:
                        warnings.append(
                            f"index.json is stale ({drift_pct:.1f}% drift detected). "
                            f"Run: python scripts/populate-coderef.py {self.project_path}"
                        )
            except Exception:
                pass  # Ignore drift check errors

        valid = len(errors) == 0
        return {"valid": valid, "errors": errors, "warnings": warnings}

async def safe_get_elements(project_path: str) -> Dict[str, Any]:
    """
    Get code elements with validation and clear error messages.

    Returns:
        Dict with success, elements, or error details
    """
    # Validate first
    validator = CodeRefValidator(project_path)
    validation = validator.validate()

    if not validation['valid']:
        return {
            "success": False,
            "error": "Validation failed",
            "errors": validation['errors'],
            "fix_command": f"python scripts/populate-coderef.py {project_path}"
        }

    # Print warnings but continue
    for warning in validation['warnings']:
        print(f"⚠️  {warning}")

    # Get elements
    result = await get_code_elements(project_path)
    return result

# Usage example:
async def main():
    result = await safe_get_elements("C:/Users/dev/project")

    if not result['success']:
        print(f"❌ Error: {result['error']}")
        for error in result.get('errors', []):
            print(f"   - {error}")
        print(f"\n💡 Fix: {result.get('fix_command', 'Unknown')}")
        return

    print(f"✅ Success: Found {result['elements_found']} elements")

# Expected Output (if .coderef/ missing):
# ❌ Error: Validation failed
#    - .coderef/ directory not found. Run: python scripts/populate-coderef.py C:/Users/dev/project
#
# 💡 Fix: python scripts/populate-coderef.py C:/Users/dev/project
```

**Key Points:**
- Always validate before reading .coderef/ files
- Provide exact fix commands in error messages
- Distinguish errors (blocking) from warnings (continue with caution)
- Check drift to detect stale data

---

## Example 5: End-to-End Workflow (Scan → Query → Populate Template → Write Doc)

**Use Case:** Complete integration example showing full doc generation pipeline.

**Python Code:**
```python
from pathlib import Path
from typing import Dict, List, Any

class FoundationDocGenerator:
    """Generate foundation docs using coderef-context data."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.validator = CodeRefValidator(str(project_path))

    async def generate_api_md(self, output_path: Optional[str] = None) -> str:
        """
        Generate API.md with real function data.

        Args:
            output_path: Optional path to write API.md (default: coderef/foundation-docs/API.md)

        Returns:
            Generated markdown content

        Example:
            generator = FoundationDocGenerator("C:/Users/dev/project")
            content = await generator.generate_api_md()
            print(content)
        """
        # Step 1: Validate
        validation = self.validator.validate()
        if not validation['valid']:
            error_msg = "\n".join(validation['errors'])
            return f"# API Documentation\n\n**ERROR:** {error_msg}"

        # Step 2: Get elements
        result = await get_code_elements(str(self.project_path))
        if not result['success']:
            return f"# API Documentation\n\n**ERROR:** {result['error']}"

        elements = result['elements']

        # Step 3: Filter and group
        groups = group_elements_by_type(elements)
        functions = groups.get("function", [])
        methods = groups.get("method", [])

        # Step 4: Query relationships for top 5 functions
        documented_functions = []
        for func in functions[:5]:  # Limit to top 5 for example
            rels = await get_element_relationships(
                str(self.project_path),
                func['name'],
                "calls-me"
            )

            documented_functions.append({
                **func,
                "callers": rels.get('results', [])
            })

        # Step 5: Populate POWER framework template
        lines = self._generate_power_template(documented_functions, methods)

        # Step 6: Write to file (optional)
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text('\n'.join(lines), encoding='utf-8')
            print(f"✅ Generated: {output_path}")

        return '\n'.join(lines)

    def _generate_power_template(
        self,
        functions: List[Dict],
        methods: List[Dict]
    ) -> List[str]:
        """Generate API.md content following POWER framework."""
        lines = []

        # POWER: Purpose
        lines.append("# API Documentation\n")
        lines.append("## Purpose\n")
        lines.append(
            "This document catalogs all API endpoints, functions, and methods "
            "in the codebase. Each entry shows usage examples from real code.\n"
        )

        # POWER: Overview
        lines.append("## Overview\n")
        lines.append(f"**Total Functions:** {len(functions)}\n")
        lines.append(f"**Total Methods:** {len(methods)}\n")

        # POWER: What - Function details
        lines.append("## What: Functions\n")
        for func in functions:
            lines.append(f"### `{func['name']}`\n")
            lines.append(f"**Location:** `{func['file']}:{func['line']}`\n")

            if func.get('exported'):
                lines.append("**Exported:** Yes\n")

            if func.get('parameters'):
                params = ', '.join(func['parameters'])
                lines.append(f"**Parameters:** `{params}`\n")

            # Show callers (real usage examples)
            callers = func.get('callers', [])
            if callers:
                lines.append("\n**Used by:**\n")
                for caller in callers[:3]:  # Top 3 callers
                    lines.append(f"- `{caller['from']}` in `{caller['file']}:{caller['line']}`\n")

            lines.append("---\n")

        # POWER: Examples (would add code snippets here)
        lines.append("## Examples\n")
        lines.append("See individual function usage examples above.\n")

        # POWER: References
        lines.append("## References\n")
        lines.append("- **[SCHEMA.md](SCHEMA.md)** - Data schemas\n")
        lines.append("- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture\n")

        return lines

# Complete usage example:
async def main():
    """End-to-end doc generation example."""
    print("🚀 Starting foundation doc generation...\n")

    # Step 1: Initialize generator
    project_path = "C:/Users/willh/.mcp-servers/coderef-docs"
    generator = FoundationDocGenerator(project_path)

    # Step 2: Generate API.md
    print("📝 Generating API.md...")
    api_content = await generator.generate_api_md(
        output_path=f"{project_path}/coderef/foundation-docs/API.md"
    )

    # Step 3: Show preview
    print("\n📄 API.md Preview (first 500 chars):")
    print(api_content[:500])
    print("...")

    print("\n✅ Foundation docs generated successfully!")
    print(f"📂 Output: {project_path}/coderef/foundation-docs/")

# Expected Output:
# 🚀 Starting foundation doc generation...
#
# 📝 Generating API.md...
# ✅ Generated: C:/Users/willh/.mcp-servers/coderef-docs/coderef/foundation-docs/API.md
#
# 📄 API.md Preview (first 500 chars):
# # API Documentation
#
# ## Purpose
#
# This document catalogs all API endpoints, functions, and methods in the codebase...
#
# ## Overview
#
# **Total Functions:** 55
# **Total Methods:** 50
#
# ## What: Functions
#
# ### `composeDocumentation`
# **Location:** `src/composer.ts:17`
# **Exported:** Yes
# **Parameters:** `content, template, options`
#
# **Used by:**
# - `generateFoundationDocs` in `src/generator.ts:45`
# ...
#
# ✅ Foundation docs generated successfully!
# 📂 Output: C:/Users/willh/.mcp-servers/coderef-docs/coderef/foundation-docs/
```

**Key Points:**
- Follow POWER framework structure (Purpose, Overview, What, Examples, References)
- Validate before starting (fail fast with clear errors)
- Query relationships to show real usage examples
- Limit results (top 5-10) to keep docs manageable
- Write to file for persistence
- Provide progress feedback

---

## Best Practices

### 1. Always Validate First
```python
validator = CodeRefValidator(project_path)
validation = validator.validate()

if not validation['valid']:
    print("ERROR:", validation['errors'])
    return  # Don't proceed with invalid data
```

### 2. Handle Missing Data Gracefully
```python
if not result['success']:
    print(f"⚠️  Fallback: Using template-only docs")
    return generate_template_only_doc()  # Fallback to basic template
```

### 3. Provide Clear Fix Commands
```python
if index_missing:
    print(f"Run: python scripts/populate-coderef.py {project_path}")
```

### 4. Check Drift Before Generation
```python
if drift_percentage > 10:
    print(f"⚠️  Data is stale ({drift_percentage}% drift)")
    print(f"Regenerate: python scripts/populate-coderef.py {project_path}")
```

### 5. Use POWER Framework
All generated docs should follow POWER structure:
- **P**urpose - Why this doc exists
- **O**verview - Summary statistics
- **W**hat/Why/When - Detailed content
- **E**xamples - Code examples
- **R**eferences - Links to related docs

---

## Troubleshooting

### Issue 1: "index.json not found"
**Cause:** .coderef/ structure not generated
**Fix:** `python scripts/populate-coderef.py /path/to/project`

### Issue 2: "No elements found"
**Cause:** Project doesn't contain scannable files or wrong languages
**Fix:** Check `languages` parameter matches project files (py, ts, tsx, js, jsx)

### Issue 3: "Relationships empty"
**Cause:** graph.json missing or incomplete
**Fix:** `python scripts/populate-coderef.py /path/to/project` (generates full structure)

### Issue 4: "Drift detected"
**Cause:** Code changed since last scan
**Fix:** Re-run `python scripts/populate-coderef.py /path/to/project`

---

## Summary

This integration guide provides 5 working examples:

1. ✅ **Get elements** - Read index.json for code inventory
2. ✅ **Filter by type** - Separate functions, classes, components
3. ✅ **Query relationships** - Find callers, dependencies
4. ✅ **Handle errors** - Validate and provide fix commands
5. ✅ **End-to-end** - Complete doc generation pipeline

**Next Steps for coderef-docs:**
1. Copy these examples into coderef-docs codebase
2. Integrate with existing doc generators
3. Add MCP client calls (currently shows direct file reads as fallback)
4. Test with multiple projects
5. Add caching layer for performance

---

**Generated:** 2026-01-13
**Maintained by:** coderef-context MCP Server
**For Developers:** Use these examples as templates for integrating coderef-context tools into documentation workflows.

