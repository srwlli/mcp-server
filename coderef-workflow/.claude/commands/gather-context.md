Gather feature requirements and context before planning implementation using interactive AskUserQuestion workflow.

This workflow helps you create a structured briefing (context.json) that captures WHAT the user wants before diving into HOW to implement it.

## Workflow

### Step 1: Get Feature Name

Use AskUserQuestion to ask for the feature name:

```
Question: "What's the feature name? (Use alphanumeric, hyphens, or underscores only)"
Header: "Feature Name"
multiSelect: false
Options: [
  {"label": "Let me type it", "description": "I'll provide a custom feature name"}
]
```

User will type their feature name in the "Other" field (e.g., "user-authentication", "dark-mode-toggle").

### Step 2: Get Feature Goal and Description

Use AskUserQuestion (2 separate questions):

**Question 1: What's the main goal?**
```
Question: "What's the primary goal of this feature?"
Header: "Main Goal"
multiSelect: false
Options:
  1. {"label": "Improve UX", "description": "Enhance user experience"}
  2. {"label": "Add functionality", "description": "New capability or feature"}
  3. {"label": "Fix bugs", "description": "Resolve existing issues"}
  4. {"label": "Performance", "description": "Speed or efficiency gains"}
```

**Question 2: Describe the feature**
```
Question: "Briefly describe what you want to build"
Header: "Description"
multiSelect: false
Options: [
  {"label": "Let me describe it", "description": "I'll provide a description"}
]
```

User types description in "Other" field.

### Step 3: Gather Requirements (Multi-Select)

Use AskUserQuestion with multiSelect: true

**Question: What are the must-have requirements? (Select all that apply)**
```
Question: "What are the must-have requirements? (Select all that apply)"
Header: "Requirements"
multiSelect: true
Options:
  1. {"label": "User authentication", "description": "Login/logout functionality"}
  2. {"label": "Data persistence", "description": "Save to database"}
  3. {"label": "API integration", "description": "Connect to external service"}
  4. {"label": "UI components", "description": "Visual interface elements"}
  5. {"label": "File operations", "description": "Read/write files"}
  6. {"label": "Real-time updates", "description": "WebSocket or SSE"}
  7. {"label": "Search functionality", "description": "Search and filter"}
  8. {"label": "Notifications", "description": "User alerts or messages"}
```

User can select multiple options + add custom requirements in "Other" field.

### Step 4: Identify Out of Scope Items

Use AskUserQuestion (conditional - ask if there are exclusions):

**Question: Are there features explicitly NOT included in this phase?**
```
Question: "Are there features explicitly NOT included in this phase?"
Header: "Out of Scope"
multiSelect: false
Options:
  1. {"label": "Yes", "description": "I'll specify what's excluded"}
  2. {"label": "No", "description": "Everything is in scope for now"}
```

If user selects "Yes", follow up with:
```
Question: "What features should be excluded? (Select all that apply)"
Header: "Excluded Items"
multiSelect: true
Options:
  1. {"label": "OAuth/Social login", "description": "Deferred to future phase"}
  2. {"label": "Two-factor auth", "description": "Deferred to future phase"}
  3. {"label": "Advanced analytics", "description": "Deferred to future phase"}
  4. {"label": "Mobile app", "description": "Deferred to future phase"}
  5. {"label": "Internationalization", "description": "Deferred to future phase"}
```

### Step 5: Gather Constraints (Multi-Select)

Use AskUserQuestion with multiSelect: true

**Question: Are there technical or business constraints? (Select all that apply)**
```
Question: "Are there technical or business constraints? (Select all that apply)"
Header: "Constraints"
multiSelect: true
Options:
  1. {"label": "Must work with PostgreSQL", "description": "Database compatibility"}
  2. {"label": "Must work with MySQL", "description": "Database compatibility"}
  3. {"label": "Must support mobile", "description": "Responsive design required"}
  4. {"label": "Performance < 100ms", "description": "Speed requirement"}
  5. {"label": "Backward compatible", "description": "Don't break existing features"}
  6. {"label": "Must work offline", "description": "Offline-first capability"}
  7. {"label": "Security compliant", "description": "GDPR, HIPAA, etc."}
  8. {"label": "Budget limited", "description": "Cost constraints"}
```

### Step 6: Call MCP Tool

After gathering all data via AskUserQuestion, call the MCP tool:

```python
mcp__docs_mcp__gather_context({
    "project_path": <current_working_directory>,
    "feature_name": <from_step_1>,
    "description": <from_step_2>,
    "goal": <from_step_2_question_1>,
    "requirements": [<from_step_3>],  # Array of selected labels
    "out_of_scope": [<from_step_4>],   # Array of excluded items or []
    "constraints": [<from_step_5>]     # Array of selected constraints or []
})
```

### Step 7: Confirm and Present Summary

After MCP tool creates context.json, present summary:

```
✅ Context gathered for feature: {feature_name}

📋 Summary:
- Goal: {goal}
- Requirements: {count} items
- Out of scope: {count} items
- Constraints: {count} items

📁 Saved to: coderef/workorder/{feature_name}/context.json

🔜 Next steps:
1. Run /analyze-for-planning to discover project details
2. Run /create-plan to generate implementation plan
3. Run /validate-plan to score plan quality
```

## Benefits of This Approach

✅ **Structured input** - Clear options vs. free-form text
✅ **Multi-select** - Choose multiple requirements/constraints at once
✅ **Faster** - Less back-and-forth typing
✅ **Validated** - Options ensure consistent data format
✅ **User-friendly** - Visual checkboxes and clear choices

## Context File Structure

The MCP tool creates this JSON structure:

```json
{
  "feature_name": "user-authentication",
  "description": "Add user login and registration system",
  "goal": "Add functionality - Enable user accounts",
  "requirements": [
    "User authentication",
    "Data persistence",
    "UI components"
  ],
  "out_of_scope": [
    "OAuth/Social login",
    "Two-factor auth"
  ],
  "constraints": [
    "Must work with PostgreSQL",
    "Backward compatible"
  ]
}
```

## Implementation Notes

**For AI Assistants:**
- Use AskUserQuestion tool for each step
- Set multiSelect: true for requirements, out_of_scope, constraints
- Set multiSelect: false for feature_name, description, goal
- Always provide options (Claude Code automatically adds "Other")
- Collect all responses BEFORE calling MCP tool
- Call mcp__docs_mcp__gather_context with all collected data at once
- Present confirmation summary after context.json is created

**Key principle:** This is REQUIREMENTS GATHERING, not implementation planning. Keep it simple - just capture WHAT and WHY, not HOW.
