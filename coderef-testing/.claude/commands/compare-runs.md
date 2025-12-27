# Compare Runs

Compare two test runs to detect regressions or improvements.

## Usage

```bash
compare_runs [project_path] [run1] [run2] [options]
```

## Arguments

- `project_path` - Path to project
- `run1` - First test run (timestamp or ID)
- `run2` - Second test run (timestamp or ID, or 'latest' for most recent)
- `--format FORMAT` - Output format: summary, detailed (default: summary)

## What It Does

1. Retrieves two test runs
2. Compares results
3. Identifies regressions (new failures)
4. Identifies improvements (fixed tests)
5. Calculates metric deltas

## Examples

Compare latest run with previous:
```bash
compare_runs C:\Users\willh\.mcp-servers\coderef-context 2025-12-27T10:00:00 latest
```

Compare two specific runs:
```bash
compare_runs /path 2025-12-27T10:00:00 2025-12-27T14:00:00
```

Detailed comparison:
```bash
compare_runs /path 2025-12-26 latest --format detailed
```

Output (summary):
```
Comparison: Run 1 vs Run 2

Trend: REGRESSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tests Changed:
  Before: 45 total | 45 passed | 0 failed
  After:  45 total | 43 passed | 2 failed

Changes:
  ❌ 2 new failures
  ✅ 0 fixed
  ± 0 new tests

Failed Tests (NEW):
  - test_invalid_schema
  - test_deployment_check

Performance:
  Before: 12.1s average
  After:  12.4s average
  Δ: +0.3s (+2.5%)
```

## Trend Types

- **IMPROVEMENT** - Fewer failures, more passes
- **REGRESSION** - More failures than before
- **STABLE** - Same number of passes/failures

## Key Metrics

- Pass rate change
- Failure count change
- Duration change
- New tests added
- Tests removed
- Status changes per test

## Related Commands

- `/test-results` - View all results
- `/test-trends` - Show historical trends
- `/test-report` - Generate detailed report
- `/detect-flaky` - Find intermittently failing tests

## Tips

- Use 'latest' to always compare against most recent
- Run after code changes to catch regressions
- Detailed format shows all test changes
- Good for CI/CD validation
