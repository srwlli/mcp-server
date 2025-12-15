"""
Mermaid Diagram Formatter - Generate Mermaid diagrams from coderef graph.json.

Provides utilities for:
- Module dependency diagrams
- Element-focused diagrams
- Graph metrics computation
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

__all__ = [
    'generate_module_diagram',
    'generate_element_diagram',
    'compute_graph_metrics',
    'get_high_impact_elements'
]


def generate_module_diagram(graph: Dict, max_depth: int = 2, max_nodes: int = 20) -> str:
    """
    Generate Mermaid diagram showing module-level dependencies.

    Args:
        graph: Graph data from graph.json
        max_depth: Maximum depth of dependencies to show (default: 2)
        max_nodes: Maximum number of nodes to include (default: 20)

    Returns:
        Mermaid diagram string (graph TB format)
    """
    if not graph:
        return '```mermaid\ngraph TB\n    empty[No graph data available]\n```'

    # Extract nodes and edges
    nodes = _parse_nodes(graph)
    edges = _parse_edges(graph)

    if not nodes:
        return '```mermaid\ngraph TB\n    empty[No elements found]\n```'

    # Group nodes by file/module
    modules = _group_by_module(nodes)

    # Build module-level edges
    module_edges = _build_module_edges(edges, nodes)

    # Generate Mermaid
    lines = ['```mermaid', 'graph TB']

    # Add subgraphs for each module (limit to max_nodes)
    module_list = list(modules.items())[:max_nodes]

    for module_name, module_nodes in module_list:
        safe_name = _sanitize_id(module_name)
        display_name = module_name.replace('_', ' ').title()

        if len(module_nodes) > 1:
            lines.append(f'    subgraph {safe_name}["{display_name}"]')
            for node in module_nodes[:5]:  # Limit nodes per module
                node_id = _sanitize_id(node.get('id', node.get('name', '')))
                node_name = node.get('name', 'unknown')
                lines.append(f'        {node_id}[{node_name}]')
            lines.append('    end')
        else:
            node = module_nodes[0]
            node_id = _sanitize_id(node.get('id', node.get('name', '')))
            lines.append(f'    {node_id}["{display_name}"]')

    # Add module-level edges
    added_edges = set()
    for source_mod, target_mod in list(module_edges)[:30]:  # Limit edges
        if source_mod != target_mod:
            edge_key = f"{source_mod}->{target_mod}"
            if edge_key not in added_edges:
                source_id = _sanitize_id(source_mod)
                target_id = _sanitize_id(target_mod)
                lines.append(f'    {source_id} --> {target_id}')
                added_edges.add(edge_key)

    lines.append('```')
    return '\n'.join(lines)


def generate_element_diagram(graph: Dict, element_id: str, depth: int = 1) -> str:
    """
    Generate focused Mermaid diagram for a single element.

    Shows the element's callers (incoming) and callees (outgoing).

    Args:
        graph: Graph data from graph.json
        element_id: The element's ID to focus on
        depth: How many levels of relationships to show (default: 1)

    Returns:
        Mermaid diagram string
    """
    if not graph:
        return '```mermaid\ngraph LR\n    empty[No graph data]\n```'

    nodes = _parse_nodes(graph)
    edges = _parse_edges(graph)

    # Find element node
    element_node = None
    for node in nodes:
        if node.get('id') == element_id or node.get('name') == element_id:
            element_node = node
            break

    if not element_node:
        return f'```mermaid\ngraph LR\n    notfound[Element {element_id} not found]\n```'

    # Find callers and callees
    callers = []
    callees = []

    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')

        if target == element_id:
            callers.append(source)
        elif source == element_id:
            callees.append(target)

    # Generate Mermaid
    lines = ['```mermaid', 'graph LR']

    # Add callers (left side)
    for caller in callers[:5]:
        caller_id = _sanitize_id(caller)
        lines.append(f'    {caller_id}[{_get_short_name(caller)}] --> center')

    # Center element
    center_id = _sanitize_id(element_id)
    center_name = element_node.get('name', element_id)
    lines.append(f'    center["{center_name}"]')

    # Add callees (right side)
    for callee in callees[:5]:
        callee_id = _sanitize_id(callee)
        lines.append(f'    center --> {callee_id}[{_get_short_name(callee)}]')

    # Style the center node
    lines.append(f'    style center fill:#f9f,stroke:#333,stroke-width:2px')

    lines.append('```')
    return '\n'.join(lines)


def compute_graph_metrics(graph: Dict) -> Dict[str, Any]:
    """
    Calculate graph metrics: density, circularity, degree distribution.

    Args:
        graph: Graph data from graph.json

    Returns:
        Dict with metrics:
        - node_count: Total nodes
        - edge_count: Total edges
        - density: Edge density (edges / possible edges)
        - circular_dependencies: List of circular dependency chains
        - isolated_nodes: Nodes with no connections
        - avg_in_degree: Average incoming edges per node
        - avg_out_degree: Average outgoing edges per node
    """
    if not graph:
        return {
            'node_count': 0,
            'edge_count': 0,
            'density': 0.0,
            'circular_dependencies': [],
            'isolated_nodes': [],
            'avg_in_degree': 0.0,
            'avg_out_degree': 0.0
        }

    nodes = _parse_nodes(graph)
    edges = _parse_edges(graph)

    node_count = len(nodes)
    edge_count = len(edges)

    # Calculate density
    max_edges = node_count * (node_count - 1) if node_count > 1 else 1
    density = round(edge_count / max_edges, 3) if max_edges > 0 else 0.0

    # Calculate degrees
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    node_ids = {n.get('id', n.get('name', '')) for n in nodes}

    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        out_degree[source] += 1
        in_degree[target] += 1

    # Find isolated nodes
    isolated = []
    for node in nodes:
        node_id = node.get('id', node.get('name', ''))
        if in_degree[node_id] == 0 and out_degree[node_id] == 0:
            isolated.append(node.get('name', node_id))

    # Calculate averages
    avg_in = round(sum(in_degree.values()) / node_count, 2) if node_count > 0 else 0.0
    avg_out = round(sum(out_degree.values()) / node_count, 2) if node_count > 0 else 0.0

    # Detect circular dependencies (simplified - direct cycles only)
    circular = _detect_direct_cycles(edges)

    return {
        'node_count': node_count,
        'edge_count': edge_count,
        'density': density,
        'circular_dependencies': circular[:10],  # Limit to 10
        'isolated_nodes': isolated[:20],  # Limit to 20
        'avg_in_degree': avg_in,
        'avg_out_degree': avg_out
    }


def get_high_impact_elements(graph: Dict, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get elements with the most dependents (high impact on codebase).

    Args:
        graph: Graph data from graph.json
        limit: Maximum number of elements to return (default: 10)

    Returns:
        List of dicts with:
        - name: Element name
        - id: Element ID
        - dependents: Count of elements that depend on this
        - dependencies: Count of elements this depends on
        - risk: HIGH (>15 dependents), MEDIUM (>5), LOW (<=5)
    """
    if not graph:
        return []

    nodes = _parse_nodes(graph)
    edges = _parse_edges(graph)

    # Count incoming edges (dependents)
    dependents_count = defaultdict(int)
    dependencies_count = defaultdict(int)

    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        dependents_count[target] += 1
        dependencies_count[source] += 1

    # Build result list
    results = []
    for node in nodes:
        node_id = node.get('id', node.get('name', ''))
        node_name = node.get('name', node_id)
        deps = dependents_count.get(node_id, 0)

        if deps > 0:  # Only include nodes with dependents
            risk = 'HIGH' if deps > 15 else ('MEDIUM' if deps > 5 else 'LOW')
            results.append({
                'name': node_name,
                'id': node_id,
                'file': node.get('file', ''),
                'dependents': deps,
                'dependencies': dependencies_count.get(node_id, 0),
                'risk': risk
            })

    # Sort by dependents descending
    results.sort(key=lambda x: x['dependents'], reverse=True)
    return results[:limit]


