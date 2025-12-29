# Update Docs Refactor - Analysis Notes

**Workorder:** WO-UPDATE-DOCS-REFACTOR-001
**Created:** 2025-12-28
**Context:** Consolidation analysis of redundant documentation commands

---

## Current State - Overlap Analysis

| Command | Tool | Updates | Approach | Version Handling |
|---------|------|---------|----------|------------------|
| `/record-changes` | `record_changes` | CHANGELOG.json only | Git auto-detection | Auto-calculates from git |
| `/update-docs` | `update_all_documentation` | README + CLAUDE.md + CHANGELOG.json | Agentic (agent memory) | Auto-increments semantic version |
| `/update-foundation-docs` | Manual edits | API.md, my-guide.md, user-guide.md | Manual workflow | No versioning |

## Redundancy Found

**Both `/record-changes` and `/update-docs` update CHANGELOG.json:**
- `/record-changes` - Git-based detection, changelog only
- `/update-docs` - Agent-based context, changelog + version files

**This IS redundant!** `/update-docs` is a superset of `/record-changes`.

---

## Proposed Solution: Unified Command

### New `/update-docs` Command Modes

```bash
# Full update (default) - all version control files
/update-docs feature-name

# Changelog only (replaces /record-changes)
/update-docs feature-name --changelog-only

# Include foundation docs review (replaces /update-foundation-docs)
/update-docs feature-name --with-foundation
```

### Unified Tool Design

**Tool:** `update_all_documentation` (enhanced)

**New Parameter:**
```python
scope: Literal["full", "changelog-only", "with-foundation"] = "full"
```

**Behavior by Scope:**

1. **"full" (default)**
   - Updates: README.md + CLAUDE.md + CHANGELOG.json
   - Uses: Agent context (current behavior)
   - Version: Auto-increments semantic version

2. **"changelog-only"**
   - Updates: CHANGELOG.json only
   - Uses: Git auto-detection (from record_changes)
   - Version: Auto-calculates from git diff

3. **"with-foundation"**
   - Updates: README + CLAUDE.md + CHANGELOG.json (like "full")
   - Then: Guides user through API.md, my-guide.md, user-guide.md updates
   - Manual: User reviews and updates foundation docs

---

## Implementation Plan

### Phase 1: Enhance Tool (2-3 hours)

**File:** `tool_handlers.py`

1. Add `scope` parameter to `update_all_documentation` tool schema
2. Merge git detection logic from `record_changes` into tool handler
3. Add foundation docs guidance when scope="with-foundation":
   ```python
   if scope == "with-foundation":
       # Guide user through:
       # - API.md (new tools)
       # - my-guide.md (tool lists)
       # - user-guide.md (features)
       # - ARCHITECTURE.md (patterns)
   ```

### Phase 2: Update Command (30 mins)

**File:** `~/.claude/commands/update-docs.md`

1. Add flag parsing:
   ```markdown
   Parameters:
   - feature-name (required)
   - --changelog-only (optional)
   - --with-foundation (optional)
   ```

2. Map flags to scope:
   ```
   No flags → scope="full"
   --changelog-only → scope="changelog-only"
   --with-foundation → scope="with-foundation"
   ```

### Phase 3: Deprecate Old Commands (15 mins)

**Files:**
- `~/.claude/commands/record-changes.md`
- `~/.claude/commands/update-foundation-docs.md`

Add deprecation notice:
```markdown
⚠️ DEPRECATED: This command is replaced by /update-docs

Use instead:
- /update-docs feature-name --changelog-only

Migration: [link to migration guide]
```

### Phase 4: Update Workflows (30 mins)

**Files to update:**
- `~/.claude/commands/complete-workorder.md`
- `~/.claude/commands/create-workorder.md`
- `coderef-workflow/CLAUDE.md`
- `coderef-workflow/README.md`

Replace references:
```
OLD: /record-changes → /update-docs
OLD: /update-foundation-docs → /update-docs --with-foundation
```

