# EXPLICIT REWORK INSTRUCTIONS - True Direct Integration

**Date:** 2026-01-10
**Reason:** Current implementation uses "enhanced instructions" (Claude executes). Gap report requires TRUE direct integration (tool executes).

---

## What You Built (INCORRECT)

**Current approach:**
```python
# In tool_handlers.py - Tool returns TEXT instructions
result += "```python\n"
result += "from utils.validation_helpers import write_validation_metadata_to_frontmatter\n"
result += "validation_result = validator.validate_file(file_path)\n"
result += "write_validation_metadata_to_frontmatter(file_path, validation_result)\n"
result += "```\n"
# Claude reads this text and executes the code
```

**Problem:** Tool outputs instructions, Claude executes. This is NOT direct integration.

---

## What You MUST Build (CORRECT)

**Required approach:**
```python
# In tool_handlers.py - Tool EXECUTES code directly
from papertrail.validators.foundation import FoundationDocValidator
from utils.validation_helpers import write_validation_metadata_to_frontmatter
from pathlib import Path

# Tool saves file
output_path = Path(f"path/to/{template_name}.md")
with open(output_path, 'w') as f:
    f.write(content)

# Tool runs validator
validator = FoundationDocValidator()
validation_result = validator.validate_file(output_path)

# Tool writes metadata
write_validation_metadata_to_frontmatter(output_path, validation_result)

# Tool logs result
logger.info(f'Validation: {validation_result.score}/100')

# Tool returns simple message (NOT instructions)
return f"{template_name.upper()}.md generated and validated (score: {validation_result.score}/100)"
```

**Key difference:** Tool DOES the work, not Claude.

---

## Required Changes

### 1. Modify Foundation Doc Generator (tool_handlers.py)

**Function:** `handle_generate_individual_doc()`

**REMOVE:** All instruction-based validation blocks (lines 346-385)
**REMOVE:** Text that outputs Python code for Claude to execute

**ADD:** Direct validation code that tool executes

**Before (WRONG):**
```python
def handle_generate_individual_doc(template_name: str, project_path: str):
    # ... generate content ...

    # Return content + instructions for Claude
    result = template_content
    result += "\nVALIDATION:\n```python\n..."  # ❌ Returns instructions
    return result
```

**After (CORRECT):**
```python
def handle_generate_individual_doc(template_name: str, project_path: str):
    from papertrail.validators.foundation import FoundationDocValidator
    from utils.validation_helpers import write_validation_metadata_to_frontmatter
    from pathlib import Path
    import logging

    logger = logging.getLogger(__name__)

    # Generate content
    content = generate_template_content(template_name, project_path)

    # Determine output path
    output_path = Path(project_path) / f"{template_name.upper()}.md"

    # Save file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Run validator
    validator = FoundationDocValidator()
    validation_result = validator.validate_file(output_path)

    # Write validation metadata to frontmatter
    write_validation_metadata_to_frontmatter(output_path, validation_result)

    # Log validation result
    logger.info(f'{template_name}: Validation score {validation_result.score}/100')
    if validation_result.score < 90:
        logger.warning(f'{template_name}: Validation below threshold')
        for error in validation_result.errors:
            logger.error(f'  {error.severity}: {error.message}')

    # Return simple message (NO instructions)
    return {
        "file": str(output_path),
        "validation_score": validation_result.score,
        "errors": len(validation_result.errors),
        "warnings": len(validation_result.warnings),
        "message": f"{template_name.upper()}.md generated and validated"
    }
```

**Critical:** Tool SAVES file, RUNS validator, WRITES metadata. Claude does NOT execute code.

---

### 2. Modify Standards Doc Generator (tool_handlers.py)

**Function:** `handle_establish_standards()`

**REMOVE:** All instruction-based validation blocks (lines 816-865)

**ADD:** Direct validation code for all 3 standards files

**Before (WRONG):**
```python
def handle_establish_standards(project_path: str):
    # ... generate 3 standards files ...

    # Return instructions for Claude to validate
    result += "\nVALIDATION:\n```python\n..."  # ❌ Returns instructions
    return result