# --- Helper Functions ---

def _parse_nodes(graph: Dict) -> List[Dict]:
    """Parse nodes from graph.json format."""
    nodes = graph.get('nodes', [])
    result = []

    for node_entry in nodes:
        if isinstance(node_entry, list) and len(node_entry) >= 2:
            # Format: [nodeId, nodeData]
            result.append(node_entry[1])
        elif isinstance(node_entry, dict):
            result.append(node_entry)

    return result


def _parse_edges(graph: Dict) -> List[Dict]:
    """Parse edges from graph.json format."""
    edges = graph.get('edges', [])
    result = []

    for edge_entry in edges:
        if isinstance(edge_entry, list) and len(edge_entry) >= 2:
            # Format: [edgeId, edgeData]
            result.append(edge_entry[1])
        elif isinstance(edge_entry, dict):
            result.append(edge_entry)

    return result


def _group_by_module(nodes: List[Dict]) -> Dict[str, List[Dict]]:
    """Group nodes by their file/module."""
    modules = defaultdict(list)

    for node in nodes:
        file_path = node.get('file', 'unknown')
        # Extract module name from file path
        if '/' in file_path:
            module = file_path.rsplit('/', 1)[-1].replace('.py', '').replace('.ts', '').replace('.js', '')
        elif '\\' in file_path:
            module = file_path.rsplit('\\', 1)[-1].replace('.py', '').replace('.ts', '').replace('.js', '')
        else:
            module = file_path.replace('.py', '').replace('.ts', '').replace('.js', '')

        modules[module].append(node)

    return dict(modules)


