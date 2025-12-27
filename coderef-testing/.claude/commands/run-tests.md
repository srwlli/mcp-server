# Run Tests

Execute all tests in a project with automatic framework detection.

## Usage

```bash
run_tests [project_path] [options]
```

## Arguments

- `project_path` - (Optional) Path to project. Defaults to current directory.
- `--verbose` - Enable verbose output (show individual test results)
- `--timeout SECONDS` - Timeout per test (default: 300 seconds / 5 minutes)
- `--workers N` - Parallel workers (default: 8, max based on CPU cores)

## What It Does

1. Detects test framework in project
2. Discovers all tests
3. Executes tests in parallel with configurable workers
4. Captures results (pass/fail, duration, output)
5. Returns unified result summary

## Example

Run all tests in coderef-context:
```bash
run_tests C:\Users\willh\.mcp-servers\coderef-context
```

With options:
```bash
run_tests C:\Users\willh\.mcp-servers\coderef-workflow --verbose --workers 4 --timeout 600
```

Output includes:
```
Framework: pytest
Total: 45 tests
Passed: 43
Failed: 2
Skipped: 0
Duration: 12.4 seconds

Failed tests:
- test_plan_validation (4.2s)
- test_deployment_check (3.1s)
```

## Performance Notes

- Default 8 parallel workers for optimal speed
- Adjust `--workers` based on system resources
- Use `--timeout` for slow test suites (default 5 minutes)
- Results are logged for later review with `/test-results`

## Output Formats

- Summary view (default) - High-level pass/fail
- Verbose view - All test details with timings
- JSON export - Via `/test-report` command

## Related Commands

- `/discover-tests` - List all tests first
- `/test-results` - View previous test results
- `/test-report` - Generate formatted report
- `/test-performance` - Analyze test speed
- `/detect-flaky` - Find intermittently failing tests

## Tips

- Run after code changes to catch regressions
- Use verbose mode when debugging failures
- Adjust workers and timeout for your system
- Check `/test-health` for overall test suite status
