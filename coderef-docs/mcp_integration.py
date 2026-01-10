"""
.coderef/ Integration Helper - Leverages pre-generated code intelligence files.

NO SCANNING during doc generation - all .coderef/ files must already exist.
If files are missing, warn the user to run scanning first.

Available .coderef/ Resources:
- index.json - All code elements (functions, classes, components)
- context.json - Structured project overview
- context.md - Human-readable project summary
- graph.json - Full dependency graph
- reports/patterns.json - Code patterns and conventions
- reports/coverage.json - Test coverage data
- reports/drift.json - Index drift detection
- reports/validation.json - CodeRef validation results
- diagrams/ - Dependency, call, import diagrams
- exports/ - Various export formats

Template-Specific Context Mapping:
- README: context.md, patterns.json (project overview + conventions)
- ARCHITECTURE: context.json, graph.json, diagrams/ (structure + dependencies)
- API: index.json (filter for endpoints/routes), patterns.json
- SCHEMA: index.json (filter for models/entities), context.json
- COMPONENTS: index.json (filter for UI components), patterns.json

Performance: < 50ms per file read (no MCP calls, no scanning)
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json

__all__ = [
    'check_coderef_resources',
    'get_template_context_files',
    'get_context_instructions',
    'format_missing_resources_warning',
    # Legacy exports (kept for backward compatibility)
    'get_scan_instructions',
    'get_query_instructions',
    'format_scan_request',
    'format_query_request',
    'process_scan_response',
    'process_query_response'
]


def get_scan_instructions(project_path: Path) -> Dict[str, Any]:
    """
    Generate instructions for Claude to call coderef_scan MCP tool.

    Args:
        project_path: Absolute path to project directory

    Returns:
        Dict with instructions, example call, and expected response format
    """
    return {
        'action': 'call_mcp_tool',
        'tool_name': 'coderef_scan',
        'description': 'Scan project to discover code elements (functions, classes, components)',
        'example_call': {
            'project_path': str(project_path),
            'languages': ['ts', 'tsx', 'js', 'jsx', 'py'],
            'use_ast': True
        },
        'expected_response': {
            'elements': 'List[Dict] with name, type, file, line_number',
            'total_count': 'int',
            'scan_time_ms': 'float'
        },
        'next_step': 'Pass scan results to generate_foundation_docs for processing'
    }


def get_query_instructions(
    project_path: Path,
    query_type: str,
    target: str
) -> Dict[str, Any]:
    """
    Generate instructions for Claude to call coderef_query MCP tool.

    Args:
        project_path: Absolute path to project directory
        query_type: Type of query (calls, imports, depends-on, etc.)
        target: Element to query (e.g., 'AuthService')

    Returns:
        Dict with instructions and example call
    """
    return {
        'action': 'call_mcp_tool',
        'tool_name': 'coderef_query',
        'description': f'Query {query_type} relationships for {target}',
        'example_call': {
            'project_path': str(project_path),
            'query_type': query_type,
            'target': target,
            'max_depth': 3
        },
        'expected_response': {
            'relationships': 'List[Dict] with source, target, type',
            'depth': 'int'
        }
    }


def format_scan_request(project_path: Path, languages: Optional[List[str]] = None) -> str:
    """
    Format a ready-to-use coderef_scan MCP tool call instruction for Claude.

    Args:
        project_path: Absolute path to project
        languages: Languages to scan (default: ['ts', 'tsx', 'js', 'jsx', 'py'])

    Returns:
        Formatted instruction string
    """
    if languages is None:
        languages = ['ts', 'tsx', 'js', 'jsx', 'py']

    return f"""
To scan the codebase for code elements, call the coderef_scan MCP tool:

```
mcp__coderef_context__coderef_scan(
    project_path="{project_path}",
    languages={languages},
    use_ast=True
)
```

This will return a list of all functions, classes, and components with their locations.
"""


def format_query_request(
    project_path: Path,
    query_type: str,
    target: str,
    max_depth: int = 3
) -> str:
    """
    Format a ready-to-use coderef_query MCP tool call instruction for Claude.

    Args:
        project_path: Absolute path to project
        query_type: Type of relationship query
        target: Element to query
        max_depth: Maximum traversal depth

    Returns:
        Formatted instruction string
    """
    return f"""
