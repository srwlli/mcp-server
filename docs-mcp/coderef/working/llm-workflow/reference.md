# LLM Workflow Reference

## Goal

**Get the best, most comprehensive information by consolidating responses from multiple LLMs.**

Not rating models. Not comparing quality. Just: **don't miss anything important.**

---

## The Problem

When you ask one LLM to review code or suggest improvements:
- It catches some issues, misses others
- Limited to one perspective/training
- No way to know what was missed

When you ask multiple LLMs:
- Each catches different things
- Different perspectives and approaches
- But now you have 3 walls of text to manually synthesize

---

## The Solution

```
You: "Review this code for issues"
     │
     ├──► ChatGPT sees: memory leak, naming issues
     ├──► Claude sees: security flaw, edge case bug
     ├──► Gemini sees: performance issue, missing validation
     │
     ▼
Consolidated: ALL issues found (none missed)
```

**Collective intelligence > Single perspective**

---

## Use Cases

| Task | Why Multiple LLMs Help |
|------|------------------------|
| Code review | Each catches different bugs |
| Architecture suggestions | Different patterns and approaches |
| Implementation planning | More comprehensive requirements |
| Security audit | Different threat models |
| Refactoring ideas | Various approaches to consider |
| API design | Different conventions and best practices |
| Test coverage | Different edge cases identified |

---

## Integration with `/create-plan`

### Before
```
You ──► Single LLM ──► Plan (limited perspective)
```

### After
```
You ──► Multiple LLMs ──► Consolidated insights ──► Plan (comprehensive)
```

### Example

**Prompt:** "What should I consider when implementing user authentication?"

| LLM | Points Raised |
|-----|---------------|
| ChatGPT | JWT, session management, rate limiting |
| Claude | Password hashing, token refresh, audit logging |
| Gemini | OAuth flows, MFA, account recovery |

**Consolidated output feeds into create-plan:**
- All points captured
- Nothing missed
- Plan covers all angles
- Better implementation from the start

---

## Phased Implementation

### Phase 1: Manual Consolidation Tool (Now)

**Workflow:**
1. Query LLMs manually in browser
2. Copy/paste all responses into one text file
3. Run MCP tool to parse and consolidate
4. Get structured output with all insights

**What the tool does:**
- Auto-detect LLM response boundaries
- Extract and organize all points raised
- Identify unique insights (only one LLM mentioned)
- Flag conflicts that need human decision
- Generate consolidated summary

### Phase 2: Interactive Mode (Next)

- Ask clarifying questions: "Focus on security or performance?"
- Multiple output formats (markdown, JSON)
- Template system for consistent prompts

### Phase 3: API Automation (Future)

- Single prompt → auto-query all LLMs
- Real-time consolidation as responses arrive
- Optional, requires API keys

---

## Phase 1 Details

### Input (what you paste)

Messy is fine. Tool auto-detects:

```text
=== ChatGPT ===
When reviewing this code, I notice several issues...
- Memory leak in the connection handler
- Variable naming could be clearer

=== Claude ===
Looking at this code, here are my observations...
- Security: SQL injection vulnerability on line 45
- Edge case: null check missing for user input

=== Gemini ===
Code review findings:
- Performance: N+1 query in the loop
- Validation: Missing input sanitization
```

### Output (what you get)

```markdown
# Consolidated: Code Review Results

**Sources:** 3 LLMs
**Date:** 2025-12-06

## All Issues Found

### Security
- SQL injection vulnerability (line 45)
- Missing input sanitization

### Performance
- Memory leak in connection handler
- N+1 query in loop

### Code Quality
- Variable naming unclear
- Null check missing for user input

## Unique Insights
These were only mentioned by one LLM - worth extra attention:
- **Memory leak** - only ChatGPT caught this
- **N+1 query** - only Gemini caught this

## Conflicts to Resolve
- None identified

## Recommended Priority
1. SQL injection (security - critical)
2. Memory leak (will cause production issues)
3. N+1 query (performance)
4. Input validation (security)
5. Code quality items (cleanup)
```

---

## MCP Tool Design

### Tool: `consolidate_llm_outputs`

**Parameters:**
| Param | Required | Description |
|-------|----------|-------------|
| `input_file_path` | Yes | Text file with pasted LLM responses |
| `output_dir` | No | Where to save outputs (default: same dir as input) |
| `output_formats` | No | Array: ["json", "markdown", "html"] (default: ["json"]) |
| `focus` | No | What to emphasize: "all", "security", "performance" |

**Output Formats:**
| Format | File | Use Case |
|--------|------|----------|
| `json` | `consolidated.json` | Agentic consumption, feeds into /create-plan |
| `markdown` | `consolidated.md` | Human review, documentation |
| `html` | `consolidated.html` | Visual review, side-by-side comparison |

**Usage:**
```
mcp__docs_mcp__consolidate_llm_outputs({
    "input_file_path": "/path/to/responses.txt",
    "output_formats": ["json", "html"]
})
```

