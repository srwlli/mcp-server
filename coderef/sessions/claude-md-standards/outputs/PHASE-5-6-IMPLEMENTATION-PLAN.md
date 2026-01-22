# Phase 5 & 6 Implementation Plan

**Session:** claude-md-standards
**Workorder:** WO-CLAUDE-MD-STANDARDS-001
**Status:** Ready for Implementation
**Date:** 2026-01-22

---

## Overview

**Current Status:** Phases 1-4 complete (research, audit, standards, schemas)
**Next Steps:** Implement validator tools (Phase 5) and generator tools (Phase 6)

**Estimated Time:**
- Phase 5: 4-6 hours (Python implementation + testing)
- Phase 6: 4-6 hours (Python implementation + testing)
- **Total:** 8-12 hours

---

## Phase 5: Build Validator Tools (Papertrail MCP)

### Objective
Extend Papertrail MCP server with 4 new validator tools for CLAUDE.md and skill.md files.

### Implementation Location
**File:** `C:\Users\willh\.mcp-servers\papertrail\papertrail\server.py`

---

### Step 1: Add Tool Definitions to `list_tools()`

**Location:** `papertrail/server.py`, lines 22-147 (after existing tools)

**Code to add:**

```python
        Tool(
            name="validate_claude_md",
            description="Validate a CLAUDE.md file against claude-md-frontmatter-schema.json. Checks YAML frontmatter, line budget (530-600 for project, 300-400 for child), required sections, and progressive disclosure. Returns score (0-100), errors, and warnings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to CLAUDE.md file"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="check_all_claude_md",
            description="Validate all CLAUDE.md files in a directory recursively. Scans for files named CLAUDE.md, validates each against claude-md-frontmatter-schema.json, and returns summary with pass/fail counts, average score, and detailed results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Absolute path to directory to scan"
                    }
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="validate_skill",
            description="Validate a skill.md file against skill-frontmatter-schema.json. Checks YAML frontmatter (name, description, allowed-tools, model, context), line budget (300-500 lines), and content structure. Returns score (0-100), errors, and warnings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to skill.md file (in .claude/skills/ directory)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="check_all_skills",
            description="Validate all skill.md files in .claude/skills/ directory. Scans for all *.md files in skills directory, validates each against skill-frontmatter-schema.json, and returns summary with pass/fail counts and average score.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Absolute path to .claude/skills/ directory"
                    }
                },
                "required": ["directory"]
            }
        )
```

---

### Step 2: Add Tool Handlers to `call_tool()`

**Location:** `papertrail/server.py`, lines 154-171 (add elif branches before final else)

**Code to add:**

```python
    elif name == "validate_claude_md":
        return await validate_claude_md(arguments)
    elif name == "check_all_claude_md":
        return await check_all_claude_md(arguments)
    elif name == "validate_skill":
        return await validate_skill(arguments)
    elif name == "check_all_skills":
        return await check_all_skills(arguments)
```

---

### Step 3: Implement `validate_claude_md()` Function

**Location:** `papertrail/server.py` (after existing async functions)

**Implementation Pattern:** Based on existing `validate_resource_sheet()` (lines 247+)

**Pseudocode:**

