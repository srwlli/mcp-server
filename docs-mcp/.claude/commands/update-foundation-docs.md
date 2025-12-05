Update foundation documentation after implementing a feature.

This command guides you through updating the relevant foundation docs based on what changed.

## When to Use

Run this **after** `/update-docs` and **before** `/archive-feature` when your feature:
- Adds new MCP tools (update API.md, my-guide.md)
- Changes architecture patterns (update ARCHITECTURE.md)
- Adds new components/generators (update COMPONENTS.md)
- Changes data schemas (update SCHEMA.md)
- Adds user-facing features (update user-guide.md, README.md)

## Workflow Position

```
/start-feature → implement → /update-deliverables → /update-docs → /update-foundation-docs → /archive-feature
```

## Instructions

### Step 1: Identify What Changed

Review your implementation to identify:
- New MCP tools added to server.py
- New slash commands added to .claude/commands/
- New generators added to generators/
- Architecture changes (new patterns, modules)
- Schema changes (new TypedDicts, JSON schemas)
- User-facing feature changes

### Step 2: Check Which Foundation Docs Exist

Look for these files in the project root or coderef/foundation-docs/:
- README.md - Project overview, features, quick start
- API.md - MCP tool documentation
- ARCHITECTURE.md - System design, patterns, modules
- COMPONENTS.md - Component/generator documentation
- SCHEMA.md - Data structures, TypedDicts, JSON schemas
- user-guide.md - Comprehensive usage documentation
- my-guide.md - Quick reference for tools/commands

### Step 3: Update Relevant Docs

For each doc that needs updating:

**If you added a new MCP tool:**
1. Update API.md - Add tool documentation (name, description, parameters, example)
2. Update my-guide.md - Add to tool list under appropriate category
3. Update user-guide.md - Add usage examples if user-facing
4. Update README.md - Add to features list if significant

**If you added a new slash command:**
1. Update my-guide.md - Add to slash commands section
2. Update user-guide.md - Add usage documentation
3. Update CLAUDE.md - Add to slash commands section (already done by /update-docs)

**If you changed architecture:**
1. Update ARCHITECTURE.md - Document new patterns, modules, or design decisions
2. Update COMPONENTS.md - Document new generators or components

**If you changed schemas:**
1. Update SCHEMA.md - Document new TypedDicts or JSON schemas
2. Update API.md - Update parameter/return types if affected

### Step 4: Verify Updates

After updating, verify:
- [ ] All new tools documented in API.md
- [ ] All new commands documented in my-guide.md
- [ ] User-facing features documented in user-guide.md
- [ ] Architecture changes documented in ARCHITECTURE.md
- [ ] README.md reflects current feature set

## Example

After adding a new `assess_risk` tool:

```
Updated files:
1. API.md - Added assess_risk tool documentation
2. my-guide.md - Added to "Risk Assessment Tools" section
3. user-guide.md - Added "Risk Assessment" usage guide
4. README.md - Added to features list
```

## Skip Conditions

You can skip this command if:
- Only internal refactoring (no API changes)
- Only bug fixes (no new features)
- Only test additions (no user-facing changes)
- Documentation-only changes

## Related Commands

- `/update-docs` - Updates changelog, README version, CLAUDE.md (run before this)
- `/generate-docs` - Regenerates foundation docs from scratch
- `/archive-feature` - Archives completed feature (run after this)
