"""
Export Processor for CodeRef Context

Handles export operations for various output formats:
- JSON (raw index data)
- JSON-LD (Linked Data format for semantic web)
- Mermaid (wrapped diagram with title/description)
- DOT (GraphViz format for visualization)

Architecture:
- Wraps @coderef/core CLI export command
- Async subprocess execution for non-blocking operation
- JSON parsing for structured output
- Timeout handling (120s for large exports)
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.types import TextContent


async def export_coderef(
    cli_command: List[str],
    project_path: str,
    format: str,
    output_path: Optional[str] = None,
    max_nodes: Optional[int] = None,
    timeout: int = 120
) -> List[TextContent]:
    """
    Export coderef data in specified format.

    Args:
        cli_command: CLI command array (e.g., ["node", "cli.js"] or ["coderef"])
        project_path: Absolute path to project root
        format: Export format (json|jsonld|mermaid|dot)
        output_path: Optional output file path (defaults to .coderef/exports/{format})
        max_nodes: Optional limit on graph nodes (for large codebases)
        timeout: Subprocess timeout in seconds (default: 120)

    Returns:
        TextContent with export result (success/error)
    """
    # Validate format
    valid_formats = ["json", "jsonld", "mermaid", "dot"]
    if format not in valid_formats:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Invalid format '{format}'. Must be one of: {', '.join(valid_formats)}"
            }, indent=2)
        )]

    # Set default output path if not provided
    if not output_path:
        exports_dir = Path(project_path) / ".coderef" / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(exports_dir / f"export.{format}")

    # Build CLI command: coderef export -f <format> -o <path> -s <sourceDir> [-m N]
    cmd = [
        *cli_command, "export",
        "-f", format,
        "-o", output_path,
        "-s", project_path
    ]

    if max_nodes is not None:
        cmd.extend(["-m", str(max_nodes)])

    try:
        # Execute async subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=project_path
        )

        # Wait for completion with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Export timeout ({timeout}s exceeded) for format '{format}'"
                }, indent=2)
            )]

        # Check for errors
        if process.returncode != 0:
            error_msg = stderr.decode().strip() if stderr else "Unknown error"
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": error_msg,
                    "format": format,
                    "output_path": output_path
                }, indent=2)
            )]

        # Parse success output
        stdout_text = stdout.decode().strip() if stdout else ""

        # Verify file was created
        if not os.path.exists(output_path):
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Export file not created at {output_path}",
                    "cli_output": stdout_text
                }, indent=2)
            )]

        # Get file size
        file_size = os.path.getsize(output_path)

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "format": format,
                "output_path": output_path,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "cli_output": stdout_text
            }, indent=2)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "format": format,
                "command": " ".join(cmd)
            }, indent=2)
        )]


async def validate_export_format(format: str) -> Dict[str, Any]:
    """
    Validate export format and return metadata.

    Returns:
        Dictionary with validation result and format metadata
    """
    format_metadata = {
        "json": {
            "valid": True,
            "description": "Raw JSON index data",
            "file_extension": "json",
            "typical_size_mb": "2-10"
        },
        "jsonld": {
            "valid": True,
            "description": "JSON-LD (Linked Data) format for semantic web",
            "file_extension": "jsonld",
            "typical_size_mb": "3-15"
        },
        "mermaid": {
            "valid": True,
            "description": "Mermaid diagram with title and description",
            "file_extension": "mmd",
            "typical_size_mb": "0.5-5"
        },
        "dot": {
            "valid": True,
            "description": "GraphViz DOT format for visualization",
            "file_extension": "dot",
            "typical_size_mb": "1-8"
        }
    }

    if format in format_metadata:
        return {
            "format": format,
            **format_metadata[format]
        }
    else:
        return {
            "format": format,
            "valid": False,
            "error": f"Unknown format '{format}'. Valid formats: {', '.join(format_metadata.keys())}"
        }
