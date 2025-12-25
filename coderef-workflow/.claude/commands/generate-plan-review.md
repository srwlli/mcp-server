Generate a JSON review report from implementation plan validation results.

Ask the user for the plan file path (e.g., "coderef/working/outdoor-gear-category/plan.json"), then call the `mcp__coderef-docs__generate_plan_review_report` tool with:
- project_path: current working directory
- plan_file_path: the user-provided plan path
- output_path: same directory as plan file, named "review.json"

For example, if plan is at `coderef/working/outdoor-gear-category/plan.json`, save review to `coderef/working/outdoor-gear-category/review.json`.

This tool transforms validation results into a comprehensive JSON report with:
1. Executive Summary (score, grade, result type, approval status)
2. Critical Issues (blocking problems that must be fixed)
3. Major Issues (significant concerns requiring attention)
4. Minor Issues (improvements and polish items)
5. Recommendations (actionable next steps prioritized by impact)
6. Validation Metadata (timestamp, plan file, score breakdown)

The report makes validation issues actionable and easy to understand for both humans and AI agents.

Use this after running /validate-plan to generate a formatted report for review or documentation.