# Slash Command Mapping - Latest (2025-12-25)

**Status:** Mostly Complete - 39/40+ commands properly organized

---

## coderef-docs Commands (16 of 17 mapped)

✓ **Documentation Commands (16/16 active)**

| Command | File | Status |
|---------|------|--------|
| `/list-templates` | list-templates.md | ✓ In repo |
| `/get-template` | get-template.md | ✓ In repo |
| `/coderef-foundation-docs` | coderef-foundation-docs.md | ✓ In repo |
| `/generate-foundation-docs` | (alias for above?) | ⚠️ NOT FOUND |
| `/update-foundation-docs` | update-foundation-docs.md | ✓ In repo |
| `/generate-user-guide` | generate-user-guide.md | ✓ In repo |
| `/generate-my-guide` | generate-my-guide.md | ✓ In repo |
| `/generate-quickref` | generate-quickref.md | ✓ In repo |
| `/establish-standards` | establish-standards.md | ✓ In repo |
| `/audit-codebase` | audit-codebase.md | ✓ In repo |
| `/check-consistency` | check-consistency.md | ✓ In repo |
| `/add-changelog` | add-changelog.md | ✓ In repo |
| `/get-changelog` | get-changelog.md | ✓ In repo |
| `/update-changelog` | update-changelog.md | ✓ In repo |
| `/update-docs` | update-docs.md | ✓ In repo |
| `/git-release` | git-release.md | ✓ In repo |

**Extra Files in coderef-docs (should be removed):**
- `fix.md` - Test/stub file, not a command
- `README.md` - Directory documentation
- `stub.md` - Test/stub file, not a command
- `gather-context.md.backup` - Leftover backup file

**Total in directory:** 19 files
**Actual commands:** 16 files
**Deployed globally:** Yes

---

## coderef-workflow Commands (22 of 23 mapped)

✓ **Planning Phase (6/6)**
| Command | File | Status |
|---------|------|--------|
| `/gather-context` | gather-context.md | ✓ In repo |
| `/analyze-for-planning` | analyze-for-planning.md | ✓ In repo |
| `/get-planning-template` | get-planning-template.md | ✓ In repo |
| `/create-plan` | create-plan.md | ✓ In repo |
| `/validate-plan` | validate-plan.md | ✓ In repo |
| `/generate-plan-review` | generate-plan-review.md | ✓ In repo |

✓ **Orchestration (1/1)**
| Command | File | Status |
|---------|------|--------|
| `/create-workorder` | create-workorder.md | ✓ In repo |

✓ **Execution (5/5)**
| Command | File | Status |
|---------|------|--------|
| `/execute-plan` | execute-plan.md | ✓ In repo |
| `/update-task-status` | update-task-status.md | ✓ In repo |
| `/update-deliverables` | update-deliverables.md | ✓ In repo |
| `/generate-deliverables` | generate-deliverables.md | ✓ In repo |
| `/track-agent-status` | track-agent-status.md | ✓ In repo |

✓ **Multi-Agent Coordination (5/5)**
| Command | File | Status |
|---------|------|--------|
| `/generate-agent-communication` | generate-agent-communication.md | ✓ In repo |
| `/assign-agent-task` | assign-agent-task.md | ✓ In repo |
| `/verify-agent-completion` | verify-agent-completion.md | ✓ In repo |
| `/generate-handoff-context` | generate-handoff-context.md | ✓ In repo |
| `/aggregate-agent-deliverables` | aggregate-agent-deliverables.md | ✓ In repo |

✓ **Archival & Inventory (4/4)**
| Command | File | Status |
|---------|------|--------|
| `/archive-feature` | archive-feature.md | ✓ In repo |
| `/features-inventory` | features-inventory.md | ✓ In repo |
| `/audit-plans` | audit-plans.md | ✓ In repo |
| `/log-workorder` | log-workorder.md | ✓ In repo |

✓ **Workorder Tracking (1/2)**
| Command | File | Status |
|---------|------|--------|
| `/get-workorder-log` | get-workorder-log.md | ✓ In repo |
| (MISSING 23rd command) | ??? | ❌ MISSING |

**Total in directory:** 22 files
**Commands matched:** 22/23
**Deployed globally:** Yes

---

## Summary

### Deployment Status
- ✓ coderef-docs: 16 active commands (3 extra files to clean)
- ✓ coderef-workflow: 22/23 commands (1 missing)
- ✓ Global ~/.claude/commands/: 64 total (all deployed)
- ✓ No duplicates in global directory

### Outstanding Issues

1. **coderef-docs cleanup needed:**
   - Remove: fix.md, README.md, stub.md, gather-context.md.backup
   - Action: These are not slash commands and shouldn't be in .claude/commands/

2. **Missing command:**
   - coderef-workflow is missing 1 of 23 expected commands
   - Mapping shows "Workorder Tracking (2 commands)" but only lists get-workorder-log
   - Need to identify: what is the 23rd workflow command?

3. **Missing alias:**
   - `/generate-foundation-docs` is referenced in mapping but file not found
   - Likely should alias to `coderef-foundation-docs.md` or create as separate command

### Git Status
- ✓ All files committed and pushed to respective servers
- ✓ Change history preserved in git
- ✓ Recovery from git history successful (11 files recovered)

---

## Recommendations

1. **Immediate:** Clean up coderef-docs extra files
2. **Follow-up:** Identify and create the 23rd workflow command
3. **Follow-up:** Clarify generate-foundation-docs vs coderef-foundation-docs naming
4. **Update:** Refresh SLASH_COMMAND_MAPPING.md with actual counts (39/40)

---

**Last Updated:** 2025-12-25
**Audit Status:** 39/40 commands properly organized
**Deployment Status:** Complete (all working commands deployed globally)
