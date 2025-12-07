Generate a structured LLM prompt for multi-LLM querying with consistent JSON output.

## Workflow

1. Ask user for task type using AskUserQuestion:
   - code-review: Analyze code for issues and improvements
   - architecture: Evaluate design and suggest patterns
   - security-audit: Identify vulnerabilities and risks
   - implementation: Suggest approaches for requirements
   - refactor: Identify improvement opportunities

2. Ask user for their input (code, requirements, or description)

3. Load the appropriate template from `templates/prompts/{task-type}.json`

4. Generate the prompt by:
   - Reading the template
   - Substituting the user's input into the context.input field
   - Formatting as a ready-to-paste prompt

5. Output the prompt in this format:

```
# Task: {task}

## Instruction
{instruction}

## Context
{user_input}

## Focus Areas
{focus_areas as bullet list}

## Required Output Format
Respond with ONLY valid JSON matching this schema:

{output_schema}

## Success Criteria
{success_criteria as bullet list}
```

6. Tell user: "Copy this prompt and paste into ChatGPT, Claude, and Gemini. Collect their JSON responses into a single file, then run /consolidate"
