Generate a structured LLM prompt for multi-LLM querying with consistent JSON output.

## Workflow

1. Ask user for feature name (e.g., "playergenerator", "auth-module")
   - This will be used for the folder name in `coderef/working/{feature-name}/`
   - Must be alphanumeric with hyphens/underscores only

2. Ask user for task type using AskUserQuestion:
   - code-review: Analyze code for issues and improvements
   - architecture: Evaluate design and suggest patterns
   - security-audit: Identify vulnerabilities and risks
   - implementation: Suggest approaches for requirements
   - refactor: Identify improvement opportunities

3. Ask user for their input (code, requirements, or description)
   - Or tell them they can paste the code at the bottom of the saved file

4. Load the appropriate template from `templates/prompts/{task-type}.json`

5. Create the feature working directory if it doesn't exist:
   - `coderef/working/{feature-name}/`

6. Generate and save the prompt as JSON to:
   - `coderef/working/{feature-name}/llm-prompt.json`

7. The saved file format:

```json
{
  "task": "{task_type}",
  "instruction": "{instruction from template}",
  "context": {
    "input": "[PASTE CODE HERE]",
    "focus_areas": ["{areas from template}"]
  },
  "output_schema": {
    "findings": [],
    "recommendations": [],
    "risks": [],
    "metrics": {},
    "ranked_actions": []
  },
  "success_criteria": ["{criteria from template}"]
}
```

8. Tell user:
   - "Saved to coderef/working/{feature-name}/llm-prompt.json"
   - "Paste your code in the 'input' field, then copy the entire JSON to each LLM"
   - "Save responses to coderef/working/{feature-name}/llm-responses.txt and run /consolidate"

## Integration with Planning Workflow

This command creates files in the same `coderef/working/{feature-name}/` folder used by:
- `/gather-context` → context.json
- `/analyze-for-planning` → analysis.json
- `/create-plan` → plan.json
- `/llm-prompt` → llm-prompt.json (this command)
- `/consolidate` → llm-consolidated.json