```python
async def validate_claude_md(arguments: dict) -> list[TextContent]:
    """Validate a CLAUDE.md file against claude-md-frontmatter-schema.json."""
    file_path = Path(arguments["file_path"])

    # 1. Check file exists
    if not file_path.exists():
        return [TextContent(type="text", text=f"Error: File not found: {file_path}")]

    # 2. Enforce naming convention
    if not file_path.name == "CLAUDE.md":
        return [TextContent(type="text", text=f"Error: File must be named 'CLAUDE.md', got: {file_path.name}")]

    try:
        # 3. Extract YAML frontmatter
        frontmatter, body = extract_yaml_frontmatter(file_path)

        # 4. Validate frontmatter against schema
        schema_path = Path(__file__).parent / "schemas" / "documentation" / "claude-md-frontmatter-schema.json"
        is_valid, errors, warnings = validate_json_against_schema(frontmatter, schema_path)

        # 5. Calculate line count
        line_count = count_lines(file_path)

        # 6. Check line budget based on file_type
        file_type = frontmatter.get("file_type", "project")
        if file_type == "project":
            target_min, target_max = 530, 600
        else:  # child
            target_min, target_max = 300, 400

        # 7. Check line budget compliance
        if line_count < target_min:
            warnings.append(f"Line count below target: {line_count} < {target_min}")
        elif line_count > target_max:
            errors.append(f"Line count exceeds budget: {line_count} > {target_max}")

        # 8. Check required sections (parse markdown headers)
        required_sections = get_required_sections(file_type)  # from schema
        found_sections = extract_markdown_headers(body)
        missing_sections = set(required_sections) - set(found_sections)

        if missing_sections:
            errors.extend([f"Missing required section: {section}" for section in missing_sections])

        # 9. Calculate compliance score (0-100)
        score = calculate_compliance_score(
            line_count=line_count,
            target_min=target_min,
            target_max=target_max,
            sections_found=len(found_sections),
            sections_required=len(required_sections),
            errors=len(errors),
            warnings=len(warnings)
        )

        # 10. Format response
        response = format_validation_response(
            file_path=file_path,
            is_valid=is_valid,
            score=score,
            line_count=line_count,
            target_range=(target_min, target_max),
            errors=errors,
            warnings=warnings,
            file_type=file_type
        )

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error validating CLAUDE.md: {str(e)}")]
```

---

### Step 4: Implement `check_all_claude_md()` Function

**Implementation Pattern:** Based on existing `check_all_resource_sheets()` (similar batch pattern)

**Pseudocode:**

```python
async def check_all_claude_md(arguments: dict) -> list[TextContent]:
    """Batch validate all CLAUDE.md files in directory."""
    directory = Path(arguments["directory"])

    # 1. Find all CLAUDE.md files recursively
    claude_md_files = list(directory.rglob("CLAUDE.md"))

    if not claude_md_files:
        return [TextContent(type="text", text=f"No CLAUDE.md files found in: {directory}")]

    # 2. Validate each file
    results = []
    for file_path in claude_md_files:
        result = await validate_claude_md({"file_path": str(file_path)})
        results.append((file_path, result))

    # 3. Calculate summary stats
    total_files = len(results)
    passed_files = sum(1 for _, result in results if "[PASS]" in result[0].text)
    failed_files = total_files - passed_files

    # 4. Calculate average score (parse scores from results)
    scores = [extract_score_from_result(result) for _, result in results]
    avg_score = sum(scores) / len(scores) if scores else 0

    # 5. Format summary response
    response = f"# CLAUDE.md Validation Summary\n\n"
    response += f"**Directory:** {directory}\n"
    response += f"**Files Scanned:** {total_files}\n"
    response += f"**Passed:** {passed_files} ({passed_files/total_files*100:.1f}%)\n"
    response += f"**Failed:** {failed_files} ({failed_files/total_files*100:.1f}%)\n"
    response += f"**Average Score:** {avg_score:.1f}/100\n\n"

    # 6. Add detailed results per file
    response += "## Detailed Results\n\n"
    for file_path, result in results:
        response += f"### {file_path.relative_to(directory)}\n\n"
        response += result[0].text + "\n\n---\n\n"

    return [TextContent(type="text", text=response)]
```

---

### Step 5: Implement `validate_skill()` Function

**Similar to `validate_claude_md()` but with skill-specific validation:**

**Pseudocode:**

