---
description: Debug UI issues using Chrome DevTools MCP with Ava's frontend expertise
---

Activate **Ava** (Frontend Specialist) with Chrome DevTools MCP for browser debugging workflow.

## What This Does

1. Activates Ava's frontend expertise
2. Provides access to Chrome DevTools MCP tools
3. Enables live browser debugging capabilities

## Chrome DevTools MCP Capabilities

- **Console**: View console logs, errors, and warnings
- **Network**: Inspect network requests and responses
- **DOM**: Inspect and query DOM elements
- **Screenshots**: Capture page screenshots
- **Performance**: Record performance traces
- **Automation**: Reliable browser automation with Puppeteer

## Requirements

**Before using this command:**

1. Chrome must be running with remote debugging:
   ```bash
   # Windows
   chrome.exe --remote-debugging-port=9222

   # macOS
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

   # Linux
   google-chrome --remote-debugging-port=9222
   ```

2. Or use headless mode (no UI):
   ```bash
   npx chrome-devtools-mcp@latest --headless
   ```

## Example Tasks

- "Check the console for errors on this page"
- "Take a screenshot of the current page"
- "Inspect network requests when I click this button"
- "Run a performance trace and find bottlenecks"
- "Find all elements with this CSS selector"
- "Debug why this component isn't rendering"

## Usage

After activating, Ava will have access to Chrome DevTools tools:
- `mcp__chrome-devtools__*` - All DevTools capabilities

---

**Activating Ava with DevTools debugging mode...**

mcp__personas-mcp__use_persona(name: "ava")

**DevTools MCP is now available. Make sure Chrome is running with remote debugging enabled.**
