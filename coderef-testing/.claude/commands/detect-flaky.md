# Detect Flaky

Find intermittently failing tests.

## Usage

```bash
detect_flaky [project_path] [options]
```

## Arguments

- `project_path` - (Optional) Path to project. Defaults to current directory.
- `--min-flakiness N` - Minimum flakiness % to report (default: 10)
- `--runs N` - Use last N test runs for analysis (default: 5)
- `--format FORMAT` - Output format: summary, detailed (default: summary)

## What It Does

1. Analyzes multiple test runs
2. Identifies tests with inconsistent results
3. Calculates flakiness percentage
4. Suggests fixes

## Examples

Find flaky tests:
```bash
detect_flaky C:\Users\willh\.mcp-servers\coderef-context
```

Detailed flakiness analysis:
```bash
detect_flaky /path --min-flakiness 20 --format detailed
```

Analyze across 10 runs:
```bash
detect_flaky /path --runs 10
```

Output (summary):
```
Flaky Test Detection

Analysis: Last 5 test runs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found: 3 Flaky Tests

🔴 CRITICAL (40-60% flaky)
- test_external_api_call (56% flaky)
  Passed: 2/5 | Failed: 3/5
  Pattern: Fails randomly (network timeout)

🟡 WARNING (20-40% flaky)
- test_concurrent_access (28% flaky)
  Passed: 4/5 | Failed: 1/5
  Pattern: Fails under load

- test_file_cleanup (25% flaky)
  Passed: 4/5 | Failed: 1/5
  Pattern: Order-dependent cleanup

Recommendations:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For test_external_api_call:
  → Mock API responses instead of calling live
  → Add retry logic with exponential backoff
  → Increase timeout to handle slow networks

For test_concurrent_access:
  → Use test fixtures to isolate state
  → Reduce parallelization during test
  → Add synchronization primitives

For test_file_cleanup:
  → Use setup/teardown properly
  → Don't depend on test execution order
  → Use temp directories per test
```

## Flakiness Levels

| % Flaky | Severity | Action |
|---------|----------|--------|
| < 10% | Minor | Monitor |
| 10-25% | Medium | Investigate |
| 25-50% | High | Fix soon |
| > 50% | Critical | Fix immediately |

## Common Causes

- **External dependencies** - Network, APIs, databases
- **Race conditions** - Concurrent access, timing issues
- **Non-deterministic code** - Random numbers, timestamps
- **Order dependency** - Tests affecting each other
- **Resource contention** - File locks, ports, memory
- **Timeouts** - Tests timeout under load

## Fixing Strategies

| Problem | Solution |
|---------|----------|
| External API | Mock responses |
| Race condition | Add locks/events |
| Non-determinism | Use seeded RNG |
| Order dependency | Isolate tests |
| Resource conflict | Use unique resources |
| Timeout | Increase or optimize |

## Related Commands

- `/run-tests` - Execute tests multiple times
- `/test-results` - View historical data
- `/test-trends` - See patterns over time
- `/run-parallel` - Test under load

## Tips

- Run tests multiple times to catch flakiness
- Focus on critical tests first
- Add `@flaky` marker to known flaky tests
- Re-run flaky tests to verify fixes
- Monitor after deployment for new flakiness
