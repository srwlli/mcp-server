# DELIVERABLES: git-workflow-mcp

**Project**: docs-mcp
**Feature**: git-workflow-mcp
**Workorder**: WO-GIT-WORKFLOW-MCP-001
**Status**: 🚧 Not Started
**Generated**: 2025-12-20

---

## Executive Summary

**Goal**: TBD

**Description**: TBD

---

## Implementation Phases

### Phase 1: Setup & Scaffolding

**Description**: Create version_manager.py module and unit tests for version parsing

**Estimated Duration**: TBD

**Deliverables**:
- generators/version_manager.py with parse_pyproject_toml(), parse_package_json(), parse_version_py()
- tests/unit/test_version_manager.py with 15+ test cases

### Phase 2: Core Git Workflow Logic

**Description**: Implement version auto-update, git staging, commit message generation, push, and optional tagging

**Estimated Duration**: TBD

**Deliverables**:
- update_version_files() function in version_manager.py
- stage_all_changes() function with comprehensive scope
- generate_commit_message() with metrics from DELIVERABLES.md
- push_to_remote() with error handling
- create_release_tag() with changelog integration

### Phase 3: MCP Handler & Slash Command

**Description**: Create MCP tool handler, register in server.py, and create slash command

**Estimated Duration**: TBD

**Deliverables**:
- handle_git_workflow() in tool_handlers.py with @decorators
- git_workflow tool definition in server.py
- .claude/commands/git-workflow.md
- Updated .claude/commands.json

### Phase 4: Testing & Validation

**Description**: Create integration tests and validate error handling

**Estimated Duration**: TBD

**Deliverables**:
- tests/integration/test_git_workflow.py with end-to-end workflow tests
- Version detection tests for Python/Node/mixed projects
- Error handling tests for git failures

### Phase 5: Documentation & Integration

**Description**: Update all documentation and validate complete workflow lifecycle

**Estimated Duration**: TBD

**Deliverables**:
- Updated CLAUDE.md with git_workflow tool catalog entry
- Updated user-guide.md with workflow examples
- Updated README.md feature list
- Updated /archive-feature docs to reference /git-workflow
- Validated complete lifecycle from /create-workorder to /git-workflow


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

- [ ] [SETUP-001] Create generators/version_manager.py with version file parsers
- [ ] [SETUP-002] Create tests/unit/test_version_manager.py with parser tests
- [ ] [CORE-001] Implement version detection and auto-update logic in version_manager.py
- [ ] [CORE-002] Implement git staging logic for comprehensive commit scope
- [ ] [CORE-003] Implement commit message generation with metrics from DELIVERABLES.md
- [ ] [CORE-004] Implement git push logic with error handling
- [ ] [CORE-005] Implement optional release tag creation with changelog integration
- [ ] [HANDLER-001] Create handle_git_workflow in tool_handlers.py with pre-flight validation
- [ ] [HANDLER-002] Add git_workflow tool definition to server.py list_tools()
- [ ] [HANDLER-003] Register handle_git_workflow in TOOL_HANDLERS dict
- [ ] [CMD-001] Create .claude/commands/git-workflow.md slash command
- [ ] [CMD-002] Register /git-workflow in .claude/commands.json
- [ ] [TEST-001] Create tests/integration/test_git_workflow.py with full workflow tests
- [ ] [TEST-002] Test version detection across Python and Node projects
- [ ] [TEST-003] Test error handling for git failures (network, auth, branch protection)
- [ ] [DOC-001] Update CLAUDE.md with git_workflow tool documentation
- [ ] [DOC-002] Update user-guide.md with /git-workflow workflow examples
- [ ] [DOC-003] Update README.md feature list to include git workflow automation
- [ ] [INTEG-001] Update /archive-feature documentation to mention /git-workflow as next step
- [ ] [INTEG-002] Test complete lifecycle: /create-workorder → implement → /update-deliverables → /update-docs → /archive-feature → /git-workflow

---

## Files Created/Modified

- **.claude/commands/git-workflow.md** - Slash command definition for /git-workflow
- **generators/version_manager.py** - Version file parsing and updating logic (pyproject.toml, package.json, __version__.py)
- **tests/unit/test_version_manager.py** - Unit tests for version parsing and updating
- **tests/integration/test_git_workflow.py** - Integration tests for git_workflow tool
- **server.py** - TBD
- **tool_handlers.py** - TBD
- **.claude/commands.json** - TBD

---

## Success Criteria

- Tool successfully detects and updates version in 100% of cases for pyproject.toml, package.json, __version__.py
- Tool stages all implementation code, updated docs, and archived artifacts (minimum 5 file types: .py, .md, .json, archived/, index)
- Tool creates commit with comprehensive message including workorder ID and >= 3 metrics (LOC, commits, time)
- Tool pushes commit to remote successfully with 0 push failures in normal conditions
- Tool optionally creates release tag for 100% of minor/major versions when requested
- Pre-flight validation catches >= 95% of missing prerequisites (no archive, no git repo, no remote)
- Error handling provides clear, actionable messages for >= 10 common failure modes (network, auth, branch protection, etc.)

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated**: 2025-12-20
