"""
Papertrail MCP Server

Provides MCP tools for Universal Documentation Standards (UDS) validation.
Enables agents to validate documents against UDS schemas and get quality scores.
"""

from pathlib import Path
from typing import Any, Optional
import json

from mcp.server import Server
from mcp.types import Tool, TextContent

from papertrail.validators.factory import ValidatorFactory

# Initialize MCP server
app = Server("papertrail")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Papertrail MCP tools."""
    return [
        Tool(
            name="validate_resource_sheet",
            description="Validate a resource sheet document against RSMS v2.0 schema. Checks snake_case frontmatter, required fields (subject, parent_project, category), naming convention (-RESOURCE-SHEET.md suffix), and recommended sections. Returns score (0-100), errors, and warnings. Use this for /create-resource-sheet workflow validation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to resource sheet file (must end with -RESOURCE-SHEET.md)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="check_all_resource_sheets",
            description="Validate all resource sheet documents in a directory against RSMS v2.0 standards. Automatically scans for files ending with -RESOURCE-SHEET.md. Returns summary with pass/fail counts, average score, and detailed results per file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Absolute path to directory containing resource sheets"
                    }
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="validate_document",
            description="Validate any document against UDS schema. Auto-detects document type (foundation, workorder, system, session, etc.) and returns validation results with score (0-100), errors, and warnings. For resource sheets, use validate_resource_sheet instead.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to document file (markdown or JSON)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="check_all_docs",
            description="Validate all documents in a directory recursively against UDS schemas. Returns summary with pass/fail counts and average score. For resource sheets only, use check_all_resource_sheets instead.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Absolute path to directory to scan"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Optional glob pattern (default: **/*.md)"
                    }
                },
                "required": ["directory"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle MCP tool calls."""

    if name == "validate_resource_sheet":
        return await validate_resource_sheet(arguments)
    elif name == "check_all_resource_sheets":
        return await check_all_resource_sheets(arguments)
    elif name == "validate_document":
        return await validate_document(arguments)
    elif name == "check_all_docs":
        return await check_all_docs(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def validate_resource_sheet(arguments: dict) -> list[TextContent]:
    """Validate a resource sheet against RSMS v2.0 schema."""
    file_path = Path(arguments["file_path"])

    if not file_path.exists():
        return [TextContent(
            type="text",
            text=f"Error: File not found: {file_path}"
        )]

    # Enforce naming convention
    if not file_path.name.endswith("-RESOURCE-SHEET.md"):
        return [TextContent(
            type="text",
            text=f"Error: Resource sheet must end with -RESOURCE-SHEET.md\n\nGot: {file_path.name}\n\nPlease rename the file to follow the convention: {{Subject}}-RESOURCE-SHEET.md"
        )]

    try:
        # Force use of ResourceSheetValidator
        from papertrail.validators.resource_sheet import ResourceSheetValidator
        validator = ResourceSheetValidator()

        # Validate
        result = validator.validate_file(file_path)

        # Format response with RSMS v2.0 specific messaging
        response = f"# RSMS v2.0 Validation: {file_path.name}\n\n"
        response += f"**Valid:** {'Yes ✅' if result.valid else 'No ❌'}\n"
        response += f"**Score:** {result.score}/100\n"
        response += f"**Standard:** Resource Sheet Metadata Standards (RSMS) v2.0\n\n"

        if result.errors:
            response += f"## Errors ({len(result.errors)})\n\n"
            for error in result.errors:
                response += f"- [{error.severity.value}] {error.message}"
                if error.field:
                    response += f" (field: {error.field})"
                response += "\n"
            response += "\n**Fix these errors to achieve RSMS v2.0 compliance.**\n"

        if result.warnings:
            response += f"\n## Warnings ({len(result.warnings)})\n\n"
            for warning in result.warnings:
                response += f"- {warning}\n"
            response += "\n**Address warnings to improve documentation quality.**\n"

        if result.valid and result.score >= 90:
            response += "\n✅ **Resource sheet is RSMS v2.0 compliant!**\n"
        elif result.valid:
            response += f"\n⚠️ **Resource sheet validates but has warnings (score: {result.score}/100). Consider addressing warnings.**\n"
        else:
            response += f"\n❌ **Resource sheet failed validation (score: {result.score}/100). Fix errors above.**\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error validating resource sheet: {str(e)}"
        )]


