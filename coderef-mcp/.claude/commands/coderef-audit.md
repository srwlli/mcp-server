Audit CodeRef2 elements for validation, coverage, and performance issues.

Call the `mcp__coderef__audit` tool to perform comprehensive codebase audit.

**Usage Examples:**
- `/coderef-audit` - Audit entire codebase
- `/coderef-audit --scope element @Fn/utils/format` - Audit specific element
- `/coderef-audit --type coverage` - Coverage audit only

**Parameters:**
- scope: Audit scope - "all", "element", "path", "type" (default: "all")
- target: Optional target reference or path
- audit_type: Type of audit - "validation", "coverage", "performance" (default: "validation")
- include_issues: Include detailed issue list (default: true)

Returns: Audit report with issues, metrics, coverage analysis, and recommendations.
