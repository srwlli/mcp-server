Update DELIVERABLES.md with actual metrics from git commit history.

Ask the user for the feature name, then call the `mcp__docs-mcp__update_deliverables` tool with:
- project_path: current working directory
- feature_name: the user-provided feature name

This parses git history to calculate implementation metrics:
- **Lines of Code**: Added, deleted, net LOC from git diff
- **Commits**: Total commits, contributors from git log
- **Time Spent**: Days elapsed, wall clock hours from first to last commit

Replaces TBD placeholders in DELIVERABLES.md with actual values.
Updates status from 🚧 Not Started to ✅ Complete if commits found.

**Prerequisites**:
- DELIVERABLES.md must exist in coderef/working/{feature-name}/
- Project must be a git repository
- Feature-related commits must include feature name in commit messages

**Git Search**:
Searches commit messages for feature name (case-insensitive).
For best results, include feature name in your commit messages.

Example commits that will be found for feature "auth-system":
- "feat: implement auth-system with JWT tokens"
- "fix: auth-system validation bug"
- "docs: update AUTH-SYSTEM documentation"

**When to use**:
Run this command AFTER completing feature implementation to populate metrics.
Metrics are calculated from git history, so commit your work first.

Returns:
- Deliverables file path
- Commits found count
- LOC added/deleted/net
- Days/hours elapsed
