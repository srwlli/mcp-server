# MCP Server Setup Guide - Complete Walkthrough

**Last Updated**: 2025-10-11
**Author**: Claude (via Claude Code debugging session)

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Creating Your First MCP Server](#creating-your-first-mcp-server)
4. [Configuration for Each IDE](#configuration-for-each-ide)
5. [Testing Your Server](#testing-your-server)
6. [Troubleshooting](#troubleshooting)
7. [Adding More Tools](#adding-more-tools)

---

## Overview

This guide documents the complete process of setting up MCP (Model Context Protocol) servers that work globally across multiple AI coding assistants:

- **Claude Code** (Terminal CLI)
- **Cursor** (IDE)
- **VS Code** (with AI extensions)
- **Windsurf** (IDE)

MCP servers expose custom tools that AI assistants can use to interact with your local system, read files, execute commands, or provide specialized functionality.

**Advanced Example**: For a production MCP server with 13 tools, see the `docs-mcp` server in this directory. Refer to `docs-mcp/coderef/quickref.md` for complete tool documentation.

---

## Directory Structure

**Recommended central location**: `C:\Users\<username>\.mcp-servers\`

Example structure for the `hello-mcp` server:

```
C:\Users\willh\.mcp-servers\
└── hello-mcp\
    ├── server.py           # MCP server implementation
    ├── hello-world.txt     # Data file
    └── requirements.txt    # Python dependencies
```

**Why this location?**
- Central, user-specific location
- Easy to manage multiple servers
- Consistent path for all IDE configurations

---

## Creating Your First MCP Server

### Step 1: Create Directory Structure

```bash
mkdir C:\Users\<username>\.mcp-servers\hello-mcp
cd C:\Users\<username>\.mcp-servers\hello-mcp
```

### Step 2: Create `requirements.txt`

```txt
mcp>=1.0.0
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Step 3: Create Data File

Create `hello-world.txt`:
```txt
Hello World!
```

### Step 4: Create `server.py`

```python
#!/usr/bin/env python3
import asyncio
import os
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HELLO_FILE = os.path.join(SCRIPT_DIR, "hello-world.txt")

# Create an MCP server
app = Server("hello-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="read_document",
            description="Reads and returns the contents of hello-world.txt",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "read_document":
        try:
            with open(HELLO_FILE, "r") as f:
                content = f.read()
            return [TextContent(type="text", text=content)]
        except FileNotFoundError:
            return [TextContent(type="text", text="Error: hello-world.txt not found")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading file: {str(e)}")]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
```

### Step 5: Test Manually

```bash
python C:\Users\<username>\.mcp-servers\hello-mcp\server.py
```

The server should start and wait for stdio input. This confirms it runs without errors.

**Check for syntax errors:**
```bash
python -m py_compile C:\Users\<username>\.mcp-servers\hello-mcp\server.py
```

---

## Configuration for Each IDE

### 1. Claude Code (Terminal CLI)

**Config Location**: `C:\Users\<username>\.claude.json` (managed automatically)

**Setup Command**:
```bash
claude mcp add --scope user hello-mcp python "C:\Users\<username>\.mcp-servers\hello-mcp\server.py"
```

**Key Flags**:
- `--scope user` - Makes server available globally (all directories)
- `--scope local` - Makes server available only in current project
- `--scope project` - Project-specific configuration

**Verify**:
```bash
claude mcp list
```

**Expected Output**:
```
Checking MCP server health...

hello-mcp: python C:\Users\willh\.mcp-servers\hello-mcp\server.py - ✓ Connected
```

**Test from any directory**:
```bash
cd ~
claude mcp list
# Should still show hello-mcp as connected
```

---

### 2. Cursor IDE

**Config Location**: `C:\Users\<username>\.cursor\mcp.json`

**Manual Configuration**:

Create or edit `C:\Users\<username>\.cursor\mcp.json`:

```json
{
  "mcpServers": {
    "hello-mcp": {
      "command": "python",
      "args": ["C:\\Users\\<username>\\.mcp-servers\\hello-mcp\\server.py"]
    }
  }
}
```

**Important Notes**:
- Use double backslashes (`\\`) in Windows paths
- Cursor reads this config on startup
- Restart Cursor after modifying config

**Verify in Cursor**:

Check logs at: `C:\Users\<username>\AppData\Roaming\Cursor\logs\<timestamp>\window1\exthost\anysphere.cursor-mcp\`

Look for `MCP user-hello-mcp.log`:
```
Successfully connected to stdio server
Found 1 tools, 0 prompts, and 0 resources
```

---

### 3. VS Code

**Possible Config Locations** (check your VS Code setup):
- `C:\Users\<username>\.vscode\mcp.json`
- `C:\Users\<username>\AppData\Roaming\Code\User\mcp.json`

**Manual Configuration** (same format as Cursor):

```json
{
  "mcpServers": {
    "hello-mcp": {
      "command": "python",
      "args": ["C:\\Users\\<username>\\.mcp-servers\\hello-mcp\\server.py"]
    }
  }
}
```

**Note**: The exact location depends on your VS Code AI extension. Check extension documentation.

---

### 4. Windsurf IDE

**Possible Config Locations**:
- `C:\Users\<username>\.windsurf\mcp.json`
- `C:\Users\<username>\AppData\Roaming\Windsurf\User\mcp.json`

**Manual Configuration** (same format):

```json
{
  "mcpServers": {
    "hello-mcp": {
      "command": "python",
      "args": ["C:\\Users\\<username>\\.mcp-servers\\hello-mcp\\server.py"]
    }
  }
}
```

---

## Testing Your Server

### Test in Claude Code

1. Start Claude Code in any directory:
   ```bash
   claude
   ```

2. Ask: "What MCP tools do you have?"

3. Expected response should mention `read_document` tool

4. Test the tool:
   ```
   Use the read_document tool to read the hello world file
   ```

5. Expected output: "Hello World!"

### Test in Cursor

1. Open Cursor
2. Open the AI chat
3. Ask: "What MCP tools do you have?"
4. Look for `read_document` tool
5. Test it: "Use read_document to show me the file contents"

### Test in VS Code / Windsurf

Similar process to Cursor - ask the AI assistant about available MCP tools.

---

## Troubleshooting

### Issue: "No MCP servers configured"

**Cause**: Server not added to config or wrong scope

**Solution**:
```bash
# For Claude Code, ensure using user scope
claude mcp add --scope user hello-mcp python "C:\path\to\server.py"
```

---

### Issue: "Failed to connect" in `claude mcp list`

**Causes**:
1. Python path issues
2. Missing dependencies
3. Syntax errors in server.py
4. Incorrect file path

**Debug Steps**:

1. **Test Python directly**:
   ```bash
   python C:\Users\<username>\.mcp-servers\hello-mcp\server.py
   ```
   Should start without errors

2. **Check syntax**:
   ```bash
   python -m py_compile C:\Users\<username>\.mcp-servers\hello-mcp\server.py
   ```

3. **Verify dependencies**:
   ```bash
   pip list | grep mcp
   ```

4. **Check path in config**:
   - Ensure backslashes are escaped (`\\`)
   - Use absolute paths
   - Verify file exists at that path

---

### Issue: Path corrupted (backslashes removed)

**Symptom**:
```
hello-mcp: python C:Userswillh.mcp-servershello-mcpserver.py - ✗ Failed
```

**Solution**: Always quote paths when using CLI:
```bash
claude mcp add --scope user hello-mcp python "C:\Users\<username>\.mcp-servers\hello-mcp\server.py"
```

---

### Issue: Server works in one IDE but not another

**Cause**: Each IDE has separate configuration

**Solution**:
1. Check that IDE's specific config file
2. Verify config syntax (JSON formatting)
3. Restart the IDE after config changes
4. Check IDE logs for MCP errors

**Cursor Logs**: `C:\Users\<username>\AppData\Roaming\Cursor\logs\`

**Look for**:
- Connection success/failure messages
- Tool discovery confirmation
- Error details

---

### Issue: "Command 'claude' not found"

**Causes**:
1. Claude Code not installed
2. PATH not configured
3. Using wrong shell

**Solution**:
```bash
# Find claude location
where claude

# If found but not working, use full path
/c/Users/<username>/AppData/Roaming/npm/claude mcp list
```

---

## Adding More Tools

### Expand Existing Server

Edit `server.py` to add more tools:

```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="read_document",
            description="Reads and returns the contents of hello-world.txt",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="write_document",
            description="Writes content to hello-world.txt",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    }
                },
                "required": ["content"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "read_document":
        try:
            with open(HELLO_FILE, "r") as f:
                content = f.read()
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "write_document":
        try:
            content = arguments.get("content", "")
            with open(HELLO_FILE, "w") as f:
                f.write(content)
            return [TextContent(type="text", text="Successfully wrote to file")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    else:
        raise ValueError(f"Unknown tool: {name}")
```

**After modifying**:
1. Test manually: `python server.py`
2. Check syntax: `python -m py_compile server.py`
3. Restart AI assistants to reload the server
4. Verify new tools appear: "What MCP tools do you have?"

---

## Best Practices

### 1. Server Organization

- One directory per server
- Include README.md in each server directory
- Keep data files local to server directory
- Use relative paths for local files

### 2. Error Handling

Always wrap tool operations in try-catch:
```python
try:
    # Tool operation
    return [TextContent(type="text", text=result)]
except Exception as e:
    return [TextContent(type="text", text=f"Error: {str(e)}")]
```

### 3. Tool Descriptions

Make descriptions clear and specific:
```python
Tool(
    name="read_config",
    description="Reads the application configuration file (config.json) and returns its contents as JSON",
    # ...
)
```

### 4. Input Validation

Validate arguments in `call_tool()`:
```python
if name == "process_data":
    if "data" not in arguments:
        return [TextContent(type="text", text="Error: 'data' argument required")]
    # Process data...
```

### 5. Testing

Create a test script for each server:
```python
# test_server.py
import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client import ClientSession

async def test():
    params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("read_document", {})
            print(result.content[0].text)

asyncio.run(test())
```

---

## Summary

### Quick Setup Checklist

- [ ] Create directory: `C:\Users\<username>\.mcp-servers\<server-name>\`
- [ ] Write `server.py` with MCP tools
- [ ] Create `requirements.txt` and install dependencies
- [ ] Test manually: `python server.py`
- [ ] Check syntax: `python -m py_compile server.py`
- [ ] Configure for Claude Code: `claude mcp add --scope user ...`
- [ ] Configure for Cursor: Edit `~/.cursor/mcp.json`
- [ ] Configure for VS Code: Edit VS Code MCP config
- [ ] Configure for Windsurf: Edit Windsurf MCP config
- [ ] Test in each IDE: "What MCP tools do you have?"
- [ ] Verify tool works: Test actual tool functionality

---

## Configuration Scope Reference

### Claude Code Scopes

```bash
--scope user     # Global, available everywhere
--scope local    # Current project only
--scope project  # Project-specific config
```

**Storage**:
- User scope: `~/.claude.json` (user-level section)
- Local/Project scope: `~/.claude.json` (project-specific section)

---

## Key Learnings from Debugging

1. **Claude Code uses project-specific configs** stored in `~/.claude.json`, not separate global config files
2. **Cursor reads from** `~/.cursor/mcp.json` on startup
3. **Path escaping matters** - always use `\\` in JSON configs on Windows
4. **Quoting matters in CLI** - quote paths with spaces or special characters
5. **Restart required** - Most IDEs need restart after config changes
6. **Logs are your friend** - Check IDE logs for MCP connection details
7. **Test manually first** - Always test server runs before configuring IDEs

---

## Additional Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/anthropics/mcp-python)
- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [Example MCP Servers](https://github.com/anthropics/mcp-servers)
- [docs-mcp Quick Reference](./docs-mcp/coderef/quickref.md) - Advanced MCP server example with 13 tools

---

**End of Guide**

*This guide was created through live debugging and discovery. All commands and configurations have been tested and verified working as of 2025-10-08.*
