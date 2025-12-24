Quick consistency check on modified files in the current project (pre-commit gate).

Call the `mcp__docs-mcp__check_consistency` tool with the current working directory as the project_path.

This is a lightweight, fast consistency check that:
1. Auto-detects git changes (staged files by default)
2. Only scans modified files (not the entire codebase)
3. Checks against established standards in coderef/standards/
4. Reports violations at or above the severity threshold
5. Can fail the check if violations are found (useful for CI/CD)

This is ideal for:
- Pre-commit hooks
- Pull request checks
- CI/CD pipeline gates
- Quick local validation before pushing

Much faster than a full codebase audit since it only checks changed files.