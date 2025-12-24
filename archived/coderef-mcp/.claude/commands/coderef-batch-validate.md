Validate multiple CodeRef2 references in batch (sequential or parallel).

Call the `mcp__coderef__batch_validate` tool for bulk validation.

**Usage Examples:**
- `/coderef-batch-validate` - Validate all references in current file
- `/coderef-batch-validate --parallel` - Parallel processing

**Parameters:**
- references: Array of references to validate (required)
- parallel: Process in parallel (default: true)
- max_workers: Max concurrent workers (default: 5)
- timeout_ms: Timeout in milliseconds (default: 5000)

Returns: Batch validation results with per-reference status and aggregate metrics.