To query {query_type} relationships for '{target}', call the coderef_query MCP tool:

```
mcp__coderef_context__coderef_query(
    project_path="{project_path}",
    query_type="{query_type}",
    target="{target}",
    max_depth={max_depth}
)
```

This will return relationship data for the specified element.
"""


def process_scan_response(response: Dict[str, Any]) -> Dict[str, List[Dict]]:
    """
    Process coderef_scan MCP tool response into categorized elements.

    Args:
        response: Raw response from coderef_scan MCP tool

    Returns:
        Dict with categorized elements (functions, classes, components, etc.)
    """
    elements = response.get('elements', [])

    categorized = {
        'functions': [],
        'classes': [],
        'components': [],
        'interfaces': [],
        'types': [],
        'all': elements
    }

    for elem in elements:
        elem_type = elem.get('type', '').lower()
        if elem_type == 'function':
            categorized['functions'].append(elem)
        elif elem_type == 'class':
            categorized['classes'].append(elem)
        elif elem_type == 'component':
            categorized['components'].append(elem)
        elif elem_type == 'interface':
            categorized['interfaces'].append(elem)
        elif elem_type == 'type':
            categorized['types'].append(elem)

    return categorized


def process_query_response(response: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Process coderef_query MCP tool response into simplified relationship data.

    Args:
        response: Raw response from coderef_query MCP tool

    Returns:
        Dict with simplified relationship lists
    """
    relationships = response.get('relationships', [])

    processed = {
        'callers': [],
        'callees': [],
        'importers': [],
        'imports': [],
        'dependencies': []
    }

    for rel in relationships:
        rel_type = rel.get('type', '').lower()
        source = rel.get('source')
        target = rel.get('target')

        if rel_type == 'calls':
            processed['callees'].append(target)
        elif rel_type == 'called_by':
            processed['callers'].append(source)
        elif rel_type == 'imports':
            processed['imports'].append(target)
        elif rel_type == 'imported_by':
            processed['importers'].append(source)
        elif rel_type == 'depends_on':
            processed['dependencies'].append(target)

    return processed


def check_coderef_resources(project_path: Path) -> Dict[str, Any]:
    """
    Check if .coderef/ resources exist (NO scanning fallback).

    Args:
        project_path: Absolute path to project directory

    Returns:
        Dict with resource status and available files
    """
    coderef_dir = Path(project_path) / ".coderef"

    if not coderef_dir.exists():
        return {
            'resources_available': False,
            'missing': ['.coderef/ directory'],
            'warning': 'Run coderef_scan to generate code intelligence files first'
        }

    # Check for key files
    key_files = {
        'index.json': coderef_dir / "index.json",
        'context.md': coderef_dir / "context.md",
        'context.json': coderef_dir / "context.json",
        'graph.json': coderef_dir / "graph.json",
        'patterns.json': coderef_dir / "reports" / "patterns.json"
    }

    available = {}
    missing = []

    for name, path in key_files.items():
        if path.exists():
            try:
                if path.suffix == '.json':
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    available[name] = {
                        'path': str(path),
                        'size': len(data) if isinstance(data, list) else 'N/A'
                    }
                else:
                    available[name] = {'path': str(path)}
            except Exception as e:
                missing.append(f"{name} (corrupted: {str(e)})")
        else:
            missing.append(name)

    return {
        'resources_available': len(available) > 0,
        'available': available,
        'missing': missing,
        'coderef_dir': str(coderef_dir)
    }


def get_template_context_files(template_name: str) -> List[str]:
    """
    Get list of .coderef/ files needed for specific template.

    Args:
        template_name: Template being generated

    Returns:
        List of .coderef/ filenames to read
    """
    mapping = {
        'readme': ['context.md', 'patterns.json'],
        'architecture': ['context.json', 'graph.json', 'diagrams/'],
        'api': ['index.json', 'patterns.json'],
        'schema': ['index.json', 'context.json'],
        'components': ['index.json', 'patterns.json']
    }

    return mapping.get(template_name, ['index.json'])


