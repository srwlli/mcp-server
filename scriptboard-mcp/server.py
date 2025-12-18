#!/usr/bin/env python3
"""
Scriptboard MCP Server

Provides tools to control Scriptboard clipboard companion:
- set_prompt: Set prompt text
- clear_prompt: Clear prompt
- add_attachment: Add file/context
- clear_attachments: Clear all attachments
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from http_client import get_client

app = Server("scriptboard-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="mcp__scriptboard__set_prompt",
            description="Set the current prompt text in Scriptboard. Use this to prepare prompts for export to other LLMs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The prompt text to set"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="mcp__scriptboard__clear_prompt",
            description="Clear the current prompt in Scriptboard.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="mcp__scriptboard__add_attachment",
            description="Add a text attachment to Scriptboard (code files, logs, etc.). Can be called multiple times to add multiple files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text content to attach"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional filename (e.g., 'auth.py', 'error.log')"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="mcp__scriptboard__clear_attachments",
            description="Clear all attachments in Scriptboard. Use before adding new attachments to start fresh.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        # CodeRef Tools
        Tool(
            name="mcp__scriptboard__coderef_status",
            description="Check if CodeRef CLI is available. Returns CLI path and availability status.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="mcp__scriptboard__coderef_scan",
            description="Scan a directory for code elements (functions, classes, variables, etc.). Returns structured list of all code elements found.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_dir": {
                        "type": "string",
                        "description": "Directory path to scan (e.g., 'C:/projects/myapp/src')"
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Languages to scan (default: ['ts', 'tsx', 'js', 'jsx'])"
                    },
                    "use_ast": {
                        "type": "boolean",
                        "description": "Use AST mode for more accurate parsing (slower)"
                    }
                },
                "required": ["source_dir"]
            }
        ),
        Tool(
            name="mcp__scriptboard__coderef_query",
            description="Query dependencies and usages of a code element. Find what depends on a function, class, or variable.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Element to query (e.g., 'MyClass', 'handleSubmit', 'API_URL')"
                    },
                    "source_dir": {
                        "type": "string",
                        "description": "Optional: Limit search to this directory"
                    }
                },
                "required": ["target"]
            }
        ),
        Tool(
            name="mcp__scriptboard__coderef_impact",
            description="Analyze the impact of changing a code element. Shows what would be affected by modifying a function, class, or variable.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Element to analyze (e.g., 'UserService', 'calculateTotal')"
                    },
                    "source_dir": {
                        "type": "string",
                        "description": "Optional: Limit analysis to this directory"
                    },
                    "depth": {
                        "type": "integer",
                        "description": "Analysis depth (default: 3)"
                    }
                },
                "required": ["target"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    client = get_client()

    if name == "mcp__scriptboard__set_prompt":
        text = arguments.get("text", "")
        if not text:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "text parameter is required"
            }))]

        response = await client.set_prompt(text)
        return [TextContent(type="text", text=json.dumps({
            "success": response.success,
            "message": "Prompt set in Scriptboard" if response.success else response.error,
            "data": response.data
        }, indent=2))]

    elif name == "mcp__scriptboard__clear_prompt":
        response = await client.clear_prompt()
        return [TextContent(type="text", text=json.dumps({
            "success": response.success,
            "message": "Prompt cleared" if response.success else response.error
        }, indent=2))]

    elif name == "mcp__scriptboard__add_attachment":
        text = arguments.get("text", "")
        filename = arguments.get("filename")

        if not text:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "text parameter is required"
            }))]

        response = await client.add_attachment(text, filename)
        return [TextContent(type="text", text=json.dumps({
            "success": response.success,
            "message": f"Attachment added: {filename or 'unnamed'}" if response.success else response.error,
            "data": response.data
        }, indent=2))]

    elif name == "mcp__scriptboard__clear_attachments":
        response = await client.clear_attachments()
        return [TextContent(type="text", text=json.dumps({
            "success": response.success,
            "message": "All attachments cleared" if response.success else response.error
        }, indent=2))]

    # CodeRef Tools
    elif name == "mcp__scriptboard__coderef_status":
        response = await client.coderef_status()
        return [TextContent(type="text", text=json.dumps({
            "success": response.success,
            "data": response.data if response.success else None,
            "error": response.error if not response.success else None
        }, indent=2))]

    elif name == "mcp__scriptboard__coderef_scan":
        source_dir = arguments.get("source_dir", "")
        if not source_dir:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "source_dir parameter is required"
            }))]

        languages = arguments.get("languages")
        use_ast = arguments.get("use_ast", False)

        response = await client.coderef_scan(source_dir, languages, use_ast)
        return [TextContent(type="text", text=json.dumps({
            "success": response.success,
            "data": response.data if response.success else None,
            "error": response.error if not response.success else None
        }, indent=2))]

    elif name == "mcp__scriptboard__coderef_query":
        target = arguments.get("target", "")
        if not target:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "target parameter is required"
            }))]

        source_dir = arguments.get("source_dir")

        response = await client.coderef_query(target, source_dir)
        return [TextContent(type="text", text=json.dumps({
            "success": response.success,
            "data": response.data if response.success else None,
            "error": response.error if not response.success else None
        }, indent=2))]

    elif name == "mcp__scriptboard__coderef_impact":
        target = arguments.get("target", "")
        if not target:
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "target parameter is required"
            }))]

        source_dir = arguments.get("source_dir")
        depth = arguments.get("depth", 3)

        response = await client.coderef_impact(target, source_dir, depth)
        return [TextContent(type="text", text=json.dumps({
            "success": response.success,
            "data": response.data if response.success else None,
            "error": response.error if not response.success else None
        }, indent=2))]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
