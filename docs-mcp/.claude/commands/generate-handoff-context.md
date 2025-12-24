Generate automated agent handoff context for current feature.

Call the `mcp__coderef-docs__generate_handoff_context` tool with:
- Current working directory as project_path
- Feature name (ask user if not obvious from context)
- Mode: "full" for comprehensive context or "minimal" for quick summary (default: full)

This generates `claude.md` in `coderef/working/{feature}/` with:
- Auto-populated project overview from plan.json
- Current progress and task status
- Recent git commits and uncommitted changes
- Next steps from implementation checklist
- File references and resources

Reduces handoff time from 20-30 minutes to under 5 minutes by auto-populating 80%+ fields.

**Usage:**
```
/generate-handoff-context
# Claude asks: Which feature? (e.g., "auth-system")
# Claude asks: Mode? (full/minimal, default: full)
# Generates coderef/working/{feature}/claude.md
```

**When to use:**
- Before passing feature work to another agent
- Mid-phase checkpoints for progress documentation
- Creating quick context summaries (minimal mode)
