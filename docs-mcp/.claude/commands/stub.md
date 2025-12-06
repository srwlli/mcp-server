Log a quick idea as a stub for future feature work.

Ask the user for:
1. **Feature name** (slug format: lowercase, hyphens, e.g., "dark-mode-toggle")
2. **Description** (brief, 1-2 sentences)
3. **Category** (feature/fix/improvement/idea/refactor) - default: idea
4. **Priority** (low/medium/high) - default: medium

Then:
1. Create folder: `coderef/working/{feature-name}/`
2. Create `stub.json` with:
```json
{
  "feature_name": "{feature-name}",
  "description": "{description}",
  "category": "{category}",
  "priority": "{priority}",
  "created": "{ISO timestamp}",
  "status": "stub"
}
```

Confirm with: "Stubbed: coderef/working/{feature-name}/stub.json"

Note: When /start-feature runs, it will detect stub.json and use it as initial context.
