# 🟡 READY: Agent Handoff - Phase 3C Available

**Agent:** coderef-docs
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001 Phase 3C
**Priority:** MEDIUM
**Status:** READY - Can start anytime
**Depends on:** None (can run in parallel with Phase 3B)

---

## Your Mission

You are the **coderef-docs agent**. The resource sheet generator outputs markdown but lacks **writing standards enforcement** and **documentation hierarchy**.

**Current problem:** Generated docs have inconsistent voice/tone, no navigation system
**Your job:** Build post-processor for writing standards + create 4-tier documentation hierarchy

---

## What You Must Do

### Task 1: PORT-001 - Writing Standards Post-Processor

**File to create:** `resource_sheet/processing/post_processor.py`

**Extract guidelines from:** `.claude/commands/create-resource-sheet.md` (lines 105-145)

**Writing guidelines to enforce:**

1. **Voice & Tone:** Imperative, not conversational
   - ❌ BAD: "We persist the state"
   - ✅ GOOD: "Component persists state"

2. **Precision:** No hedging words
   - ❌ BAD: "should probably", "might", "could"
   - ✅ GOOD: "must", "will", "does"

3. **Active Voice:** Avoid passive constructions
   - ❌ BAD: "State is managed by the component"
   - ✅ GOOD: "Component manages state"

4. **Tables Over Prose:** Structured data should be tables
   - ❌ BAD: Long paragraphs listing state fields
   - ✅ GOOD: State ownership table

5. **No Ambiguity:** Replace "should" with "must" or "may"
   - ❌ BAD: "You should validate input"
   - ✅ GOOD: "Must validate input"

**Implementation pattern:**

```python
"""
Post-processor for resource sheet writing standards.

WO-RESOURCE-SHEET-MCP-TOOL-001 Phase 3C
"""

from typing import List, Dict, Any
import re


class WritingViolation:
    """Represents a writing guideline violation."""
    def __init__(self, category: str, line: int, text: str, suggestion: str):
        self.category = category  # voice_tone, precision, active_voice, tables, ambiguity
        self.line = line
        self.text = text
        self.suggestion = suggestion


class DocumentPostProcessor:
    """Enforces writing guidelines on generated markdown."""

    def check_voice_tone(self, markdown: str) -> List[WritingViolation]:
        """Detect conversational phrases like 'we', 'you can'."""
        violations = []
        lines = markdown.split("\n")

        for i, line in enumerate(lines):
            # Check for "we" in imperative context
            if re.search(r'\bwe\s+(persist|manage|handle|create)', line, re.IGNORECASE):
                violations.append(WritingViolation(
                    category="voice_tone",
                    line=i+1,
                    text=line.strip(),
                    suggestion="Use imperative: 'Component persists' not 'We persist'"
                ))

            # Check for "you can"
            if re.search(r'\byou\s+can\b', line, re.IGNORECASE):
                violations.append(WritingViolation(
                    category="voice_tone",
                    line=i+1,
                    text=line.strip(),
                    suggestion="Use declarative: 'Clients call' not 'You can call'"
                ))

        return violations

    def check_precision(self, markdown: str) -> List[WritingViolation]:
        """Detect hedging words like 'probably', 'might'."""
        violations = []
        hedge_words = [
            r'\bshould probably\b',
            r'\bmight\b',
            r'\bcould\b',
            r'\bmaybe\b',
            r'\bperhaps\b'
        ]

        lines = markdown.split("\n")
        for i, line in enumerate(lines):
            for pattern in hedge_words:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(WritingViolation(
                        category="precision",
                        line=i+1,
                        text=line.strip(),
                        suggestion="Remove hedging - use 'must', 'will', or 'does'"
                    ))

        return violations

    def check_active_voice(self, markdown: str) -> List[WritingViolation]:
        """Detect passive voice patterns."""
        violations = []
        passive_patterns = [
            r'is managed by',
            r'was created by',
            r'are handled by',
            r'is used by'
        ]

        lines = markdown.split("\n")
        for i, line in enumerate(lines):
            for pattern in passive_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(WritingViolation(
                        category="active_voice",
                        line=i+1,
                        text=line.strip(),
                        suggestion="Use active voice: 'Component manages' not 'is managed by'"
                    ))

        return violations

    def check_table_usage(self, markdown: str) -> List[WritingViolation]:
        """Detect lists that should be tables."""
        # TODO: Implement detection logic
        # Look for repeated list patterns that could be tables
        return []

    def check_ambiguity(self, markdown: str) -> List[WritingViolation]:
        """Detect ambiguous 'should' usage."""
        violations = []
        lines = markdown.split("\n")

        for i, line in enumerate(lines):
            if re.search(r'\bshould\b', line, re.IGNORECASE):
                violations.append(WritingViolation(
                    category="ambiguity",
                    line=i+1,
                    text=line.strip(),
                    suggestion="Replace 'should' with 'must' (requirement) or 'may' (optional)"
                ))

        return violations

    def check_all(self, markdown: str) -> Dict[str, List[WritingViolation]]:
        """Run all checks and return violations by category."""
        return {
            "voice_tone": self.check_voice_tone(markdown),
            "precision": self.check_precision(markdown),
            "active_voice": self.check_active_voice(markdown),
            "tables": self.check_table_usage(markdown),
            "ambiguity": self.check_ambiguity(markdown)
        }

    def format_report(self, violations: Dict[str, List[WritingViolation]]) -> str:
        """Format violations as readable report."""
        report = []
        total = sum(len(v) for v in violations.values())

        report.append(f"# Writing Standards Report ({total} violations)\n")

        for category, items in violations.items():
            if items:
                report.append(f"\n## {category.replace('_', ' ').title()} ({len(items)})\n")
                for v in items:
                    report.append(f"- Line {v.line}: {v.text}\n")
                    report.append(f"  💡 {v.suggestion}\n")

        return "".join(report)
```

