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
                    "hint": "Use dashboard scanner or run: python scripts/populate-coderef.py " + project_path
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

        # Try to include visual architecture diagram
        visual_arch = None
        try:
            visual_arch = reader._load_text("exports/diagram-wrapped.md")
        except FileNotFoundError:
            pass  # File doesn't exist yet, no problem

        # Add elements_by_type breakdown
        elements_by_type = None
        try:
            index = reader.get_index()
            type_counts = {}
            type_samples = {}

            for elem in index:
                elem_type = elem.get("type", "unknown")
                type_counts[elem_type] = type_counts.get(elem_type, 0) + 1

                # Keep top 5 samples per type
                if elem_type not in type_samples:
                    type_samples[elem_type] = []
                if len(type_samples[elem_type]) < 5:
                    type_samples[elem_type].append({
                        "name": elem.get("name"),
                        "file": elem.get("file"),
                        "line": elem.get("line")
                    })

            elements_by_type = {
                "counts": type_counts,
                "samples": type_samples,
                "total": len(index)
            }
        except Exception:
            pass  # Index doesn't exist or parsing failed

        # Add complexity_hotspots (top 10 complex files)
        complexity_hotspots = None
        try:
            complexity_data = reader._load_json("reports/complexity.json")
            if complexity_data and "functions" in complexity_data:
                # Group by file and aggregate complexity
                file_complexity = {}
                for func in complexity_data["functions"]:
                    file_path = func.get("file", "unknown")
                    complexity = func.get("cyclomatic_complexity", 0)
                    if file_path not in file_complexity:
                        file_complexity[file_path] = {
                            "file": file_path,
                            "total_complexity": 0,
                            "function_count": 0,
                            "max_complexity": 0
                        }
                    file_complexity[file_path]["total_complexity"] += complexity
                    file_complexity[file_path]["function_count"] += 1
                    file_complexity[file_path]["max_complexity"] = max(
                        file_complexity[file_path]["max_complexity"],
                        complexity
                    )

                # Sort by total complexity and take top 10
                sorted_files = sorted(
                    file_complexity.values(),
                    key=lambda x: x["total_complexity"],
                    reverse=True
                )
                complexity_hotspots = sorted_files[:10]
        except Exception:
            pass  # Complexity data doesn't exist or parsing failed

        # Add documentation_summary (coverage, gaps, quality score)
        documentation_summary = None
        try:
            index = reader.get_index()
            total_elements = len(index)
            documented_elements = 0
            undocumented_files = set()

            for elem in index:
                # Check if element has JSDoc/docstring (common doc indicators)
                if elem.get("jsdoc") or elem.get("docstring") or elem.get("doc"):
                    documented_elements += 1
                else:
                    undocumented_files.add(elem.get("file", "unknown"))

            coverage_percent = (documented_elements / total_elements * 100) if total_elements > 0 else 0

            # Calculate quality score (0-100)
            # Based on: coverage (70%), gaps (20%), consistency (10%)
            quality_score = int(
                (coverage_percent * 0.7) +
                (max(0, 100 - len(undocumented_files) * 5) * 0.2) +
                (50 * 0.1)  # Baseline consistency score
            )

            documentation_summary = {
                "coverage_percent": round(coverage_percent, 2),
                "documented_elements": documented_elements,
                "total_elements": total_elements,
                "gaps": {
                    "undocumented_count": total_elements - documented_elements,
                    "files_with_gaps": sorted(list(undocumented_files))[:10]  # Top 10
                },
                "quality_score": quality_score
            }
        except Exception:
            pass  # Index doesn't exist or parsing failed

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "format": output_format,
                "context": context,
                "visual_architecture": visual_arch,
                "elements_by_type": elements_by_type,
                "complexity_hotspots": complexity_hotspots,
                "documentation_summary": documentation_summary
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


