Parse and consolidate multiple LLM responses into unified output.

## Workflow

1. Ask user for the input file path using AskUserQuestion:
   - "What is the path to your LLM responses file?"

2. Ask user for output formats using AskUserQuestion (multiSelect: true):
   - json: Machine-readable, feeds into /create-plan
   - markdown: Human review, documentation
   - html: Visual comparison, side-by-side view

3. Call the `mcp__docs-mcp__consolidate_llm_outputs` tool with:
   - input_file_path: The file path provided by user
   - output_formats: The formats selected by user (default to ["json"] if none selected)

4. Report results to user:
   - Number of LLM sources detected
   - Total findings consolidated
   - Unique insights identified (only one LLM mentioned)
   - Conflicts found (if any)
   - Output file paths generated

5. If unique insights > 0, highlight them:
   "These insights were only caught by one LLM - worth extra attention"

6. If conflicts > 0, advise:
   "Review the conflicts section - these need human decision"

## Expected Input File Format

The tool auto-detects LLM boundaries. Example:

```text
=== ChatGPT ===
{
  "findings": [...],
  "recommendations": [...],
  "metrics": {...}
}

=== Claude ===
{
  "findings": [...],
  "recommendations": [...],
  "metrics": {...}
}

=== Gemini ===
{
  "findings": [...],
  "recommendations": [...],
  "metrics": {...}
}
```

## Integration

After consolidation, the JSON output can be used with:
- `/create-plan` - Feed consolidated insights into implementation planning
- Manual review - Use markdown/html for human analysis