```python
async def validate_skill(arguments: dict) -> list[TextContent]:
    """Validate a skill.md file against skill-frontmatter-schema.json."""
    file_path = Path(arguments["file_path"])

    # 1. Check file exists
    if not file_path.exists():
        return [TextContent(type="text", text=f"Error: File not found: {file_path}")]

    # 2. Enforce naming convention (must be in .claude/skills/ and end with .md)
    if not file_path.suffix == ".md":
        return [TextContent(type="text", text=f"Error: Skill file must be .md file, got: {file_path.suffix}")]

    try:
        # 3. Extract YAML frontmatter
        frontmatter, body = extract_yaml_frontmatter(file_path)

        # 4. Validate frontmatter against schema
        schema_path = Path(__file__).parent / "schemas" / "documentation" / "skill-frontmatter-schema.json"
        is_valid, errors, warnings = validate_json_against_schema(frontmatter, schema_path)

        # 5. Check required frontmatter fields
        if "name" not in frontmatter:
            errors.append("Missing required field: name")
        elif not is_kebab_case(frontmatter["name"]):
            errors.append(f"Skill name must be kebab-case, got: {frontmatter['name']}")

        if "description" not in frontmatter:
            errors.append("Missing required field: description")

        # 6. Calculate line count
        line_count = count_lines(file_path)
        target_min, target_max = 300, 500

        # 7. Check line budget
        if line_count < target_min:
            warnings.append(f"Line count below target: {line_count} < {target_min}")
        elif line_count > target_max:
            errors.append(f"Line count exceeds budget: {line_count} > {target_max}")

        # 8. Check content structure (has step headers, verification section)
        has_steps = check_for_step_headers(body)  # "## Step 1:", "## Step 2:", etc.
        has_verification = "## Verification" in body

        if not has_steps:
            warnings.append("Content should have step-by-step structure (## Step 1:, ## Step 2:, etc.)")
        if not has_verification:
            warnings.append("Missing ## Verification section (how to verify success)")

        # 9. Calculate compliance score
        score = calculate_skill_compliance_score(
            line_count=line_count,
            target_min=target_min,
            target_max=target_max,
            has_required_fields=("name" in frontmatter and "description" in frontmatter),
            has_steps=has_steps,
            has_verification=has_verification,
            errors=len(errors),
            warnings=len(warnings)
        )

        # 10. Format response
        response = format_skill_validation_response(
            file_path=file_path,
            is_valid=is_valid,
            score=score,
            line_count=line_count,
            target_range=(target_min, target_max),
            errors=errors,
            warnings=warnings,
            frontmatter=frontmatter
        )

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error validating skill: {str(e)}")]
```

---

### Step 6: Implement `check_all_skills()` Function

**Similar to `check_all_claude_md()` but scans .claude/skills/ directory:**

**Pseudocode:**

```python
async def check_all_skills(arguments: dict) -> list[TextContent]:
    """Batch validate all skill.md files in .claude/skills/ directory."""
    directory = Path(arguments["directory"])

    # 1. Find all .md files in skills directory (not recursive for skills)
    skill_files = list(directory.glob("*.md"))

    # 2. Also check subdirectories (for skills with directory structure)
    skill_files.extend(list(directory.glob("*/skill.md")))

    if not skill_files:
        return [TextContent(type="text", text=f"No skill files found in: {directory}")]

    # 3. Validate each file
    results = []
    for file_path in skill_files:
        result = await validate_skill({"file_path": str(file_path)})
        results.append((file_path, result))

    # 4. Calculate summary stats (similar to check_all_claude_md)
    total_files = len(results)
    passed_files = sum(1 for _, result in results if "[PASS]" in result[0].text)
    failed_files = total_files - passed_files
    scores = [extract_score_from_result(result) for _, result in results]
    avg_score = sum(scores) / len(scores) if scores else 0

    # 5. Format summary response
    response = f"# Skill Validation Summary\n\n"
    response += f"**Directory:** {directory}\n"
    response += f"**Skills Scanned:** {total_files}\n"
    response += f"**Passed:** {passed_files} ({passed_files/total_files*100:.1f}%)\n"
    response += f"**Failed:** {failed_files} ({failed_files/total_files*100:.1f}%)\n"
    response += f"**Average Score:** {avg_score:.1f}/100\n\n"

    # 6. Add detailed results per file
    response += "## Detailed Results\n\n"
    for file_path, result in results:
        response += f"### {file_path.name}\n\n"
        response += result[0].text + "\n\n---\n\n"

    return [TextContent(type="text", text=response)]
```

---

### Step 7: Create Helper Functions

**File:** `papertrail/validators/claude_md_helpers.py` (new file)

**Functions needed:**

