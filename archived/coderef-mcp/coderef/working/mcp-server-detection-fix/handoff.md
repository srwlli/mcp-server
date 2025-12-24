# MCP Server Detection Fix - Session Handoff

**Date**: 2025-10-17
**Feature**: mcp-server-detection-fix
**Status**: In Progress - Partial Fix Applied
**Next Session**: Needs further investigation

---

## Executive Summary

**Goal**: Fix coderef2-mcp server so it can be detected by Claude Code and used via slash commands in IDE/terminal.

**Current Status**:
- ✅ Root cause identified and fixed (stdout → stderr logging)
- ✅ Changes committed and pushed to repository
- ❌ Server still not detected by Claude Code after fix
- 🔍 Requires additional investigation to identify remaining blocker

---

## What Was Done This Session

### 1. Root Cause Analysis (Phase 1: Investigation)
**Tasks Completed**: T001, T002, T003

- **Compared server.py implementations** between working docs-mcp and failing coderef2-mcp
  - Structure is nearly identical
  - Both use `stdio_server()` and proper MCP protocol

- **Found critical issue in logger_config.py**:
  - ❌ coderef2-mcp used `StreamHandler()` → defaults to stdout
  - ✅ docs-mcp uses `StreamHandler(sys.stderr)` → stderr
  - **Why this matters**: MCP protocol uses stdin/stdout for communication. Logging to stdout corrupts protocol messages!

### 2. Fix Implementation (Phase 2: Fix)
**Tasks Completed**: T004, T005, T006

**File Modified**: `logger_config.py`
```python
# BEFORE:
console_handler = logging.StreamHandler()  # Bad - stdout

# AFTER:
import sys
console_handler = logging.StreamHandler(sys.stderr)  # Good - stderr
```

**Commits**:
1. Commit `bba8b18` - Added implementation plan and context
2. Commit `d3cea88` - Fixed logger to use stderr instead of stdout

**Repository**: https://github.com/srwlli/coderef-mcp.git

### 3. Verification (Phase 3: Incomplete)
**Task T007**: Partially completed

- ✅ Server imports successfully: `python -c "import server"` works
- ✅ Server starts without errors when run directly
- ✅ Logs now go to stderr (not stdout)
- ❌ `claude mcp list` still only shows docs-mcp
- ❌ coderef2-mcp not detected by Claude Code

---

## Current Configuration

**MCP Config File**: `C:\Users\willh\.claude\.mcp.json`
```json
{
  "mcpServers": {
    "docs-mcp": {
      "command": "python",
      "args": ["C:\\Users\\willh\\.mcp-servers\\docs-mcp\\server.py"]
    },
    "coderef2-mcp": {
      "command": "python",
      "args": ["C:\\Users\\willh\\.mcp-servers\\coderef2-mcp\\server.py"]
    }
  }
}
```

**Status**:
- docs-mcp: ✓ Connected
- coderef2-mcp: Not appearing at all

---

## Problem Statement

Despite fixing the logger issue, coderef2-mcp is still not detected by Claude Code's MCP client.

**What Works**:
- Server code imports successfully
- Server starts without errors when run manually
- Logs properly go to stderr (not corrupting stdout)
- Server structure matches working docs-mcp pattern
- Config file is correct and matches docs-mcp pattern

**What Doesn't Work**:
- Server does not appear in `claude mcp list`
- No error messages visible in our testing
- Claude Code seems to not even attempt to start coderef2-mcp

---

## Hypotheses for Remaining Issue

### 1. Claude Code Config Not Reloaded
**Likelihood**: High
**Evidence**: Config changes sometimes require full restart
**Next Step**: User needs to fully quit and restart Claude Code (not just close window)

### 2. Silent Startup Failure
**Likelihood**: Medium
**Evidence**: Server works in our tests but may fail in Claude Code's environment
**Next Step**: Check Claude Code logs at `C:\Users\willh\AppData\Local\Claude Code\logs`

### 3. Python Environment Mismatch
**Likelihood**: Medium
**Evidence**: `python` command may resolve to different interpreters
**Next Step**: Try absolute Python path in config (e.g., `C:\Python\python.exe`)

