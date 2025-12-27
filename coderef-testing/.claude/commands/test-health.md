# Test Health

Check overall test suite health and get a health score.

## Usage

```bash
test_health [project_path] [options]
```

## Arguments

- `project_path` - (Optional) Path to project. Defaults to current directory.
- `--detailed` - Show detailed health breakdown

## What It Does

1. Analyzes latest test results
2. Calculates health score (0-100)
3. Assigns letter grade (A-F)
4. Provides health status and recommendations

## Examples

Quick health check:
```bash
test_health C:\Users\willh\.mcp-servers\coderef-context
```

Detailed health analysis:
```bash
test_health /path --detailed
```

Output (summary):
```
Test Suite Health: coderef-context

Health Score: 87/100  Grade: B
Status: HEALTHY ✅

Metrics:
  Pass Rate:   95.6% (43/45)
  Error Rate:  0% (0/45)
  Skip Rate:   4.4% (2/45)

Performance:
  Duration:    12.4 seconds
  Average:     0.27s per test
  p95:         1.1 seconds

Summary:
  • Strong pass rate (95.6%)
  • No critical errors
  • Good performance profile
  • 2 tests skipped (check if intentional)

Recommendations:
  ✓ Passing (no changes needed)
  ⚠ Review skipped tests - ensure they're intentional
  💡 Consider increasing to 98%+ target
```

Detailed output:
```
Test Suite Health: coderef-context

Health Score: 87/100  Grade: B
Status: HEALTHY ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Metrics:
  Total Tests:       45
  Passed:            43 (95.6%) ✓
  Failed:            2 (4.4%) ✗
  Skipped:           0 (0%)
  Errors:            0 (0%)

Health Score Breakdown:
  Pass Rate:         95.6% → 38.2 points (weight: 40%)
  Error Rate:        0% → 40.0 points (weight: 40%)
  Skip Rate:         0% → 20.0 points (weight: 20%)
  ─────────────────────────────────
  Total Score:       98.2/100

Grade: A
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Performance:
  Total Duration:    12.4s
  Avg per Test:      0.27s
  Slowest Test:      4.2s
  Fastest Test:      0.01s
  Median (p50):      0.15s
  95th Percentile:   1.1s
  99th Percentile:   4.2s

Status Determination:
  Pass Rate > 95%:   HEALTHY
  No Errors:         ✓
  Skip Rate < 50%:   ✓
  Overall:           HEALTHY ✅

Trend Analysis:
  7-day trend:       Improving +2.3%
  Previous run:      Stable (-0.1%)

Recommendations:
  1. ✓ Maintain current pass rate
  2. ⚠ Investigate 2 failures in detail
  3. 💡 Consider caching strategy for slow tests
  4. 📈 Track trends to catch degradation early
```

## Health Grades

| Score | Grade | Status | Action |
|-------|-------|--------|--------|
| 90-100 | A | HEALTHY | ✓ Good |
| 80-89 | B | WARNING | ⚠ Monitor |
| 70-79 | C | FAILING | ✗ Fix soon |
| 60-69 | D | CRITICAL | 🚨 Fix now |
| <60 | F | FAILING | 🚨 Emergency |

## What's Included

- **Pass rate** - Percentage of passing tests (40%)
- **Error rate** - Percentage of tests with errors (40%)
- **Skip rate** - Percentage of skipped tests (20%)

## Status Types

- **HEALTHY** - 95%+ pass rate, no errors
- **WARNING** - 80-95% pass rate, some issues
- **FAILING** - < 80% pass rate, multiple failures
- **ERRORS** - High error rate (unexpected failures)
- **UNSTABLE** - High skip rate or flaky tests

## Related Commands

- `/run-tests` - Run tests to generate health data
- `/test-trends` - View health trends over time
- `/detect-flaky` - Find flaky tests
- `/test-report` - Detailed health report

## Tips

- Check health after code changes
- Monitor grade trends
- A grade (90+) is good for most projects
- B grade (80+) is acceptable with improvements planned
- <80 indicates serious issues to fix
- Use detailed mode for comprehensive analysis
