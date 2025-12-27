# Test Performance

Analyze test execution performance and speed.

## Usage

```bash
test_performance [project_path] [options]
```

## Arguments

- `project_path` - (Optional) Path to project. Defaults to current directory.
- `--format FORMAT` - Output format: summary, detailed (default: summary)
- `--threshold SECONDS` - Flag tests slower than threshold
- `--count N` - Show top N slowest tests (default: 5)

## What It Does

1. Analyzes test execution times
2. Identifies slow tests
3. Calculates performance percentiles
4. Suggests optimization targets

## Examples

Check overall performance:
```bash
test_performance C:\Users\willh\.mcp-servers\coderef-context
```

Detailed performance analysis:
```bash
test_performance /path --format detailed --count 10
```

Find tests slower than 2 seconds:
```bash
test_performance /path --threshold 2.0
```

Output (summary):
```
Test Performance Analysis

Execution Metrics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Duration:   12.4 seconds
Average:          0.27 seconds per test
Median (p50):     0.15 seconds
p95:              1.1 seconds
p99:              4.2 seconds

Slowest Tests (Top 5):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. test_database_migration (4.2s) - database operations
2. test_api_integration (3.8s) - HTTP requests
3. test_file_processing (2.9s) - I/O operations
4. test_deployment_check (2.4s) - system calls
5. test_external_api (2.1s) - network latency

Fastest Tests (Top 5):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. test_auth_parse (0.01s)
2. test_validation_rules (0.02s)
3. test_schema_mapping (0.03s)
4. test_string_formatting (0.04s)
5. test_basic_arithmetic (0.05s)

Opportunities:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 5 tests > 2 seconds (consider optimization)
💡 Mock external APIs to speed up tests
💡 Use in-memory database for tests
💡 Parallelize independent test groups
```

## Performance Categories

| Duration | Category | Action |
|----------|----------|--------|
| < 0.1s | Fast | Excellent |
| 0.1-0.5s | Normal | Good |
| 0.5-2.0s | Slow | Review |
| > 2.0s | Very Slow | Optimize |

## Optimization Tips

- **Database tests** - Use in-memory DB or transactions
- **API tests** - Mock external services
- **File operations** - Use temp files, cleanup
- **Network tests** - Reduce timeouts, mock responses
- **Parallelization** - Run independent tests concurrently

## Related Commands

- `/run-tests` - Execute tests
- `/run-parallel` - Control parallelization
- `/test-health` - Overall health check
- `/detect-flaky` - Find unreliable tests

## Tips

- Regular performance monitoring catches regressions
- p95/p99 show max reasonable wait times
- Profile slow tests to find bottlenecks
- Use mocking to eliminate external dependencies
- Cache test data when possible
