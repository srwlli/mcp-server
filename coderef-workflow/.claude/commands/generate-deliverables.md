Generate DELIVERABLES.md template for a feature from its plan.json file.

Ask the user for the feature name (alphanumeric, hyphens, underscores only), then call the `mcp__coderef-docs__generate_deliverables_template` tool with:
- project_path: current working directory
- feature_name: the user-provided feature name

This generates DELIVERABLES.md in coderef/workorder/{feature-name}/ with:
- Phase structure from plan.json
- Task checklists with [ ] checkboxes
- Metric placeholders (TBD) for LOC, commits, time spent
- Workorder ID from plan
- Status: 🚧 Not Started

**Prerequisites**:
- plan.json must exist in coderef/workorder/{feature-name}/
- Run `/create-plan` first if plan doesn't exist

**Note**: This command is automatically called by `/create-plan`, so you usually don't need to run it manually. Use this if you need to regenerate DELIVERABLES.md or if automatic generation failed.

Returns:
- Deliverables file path
- Feature name
- Workorder ID
- Phases count
- Tasks count
