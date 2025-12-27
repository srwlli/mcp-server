# Test Report

Generate formatted test reports in multiple formats.

## Usage

```bash
test_report [project_path] [options]
```

## Arguments

- `project_path` - (Optional) Path to project. Defaults to current directory.
- `--format FORMAT` - Output format: markdown, html, json (default: markdown)
- `--output FILE` - Save to file (optional, prints to console if omitted)
- `--include SECTIONS` - Sections to include: summary, details, metrics, trends (comma-separated)

## What It Does

1. Gathers latest test results
2. Analyzes results for insights
3. Formats report in requested format
4. Optionally saves to file

## Examples

Generate markdown report to console:
```bash
test_report C:\Users\willh\.mcp-servers\coderef-context
```

Generate HTML report and save:
```bash
test_report /path --format html --output report.html
```

Generate JSON for integration:
```bash
test_report /path --format json --output results.json
```

Generate detailed report with all sections:
```bash
test_report /path --format markdown --include summary,details,metrics,trends
```

Output (markdown format):
```markdown
# Test Report: coderef-context

**Generated:** 2025-12-27 14:25:30

## Summary
- Framework: pytest
- Total: 45 tests
- Passed: 43 (95.6%)
- Failed: 2 (4.4%)
- Duration: 12.4 seconds

## Status
🔴 FAILING - 2 test failures detected

## Failed Tests
1. test_invalid_schema (test_models.py:45)
2. test_deployment_check (test_integration.py:128)

## Performance
- Slowest: test_database_migration (4.2s)
- Average: 0.27s per test
- p95: 1.1s

## Trends
- Last 5 runs: 43 ✓, 45 ✓, 44 ⚠, 45 ✓, 43 ✗
- Trend: Unstable
```

## Format Details

| Format | Use Case |
|--------|----------|
| **markdown** | Documentation, GitHub, emails |
| **html** | Web browsers, dashboards |
| **json** | CI/CD integration, parsing |

## Report Sections

- **summary** - Overview stats
- **details** - Individual test results
- **metrics** - Performance, coverage analysis
- **trends** - Historical comparison

## Related Commands

- `/run-tests` - Generate fresh test results
- `/test-results` - View previous results
- `/test-trends` - Show historical trends
- `/test-coverage` - Code coverage details
- `/test-health` - Overall health check

## Tips

- Use markdown for sharing with team
- Use HTML for dashboards and reports
- Use JSON for CI/CD automation
- Include all sections for comprehensive reports
- Save to file for archiving and sharing