async def check_all_resource_sheets(arguments: dict) -> list[TextContent]:
    """Validate all resource sheets in a directory."""
    directory = Path(arguments["directory"])

    # Hardcode pattern for resource sheets
    pattern = "**/*-RESOURCE-SHEET.md"

    if not directory.exists():
        return [TextContent(
            type="text",
            text=f"Error: Directory not found: {directory}"
        )]

    try:
        # Find all resource sheets
        files = list(directory.glob(pattern))

        if not files:
            return [TextContent(
                type="text",
                text=f"No resource sheets found in: {directory}\n\nLooking for files ending with: -RESOURCE-SHEET.md"
            )]

        # Validate each resource sheet
        from papertrail.validators.resource_sheet import ResourceSheetValidator
        validator = ResourceSheetValidator()

        results = []
        total_score = 0
        passed = 0
        failed = 0

        for file_path in files:
            try:
                result = validator.validate_file(file_path)

                results.append({
                    "file": file_path.name,
                    "valid": result.valid,
                    "score": result.score,
                    "errors": len(result.errors),
                    "warnings": len(result.warnings)
                })

                total_score += result.score
                if result.valid:
                    passed += 1
                else:
                    failed += 1

            except Exception as e:
                results.append({
                    "file": file_path.name,
                    "valid": False,
                    "score": 0,
                    "error": str(e)
                })
                failed += 1

        # Format summary
        avg_score = total_score / len(results) if results else 0

        response = f"# RSMS v2.0 Batch Validation: {directory.name}\n\n"
        response += f"**Total Resource Sheets:** {len(results)}\n"
        response += f"**Passed:** {passed} ✅\n"
        response += f"**Failed:** {failed} ❌\n"
        response += f"**Average Score:** {avg_score:.1f}/100\n"
        response += f"**Standard:** Resource Sheet Metadata Standards (RSMS) v2.0\n\n"

        response += "## Results\n\n"
        for r in results:
            status = "✅" if r["valid"] else "❌"
            response += f"{status} **{r['file']}** - Score: {r['score']}/100"
            if "error" in r:
                response += f" (Error: {r['error']})"
            elif r["errors"] > 0:
                response += f" ({r['errors']} errors, {r['warnings']} warnings)"
            response += "\n"

        if passed == len(results):
            response += "\n✅ **All resource sheets are RSMS v2.0 compliant!**\n"
        elif failed > 0:
            response += f"\n⚠️ **{failed} resource sheet(s) failed validation. Use validate_resource_sheet to see detailed errors.**\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error checking resource sheets: {str(e)}"
        )]


async def validate_document(arguments: dict) -> list[TextContent]:
    """Validate a single document against UDS schema."""
    file_path = Path(arguments["file_path"])
    
    if not file_path.exists():
        return [TextContent(
            type="text",
            text=f"Error: File not found: {file_path}"
        )]
    
    try:
        # Auto-detect validator type
        validator = ValidatorFactory.get_validator(file_path)
        
        # Validate
        result = validator.validate_file(file_path)
        
        # Format response
        response = f"# Validation Results: {file_path.name}\n\n"
        response += f"**Valid:** {'Yes' if result.valid else 'No'}\n"
        response += f"**Score:** {result.score}/100\n"
        response += f"**Category:** {validator.doc_category}\n\n"
        
        if result.errors:
            response += f"## Errors ({len(result.errors)})\n\n"
            for error in result.errors:
                response += f"- [{error.severity.value}] {error.message}"
                if error.field:
                    response += f" (field: {error.field})"
                response += "\n"
        
        if result.warnings:
            response += f"\n## Warnings ({len(result.warnings)})\n\n"
            for warning in result.warnings:
                response += f"- {warning}\n"
        
        if result.valid and not result.errors:
            response += "\n✅ Document validates successfully!\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error validating document: {str(e)}"
        )]


async def check_all_docs(arguments: dict) -> list[TextContent]:
    """Validate all documents in a directory."""
    directory = Path(arguments["directory"])
    pattern = arguments.get("pattern", "**/*.md")
    
    if not directory.exists():
        return [TextContent(
            type="text",
            text=f"Error: Directory not found: {directory}"
        )]
    
    try:
        # Find all matching files
        files = list(directory.glob(pattern))
        
        if not files:
            return [TextContent(
                type="text",
                text=f"No files found matching pattern: {pattern}"
            )]
        
        # Validate each file
        results = []
        total_score = 0
        passed = 0
        failed = 0
        
        for file_path in files:
            try:
                validator = ValidatorFactory.get_validator(file_path)
                result = validator.validate_file(file_path)
                
                results.append({
                    "file": str(file_path.relative_to(directory)),
                    "valid": result.valid,
                    "score": result.score,
                    "category": validator.doc_category,
                    "errors": len(result.errors),
                    "warnings": len(result.warnings)
                })
                
                total_score += result.score
                if result.valid:
                    passed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                results.append({
                    "file": str(file_path.relative_to(directory)),
                    "valid": False,
                    "score": 0,
                    "category": "unknown",
                    "error": str(e)
                })
                failed += 1
        
        # Format summary
        avg_score = total_score / len(results) if results else 0
        
        response = f"# Validation Summary: {directory.name}\n\n"
        response += f"**Total Files:** {len(results)}\n"
        response += f"**Passed:** {passed}\n"
        response += f"**Failed:** {failed}\n"
        response += f"**Average Score:** {avg_score:.1f}/100\n\n"
        
        response += "## Results\n\n"
        for r in results:
            status = "✅" if r["valid"] else "❌"
            response += f"{status} **{r['file']}** - Score: {r['score']}/100"
            if "error" in r:
                response += f" (Error: {r['error']})"
            elif r["errors"] > 0:
                response += f" ({r['errors']} errors, {r['warnings']} warnings)"
            response += f"\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error checking documents: {str(e)}"
        )]


if __name__ == "__main__":
    import asyncio
    import mcp.server.stdio
    
    async def main():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    
    asyncio.run(main())