```python
import re
import yaml
from pathlib import Path
from typing import Tuple, List, Dict, Any

def extract_yaml_frontmatter(file_path: Path) -> Tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and body from markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for YAML frontmatter (starts with --- and ends with ---)
    if not content.startswith('---'):
        return {}, content

    # Find end of frontmatter
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return {}, content

    frontmatter_str = match.group(1)
    body = match.group(2)

    frontmatter = yaml.safe_load(frontmatter_str)
    return frontmatter, body

def count_lines(file_path: Path) -> int:
    """Count total lines in file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return len(f.readlines())

def extract_markdown_headers(content: str) -> List[str]:
    """Extract ## headers from markdown content."""
    headers = re.findall(r'^## (.+)$', content, re.MULTILINE)
    return headers

def is_kebab_case(text: str) -> bool:
    """Check if text is kebab-case (lowercase with hyphens)."""
    return bool(re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', text))

def check_for_step_headers(content: str) -> bool:
    """Check if content has step-by-step headers (## Step 1:, etc.)."""
    return bool(re.search(r'## Step \d+:', content))

def calculate_compliance_score(
    line_count: int,
    target_min: int,
    target_max: int,
    sections_found: int,
    sections_required: int,
    errors: int,
    warnings: int
) -> int:
    """Calculate compliance score (0-100) based on multiple factors."""
    score = 100

    # Line budget (25 points)
    if target_min <= line_count <= target_max:
        line_budget_score = 25
    elif line_count < target_min:
        under_by = target_min - line_count
        line_budget_score = max(0, 25 - (under_by / 50) * 10)  # -10 pts per 50 lines under
    else:  # line_count > target_max
        over_by = line_count - target_max
        line_budget_score = max(0, 25 - (over_by / 50) * 10)  # -10 pts per 50 lines over

    # Sections (30 points)
    section_score = (sections_found / sections_required) * 30 if sections_required > 0 else 30

    # Errors (deduct 5 pts per error, max -25)
    error_deduction = min(25, errors * 5)

    # Warnings (deduct 2 pts per warning, max -15)
    warning_deduction = min(15, warnings * 2)

    # Format quality (15 points) - placeholder for now
    format_score = 15  # TODO: Check tables, code blocks, etc.

    score = line_budget_score + section_score + format_score - error_deduction - warning_deduction
    return max(0, min(100, int(score)))

def get_required_sections(file_type: str) -> List[str]:
    """Get required sections based on CLAUDE.md file type."""
    if file_type == "project":
        return [
            "Quick Summary",
            "Problem & Vision",
            "Architecture",
            "Workflows Catalog",
            "Core Workflows",
            "File Structure",
            "Design Decisions",
            "Integration Guide",
            "Essential Commands",
            "Progressive Disclosure Guide",
            "Tool Sequencing Patterns",
            "Subagent Delegation Guide"
        ]
    else:  # child
        return [
            "Quick Summary",
            "Parent Context",
            "Component Purpose",
            "Architecture",
            "Workflows Catalog",
            "Core Workflows",
            "File Structure",
            "Integration with Parent",
            "Essential Commands"
        ]
```

---

### Step 8: Testing

**Test against existing files from Phase 2 audit:**

```python
# Test 1: Validate assistant CLAUDE.md (expected score: 92/100)
await validate_claude_md({"file_path": "C:\\Users\\willh\\Desktop\\assistant\\CLAUDE.md"})

# Test 2: Validate coderef-workflow CLAUDE.md (expected score: 55/100, critical bloat)
await validate_claude_md({"file_path": "C:\\Users\\willh\\.mcp-servers\\coderef-workflow\\CLAUDE.md"})

# Test 3: Batch validate all CodeRef CLAUDE.md files
await check_all_claude_md({"directory": "C:\\Users\\willh\\.mcp-servers"})

# Test 4: Validate coderef-scanner skill
await validate_skill({"file_path": "C:\\Users\\willh\\Desktop\\assistant\\.claude\\skills\\coderef-scanner.md"})

# Test 5: Batch validate all skills
await check_all_skills({"directory": "C:\\Users\\willh\\Desktop\\assistant\\.claude\\skills"})
```

**Expected results:**
- assistant CLAUDE.md: Score ~92/100, PASS
- coderef-workflow CLAUDE.md: Score ~55/100, FAIL (line count: 1,142, critical bloat)
- Batch all CLAUDE.md: Average score ~72/100, 2 PASS, 6 FAIL
- coderef-scanner skill: Score ~90/100, PASS
- Batch all skills: Average score ~90/100 (if skills exist)

---

### Step 9: Documentation

**Update Papertrail CLAUDE.md** with new tools:

```markdown
## Essential Commands

### Validation (MCP Tools)

```typescript
// Validate single CLAUDE.md file
mcp__papertrail__validate_claude_md({
  file_path: "C:\\path\\to\\CLAUDE.md"
})

