Audit the current project for standards violations and generate a compliance report.

Call the `mcp__docs-mcp__audit_codebase` tool with the current working directory as the project_path.

This will:
1. Load established standards from coderef/standards/
2. Scan all source files for violations
3. Detect UI violations (non-standard button sizes, unapproved colors, typography issues)
4. Detect behavior violations (non-standard error messages, missing loading states)
5. Detect UX violations (missing ARIA attributes, keyboard navigation issues)
6. Calculate compliance score (0-100) and grade (A-F)
7. Generate comprehensive report in coderef/audits/

The report includes:
- Executive summary with score and grade
- Violations by severity (critical/major/minor)
- Violations by file (hotspot analysis)
- Fix recommendations

Review the report and address violations to improve code consistency.