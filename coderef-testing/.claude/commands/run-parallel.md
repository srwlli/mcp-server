# Run Parallel

Execute tests with specific parallelization settings.

## Usage

```bash
run_parallel [project_path] [options]
```

## Arguments

- `project_path` - (Optional) Path to project. Defaults to current directory.
- `--workers N` - Number of parallel workers (required)
- `--timeout SECONDS` - Timeout per test (default: 300)
- `--verbose` - Show detailed output

## What It Does

1. Detects test framework
2. Discovers all tests
3. Runs tests with specified parallelization
4. Monitors resource usage
5. Returns aggregated results

## Examples

Run tests with 4 workers:
```bash
run_parallel C:\Users\willh\.mcp-servers\coderef-context --workers 4
```

High parallelization for fast machines:
```bash
run_parallel /path --workers 16 --timeout 600
```

Low parallelization for resource-constrained systems:
```bash
run_parallel /path --workers 2 --timeout 300 --verbose
```

Output:
```
Parallelization: 4 workers
Total tests: 45
Batch 1: 12 tests → 8 passed, 4 running, 1 queued
Batch 2: 15 tests → 15 passed
Batch 3: 18 tests → 18 passed

Results:
Total: 45
Passed: 43
Failed: 2
Duration: 8.3 seconds
```

## Worker Count Guidelines

| System | Recommended |
|--------|-------------|
| 2-core laptop | 2-3 workers |
| 4-core machine | 4-6 workers |
| 8-core machine | 8-12 workers |
| 16+ core server | 12-20 workers |

## When to Use

- **High workers** - CI/CD, powerful machines, time-critical
- **Low workers** - Laptop, resource-constrained, local development
- **Default** - Auto-detected based on CPU cores

## Performance Impact

- **Too many workers** - Resource exhaustion, slower overall
- **Too few workers** - Underutilized resources
- **Optimal** - Usually 1-1.5x CPU core count

## Related Commands

- `/run-tests` - Run with default parallelization
- `/run-test-file` - Run single file
- `/test-performance` - Analyze test speed
- `/run-by-pattern` - Run matching tests

## Tips

- Monitor system resources while running
- Adjust for your specific system
- Use `/test-performance` to find bottlenecks
- Log worker output for debugging with `--verbose`
