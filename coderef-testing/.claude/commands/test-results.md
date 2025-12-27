# Test Results

View and query test execution results.

## Usage

```bash
test_results [project_path] [options]
```

## Arguments

- `project_path` - (Optional) Path to project. Defaults to current directory.
- `--format FORMAT` - Output format: json, markdown, summary (default: summary)
- `--limit N` - Show last N results (default: 5)
- `--framework FRAMEWORK` - Filter by framework (pytest, jest, etc)

## What It Does

1. Retrieves archived test results
2. Sorts by most recent first
3. Formats results for viewing
4. Shows trends and comparisons

## Examples

View latest test results:
```bash
test_results C:\Users\willh\.mcp-servers\coderef-context
```

View last 10 results:
```bash
test_results /path --limit 10
```

View as JSON for further processing:
```bash
test_results /path --format json
```

Filter by framework:
```bash
test_results /path --framework pytest --format markdown
```

Output (summary format):
```
Latest Test Results: coderef-context

Result 1: 2025-12-27 14:23:45
  Framework: pytest
  Total: 45 | Passed: 43 | Failed: 2 | Skipped: 0
  Duration: 12.4s
  Status: FAILING

Result 2: 2025-12-27 12:10:30
  Framework: pytest
  Total: 45 | Passed: 45 | Failed: 0 | Skipped: 0
  Duration: 11.8s
  Status: HEALTHY

Result 3: 2025-12-27 10:45:15
  Framework: pytest
  Total: 45 | Passed: 44 | Failed: 1 | Skipped: 0
  Duration: 12.1s
  Status: WARNING
```

## Output Formats

- **summary** - High-level overview (default)
- **markdown** - Formatted for documentation
- **json** - Full data for integration

## Related Commands

- `/run-tests` - Execute tests to generate results
- `/test-report` - Generate detailed report
- `/test-trends` - Show historical trends
- `/compare-runs` - Compare two test runs

## Tips

- Results are automatically archived with timestamps
- Use `--limit` to see historical progress
- JSON format useful for CI/CD integration
- Filter by framework for multi-framework projects
