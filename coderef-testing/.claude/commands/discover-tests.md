# Discover Tests

Scan a project to discover all tests and detect the test frameworks used.

## Usage

```bash
discover_tests [project_path]
```

## Arguments

- `project_path` - (Optional) Path to project to scan. Defaults to current directory.

## What It Does

1. Scans the project directory for test files
2. Auto-detects test frameworks (pytest, jest, vitest, cargo, mocha)
3. Lists all discovered tests with their locations
4. Shows framework versions and configuration

## Example

Discover tests in the CodeRef ecosystem:
```bash
discover_tests C:\Users\willh\.mcp-servers\coderef-context
```

Output includes:
- Test framework detected (pytest, jest, etc)
- Number of tests found
- Test files and locations
- Framework version

## Related Commands

- `/list-frameworks` - Show available test frameworks
- `/run-tests` - Execute discovered tests
- `/test-results` - View test results

## Tips

- Use relative paths or full absolute paths
- Works with any test framework (pytest, jest, vitest, cargo, mocha)
- Caches results for 5 minutes to improve performance
