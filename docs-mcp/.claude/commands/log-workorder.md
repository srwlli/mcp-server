Log a new workorder entry to the global workorder log.

Prompt the user for the following required information:
- workorder_id: Workorder ID (format: WO-FEATURE-NAME-001, e.g., "WO-AUTH-001")
- project_name: Project name (short identifier, e.g., "coderef-docs", "personas-mcp")
- description: Brief description of the workorder (max 50 chars recommended, auto-truncated if longer)

Optional information:
- timestamp: ISO 8601 timestamp (auto-generated if not provided)

Then call the `mcp__coderef-docs__log_workorder` tool with:
- project_path: Current working directory
- All the information collected above

This is useful for:
- Tracking workorder completion with simple one-line entries
- Maintaining global project activity log
- Quick visibility into recent work across projects
- Enabling traceability between features and workorders

The log file format:
```
WO-ID | Project | Description | Timestamp
```

Example entries:
```
WO-AUTH-001 | coderef-docs | Implement authentication system | 2025-10-21T02:08:51+00:00
WO-FEATURE-002 | personas-mcp | Add new persona | 2025-10-21T01:30:00+00:00
```

Key features:
- Latest entries appear at top (reverse chronological)
- Saved to: coderef/workorder-log.txt
- Simple pipe-delimited format for easy reading
- Workorder ID validation (must match pattern ^WO-[A-Z0-9-]+-\d{3}$)

Example workflow:
1. User completes a workorder/feature
2. User runs /log-workorder
3. AI prompts for workorder details
4. AI logs entry to workorder-log.txt
5. Entry appears at top of log file
