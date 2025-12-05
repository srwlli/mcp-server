Log a quick idea or improvement stub.

Ask the user for:
1. **Title** (short, max 50 chars)
2. **Description** (brief, max 200 chars)
3. **Category** (feature/fix/improvement/idea/refactor) - default: idea
4. **Priority** (low/medium/high) - default: medium

Then:
1. Read `coderef/stubs/index.json`
2. Generate next STUB-XXX id from `next_id`
3. Add new entry to `stubs` array with timestamp
4. Increment `next_id`
5. Write updated index.json

Example stub entry:
```json
{
  "id": "STUB-003",
  "title": "Dark mode toggle",
  "description": "Add theme toggle with localStorage persistence",
  "category": "feature",
  "priority": "medium",
  "created": "2025-12-05T19:00:00Z"
}
```

Confirm with: "Logged STUB-XXX: {title}"
