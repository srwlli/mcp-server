# List Frameworks

Show all detected test frameworks in a project and their versions.

## Usage

```bash
list_frameworks [project_path]
```

## Arguments

- `project_path` - (Optional) Path to project to scan. Defaults to current directory.

## What It Does

1. Auto-detects test frameworks in the project
2. Shows framework type, version, and location
3. Lists configuration files used by each framework
4. Indicates which frameworks are properly configured

## Example

List frameworks in coderef-workflow:
```bash
list_frameworks C:\Users\willh\.mcp-servers\coderef-workflow
```

Output shows:
```
Framework: pytest
  Version: 7.4.2
  Config: pyproject.toml
  Tests: /tests/*.py

Framework: (none detected)
```

## Supported Frameworks

- **pytest** - Python testing (pyproject.toml, pytest.ini, conftest.py)
- **jest** - JavaScript/TypeScript (package.json, jest.config.js)
- **vitest** - Vite test runner (vitest.config.ts, package.json)
- **cargo** - Rust testing (Cargo.toml [dev-dependencies])
- **mocha** - JavaScript test framework (package.json, .mocharc.js)

## Related Commands

- `/discover-tests` - Find all tests in project
- `/run-tests` - Execute tests for detected frameworks
- `/test-report` - Generate test results report

## Tips

- Results are cached for 5 minutes
- Run after adding new test files to refresh detection
- Works best with standard project layouts