```

**After (CORRECT):**
```python
def handle_establish_standards(project_path: str):
    from papertrail.validators.standards import StandardsDocValidator
    from utils.validation_helpers import write_validation_metadata_to_frontmatter
    from pathlib import Path
    import logging

    logger = logging.getLogger(__name__)

    # Generate 3 standards files
    standards_files = ['ui-patterns.md', 'behavior-patterns.md', 'ux-patterns.md']
    generated_files = []

    for standard_file in standards_files:
        # Generate content
        content = generate_standards_content(standard_file, project_path)

        # Save file
        output_path = Path(project_path) / 'coderef' / 'standards' / standard_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Run validator
        validator = StandardsDocValidator()
        validation_result = validator.validate_file(output_path)

        # Write validation metadata to frontmatter
        write_validation_metadata_to_frontmatter(output_path, validation_result)

        # Log validation result
        logger.info(f'{standard_file}: Validation score {validation_result.score}/100')

        generated_files.append({
            "file": str(output_path),
            "validation_score": validation_result.score
        })

    # Return summary (NO instructions)
    return {
        "files": generated_files,
        "message": f"Generated and validated {len(generated_files)} standards files"
    }
```

---

### 3. Remove Instruction-Based Validation Entirely

**Current state:** Both instruction-based AND "enhanced" instructions exist

**Required:** REMOVE all instruction-based validation
- Delete lines 346-366 (foundation instruction blocks)
- Delete lines 816-838 (standards instruction blocks)
- Delete all code that outputs ```python validation code blocks
- Keep ONLY the direct integration code (tool executes)

**Rationale:** Gap report specifies ONE pattern: direct integration. Instruction-based was unauthorized deviation.

---

### 4. Update Tests

**REMOVE:** Tests that verify instruction presence
- `test_foundation_doc_includes_direct_validation_instructions` ❌
- `test_instruction_based_validation_still_outputs` ❌
- `test_both_patterns_coexist_foundation_docs` ❌
- All tests checking for instruction blocks in output ❌

**ADD:** Tests that verify direct integration
- `test_foundation_doc_has_validation_metadata_in_file` ✅
- `test_tool_saves_file_with_metadata` ✅
- `test_validation_runs_at_tool_runtime` ✅
- `test_no_instructions_in_output` ✅

**New test example:**
```python
def test_tool_saves_file_with_validation_metadata():
    """Verify tool saves file and writes _uds metadata (not Claude)."""
    # Call tool
    result = handle_generate_individual_doc('readme', '/tmp/test')

    # Verify file exists
    assert Path('/tmp/test/README.md').exists()

    # Read file and extract frontmatter
    with open('/tmp/test/README.md') as f:
        content = f.read()

    # Extract frontmatter
    frontmatter = yaml.safe_load(content.split('---')[1])

    # Verify _uds section exists
    assert '_uds' in frontmatter
    assert 'validation_score' in frontmatter['_uds']
    assert frontmatter['_uds']['validation_score'] >= 0
    assert frontmatter['_uds']['validation_score'] <= 100

    # Verify tool output does NOT contain instructions
    assert '```python' not in str(result)
    assert 'VALIDATION' not in str(result)
