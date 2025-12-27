# Test Trends

Show historical trends in test results.

## Usage

```bash
test_trends [project_path] [options]
```

## Arguments

- `project_path` - (Optional) Path to project. Defaults to current directory.
- `--days N` - Show last N days of trends (default: 7)
- `--metric METRIC` - Focus on metric: pass_rate, failures, duration (default: pass_rate)
- `--format FORMAT` - Output format: summary, chart (default: summary)

## What It Does

1. Retrieves historical test results
2. Calculates trends over time
3. Identifies patterns (improving, degrading, stable)
4. Shows key metrics evolution

## Examples

Show last week of trends:
```bash
test_trends C:\Users\willh\.mcp-servers\coderef-context
```

Focus on failures:
```bash
test_trends /path --metric failures --days 14
```

Show test duration trends:
```bash
test_trends /path --metric duration --format chart
```

Output (summary):
```
Test Trends: coderef-context (Last 7 days)

Metric: Pass Rate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Day  Date         Pass Rate  Trend
 1   2025-12-27   95.6%      ↘ -2.2%
 2   2025-12-26   97.8%      ↗ +1.1%
 3   2025-12-25   96.7%      ↘ -2.3%
 4   2025-12-24   99.0%      → Same
 5   2025-12-23   99.0%      ↗ +4.4%
 6   2025-12-22   94.6%      ↗ +1.1%
 7   2025-12-21   93.5%      (baseline)

Analysis:
- Overall Trend: UNSTABLE
- Volatility: High (2-4% swings)
- Current State: Below 7-day average (95.6% vs 97.2%)
- Recommendation: Investigate recent changes
```

## Metrics Available

- **pass_rate** - Percentage of passing tests
- **failures** - Number of failing tests
- **duration** - Total test execution time
- **coverage** - Code coverage percentage

## Trend Types

- **↗ Improving** - Getting better over time
- **↘ Degrading** - Getting worse
- **→ Stable** - Consistent performance
- **~ Volatile** - Up and down

## Related Commands

- `/test-results` - View specific results
- `/compare-runs` - Compare two runs
- `/detect-flaky` - Find flaky tests
- `/test-health` - Overall health

## Tips

- Check trends after code changes
- Volatile trends indicate flaky tests
- Use to identify patterns in failures
- Weekly review helps catch gradual degradation
- Improving trends show positive impact