**Generates:**
```
/path/to/
├── responses.txt          (input)
├── consolidated.json      (agentic)
└── consolidated.html      (visual)
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `generators/llm_output_parser.py` | Detect LLM boundaries, extract responses |
| `generators/consolidation_engine.py` | Merge points, find uniques, flag conflicts |
| `templates/llm_query_template.txt` | Standard prompt format for consistency |
| `tool_handlers.py` | Add `handle_consolidate_llm_outputs()` |
| `server.py` | Register tool |

---

## Parser Strategy

### LLM Detection Patterns

```python
PATTERNS = [
    r"^={3,}\s*(ChatGPT|GPT-4|OpenAI)",
    r"^={3,}\s*(Claude|Anthropic)",
    r"^={3,}\s*(Gemini|Google|Bard)",
    r"^(ChatGPT|GPT-4)\s*(said|response|:)",
    r"^(Claude)\s*(said|response|:)",
    r"^(Gemini)\s*(said|response|:)",
    r"^From\s+(ChatGPT|Claude|Gemini)",
    r"^###?\s*(ChatGPT|Claude|Gemini)",
]
```

### Fallback

If can't detect source, label as "LLM 1", "LLM 2", etc. Still consolidates.

---

## Output Structure

### Markdown Format

```markdown
# Consolidated: {topic}

**Sources:** {count} LLMs
**Date:** {date}

## All Points Raised
- Point 1
- Point 2
- ...

## Unique Insights
Points only one LLM mentioned (may be important):
- **{point}** - only {LLM} mentioned this

## Conflicts
Different recommendations that need human decision:
- {topic}: LLM1 says X, LLM2 says Y

## Summary
{Consolidated recommendation or action items}
```

### JSON Format

```json
{
  "topic": "Code Review",
  "sources": ["ChatGPT", "Claude", "Gemini"],
  "all_points": [...],
  "by_category": {
    "security": [...],
    "performance": [...],
    "quality": [...]
  },
  "unique_insights": [
    {"point": "...", "source": "ChatGPT"}
  ],
  "conflicts": [],
  "summary": "..."
}
```

---

## Benefits

| Without Tool | With Tool |
|--------------|-----------|
| Read 3 long responses | Structured summary |
| Manually find overlaps | Auto-extracted |
| Miss unique insights | Highlighted |
| No conflict detection | Flagged for decision |
| Context scattered | Single document |

---

## Prompt Framework (Aligned with communication.json)

Following Lloyd's agentic communication pattern for consistent, structured output.

### Prompt Template Schema

```json
{
  "task": "{task_type}",
  "instruction": "{single sentence directive}",
  "context": {
    "input": "{user provided content}",
    "focus_areas": ["{area1}", "{area2}"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "findings": [],
      "recommendations": [],
      "risks": []
    }
  },
  "success_criteria": [
    "{criterion_1}",
    "{criterion_2}"
  ]
}
```

### Available Task Types

| Task Type | Instruction | Focus Areas |
|-----------|-------------|-------------|
| `code-review` | Analyze for issues and improvements | security, performance, quality |
| `architecture` | Evaluate design and suggest patterns | scalability, maintainability, coupling |
| `security-audit` | Identify vulnerabilities and risks | injection, auth, data exposure |
| `implementation` | Suggest approaches for requirements | feasibility, complexity, tradeoffs |
| `refactor` | Identify improvement opportunities | readability, DRY, patterns |

### Output Schema (All LLMs Return This)

```json
{
  "findings": [
    {
      "category": "string",
      "description": "string",
      "location": "string (optional)",
      "severity": "critical|high|medium|low"
    }
  ],
  "recommendations": [
    {
      "id": "string",
      "description": "string",
      "priority": "high|medium|low",
      "effort": "small|medium|large"
    }
  ],
  "risks": [
    {
      "description": "string",
      "severity": "high|medium|low",
      "likelihood": "high|medium|low"
    }
  ],
  "metrics": {
    "confidence": 0-100,
    "coverage": "comprehensive|partial|surface",
    "top_priorities": ["ranked list of most important items"],
    "summary_stats": {
      "critical_count": 0,
      "high_count": 0,
      "medium_count": 0,
      "low_count": 0
    }
  },
  "ranked_actions": [
    {
      "rank": 1,
      "action": "string",
      "reason": "why this is #1",
      "impact": "high|medium|low"
    }
  ]
}
```

### Metrics Explained

| Metric | Purpose |
|--------|---------|
| `confidence` | LLM's confidence in analysis (0-100) |
| `coverage` | How thoroughly the input was analyzed |
| `top_priorities` | Ranked list of most critical items |
| `summary_stats` | Counts by severity for quick triage |
| `ranked_actions` | Ordered list of recommended next steps |

### Why This Works

- **Consistent structure** → Easy parsing
- **JSON output** → Machine-readable, mergeable
- **Schema-defined** → All LLMs produce same shape
- **Aligned with Lloyd** → Same patterns as communication.json

---

## Success Criteria

Phase 1 is complete when:
- [ ] Tool parses messy multi-LLM input
- [ ] Extracts all points from all sources
- [ ] Identifies unique insights
- [ ] Flags conflicts
- [ ] Generates clean consolidated output
- [ ] Works with `/create-plan` workflow