// Batch validate all CLAUDE.md files
mcp__papertrail__check_all_claude_md({
  directory: "C:\\path\\to\\project"
})

// Validate single skill.md file
mcp__papertrail__validate_skill({
  file_path: "C:\\path\\to\\.claude\\skills\\deploy-production.md"
})

// Batch validate all skills
mcp__papertrail__check_all_skills({
  directory: "C:\\path\\to\\.claude\\skills"
})
```
```

---

## Phase 6: Build Generator Tools (coderef-docs MCP)

### Objective
Extend coderef-docs MCP server with 3 new generator tools for creating CLAUDE.md and skill.md files from templates.

### Implementation Location
**File:** `C:\Users\willh\.mcp-servers\coderef-docs\server.py` (similar pattern to Papertrail)

---

### Step 1: Add Tool Definitions

**Add 3 new Tool objects:**

```python
Tool(
    name="generate_claude_md",
    description="Generate project-level CLAUDE.md from CLAUDE-MD-STANDARDS template. Auto-fills with coderef-context data (project name, file structure, etc.) and validates using Papertrail. Returns generated CLAUDE.md content and validation score.",
    inputSchema={
        "type": "object",
        "properties": {
            "project_path": {
                "type": "string",
                "description": "Absolute path to project directory"
            },
            "project_type": {
                "type": "string",
                "description": "Type of project (mcp-server, dashboard, cli, orchestrator, library)",
                "enum": ["mcp-server", "dashboard", "cli", "orchestrator", "library"]
            },
            "auto_fill": {
                "type": "boolean",
                "description": "Auto-fill with coderef-context data (default: true)",
                "default": True
            }
        },
        "required": ["project_path", "project_type"]
    }
),
Tool(
    name="generate_child_claude_md",
    description="Generate child CLAUDE.md for sub-package/module from CHILD-CLAUDE-MD-GUIDE template. Auto-fills with component data and parent reference. Validates using Papertrail.",
    inputSchema={
        "type": "object",
        "properties": {
            "component_path": {
                "type": "string",
                "description": "Absolute path to component directory"
            },
            "parent_path": {
                "type": "string",
                "description": "Absolute path to parent CLAUDE.md"
            },
            "component_type": {
                "type": "string",
                "description": "Type of component (ui-library, plugin, microservice, package)",
                "enum": ["ui-library", "plugin", "microservice", "package"]
            },
            "auto_fill": {
                "type": "boolean",
                "description": "Auto-fill with coderef-context data (default: true)",
                "default": True
            }
        },
        "required": ["component_path", "parent_path", "component_type"]
    }
),
Tool(
    name="generate_skill",
    description="Generate skill.md from SKILL-TEMPLATE. Creates YAML frontmatter with proper fields and step-by-step content structure. Validates using Papertrail.",
    inputSchema={
        "type": "object",
        "properties": {
            "skill_name": {
                "type": "string",
                "description": "Skill name (kebab-case, e.g., 'deploy-production')"
            },
            "description": {
                "type": "string",
                "description": "One-sentence description of what this skill does"
            },
            "model": {
                "type": "string",
                "description": "Preferred model (haiku, sonnet, opus)",
                "enum": ["haiku", "sonnet", "opus"],
                "default": "sonnet"
            },
            "output_path": {
                "type": "string",
                "description": "Output file path (default: .claude/skills/{skill_name}.md)"
            }
        },
        "required": ["skill_name", "description"]
    }
)
```

---

### Step 2: Implement `generate_claude_md()` Function

**Pseudocode:**