def get_context_instructions(project_path: Path, template_name: str) -> str:
    """
    Generate instructions for using .coderef/ files to populate template.

    NO scanning fallback - files must exist or user gets warning.

    Args:
        project_path: Absolute path to project
        template_name: Template being generated

    Returns:
        Formatted instructions string
    """
    resources = check_coderef_resources(project_path)
    context_files = get_template_context_files(template_name)

    instructions = "\n=== CODE INTELLIGENCE (.coderef/) ===\n\n"

    if not resources['resources_available']:
        instructions += "⚠ WARNING: .coderef/ resources not found!\n\n"
        instructions += f"Missing: {', '.join(resources['missing'])}\n\n"
        instructions += "ACTION REQUIRED:\n"
        instructions += "Run coderef_scan to generate code intelligence files:\n"
        instructions += "```\n"
        instructions += f"mcp__coderef_context__coderef_scan(\n"
        instructions += f"    project_path=\"{project_path}\",\n"
        instructions += f"    languages=['ts', 'tsx', 'js', 'jsx', 'py'],\n"
        instructions += f"    use_ast=True\n"
        instructions += f")\n"
        instructions += "```\n\n"
        instructions += "For now, use regex-based detection and placeholders.\n"
        return instructions

    # Resources available
    instructions += f"✓ .coderef/ resources available\n"
    instructions += f"Location: {resources['coderef_dir']}\n\n"

    instructions += f"CONTEXT FILES FOR {template_name.upper()}:\n"
    for file in context_files:
        if file.endswith('/'):
            # Directory
            instructions += f"- {file} (diagram files)\n"
        elif file in resources['available']:
            info = resources['available'][file]
            instructions += f"- {file}"
            if 'size' in info:
                instructions += f" ({info['size']} elements)" if isinstance(info['size'], int) else f" ({info['size']})"
            instructions += f"\n"
        else:
            instructions += f"- {file} (⚠ not found, optional)\n"

    instructions += "\nINSTRUCTIONS:\n"
    instructions += "1. Read the files listed above from .coderef/ directory\n"

    # Template-specific guidance
    if template_name == 'api':
        instructions += "2. From index.json, extract:\n"
        instructions += "   - Functions with HTTP decorators (@app.route, @api, etc.)\n"
        instructions += "   - Classes with API patterns (Router, Controller, etc.)\n"
        instructions += "3. From patterns.json, extract API conventions and patterns\n"
    elif template_name == 'schema':
        instructions += "2. From index.json, extract:\n"
        instructions += "   - Classes with ORM patterns (Model, Entity, Schema, etc.)\n"
        instructions += "   - Type definitions and interfaces\n"
        instructions += "3. From context.json, extract entity relationships\n"
    elif template_name == 'components':
        instructions += "2. From index.json, extract:\n"
        instructions += "   - React/Vue components (functional or class-based)\n"
        instructions += "   - Component files matching framework patterns\n"
        instructions += "3. From patterns.json, extract component conventions\n"
    elif template_name == 'readme':
        instructions += "2. From context.md, extract project overview and summary\n"
        instructions += "3. From patterns.json, extract key conventions and standards\n"
    elif template_name == 'architecture':
        instructions += "2. From context.json, extract system structure\n"
        instructions += "3. From graph.json, extract dependency relationships\n"
        instructions += "4. Reference diagrams/ for visual representations\n"
    else:
        instructions += "2. Extract relevant data based on template purpose\n"

    instructions += "\nPerformance: < 50ms per file (no MCP calls)\n"

    return instructions


def format_missing_resources_warning(missing: List[str]) -> str:
    """
    Format a warning message for missing .coderef/ resources.

    Args:
        missing: List of missing filenames

    Returns:
        Formatted warning string
    """
    warning = "\n⚠ WARNING: Missing .coderef/ Resources\n\n"
    warning += "The following files are required but not found:\n"
    for item in missing:
        warning += f"  - {item}\n"
    warning += "\nACTION REQUIRED:\n"
    warning += "Run coderef_scan to generate these files before generating documentation.\n\n"
    warning += "For now, documentation will use:\n"
    warning += "- Regex-based detection (limited accuracy)\n"
    warning += "- Placeholders for code intelligence\n"
    warning += "\nFor full code intelligence, run scanning first.\n"

    return warning
