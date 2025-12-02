#!/usr/bin/env python3
"""Fix server.py to use TextContent instead of ToolResult."""

import re

# Read the server.py file
with open('server.py', 'r') as f:
    content = f.read()

# Replace ToolResult with TextContent and remove isError parameter
# Pattern 1: ToolResult with isError=True
content = re.sub(
    r'ToolResult\(\s*type="text",\s*text=([^,]+),\s*isError=True\s*\)',
    r'TextContent(\n                    type="text",\n                    text=\1\n                )',
    content
)

# Pattern 2: ToolResult with isError=result.get("status") == "error"
content = re.sub(
    r'ToolResult\(\s*type="text",\s*text=([^,]+),\s*isError=result\.get\("status"\) == "error"\s*\)',
    r'TextContent(\n                    type="text",\n                    text=\1\n                )',
    content
)

# Write back
with open('server.py', 'w') as f:
    f.write(content)

print("Fixed server.py - replaced ToolResult with TextContent")
