# Run By Pattern

Execute tests matching a specific pattern or name.

## Usage

```bash
run_by_pattern [project_path] [pattern] [options]
```

## Arguments

- `project_path` - Path to project root
- `pattern` - Pattern to match test names (supports wildcards and regex)
- `--verbose` - Show detailed output
- `--timeout SECONDS` - Timeout for test execution

## What It Does

1. Detects test framework
2. Finds all tests matching the pattern
3. Executes matching tests
4. Returns results for matched tests

## Pattern Examples

Match by test name:
```bash
run_by_pattern /path "test_*validation*"
```

Match by test category:
```bash
run_by_pattern /path "test_auth_*"
```

Match by file and test:
```bash
run_by_pattern /path "test_models.py::test_*"
```

Regex pattern:
```bash
run_by_pattern /path "test_(auth|security)_.*" --verbose
```

## Real Examples

Run all authentication tests:
```bash
run_by_pattern C:\Users\willh\.mcp-servers\coderef-context "test_*auth*"
```

Run all plan-related tests in workflow:
```bash
run_by_pattern C:\Users\willh\.mcp-servers\coderef-workflow "test_plan_*" --verbose
```

Run performance tests only:
```bash
run_by_pattern /path "test_perf_*" --timeout 600
```

Output:
```
Pattern: test_*auth*
Framework: pytest
Matched tests: 8
Tests run: 8
Passed: 7
Failed: 1
Duration: 4.2 seconds
```

## Pattern Syntax

- `*` - Wildcard (matches any characters)
- `?` - Single character
- `[abc]` - Character class
- `[a-z]` - Range
- Regex: Full regex support for complex patterns

## Framework-Specific Notes

- **pytest** - Matches test function names and module names
- **jest/vitest/mocha** - Matches test descriptions
- **cargo** - Matches test function names

## Related Commands

- `/run-tests` - Execute all tests
- `/run-test-file` - Run single test file
- `/run-parallel` - Run with specific parallelization
- `/test-results` - View execution results

## Tips

- Use patterns to run test categories quickly
- Useful for testing specific features
- Combine with `--verbose` for debugging
- Results stored in test history