### 4. Import Dependency Missing
**Likelihood**: Medium
**Evidence**: Works in terminal but may fail when Claude Code launches it
**Next Step**: Check if all dependencies (mcp, pythonjsonlogger, etc.) are installed

### 5. MCP Protocol Version Issue
**Likelihood**: Low
**Evidence**: Both servers should use same MCP SDK
**Next Step**: Compare MCP package versions between servers

### 6. Name Collision Issue
**Likelihood**: Low
**Evidence**: "coderef2-mcp" vs "coderef-mcp" (repo name)
**Next Step**: Check if server name conflicts with something

---

## Files Modified This Session

1. **coderef/working/mcp-server-detection-fix/context.json**
   - Documented feature goals and requirements
   - Status: Committed

2. **coderef/working/mcp-server-detection-fix/plan.json**
   - Complete implementation plan (validated, score 95/100)
   - Status: Committed

3. **logger_config.py**
   - Fixed stdout → stderr logging issue
   - Status: Committed (d3cea88)

---

## Recommended Next Steps for Next Session

### Immediate Actions (Priority 1)
1. **User to restart Claude Code completely**
   - Quit application fully
   - Kill any background processes
   - Restart and test `claude mcp list`

2. **Check Claude Code logs**
   - Location: `C:\Users\willh\AppData\Local\Claude Code\logs`
   - Look for MCP server connection errors
   - Search for "coderef2-mcp" or "coderef" mentions

### If Still Not Working (Priority 2)
3. **Verify Python environment**
   ```bash
   where python
   python --version
   python -m pip list | grep mcp
   ```

4. **Try absolute Python path in config**
   ```json
   "command": "C:\\Path\\To\\python.exe"
   ```

5. **Create minimal test MCP server**
   - Strip down to bare minimum
   - Test if ANY new MCP server can be detected
   - Isolate configuration vs. code issue

### Deep Investigation (Priority 3)
6. **Compare dependency versions**
   ```bash
   cd C:\Users\willh\.mcp-servers\docs-mcp
   python -m pip list
   cd C:\Users\willh\.mcp-servers\coderef2-mcp
   python -m pip list
   ```

7. **Test MCP handshake manually**
   - Use MCP test client/tools
   - Verify protocol communication works

8. **Check for import errors when Claude Code launches**
   - Add extensive logging to server.py
   - Log every import and initialization step

---

## Key Files for Next Session

**Implementation Plan**:
- `coderef/working/mcp-server-detection-fix/plan.json`
- `coderef/working/mcp-server-detection-fix/context.json`

**Modified Code**:
- `logger_config.py` - Fixed logger (committed)
- `server.py` - MCP server implementation (no changes needed)

**Configuration**:
- `C:\Users\willh\.claude\.mcp.json` - MCP server config

**Logs to Check**:
- `C:\Users\willh\AppData\Local\Claude Code\logs` - Claude Code logs
- Server stderr output when Claude Code starts it

---

## Testing Checklist

After next changes, verify:

- [ ] `claude mcp list` shows coderef2-mcp with ✓ Connected
- [ ] All 6 tools appear in Claude Code
- [ ] Tools can be invoked: query, analyze, validate, batch_validate, generate_docs, audit
- [ ] No errors in Claude Code logs
- [ ] Server logs show successful initialization

---

## Context for Next AI Agent

**You are continuing work on**: Fixing MCP server detection for coderef2-mcp

**What's been done**:
- Root cause found: logger was writing to stdout (fixed ✓)
- Changes committed and pushed to repository
- Server code is correct and works when tested manually

**What's NOT done**:
- Server still not detected by Claude Code
- Need to investigate why despite the fix

**Your immediate task**:
1. Help user check Claude Code logs for errors
2. Verify user has fully restarted Claude Code
3. Investigate remaining blockers from hypotheses list above
4. Continue with Phase 3 (Verification) of the implementation plan

**DO NOT**:
- Revert the logger fix (it's correct)
- Make changes without first investigating logs
- Assume the fix should have worked - there's clearly another issue

**Files you'll need**:
- Implementation plan: `coderef/working/mcp-server-detection-fix/plan.json`
- Context: `coderef/working/mcp-server-detection-fix/context.json`
- This handoff doc: `coderef/working/mcp-server-detection-fix/handoff.md`

Good luck! 🚀
