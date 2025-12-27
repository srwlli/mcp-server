# Test Coverage

Analyze and report code coverage metrics.

## Usage

```bash
test_coverage [project_path] [options]
```

## Arguments

- `project_path` - (Optional) Path to project. Defaults to current directory.
- `--format FORMAT` - Output format: summary, detailed (default: summary)
- `--threshold N` - Coverage threshold percentage (for validation)

## What It Does

1. Analyzes test results for coverage data
2. Calculates coverage metrics
3. Identifies gaps in coverage
4. Compares to threshold if specified

## Examples

Check coverage:
```bash
test_coverage C:\Users\willh\.mcp-servers\coderef-context
```

Detailed coverage report:
```bash
test_coverage /path --format detailed
```

Validate against 85% threshold:
```bash
test_coverage /path --threshold 85
```

Output (summary):
```
Code Coverage Analysis

Total Tests: 45
Passed: 43
Coverage: 95.6%

Coverage Status: EXCELLENT ✅

Top Covered Areas:
- Authentication module: 99.2%
- Database layer: 97.5%
- API handlers: 95.1%

Gaps to Address:
- Error handling: 78.3%
- Edge cases: 82.1%
- Legacy code: 61.5%
```

## Coverage Levels

| Score | Grade |
|-------|-------|
| 90-100% | Excellent (A) |
| 80-89% | Good (B) |
| 70-79% | Fair (C) |
| 60-69% | Poor (D) |
| <60% | Critical (F) |

## What Gets Measured

- Lines executed in tests
- Functions tested
- Branches covered
- Exception handling coverage

## Related Commands

- `/run-tests` - Generate test results
- `/test-results` - View coverage history
- `/test-health` - Overall test suite health
- `/test-report` - Detailed report with coverage

## Tips

- Run after adding new features to measure coverage impact
- Use threshold for CI/CD enforcement
- Detailed format shows specific files with gaps
- Focus on critical paths first (auth, data processing)
- Aim for 80%+ coverage in production code
