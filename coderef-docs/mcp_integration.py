"""
MCP Integration Helper - Provides guidance for Claude to call coderef-context MCP tools.

Since MCP servers cannot directly call other MCP servers, this module provides:
1. Instructions for Claude to call coderef_scan, coderef_query, etc.
2. Helper functions to format MCP tool call requests
3. Result processors for MCP tool responses
4. Hybrid mode logic (.coderef/ files first, MCP fallback)
5. Response caching to avoid redundant MCP calls

Usage Pattern:
1. coderef-docs tool returns instructions + example MCP calls
2. Claude calls coderef-context MCP tools
3. Claude passes results back to coderef-docs
4. coderef-docs processes results and generates documentation

HYBRID MODE:
- First check if .coderef/index.json exists (fast path, <50ms)
- If missing, suggest Claude call coderef_scan (smart path, ~5-60s)
- Graceful degradation if coderef-context server unavailable

CACHING:
- Session-level cache to avoid redundant MCP calls
- Cache keyed by (tool_name, project_path, params)
- Clear on session end or manual invalidation
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime, timedelta

__all__ = [
    'get_scan_instructions',
    'get_query_instructions',
    'format_scan_request',
    'format_query_request',
    'process_scan_response',
    'process_query_response',
    'check_coderef_cache',
    'get_hybrid_mode_instructions',
    'should_use_mcp_fallback'
]

# Session-level cache for MCP responses
_mcp_response_cache: Dict[str, Dict[str, Any]] = {}
_cache_ttl_seconds = 300  # 5 minutes


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


def check_coderef_cache(project_path: Path) -> Dict[str, Any]:
    """
    Check if .coderef/ cache exists for hybrid mode fast path.

    Args:
        project_path: Absolute path to project directory

    Returns:
        Dict with cache status and instructions
    """
    coderef_dir = Path(project_path) / ".coderef"
    index_file = coderef_dir / "index.json"

    if index_file.exists():
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return {
                'cache_available': True,
                'cache_path': str(index_file),
                'element_count': len(data) if isinstance(data, list) else 0,
                'recommendation': 'Use .coderef/index.json for fast code intelligence (< 50ms)',
                'mcp_fallback': False
            }
        except Exception as e:
            return {
                'cache_available': False,
                'error': f"Cache file exists but failed to read: {str(e)}",
                'recommendation': 'Use MCP fallback',
                'mcp_fallback': True
            }
    else:
        return {
            'cache_available': False,
            'cache_path': 'Not found',
            'recommendation': 'Call coderef_scan to generate .coderef/ data',
            'mcp_fallback': True
        }


def should_use_mcp_fallback(project_path: Path) -> bool:
    """
    Determine if MCP fallback should be used instead of .coderef/ cache.

    Args:
        project_path: Absolute path to project directory

    Returns:
        True if MCP tools should be called, False if cache available
    """
    cache_status = check_coderef_cache(project_path)
    return cache_status['mcp_fallback']


def get_hybrid_mode_instructions(project_path: Path, template_name: str) -> str:
    """
    Generate hybrid mode instructions for Claude based on cache availability.

    Args:
        project_path: Absolute path to project
        template_name: Template being generated (api, schema, components, etc.)

    Returns:
        Formatted instructions string for hybrid mode operation
    """
    cache_status = check_coderef_cache(project_path)

    instructions = "\n=== HYBRID MODE: CODE INTELLIGENCE ===\n\n"

    if cache_status['cache_available']:
        instructions += f"✓ FAST PATH AVAILABLE (.coderef/ cache exists)\n\n"
        instructions += f"Cache: {cache_status['cache_path']}\n"
        instructions += f"Elements: {cache_status['element_count']}\n\n"
        instructions += "INSTRUCTIONS:\n"
        instructions += "1. Read .coderef/index.json for code element data\n"
        instructions += "2. Extract relevant elements based on template type:\n"

        if template_name == 'api':
            instructions += "   - Functions with HTTP decorators (@app.route, @api, etc.)\n"
            instructions += "   - Classes with API patterns (Router, Controller, etc.)\n"
        elif template_name == 'schema':
            instructions += "   - Classes with ORM patterns (Model, Entity, Schema, etc.)\n"
            instructions += "   - Type definitions and interfaces\n"
        elif template_name == 'components':
            instructions += "   - React/Vue components (functional or class-based)\n"
            instructions += "   - Component files matching framework patterns\n"

        instructions += "3. Populate template with extracted data\n"
        instructions += "\nPerformance: < 50ms (file read only)\n"
    else:
        instructions += f"⚠ SMART PATH REQUIRED (.coderef/ cache missing)\n\n"
        instructions += "MCP FALLBACK INSTRUCTIONS:\n"
        instructions += "1. Call coderef_scan to generate .coderef/ data:\n"
        instructions += format_scan_request(Path(project_path))
        instructions += "\n2. After scan completes, .coderef/index.json will be available\n"
        instructions += "3. Read index.json and extract relevant elements\n"
        instructions += "4. Populate template with extracted data\n"
        instructions += "\nPerformance: ~5-60 seconds (one-time scan)\n"
        instructions += "\nGRACEFUL DEGRADATION:\n"
        instructions += "If coderef-context server unavailable:\n"
        instructions += "- Use regex-based detection as fallback\n"
        instructions += "- Populate template with placeholders\n"
        instructions += "- Document that full code intelligence requires coderef-context\n"

    return instructions