async def handle_validate_coderef_outputs(args: dict) -> List[TextContent]:
    """Validate .coderef/ files against schemas"""
    project_path = args.get("project_path", ".")

    try:
        reader = CodeRefReader(project_path)

        if not reader.exists():
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "No .coderef/ directory found",
                    "hint": "Run scan first: coderef scan " + project_path
                }, indent=2)
            )]

        # Files to validate
        files_to_validate = [
            ".coderef/index.json",
            ".coderef/graph.json",
            ".coderef/context.json"
        ]

        validation_results = []
        total_score = 0
        errors_found = []

        from pathlib import Path
        for file_rel_path in files_to_validate:
            file_path = Path(project_path) / file_rel_path

            if not file_path.exists():
                validation_results.append({
                    "file": file_rel_path,
                    "exists": False,
                    "score": 0,
                    "errors": [f"File not found: {file_rel_path}"]
                })
                errors_found.append(f"Missing file: {file_rel_path}")
                continue

            # Basic validation (structure check)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Validate index.json structure
                if "index.json" in file_rel_path:
                    if not isinstance(data, list):
                        errors_found.append(f"index.json must be an array, got {type(data).__name__}")
                        score = 50
                    else:
                        # Check element structure
                        required_fields = ["name", "type", "file", "line"]
                        valid_elements = sum(1 for e in data if all(f in e for f in required_fields))
                        score = int((valid_elements / len(data) * 100)) if data else 100

                # Validate graph.json structure
                elif "graph.json" in file_rel_path:
                    if not isinstance(data, dict):
                        errors_found.append(f"graph.json must be an object, got {type(data).__name__}")
                        score = 50
                    elif "nodes" not in data or "edges" not in data:
                        errors_found.append("graph.json missing 'nodes' or 'edges' fields")
                        score = 70
                    else:
                        score = 100

                # Validate context.json structure
                elif "context.json" in file_rel_path:
                    if not isinstance(data, dict):
                        errors_found.append(f"context.json must be an object, got {type(data).__name__}")
                        score = 50
                    else:
                        # Optional fields check
                        recommended_fields = ["projectPath", "version", "generatedAt"]
                        has_fields = sum(1 for f in recommended_fields if f in data)
                        score = int((has_fields / len(recommended_fields)) * 100)

                validation_results.append({
                    "file": file_rel_path,
                    "exists": True,
                    "score": score,
                    "errors": []
                })
                total_score += score

            except json.JSONDecodeError as e:
                errors_found.append(f"Invalid JSON in {file_rel_path}: {str(e)}")
                validation_results.append({
                    "file": file_rel_path,
                    "exists": True,
                    "score": 0,
                    "errors": [f"JSON parse error: {str(e)}"]
                })

        average_score = int(total_score / len(files_to_validate)) if files_to_validate else 0

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": average_score >= 80,
                "average_score": average_score,
                "validation_results": validation_results,
                "errors": errors_found,
                "note": "Basic validation only. For full schema validation, integrate with Papertrail MCP validate_document tool."
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


async def handle_coderef_incremental_scan(args: dict) -> List[TextContent]:
    """Perform incremental scan (only re-scan files with detected drift, merge with existing index)"""
    project_path = args.get("project_path", ".")

    try:
        reader = CodeRefReader(project_path)
        drift = reader.get_drift()

        # Extract unique changed files from drift report
        changed_files = set()

        # Handle different drift formats (dict or array)
        if isinstance(drift, dict):
            # Dict format with "changes" key
            for element in drift.get("changes", {}).get("added", []):
                if "file" in element:
                    changed_files.add(element["file"])

            for element in drift.get("changes", {}).get("modified", []):
                if "file" in element:
                    changed_files.add(element["file"])

            for element in drift.get("changes", {}).get("removed", []):
                if "file" in element:
                    changed_files.add(element["file"])
        elif isinstance(drift, list):
            # Array format - each item is a changed element
            for element in drift:
                if isinstance(element, dict) and "file" in element:
                    changed_files.add(element["file"])

        changed_files_list = sorted(list(changed_files))

        # Return analysis + CLI command for incremental re-scan
        # (Read-only server can't modify .coderef/index.json directly)

        if not changed_files_list:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "drift_detected": False,
                    "changed_files": [],
                    "message": "No drift detected - index is up to date"
                }, indent=2)
            )]

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "drift_detected": True,
                "changed_files": changed_files_list,
                "changed_files_count": len(changed_files_list),
                "recommendation": "Re-scan only changed files to update index",
                "cli_command": f"python scripts/populate-coderef.py {project_path}",
                "note": "Read-only MCP server cannot modify index.json. Use CLI for incremental updates."
            }, indent=2)
        )]

    except FileNotFoundError:
        return [TextContent(type="text", text="Error: No drift data found. Run full scan with populate-coderef.py")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