def _build_module_edges(edges: List[Dict], nodes: List[Dict]) -> Set[Tuple[str, str]]:
    """Build module-level edges from element edges."""
    # Create node -> module mapping
    node_to_module = {}
    for node in nodes:
        node_id = node.get('id', node.get('name', ''))
        file_path = node.get('file', 'unknown')

        if '/' in file_path:
            module = file_path.rsplit('/', 1)[-1].replace('.py', '').replace('.ts', '').replace('.js', '')
        elif '\\' in file_path:
            module = file_path.rsplit('\\', 1)[-1].replace('.py', '').replace('.ts', '').replace('.js', '')
        else:
            module = file_path.replace('.py', '').replace('.ts', '').replace('.js', '')

        node_to_module[node_id] = module

    # Build module edges
    module_edges = set()
    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')

        source_mod = node_to_module.get(source, 'unknown')
        target_mod = node_to_module.get(target, 'unknown')

        if source_mod and target_mod and source_mod != target_mod:
            module_edges.add((source_mod, target_mod))

    return module_edges


def _detect_direct_cycles(edges: List[Dict]) -> List[str]:
    """Detect direct circular dependencies (A -> B -> A)."""
    # Build adjacency for quick lookup
    adjacency = defaultdict(set)
    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        adjacency[source].add(target)

    cycles = []
    checked = set()

    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')

        # Check for direct cycle (A -> B and B -> A)
        pair_key = tuple(sorted([source, target]))
        if pair_key not in checked:
            if source in adjacency.get(target, set()):
                cycles.append(f"{source} <-> {target}")
            checked.add(pair_key)

    return cycles


def _sanitize_id(identifier: str) -> str:
    """Sanitize identifier for Mermaid node ID."""
    # Replace problematic characters
    safe = identifier.replace('.', '_').replace('/', '_').replace('\\', '_')
    safe = safe.replace('-', '_').replace(' ', '_').replace(':', '_')
    safe = ''.join(c for c in safe if c.isalnum() or c == '_')

    # Ensure it doesn't start with a number
    if safe and safe[0].isdigit():
        safe = 'n_' + safe

    return safe or 'unknown'


def _get_short_name(identifier: str) -> str:
    """Get short display name from identifier."""
    # Remove path prefix
    if '/' in identifier:
        identifier = identifier.rsplit('/', 1)[-1]
    if '\\' in identifier:
        identifier = identifier.rsplit('\\', 1)[-1]

    # Remove common prefixes
    for prefix in ['handle_', 'on_', '_']:
        if identifier.startswith(prefix):
            identifier = identifier[len(prefix):]

    return identifier[:20]  # Truncate long names
