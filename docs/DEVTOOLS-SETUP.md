# Chrome DevTools MCP Setup Guide

This guide explains how to set up and use the Chrome DevTools MCP server for browser debugging with AI agents.

## Overview

The Chrome DevTools MCP server (`chrome-devtools-mcp`) enables AI agents to:
- Inspect browser console logs, errors, and warnings
- Monitor network requests and responses
- Take screenshots of web pages
- Record performance traces
- Automate browser interactions
- Query and inspect DOM elements

## Requirements

- **Node.js 22+** (required for npx)
- **Chrome browser** (any recent version)

## Installation

The Chrome DevTools MCP server is configured in `.mcp.json`:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"]
    }
  }
}
```

Using `@latest` ensures you always have the most recent version.

## Chrome Setup Options

### Option 1: Connect to Running Chrome (Recommended)

Start Chrome with remote debugging enabled:

**Windows:**
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

**Linux:**
```bash
google-chrome --remote-debugging-port=9222
```

Then connect with:
```bash
npx chrome-devtools-mcp@latest --browser-url=http://localhost:9222
```

### Option 2: Headless Mode (CI/Server)

For automated testing or server environments:

```bash
npx chrome-devtools-mcp@latest --headless
```

This launches a headless Chrome instance automatically.

### Option 3: Let MCP Launch Chrome

By default, the MCP server can launch a new Chrome instance:

```bash
npx chrome-devtools-mcp@latest
```

## Available Tools

Once configured, these DevTools capabilities are available:

| Tool | Description |
|------|-------------|
| Console inspection | View logs, errors, warnings from browser console |
| Network monitoring | Inspect HTTP requests/responses, headers, payloads |
| Screenshots | Capture full page or element screenshots |
| Performance traces | Record and analyze performance metrics |
| DOM inspection | Query elements, get computed styles |
| Automation | Click, type, navigate with Puppeteer reliability |

## Usage with Personas

### Ava (Frontend Specialist)

Ava has DevTools in her `preferred_tools`. Use `/debug-ui` to activate:

```
/debug-ui
```

Example tasks:
- "Check the console for errors on this page"
- "Take a screenshot of the login form"
- "Inspect network requests when I submit the form"
- "Find performance bottlenecks in this page load"

### Lloyd (Coordinator)

Lloyd is aware of DevTools MCP in the ecosystem and can assign debugging tasks to Ava.

## Troubleshooting

### "Cannot connect to browser"

1. Ensure Chrome is running with `--remote-debugging-port=9222`
2. Check no firewall is blocking port 9222
3. Try `--browser-url=http://127.0.0.1:9222` instead of localhost

### "Node.js version too old"

Chrome DevTools MCP requires Node.js 22+:
```bash
node --version  # Should be v22.x.x or higher
```

### "Permission denied"

On macOS/Linux, you may need to allow Chrome in security settings when running with remote debugging.

## References

- [Chrome DevTools MCP - npm](https://www.npmjs.com/package/chrome-devtools-mcp)
- [Chrome DevTools MCP - GitHub](https://github.com/nicholmikey/chrome-devtools-mcp)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
