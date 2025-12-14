# DELIVERABLES: devtools-mcp-integration

**Project**: .mcp-servers
**Feature**: devtools-mcp-integration
**Workorder**: WO-DEVTOOLS-MCP-INTEGRATION-001
**Status**: 🚧 Not Started
**Generated**: 2025-12-13

---

## Executive Summary

**Goal**: Enable AI agents (Ava and Lloyd) to inspect browser elements, console messages, network requests, and debug UI issues through the DevTools MCP server.

**Description**: Integrate Chrome DevTools MCP server with personas-mcp, enabling Ava (frontend specialist) and Lloyd (coordinator) to access browser debugging tools via MCP protocol.

---

## Implementation Phases

### Phase 1: Configuration

**Description**: Research and configure DevTools MCP server

**Estimated Duration**: TBD

**Deliverables**:
- Working DevTools MCP in .mcp.json

### Phase 2: Persona Updates

**Description**: Update Ava and Lloyd personas with DevTools capabilities

**Estimated Duration**: TBD

**Deliverables**:
- Updated ava.json
- Updated lloyd.json

### Phase 3: Command & Docs

**Description**: Create slash command and documentation

**Estimated Duration**: TBD

**Deliverables**:
- /debug-ui command
- DEVTOOLS-SETUP.md
- Updated README


---

## Metrics

### Code Changes
- **Lines of Code Added**: TBD
- **Lines of Code Deleted**: TBD
- **Net LOC**: TBD
- **Files Modified**: TBD

### Commit Activity
- **Total Commits**: TBD
- **First Commit**: TBD
- **Last Commit**: TBD
- **Contributors**: TBD

### Time Investment
- **Days Elapsed**: TBD
- **Hours Spent (Wall Clock)**: TBD

---

## Task Completion Checklist

- [ ] [CONFIG-001] Research exact DevTools MCP npm package name and verify installation
- [ ] [CONFIG-002] Add DevTools MCP server configuration to .mcp.json
- [ ] [PERSONA-001] Add DevTools MCP tools to Ava's preferred_tools array
- [ ] [PERSONA-002] Add DevTools debugging workflow to Ava's system_prompt
- [ ] [PERSONA-003] Add DevTools awareness to Lloyd's MCP ecosystem section
- [ ] [CMD-001] Create /debug-ui slash command in personas-mcp/.claude/commands/
- [ ] [DOCS-001] Create DEVTOOLS-SETUP.md with Chrome requirements and examples
- [ ] [DOCS-002] Update root README.md with DevTools MCP section

---

## Files Created/Modified

- **personas-mcp/.claude/commands/debug-ui.md** - Slash command for UI debugging workflow
- **docs/DEVTOOLS-SETUP.md** - Chrome setup and usage documentation
- **.mcp.json** - TBD
- **personas-mcp/personas/base/ava.json** - TBD
- **personas-mcp/personas/base/lloyd.json** - TBD
- **README.md** - TBD

---

## Success Criteria

- No success criteria defined

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated**: 2025-12-13