```python
async def generate_claude_md(arguments: dict) -> list[TextContent]:
    """Generate project-level CLAUDE.md from template."""
    project_path = Path(arguments["project_path"])
    project_type = arguments["project_type"]
    auto_fill = arguments.get("auto_fill", True)

    # 1. Load CLAUDE-MD template
    template = load_claude_md_template()  # From standards doc

    # 2. Auto-fill with project data
    if auto_fill:
        # Get project name from directory
        project_name = project_path.name

        # Get file structure using coderef-context (if available)
        file_structure = get_file_structure(project_path)

        # Get workflows from coderef-workflow (if available)
        workflows = get_workflows(project_path)

        # Fill template placeholders
        template = template.replace("{{project_name}}", project_name)
        template = template.replace("{{project_type}}", project_type)
        template = template.replace("{{file_structure}}", file_structure)
        template = template.replace("{{workflows}}", workflows)
        # ... etc for other placeholders

    # 3. Generate YAML frontmatter
    frontmatter = {
        "agent": "coderef-docs v2.0.0",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "task": "CREATE",
        "file_type": "project",
        "project_name": project_path.name,
        "version": "1.0.0",
        "status": "🚧 Building",
        "created": datetime.now().strftime("%Y-%m-%d"),
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    }

    # 4. Combine frontmatter + body
    yaml_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
    claude_md_content = f"---\n{yaml_str}---\n\n{template}"

    # 5. Save to project_path/CLAUDE.md
    output_path = project_path / "CLAUDE.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(claude_md_content)

    # 6. Validate using Papertrail
    validation_result = await papertrail_validate_claude_md({"file_path": str(output_path)})

    # 7. Return response
    response = f"# Generated CLAUDE.md\n\n"
    response += f"**Output:** {output_path}\n"
    response += f"**Lines:** {len(claude_md_content.splitlines())}\n"
    response += f"**Type:** {project_type}\n\n"
    response += validation_result[0].text

    return [TextContent(type="text", text=response)]
```

---

### Step 3: Implement `generate_child_claude_md()` Function

**Similar to `generate_claude_md()` but uses CHILD-CLAUDE-MD template:**

**Key differences:**
- Uses CHILD-CLAUDE-MD-GUIDE template (not CLAUDE-MD-STANDARDS)
- Adds `parent_claude_md` field to frontmatter
- Includes "Parent Context" section with pointer to parent
- Shorter line budget (300-400 vs 530-600)

---

### Step 4: Implement `generate_skill()` Function

**Pseudocode:**

```python
async def generate_skill(arguments: dict) -> list[TextContent]:
    """Generate skill.md from SKILL-TEMPLATE."""
    skill_name = arguments["skill_name"]
    description = arguments["description"]
    model = arguments.get("model", "sonnet")
    output_path = arguments.get("output_path")

    # 1. Validate skill_name is kebab-case
    if not is_kebab_case(skill_name):
        return [TextContent(type="text", text=f"Error: skill_name must be kebab-case, got: {skill_name}")]

    # 2. Load SKILL-TEMPLATE
    template = load_skill_template()

    # 3. Generate YAML frontmatter
    frontmatter = {
        "agent": "coderef-docs v2.0.0",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "task": "CREATE",
        "name": skill_name,
        "description": description,
        "model": model
    }

    # 4. Fill template placeholders
    template = template.replace("{{skill_name}}", skill_name.replace('-', ' ').title())
    template = template.replace("{{description}}", description)

    # 5. Combine frontmatter + body
    yaml_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
    skill_content = f"---\n{yaml_str}---\n\n{template}"

    # 6. Determine output path
    if not output_path:
        output_path = Path(f".claude/skills/{skill_name}.md")
    else:
        output_path = Path(output_path)

    # 7. Create .claude/skills/ directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 8. Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(skill_content)

    # 9. Validate using Papertrail
    validation_result = await papertrail_validate_skill({"file_path": str(output_path)})

    # 10. Return response
    response = f"# Generated Skill: {skill_name}\n\n"
    response += f"**Output:** {output_path}\n"
    response += f"**Lines:** {len(skill_content.splitlines())}\n"
    response += f"**Model:** {model}\n\n"
    response += validation_result[0].text

    return [TextContent(type="text", text=response)]
```

---

### Step 5: Create Template Loaders

**File:** `coderef-docs/templates/` (new directory)

**Files:**
- `claude-md-template.md` - Project-level CLAUDE.md template
- `child-claude-md-template.md` - Child CLAUDE.md template
- `skill-template.md` - Skill template

**Load function:**

```python
def load_claude_md_template() -> str:
    """Load CLAUDE-MD template from templates directory."""
    template_path = Path(__file__).parent / "templates" / "claude-md-template.md"
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()
```

---

### Step 6: Testing

