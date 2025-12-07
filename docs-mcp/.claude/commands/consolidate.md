Parse and consolidate multiple LLM responses into unified output.

## Workflow

1. Ask user for feature name:
   - This matches the folder in `coderef/working/{feature-name}/`
   - If user provides just a name (e.g., "playergenerator"), look for:
     - `coderef/working/playergenerator/llm-responses.txt`
   - If user provides a full path, use that

2. Ask user for output formats using AskUserQuestion (multiSelect: true):
   - json: Machine-readable, feeds into /create-plan
   - markdown: Human review, documentation
   - html: Visual comparison, side-by-side view

3. Verify feature directory exists:
   - `coderef/working/{feature-name}/`

4. Call the `mcp__docs-mcp__consolidate_llm_outputs` tool with:
   - input_file_path: `coderef/working/{feature-name}/llm-responses.txt`
   - output_dir: `coderef/working/{feature-name}/`
   - output_formats: The formats selected by user (default to ["json"] if none selected)

5. Report results to user:
   - Number of LLM sources detected
   - Total findings consolidated
   - Unique insights identified (only one LLM mentioned)
   - Conflicts found (if any)
   - Output file paths generated

6. If unique insights > 0, highlight them:
   "These insights were only caught by one LLM - worth extra attention"

7. If conflicts > 0, advise:
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

## Output Location

All outputs saved to `coderef/working/{feature-name}/`:
- `llm-consolidated.json` - Machine-readable merged results
- `llm-consolidated.md` - Human-readable summary
- `llm-consolidated.html` - Visual comparison view

## Integration with Planning Workflow

This command uses the same `coderef/working/{feature-name}/` folder as:
- `/gather-context` → context.json
- `/analyze-for-planning` → analysis.json
- `/create-plan` → plan.json
- `/llm-prompt` → llm-prompt.json
- `/consolidate` → llm-consolidated.json (this command)

After consolidation, the JSON output can be used with:
- `/create-plan` - Feed consolidated insights into implementation planning
- Manual review - Use markdown/html for human analysis
