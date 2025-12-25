Log a quick idea as a stub for future feature work (centralized global backlog).

Ask the user for:
1. **Feature name** (slug format: lowercase, hyphens, e.g., "dark-mode-toggle")
2. **Description** (brief, 1-2 sentences)

Auto-detect:
- **Project** - From working directory context (agent knows this)
- **Created timestamp** - ISO format
- **Status** - Always "stub"

Then:
1. Create folder: `C:\Users\willh\Desktop\assistant\coderef\working\{feature-name}/`
2. Create `stub.json` with:
```json
{
  "feature_name": "{feature-name}",
  "description": "{description}",
  "project": "{project}",
  "created": "{ISO timestamp}",
  "status": "stub"
}
```

Confirm with: "Stubbed: C:\Users\willh\Desktop\assistant\coderef\working\{feature-name}\stub.json (from project: {project})"

Note: All stubs saved to centralized backlog location. When /create-workorder runs, it will detect stub.json and use it as initial context.
