Validate implementation plan quality for the current project.

Ask the user for the plan file path (e.g., "feature-auth-plan.json"), then call the `mcp__coderef-docs__validate_implementation_plan` tool with:
- project_path: current working directory
- plan_file_path: the user-provided plan filename

This tool validates the plan against the feature-implementation-planning-standard.json quality checklist:
1. Validates structure (all 10 sections present)
2. Validates completeness (no placeholders, all fields filled)
3. Validates quality (task descriptions ≥20 words, 5-10 edge cases, etc.)
4. Validates autonomy (zero ambiguity, actionable tasks)
5. Calculates score: 100 - (10×critical + 5×major + 1×minor)

Returns:
- Score (0-100)
- Validation result: PASS (≥90), PASS_WITH_WARNINGS (≥85), NEEDS_REVISION (≥70), FAIL (<70)
- Issues grouped by severity (critical/major/minor)
- Approval status

**Use iteratively**: Fix issues, re-validate, repeat until score ≥ 90 before presenting plan to user.