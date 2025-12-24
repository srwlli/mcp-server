Read and query the global workorder log file.

Optionally prompt the user for filtering criteria:
- project_name: Filter by project name (partial match, case-insensitive, e.g., "personas" matches "personas-mcp")
- workorder_pattern: Filter by workorder ID pattern (e.g., "WO-AUTH" matches WO-AUTH-001, WO-AUTH-002)
- limit: Maximum number of entries to return

Then call the `mcp__docs-mcp__get_workorder_log` tool with:
- project_path: Current working directory
- Optional filters from above

This is useful for:
- Viewing recent workorder activity
- Finding workorders for specific projects
- Quick project status overview
- Searching workorder history by pattern

The tool returns:
- Workorder entries in reverse chronological order (latest first)
- Total count of all entries in log
- Filtered count based on search criteria
- Each entry includes: workorder_id, project, description, timestamp

Example queries:

1. **View all workorders:**
   ```
   /get-workorder-log
   (no filters - returns all entries)
   ```

2. **Find all docs-mcp workorders:**
   ```
   /get-workorder-log
   project_name: docs-mcp
   ```

3. **Find all AUTH-related workorders:**
   ```
   /get-workorder-log
   workorder_pattern: WO-AUTH
   ```

4. **Get latest 10 workorders:**
   ```
   /get-workorder-log
   limit: 10
   ```

Response format:
```json
{
  "entries": [
    {
      "workorder_id": "WO-AUTH-001",
      "project": "docs-mcp",
      "description": "Implement authentication system",
      "timestamp": "2025-10-21T02:08:51+00:00"
    }
  ],
  "total_count": 50,
  "filtered_count": 1,
  "log_file": "coderef/workorder-log.txt"
}
```

Example workflow:
1. User wants to see recent project activity
2. User runs /get-workorder-log
3. AI optionally asks for filters
4. AI retrieves and displays workorder entries
5. User can see recent work at a glance