**Integration point:** Update `resource_sheet/composition/composer.py`:
```python
from resource_sheet.processing.post_processor import DocumentPostProcessor

# In compose_markdown():
markdown = self._build_markdown(...)

# Add post-processing
processor = DocumentPostProcessor()
violations = processor.check_all(markdown)

# Store violations in result (don't block generation)
result["writing_violations"] = violations
```

---

### Task 2: DOCS-001 - Documentation Hierarchy

**File to create:** `coderef/reference-sheets/INDEX.md`

**Structure:**

```markdown
# Resource Sheets - Documentation Index

## Navigation

**Finding documentation for any code element:**

1. **Start here:** Check if element has a reference sheet in `coderef/reference-sheets/{element}/`
2. **Not found?** Search foundation docs: `coderef/foundation-docs/` (ARCHITECTURE.md, API.md, SCHEMA.md)
3. **Still not found?** Check inline JSDoc comments in source code
4. **Need API docs?** See `docs/api/` (generated from JSDoc)

## Documentation Hierarchy (4 Tiers)

### Tier 1: Foundation Docs (Project-Wide)
- **Location:** `coderef/foundation-docs/`
- **Files:** ARCHITECTURE.md, SCHEMA.md, API.md, COMPONENTS.md
- **Purpose:** High-level project context and patterns
- **Authority:** ⭐⭐⭐⭐ Source of truth for project-wide decisions
- **Updated:** Manually by architects

### Tier 2: Reference Sheets (Element-Specific)
- **Location:** `coderef/reference-sheets/{element}/`
- **Files:** {element}.md, {element}.schema.json, {element}.jsdoc.txt
- **Purpose:** Detailed documentation for individual code elements
- **Authority:** ⭐⭐⭐ Source of truth for element behavior
- **Updated:** Via `/create-resource-sheet` command (semi-automated)

### Tier 3: Inline Documentation (In Source Code)
- **Location:** Source files (JSDoc comments)
- **Format:** `/** @see coderef/reference-sheets/{element}/{element}.md */`
- **Purpose:** IDE tooltips and quick reference
- **Authority:** ⭐⭐ Links to Tier 2, no independent authority
- **Updated:** Manually or via JSDoc file suggestions

### Tier 4: Generated API Docs (Public-Facing)
- **Location:** `docs/api/` (optional)
- **Format:** HTML/Markdown generated from JSDoc
- **Purpose:** External developer documentation
- **Authority:** ⭐ Derived from Tiers 2 and 3
- **Updated:** Generated via doc build tools

## Conflict Resolution

When documentation conflicts:

1. **Tier 1 wins for:** Project-wide patterns, architectural decisions, naming conventions
2. **Tier 2 wins for:** Element-specific behavior, state ownership, integration contracts
3. **Tier 3 links to Tier 2:** Never contradicts, only references
4. **Tier 4 derives from Tier 2/3:** Rebuild if out of sync

## Maintenance

**When code changes:**
1. Update source code (and inline JSDoc)
2. Run `/create-resource-sheet {element}` to regenerate reference sheet
3. Update foundation docs if architectural change
4. Rebuild API docs (Tier 4)

**When refactoring:**
- Reference sheets track element renames via git history
- Foundation docs reflect architectural shifts
- Inline docs stay synchronized via automation

## Quick Reference

| What are you looking for? | Where to look | Tier |
|----------------------------|---------------|------|
| How does AuthService work? | `reference-sheets/authservice/` | 2 |
| What's our error handling pattern? | `foundation-docs/ARCHITECTURE.md` | 1 |
| What params does useLocalStorage take? | Inline JSDoc in source | 3 |
| Public API documentation | `docs/api/` | 4 |

---

**Maintained by:** coderef-docs MCP tool
**Last Updated:** 2026-01-03
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001 Phase 3C
```

**Also update:** `README.md` with hierarchy diagram (add section showing 4 tiers)

---

## Success Criteria

**You are DONE when:**
- ✅ `resource_sheet/processing/post_processor.py` exists with 5 check methods
- ✅ `coderef/reference-sheets/INDEX.md` created with 4-tier hierarchy
- ✅ README.md updated with hierarchy diagram
- ✅ Post-processor integrated into composer (warnings only, doesn't block)

**How to test:**
```python
from resource_sheet.processing.post_processor import DocumentPostProcessor

# Test with intentional violations
test_markdown = """
We persist the state in localStorage.
You should probably validate input.
State is managed by the component.
"""

processor = DocumentPostProcessor()
violations = processor.check_all(test_markdown)
print(processor.format_report(violations))  # Should show 3-4 violations
```

---

## Reference Files

**Read these first:**
1. `fix-instructions-phase3c.json` - Full task specification
2. `.claude/commands/create-resource-sheet.md` (lines 105-145) - Writing guidelines to extract
3. `resource_sheet/composition/composer.py` - Where to integrate post-processor

---

## When You're Done

1. **Test post-processor** on sample markdown with violations
2. **Verify INDEX.md** provides clear navigation
3. **Update communication.json:**
```json
{
  "phase_3c_status": "complete",
  "writing_checks_implemented": 5,
  "hierarchy_tiers_documented": 4,
  "completed_by": "coderef-docs-agent",
  "completed_at": "2026-01-03T..."
}
```

4. **Notify orchestrator:** Update the main workorder that Phase 3C is complete

---

**START HERE:** Read `.claude/commands/create-resource-sheet.md` to extract writing guidelines, then create `post_processor.py`

**This is OPTIONAL for MVP** - post-processor can warn without blocking generation.
