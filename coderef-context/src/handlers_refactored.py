"""
Refactored MCP Tool Handlers

Reads from .coderef/ files instead of calling CLI subprocess.
Faster, simpler, no external dependencies.
"""

import json
from typing import List
from mcp.types import TextContent
from .coderef_reader import CodeRefReader


async def handle_coderef_scan(args: dict) -> List[TextContent]:
    """Return scan data from .coderef/index.json"""
    project_path = args.get("project_path", ".")

    try:
        reader = CodeRefReader(project_path)

        if not reader.exists():
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "No scan data found. Run scan first to create .coderef/ directory.",
                    "hint": "Use dashboard scanner or run: coderef scan " + project_path
                }, indent=2)
            )]

        elements = reader.get_index()

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "elements_found": len(elements),
                "elements": elements,
                "source": "file://" + str(reader.coderef_dir / "index.json")
            }, indent=2)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
        )]


async def handle_coderef_query(args: dict) -> List[TextContent]:
    """Query relationships from .coderef/graph.json"""
    project_path = args.get("project_path", ".")
    query_type = args.get("query_type")
    target = args.get("target")

    if not target:
        return [TextContent(type="text", text="Error: target parameter is required")]

    try:
        reader = CodeRefReader(project_path)

        if not reader.exists():
            return [TextContent(type="text", text="Error: No scan data found")]

        relationships = reader.get_element_relationships(target)

        # Map query types to data
        if query_type == "calls":
            result = relationships.get("dependencies", [])
        elif query_type == "calls-me":
            result = relationships.get("dependents", [])
        elif query_type == "imports":
            result = relationships.get("dependencies", [])
        elif query_type == "imports-me":
            result = relationships.get("dependents", [])
        elif query_type == "depends-on":
            result = relationships.get("dependencies", [])
        elif query_type == "depends-on-me":
            result = relationships.get("dependents", [])
        else:
            result = []

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "query_type": query_type,
                "target": target,
                "results": result,
                "element": relationships.get("element")
            }, indent=2)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_coderef_impact(args: dict) -> List[TextContent]:
    """Analyze impact from .coderef/graph.json"""
    project_path = args.get("project_path", ".")
    element = args.get("element")

    if not element:
        return [TextContent(type="text", text="Error: element parameter is required")]

    try:
        reader = CodeRefReader(project_path)
        relationships = reader.get_element_relationships(element)

        dependents = relationships.get("dependents", [])
        dependencies = relationships.get("dependencies", [])

        impact = {
            "element": element,
            "direct_dependents": len(dependents),
            "direct_dependencies": len(dependencies),
            "dependents_list": dependents,
            "risk_level": "HIGH" if len(dependents) > 5 else "MEDIUM" if len(dependents) > 2 else "LOW"
        }

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "impact": impact
            }, indent=2)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_coderef_complexity(args: dict) -> List[TextContent]:
    """Get complexity from .coderef/reports/complexity/"""
    project_path = args.get("project_path", ".")
    element = args.get("element")

    if not element:
        return [TextContent(type="text", text="Error: element parameter is required")]

    try:
        reader = CodeRefReader(project_path)
        element_data = reader.find_element(element)

        if not element_data:
            return [TextContent(type="text", text=f"Error: Element '{element}' not found")]

        # Basic complexity estimation from element data
        complexity = {
            "element": element,
            "type": element_data.get("type"),
            "file": element_data.get("file"),
            "line": element_data.get("line"),
            "parameters": len(element_data.get("parameters", [])),
            "complexity_estimate": "Simple" if len(element_data.get("parameters", [])) < 3 else "Moderate"
        }

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "complexity": complexity
            }, indent=2)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_coderef_patterns(args: dict) -> List[TextContent]:
    """Get patterns from .coderef/reports/patterns.json"""
    project_path = args.get("project_path", ".")

    try:
        reader = CodeRefReader(project_path)
        patterns = reader.get_patterns()

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "patterns": patterns
            }, indent=2)
        )]

    except FileNotFoundError:
        return [TextContent(type="text", text="Error: No pattern data found. Run full scan with populate-coderef.py")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_coderef_coverage(args: dict) -> List[TextContent]:
    """Get coverage from .coderef/reports/coverage.json"""
    project_path = args.get("project_path", ".")

    try:
        reader = CodeRefReader(project_path)
        coverage = reader.get_coverage()

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "coverage": coverage
            }, indent=2)
        )]

    except FileNotFoundError:
        return [TextContent(type="text", text="Error: No coverage data found. Run full scan with populate-coderef.py")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_coderef_context(args: dict) -> List[TextContent]:
    """Get context from .coderef/context.json or context.md"""
    project_path = args.get("project_path", ".")
    output_format = args.get("output_format", "json")

    try:
        reader = CodeRefReader(project_path)
        context = reader.get_context(format=output_format)

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "format": output_format,
                "context": context
            }, indent=2) if output_format == "json" else context
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_coderef_validate(args: dict) -> List[TextContent]:
    """Get validation from .coderef/reports/validation.json"""
    project_path = args.get("project_path", ".")

    try:
        reader = CodeRefReader(project_path)
        validation = reader.get_validation()

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "validation": validation
            }, indent=2)
        )]

    except FileNotFoundError:
        return [TextContent(type="text", text="Error: No validation data found. Run full scan with populate-coderef.py")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_coderef_drift(args: dict) -> List[TextContent]:
    """Get drift from .coderef/reports/drift.json"""
    project_path = args.get("project_path", ".")

    try:
        reader = CodeRefReader(project_path)
        drift = reader.get_drift()

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "drift_report": drift
            }, indent=2)
        )]

    except FileNotFoundError:
        return [TextContent(type="text", text="Error: No drift data found. Run full scan with populate-coderef.py")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_coderef_diagram(args: dict) -> List[TextContent]:
    """Get diagram from .coderef/diagrams/"""
    project_path = args.get("project_path", ".")
    diagram_type = args.get("diagram_type", "dependencies")
    format_type = args.get("format", "mermaid")

    try:
        reader = CodeRefReader(project_path)
        diagram = reader.get_diagram(diagram_type, format_type)

        return [TextContent(type="text", text=diagram)]

    except FileNotFoundError:
        return [TextContent(type="text", text=f"Error: Diagram not found. Run full scan with populate-coderef.py")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_coderef_tag(args: dict) -> List[TextContent]:
    """Tagging not supported in read-only mode"""
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": False,
            "error": "Tag operation requires CLI (modifies files). Use: coderef tag <path>"
        }, indent=2)
    )]


async def handle_coderef_export(args: dict) -> List[TextContent]:
    """Get export from .coderef/exports/"""
    project_path = args.get("project_path", ".")
    format_type = args.get("format")

    if not format_type:
        return [TextContent(type="text", text="Error: format parameter is required")]

    try:
        reader = CodeRefReader(project_path)
        export_data = reader.get_export(format_type)

        if format_type in ["json", "jsonld"]:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "format": format_type,
                    "data": export_data
                }, indent=2)
            )]
        else:
            return [TextContent(type="text", text=export_data)]

    except FileNotFoundError:
        return [TextContent(type="text", text=f"Error: Export not found. Run full scan with populate-coderef.py")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