### Phase 5: Update Documentation (1 hour)

**Files:**
- `CLAUDE.md` - Update slash commands section
- `README.md` - Update workflow examples
- `my-guide.md` - Update tool list
- `user-guide.md` - Update usage examples

---

## Benefits

**Before:** 3 confusing commands
```
/record-changes         → CHANGELOG.json
/update-docs            → README + CLAUDE.md + CHANGELOG.json
/update-foundation-docs → API.md + my-guide.md + user-guide.md
```

**After:** 1 flexible command
```
/update-docs                      → README + CLAUDE.md + CHANGELOG.json (default)
/update-docs --changelog-only     → CHANGELOG.json (quick updates)
/update-docs --with-foundation    → All docs including API.md, guides
```

**Metrics:**
- ✅ 66% reduction in commands (3 → 1)
- ✅ Clearer mental model
- ✅ Backward compatible with flags
- ✅ Easier to maintain
- ✅ Less decision fatigue for users

---

## Migration Strategy

### Version 1.3.0 - Deprecation Notice
- Add deprecation warnings to old commands
- Document new unified command
- Update all internal workflows

### Version 1.4.0 - Grace Period
- Keep old commands functional with warnings
- Encourage migration in docs

### Version 2.0.0 - Removal
- Remove deprecated commands
- Unified command is the only option

---

## Testing Checklist

- [ ] Test full scope (default) - updates README + CLAUDE + CHANGELOG
- [ ] Test changelog-only scope - only updates CHANGELOG.json
- [ ] Test with-foundation scope - guides through foundation docs
- [ ] Test version auto-increment (breaking/feature/bugfix)
- [ ] Test git auto-detection (changelog-only mode)
- [ ] Test backward compatibility (existing /update-docs calls)
- [ ] Test /complete-workorder integration
- [ ] Verify CHANGELOG.json schema validation
- [ ] Test with workorder ID tracking
- [ ] Verify all documentation examples work

---

## Files to Modify

**Core Implementation:**
1. `server.py` - Update tool schema
2. `tool_handlers.py` - Merge record_changes logic
3. `~/.claude/commands/update-docs.md` - Add flags

**Deprecation:**
4. `~/.claude/commands/record-changes.md` - Add notice
5. `~/.claude/commands/update-foundation-docs.md` - Add notice

**Workflow Updates:**
6. `~/.claude/commands/complete-workorder.md` - Use unified command
7. `~/.claude/commands/create-workorder.md` - Update examples

**Documentation:**
8. `CLAUDE.md` - Update command list
9. `README.md` - Update workflow examples
10. `my-guide.md` - Update tool reference
11. `user-guide.md` - Update usage docs

---

## Estimated Effort

- Phase 1 (Tool enhancement): 2-3 hours
- Phase 2 (Command update): 30 mins
- Phase 3 (Deprecation): 15 mins
- Phase 4 (Workflow updates): 30 mins
- Phase 5 (Documentation): 1 hour
- Testing: 1 hour

**Total: 5-6 hours**

---

## Risk Assessment

**Low Risk:**
- Backward compatible (default behavior unchanged)
- Existing workflows continue to work
- Gradual migration with deprecation period

**Potential Issues:**
- Users might not notice deprecation warnings
- Need clear migration guide
- Must test all existing workflows

**Mitigation:**
- Prominent deprecation notices
- Comprehensive migration documentation
- Thorough testing before release
- Version major bump (2.0.0) for removal

---

## Success Criteria

1. **Functional:** All 3 original command behaviors available in unified command
2. **User Experience:** Single command for all doc update scenarios
3. **Backward Compatible:** Existing /update-docs calls work without changes
4. **Documentation:** Clear examples in all workflow docs
5. **Metrics:** 66% reduction in doc commands verified

---

**Next Steps:**
1. Review this analysis
2. Get approval for consolidation approach
3. Create implementation plan in plan.json
4. Execute refactor in phases
5. Update all documentation
6. Test thoroughly
7. Release with migration guide
