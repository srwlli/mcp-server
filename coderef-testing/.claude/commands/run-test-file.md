# Run Test File

Execute a specific test file or set of test files.

## Usage

```bash
run_test_file [project_path] [test_file] [options]
```

## Arguments

- `project_path` - Path to project root
- `test_file` - Path to test file (relative to project)
- `--verbose` - Show detailed output
- `--timeout SECONDS` - Timeout for test execution

## What It Does

1. Validates test file exists in project
2. Detects framework (pytest/jest/cargo/mocha/vitest)
3. Executes only that test file
4. Returns results for tests in that file

## Examples

Run a pytest test file:
```bash
run_test_file C:\Users\willh\.mcp-servers\coderef-context tests/test_models.py
```

Run a jest test file:
```bash
run_test_file C:\Users\willh\.mcp-servers\coderef-workflow tests/unit/plan.test.js --verbose
```

Run with custom timeout:
```bash
run_test_file /path tests/slow.py --timeout 600
```

Output:
```
File: tests/test_models.py
Framework: pytest
Tests: 12
Passed: 11
Failed: 1
Skipped: 0
Duration: 2.3 seconds

Failed:
- test_invalid_schema
  Error: AssertionError at line 45
```

## Supported Formats

- `.py` files for pytest
- `.js`, `.ts`, `.jsx`, `.tsx` for jest/vitest/mocha
- `.rs` for cargo (test modules)
- Any framework-compatible test file

## Related Commands

- `/run-tests` - Execute entire test suite
- `/run-by-pattern` - Run tests matching a pattern
- `/test-results` - View all test results

## Tips

- Use after making changes to specific functionality
- Run with `--verbose` to debug failures
- Fastest way to validate single features
- Results are included in `/test-results` history
