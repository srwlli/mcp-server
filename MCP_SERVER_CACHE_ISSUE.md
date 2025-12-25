# Known Issue: MCP Server Cache Persistence in Claude Code

## Problem Description

When renaming or removing MCP servers, old server definitions persist in `claude mcp list` output even after:
- Updating `.mcp.json` configuration files
- Clearing per-project caches
- Restarting Claude Code multiple times

Old servers continue to show as "Failed to connect" indefinitely.

## Root Cause

Claude Code maintains MCP server definitions in **THREE separate locations** with different precedence:

1. **Global cache** (`~/.claude.json` - top-level `mcpServers` object)
   - Highest priority, persists across restarts
   - Not automatically cleared when configs change
   - Not synced with `.mcp.json` files

2. **Per-project cache** (`~/.claude.json` under `projects[path].mcpServers`)
   - Project-specific cached definitions
   - Can be cleared but regenerates from discovered servers

3. **Project configuration** (`.mcp.json` and `.claude/settings.local.json`)
   - Source of truth for actual server definitions
   - Changes here don't auto-sync to cache

## Solution

To completely remove old/archived MCP servers:

### Step 1: Update Configuration Files
- Update `.mcp.json` to remove old server entries
- Update `.claude/settings.local.json` to add old names to `disabledMcpjsonServers` array

### Step 2: Clear Per-Project Cache
```javascript
const fs = require('fs');
const path = require('path');
const claudeJsonPath = path.join(process.env.USERPROFILE, '.claude.json');
const data = JSON.parse(fs.readFileSync(claudeJsonPath, 'utf8'));

// Clear per-project caches
Object.keys(data.projects).forEach(key => {
  if (key.includes('mcp-servers')) {
    data.projects[key].mcpServers = {};
    data.projects[key].enabledMcpjsonServers = [];
    data.projects[key].disabledMcpjsonServers = [];
  }
});

fs.writeFileSync(claudeJsonPath, JSON.stringify(data, null, 2));
```

### Step 3: Clear Global MCP Server Definitions (CRITICAL!)
```javascript
const fs = require('fs');
const path = require('path');
const claudeJsonPath = path.join(process.env.USERPROFILE, '.claude.json');
const data = JSON.parse(fs.readFileSync(claudeJsonPath, 'utf8'));

// Remove top-level mcpServers object
if (data.mcpServers) {
  delete data.mcpServers;
}

fs.writeFileSync(claudeJsonPath, JSON.stringify(data, null, 2));
```

### Step 4: Restart Claude Code
The old server names will be completely gone from `claude mcp list`.

## Case Study: Archiving 4 MCP Servers (Dec 24, 2024)

**Objective**: Archive 4 deprecated servers (coderef-mcp, hello-world-mcp, scriptboard-mcp, chrome-devtools) and rename personas-mcp → coderef-personas for unified naming.

**Timeline**:
- Multiple configuration updates and `~/.claude.json` cache clears
- Multiple Claude Code restarts
- Old server names persisted after each restart
- Root cause: Top-level `mcpServers` object in `~/.claude.json` still contained old definitions

**Resolution**:
1. Deleted top-level `mcpServers` from `~/.claude.json`
2. Restarted Claude Code
3. Old servers completely removed from `claude mcp list`

**Final State**:
- 4 active servers all connected: coderef-personas, coderef-context, coderef-docs, coderef-workflow
- All 4 servers use consistent `python` command configuration
- All paths standardized to forward slashes
- Archived servers properly organized in `/archived` directory

## Prevention for Future Changes

When modifying MCP server configuration:

1. **Always update both files**:
   - Global: `~/.mcp.json`
   - Project: `.mcp.json` in project root

2. **Ensure naming consistency**:
   - Directory name should match configured server name
   - All servers should use same command approach (python vs uv)

3. **Add to disabled list**:
   - Add old names to `disabledMcpjsonServers` in `.claude/settings.local.json`

4. **Clean the global cache**:
   - Don't just clear per-project caches
   - Always remove top-level `mcpServers` from `~/.claude.json`

5. **Verify after restart**:
   - Run `claude mcp list` to confirm only active servers appear

## Related Bug

Claude Code Issue #13281: Manual `.mcp.json` edits don't automatically sync to `~/.claude.json` cache. This is a fundamental architectural issue where cache invalidation only happens through the CLI `mcp add`/`mcp remove` commands, not through direct file edits.

## Files Involved

- `~/.mcp.json` - Global MCP server definitions
- `~/.claude.json` - Global Claude Code settings + MCP caches
- `.mcp.json` - Project-level MCP server definitions
- `.claude/settings.local.json` - Project-local Claude Code settings (includes enabled/disabled servers)
- `.mcp-servers/` - Directory containing all MCP server implementations
