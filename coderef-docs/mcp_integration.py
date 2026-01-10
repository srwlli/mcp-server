"""
MCP Integration Helper - Provides guidance for Claude to call coderef-context MCP tools.

Since MCP servers cannot directly call other MCP servers, this module provides:
1. Instructions for Claude to call coderef_scan, coderef_query, etc.
2. Helper functions to format MCP tool call requests
3. Result processors for MCP tool responses

Usage Pattern:
1. coderef-docs tool returns instructions + example MCP calls
2. Claude calls coderef-context MCP tools
3. Claude passes results back to coderef-docs
4. coderef-docs processes results and generates documentation
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

__all__ = [
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