```

---

### 5. Update Documentation

**REMOVE:** All references to "both patterns" or "dual validation"
- CLAUDE.md: Remove "Pattern 1: Instruction-Based" section
- README.md: Remove "Why Both Patterns?" section
- ARCHITECTURAL-DECISION.md: Delete (incorrect approach)

**ADD:** Single pattern documentation
- "coderef-docs uses direct validation integration (matches gap report)"
- "Tool saves files, runs validators, writes metadata"
- "No instruction-based validation (deprecated)"

---

## What "Direct Integration" Means

**Definition:** Tool performs all operations at runtime, not Claude via instructions.

**Tool responsibilities:**
1. ✅ Generate content
2. ✅ Save file to disk
3. ✅ Run validator on saved file
4. ✅ Write validation metadata to frontmatter
5. ✅ Return simple result (NOT instructions)

**Claude responsibilities:**
1. ❌ Does NOT save file (tool already saved it)
2. ❌ Does NOT run validator (tool already ran it)
3. ❌ Does NOT write metadata (tool already wrote it)
4. ✅ Reads tool result and informs user

---

## Success Criteria (Updated)

❌ ~~Both patterns coexist~~ (WRONG - only one pattern allowed)
✅ Tool saves files directly (no Claude file writes)
✅ Tool runs validators at runtime (no Claude code execution)
✅ Tool writes `_uds` metadata to frontmatter (no Claude writes)
✅ Frontmatter `_uds` metadata appears in saved files
✅ Tool returns simple result dict (no instruction blocks)
✅ Tests verify tool behavior (not Claude behavior)
✅ No instruction-based validation code in tool output
✅ Documentation describes single pattern (direct integration)

---

## Explicit File Modifications

### File 1: tool_handlers.py

**Line 346-385: DELETE ENTIRELY**
```python
# DELETE THIS BLOCK:
if template_name in foundation_templates:
    result += "VALIDATION (WO-UDS-COMPLIANCE-CODEREF-DOCS-001):\n"
    result += "```python\n"
    # ... all instruction code ...
    result += "```\n"

    result += "DIRECT VALIDATION (WO-CODEREF-DOCS-DIRECT-VALIDATION-001):\n"
    result += "```python\n"
    # ... all instruction code ...
    result += "```\n"
```

**Replace with:**
```python
# Direct validation (tool executes)
if template_name in foundation_templates:
    from papertrail.validators.foundation import FoundationDocValidator
    from utils.validation_helpers import write_validation_metadata_to_frontmatter

    validator = FoundationDocValidator()
    validation_result = validator.validate_file(output_path)
    write_validation_metadata_to_frontmatter(output_path, validation_result)

    logger.info(f'Validated {template_name}: {validation_result.score}/100')
```

### File 2: tool_handlers.py (standards)

**Line 816-865: DELETE ENTIRELY**

**Replace with:**
```python
# Direct validation for all standards files (tool executes)
from papertrail.validators.standards import StandardsDocValidator
from utils.validation_helpers import write_validation_metadata_to_frontmatter

validator = StandardsDocValidator()
for file_path in generated_files:
    validation_result = validator.validate_file(file_path)
    write_validation_metadata_to_frontmatter(file_path, validation_result)
    logger.info(f'Validated {file_path.name}: {validation_result.score}/100')
```

### File 3: tests/test_direct_validation.py

**DELETE:** All tests checking for instruction blocks
**REWRITE:** All tests to verify file metadata, not output text

---

## Timeline

**Estimated effort:** 2-3 hours to rework

**Steps:**
1. ✅ Backup current implementation (15 min)
2. ✅ Modify tool_handlers.py foundation section (45 min)
3. ✅ Modify tool_handlers.py standards section (45 min)
4. ✅ Rewrite tests (60 min)
5. ✅ Update documentation (30 min)
6. ✅ Run tests, verify 100% passing (15 min)

---

## What You're Fixing

**Current implementation:**
- Tool outputs text instructions
- Claude reads and executes Python code
- Validation happens "indirectly" via Claude

**Correct implementation:**
- Tool executes validation code directly
- Tool saves files with metadata
- Claude receives simple result message
- Validation happens "directly" in tool runtime

**This is what gap report specified from the beginning.**

---

**STOP returning instruction blocks. START executing validation directly.**

**Questions?** None. These are explicit, mandatory instructions. Implement exactly as specified above.