```python
# Test 1: Generate project CLAUDE.md for new project
await generate_claude_md({
    "project_path": "C:\\test-project",
    "project_type": "mcp-server",
    "auto_fill": True
})
# Expected: CLAUDE.md created, score 85+/100

# Test 2: Generate child CLAUDE.md for component
await generate_child_claude_md({
    "component_path": "C:\\test-project\\packages\\ui",
    "parent_path": "C:\\test-project\\CLAUDE.md",
    "component_type": "ui-library",
    "auto_fill": True
})
# Expected: Child CLAUDE.md created, score 85+/100

# Test 3: Generate skill
await generate_skill({
    "skill_name": "test-deployment",
    "description": "Deploy test application to staging environment",
    "model": "sonnet"
})
# Expected: Skill created at .claude/skills/test-deployment.md, score 90+/100
```

---

### Step 7: Documentation

**Update coderef-docs CLAUDE.md** with new tools:

```markdown
## Essential Commands

### Generation (MCP Tools)

```typescript
// Generate project-level CLAUDE.md
mcp__coderef-docs__generate_claude_md({
  project_path: "C:\\path\\to\\project",
  project_type: "mcp-server",
  auto_fill: true
})

// Generate child CLAUDE.md for component
mcp__coderef-docs__generate_child_claude_md({
  component_path: "C:\\path\\to\\component",
  parent_path: "C:\\path\\to\\parent\\CLAUDE.md",
  component_type: "ui-library",
  auto_fill: true
})

// Generate skill
mcp__coderef-docs__generate_skill({
  skill_name: "deploy-production",
  description: "Deploy application to AWS production environment with health checks",
  model: "sonnet"
})
```
```

---

## Success Criteria

### Phase 5 Complete When:
- ✅ All 4 validators implemented (validate_claude_md, check_all_claude_md, validate_skill, check_all_skills)
- ✅ Validators tested against 8 existing CLAUDE.md files (scores match Phase 2 audit within ±5 points)
- ✅ Validators tested against 2 existing skills (if they exist)
- ✅ Helper functions created (extract_yaml_frontmatter, calculate_compliance_score, etc.)
- ✅ Papertrail CLAUDE.md updated with new tool documentation
- ✅ All tests passing

### Phase 6 Complete When:
- ✅ All 3 generators implemented (generate_claude_md, generate_child_claude_md, generate_skill)
- ✅ Templates created (claude-md-template.md, child-claude-md-template.md, skill-template.md)
- ✅ Generators tested (generated files score 85+)
- ✅ Template loaders implemented
- ✅ coderef-docs CLAUDE.md updated with new tool documentation
- ✅ All tests passing

---

## Estimated Timeline

**Phase 5:**
- Step 1-2 (Tool definitions): 30 minutes
- Step 3-4 (validate_claude_md + check_all_claude_md): 2 hours
- Step 5-6 (validate_skill + check_all_skills): 1.5 hours
- Step 7 (Helper functions): 1 hour
- Step 8 (Testing): 1 hour
- Step 9 (Documentation): 30 minutes
**Total:** 6.5 hours

**Phase 6:**
- Step 1-2 (Tool definitions): 30 minutes
- Step 3 (generate_claude_md): 1.5 hours
- Step 4 (generate_child_claude_md): 1 hour
- Step 5 (generate_skill): 1 hour
- Step 6 (Template creation): 1.5 hours
- Step 7 (Testing): 1 hour
- Step 8 (Documentation): 30 minutes
**Total:** 7 hours

**Grand Total:** 13.5 hours

---

## Next Session Instructions

To execute Phases 5 and 6:

1. **Start with Phase 5** (validators are foundational for Phase 6 generators)
2. **Work file by file:**
   - Edit `papertrail/server.py` to add tool definitions
   - Create `papertrail/validators/claude_md_helpers.py`
   - Implement validators one at a time (test each before moving on)
3. **Test incrementally:**
   - After each validator, test against actual files
   - Verify scores match Phase 2 audit
4. **Move to Phase 6** only after Phase 5 validators are working
5. **Follow same pattern** for coderef-docs generators
6. **Final validation:**
   - Generate dummy CLAUDE.md, validate with Papertrail
   - Generate dummy skill, validate with Papertrail
   - Update all CLAUDE.md files with new tool documentation

---

**Session Status:** Implementation Plan Complete | Ready for Execution
**Workorder:** WO-CLAUDE-MD-STANDARDS-001
**Author:** CodeRef Assistant (Orchestrator Persona)
**Date:** 2026-01-22
