"""
CLAUDE.md and skill.md validation helper functions.

Provides utilities for:
- YAML frontmatter extraction from markdown
- Line counting and section detection
- Compliance scoring (0-100 scale)
- Kebab-case validation
- Step-by-step content structure checks

Used by validate_claude_md, validate_skill, and batch validators.
"""

import re
import yaml
from pathlib import Path
from typing import Tuple, List, Dict, Any


def extract_yaml_frontmatter(file_path: Path) -> Tuple[Dict[str, Any], str]:
    """
    Extract YAML frontmatter and body from markdown file.

    Args:
        file_path: Path to markdown file

    Returns:
        Tuple of (frontmatter_dict, body_content)
        Returns ({}, content) if no valid frontmatter found
    """
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

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
        return frontmatter or {}, body
    except yaml.YAMLError:
        return {}, content


def count_lines(file_path: Path) -> int:
    """
    Count total lines in file.

    Args:
        file_path: Path to file

    Returns:
        Total line count
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return len(f.readlines())


def extract_markdown_headers(content: str, level: int = 2) -> List[str]:
    """
    Extract markdown headers from content.

    Args:
        content: Markdown content
        level: Header level to extract (default: 2 for ##)

    Returns:
        List of header text (without ## prefix)
    """
    pattern = f'^{"#" * level} (.+)$'
    headers = re.findall(pattern, content, re.MULTILINE)
    return headers


def is_kebab_case(text: str) -> bool:
    """
    Check if text is kebab-case (lowercase with hyphens).

    Args:
        text: String to check

    Returns:
        True if kebab-case, False otherwise

    Examples:
        >>> is_kebab_case("deploy-production")
        True
        >>> is_kebab_case("Deploy-Production")
        False
        >>> is_kebab_case("deploy_production")
        False
    """
    return bool(re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', text))


def check_for_step_headers(content: str) -> bool:
    """
    Check if content has step-by-step headers (## Step 1:, etc.).

    Args:
        content: Markdown content

    Returns:
        True if step headers found, False otherwise
    """
    return bool(re.search(r'## Step \d+:', content))


def get_required_sections(file_type: str) -> List[str]:
    """
    Get required sections based on CLAUDE.md file type.

    Args:
        file_type: "project" or "child"

    Returns:
        List of required section names
    """
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


def calculate_compliance_score(
    line_count: int,
    target_min: int,
    target_max: int,
    sections_found: int,
    sections_required: int,
    errors: int,
    warnings: int
) -> int:
    """
    Calculate compliance score (0-100) based on multiple factors.

    Scoring breakdown:
    - Line budget (25 pts): Within target = 25, over/under = deductions
    - Sections (30 pts): Percentage of required sections present
    - Format quality (15 pts): Placeholder for now
    - Error deductions (max -25): -5 pts per error
    - Warning deductions (max -15): -2 pts per warning

    Args:
        line_count: Actual line count
        target_min: Minimum target line count
        target_max: Maximum target line count
        sections_found: Number of required sections found
        sections_required: Total required sections
        errors: Number of errors
        warnings: Number of warnings

    Returns:
        Score from 0-100
    """
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


def calculate_skill_compliance_score(
    line_count: int,
    target_min: int,
    target_max: int,
    has_required_fields: bool,
    has_steps: bool,
    has_verification: bool,
    errors: int,
    warnings: int
) -> int:
    """
    Calculate compliance score for skills (0-100).

    Scoring breakdown:
    - Line budget (25 pts): Within target = 25, over/under = deductions
    - Required fields (30 pts): name + description present
    - Content structure (15 pts): Has step-by-step headers
    - Verification section (10 pts): Has ## Verification section
    - Error deductions (max -25): -5 pts per error
    - Warning deductions (max -15): -2 pts per warning

    Args:
        line_count: Actual line count
        target_min: Minimum target (300)
        target_max: Maximum target (500)
        has_required_fields: True if name and description present
        has_steps: True if step-by-step structure found
        has_verification: True if ## Verification section found
        errors: Number of errors
        warnings: Number of warnings

    Returns:
        Score from 0-100
    """
    score = 100

    # Line budget (25 points)
    if target_min <= line_count <= target_max:
        line_budget_score = 25
    elif line_count < target_min:
        under_by = target_min - line_count
        line_budget_score = max(0, 25 - (under_by / 50) * 10)
    else:  # line_count > target_max
        over_by = line_count - target_max
        line_budget_score = max(0, 25 - (over_by / 50) * 10)

    # Required fields (30 points)
    required_fields_score = 30 if has_required_fields else 0

    # Content structure (15 points)
    structure_score = 15 if has_steps else 0

    # Verification section (10 points)
    verification_score = 10 if has_verification else 0

    # Errors (deduct 5 pts per error, max -25)
    error_deduction = min(25, errors * 5)

    # Warnings (deduct 2 pts per warning, max -15)
    warning_deduction = min(15, warnings * 2)

    score = (line_budget_score + required_fields_score + structure_score +
             verification_score - error_deduction - warning_deduction)
    return max(0, min(100, int(score)))


def extract_score_from_result(result: Any) -> int:
    """
    Extract score from validation result text.

    Args:
        result: TextContent result from validator

    Returns:
        Score (0-100), or 0 if not found
    """
    if not hasattr(result, 'text'):
        return 0

    text = result.text

    # Look for "Score: XX/100" pattern
    match = re.search(r'Score:\s*(\d+)/100', text)
    if match:
        return int(match.group(1))

    return 0


def format_validation_response(
    file_path: Path,
    is_valid: bool,
    score: int,
    line_count: int,
    target_range: Tuple[int, int],
    errors: List[str],
    warnings: List[str],
    file_type: str
) -> str:
    """
    Format validation response for CLAUDE.md validation.

    Args:
        file_path: Path to validated file
        is_valid: Schema validation result
        score: Compliance score (0-100)
        line_count: Actual line count
        target_range: (min, max) target lines
        errors: List of error messages
        warnings: List of warning messages
        file_type: "project" or "child"

    Returns:
        Formatted validation response string
    """
    target_min, target_max = target_range

    # Determine pass/fail
    status = "[PASS]" if score >= 85 and len(errors) == 0 else "[FAIL]"

    # Determine line budget status
    if target_min <= line_count <= target_max:
        line_status = "✅ Within target"
    elif line_count < target_min:
        line_status = f"⚠️ Below target ({line_count}/{target_min} = {line_count/target_min*100:.0f}%)"
    elif line_count <= target_max + 50:
        line_status = f"⚠️ Slightly over ({line_count}/{target_max} = {line_count/target_max*100:.0f}%)"
    elif line_count <= target_max + 200:
        line_status = f"❌ Over budget ({line_count}/{target_max} = {line_count/target_max*100:.0f}%)"
    else:
        line_status = f"🚨 Critical bloat ({line_count}/{target_max} = {line_count/target_max*100:.0f}%)"

    response = f"# CLAUDE.md Validation Result\n\n"
    response += f"**Status:** {status}\n"
    response += f"**File:** {file_path.name}\n"
    response += f"**Type:** {file_type}\n"
    response += f"**Score:** {score}/100\n"
    response += f"**Line Count:** {line_count} (target: {target_min}-{target_max})\n"
    response += f"**Line Budget Status:** {line_status}\n\n"

    if errors:
        response += f"## Errors ({len(errors)})\n\n"
        for i, error in enumerate(errors, 1):
            response += f"{i}. {error}\n"
        response += "\n"

    if warnings:
        response += f"## Warnings ({len(warnings)})\n\n"
        for i, warning in enumerate(warnings, 1):
            response += f"{i}. {warning}\n"
        response += "\n"

    if not errors and not warnings:
        response += "✅ No issues found!\n\n"

    return response


def format_skill_validation_response(
    file_path: Path,
    is_valid: bool,
    score: int,
    line_count: int,
    target_range: Tuple[int, int],
    errors: List[str],
    warnings: List[str],
    frontmatter: Dict[str, Any]
) -> str:
    """
    Format validation response for skill validation.

    Args:
        file_path: Path to validated file
        is_valid: Schema validation result
        score: Compliance score (0-100)
        line_count: Actual line count
        target_range: (min, max) target lines
        errors: List of error messages
        warnings: List of warning messages
        frontmatter: Skill frontmatter dict

    Returns:
        Formatted validation response string
    """
    target_min, target_max = target_range

    # Determine pass/fail
    status = "[PASS]" if score >= 90 and len(errors) == 0 else "[FAIL]"

    # Determine line budget status
    if target_min <= line_count <= target_max:
        line_status = "✅ Within target (300-500)"
    elif line_count < target_min:
        line_status = f"⚠️ Below target (<300)"
    elif line_count <= 600:
        line_status = f"⚠️ Slightly over (500-600)"
    elif line_count <= 800:
        line_status = f"❌ Over budget (600-800)"
    else:
        line_status = f"🚨 Critical bloat (>800)"

    skill_name = frontmatter.get('name', 'unknown')
    model = frontmatter.get('model', 'not specified')

    response = f"# Skill Validation Result\n\n"
    response += f"**Status:** {status}\n"
    response += f"**File:** {file_path.name}\n"
    response += f"**Skill Name:** {skill_name}\n"
    response += f"**Model:** {model}\n"
    response += f"**Score:** {score}/100\n"
    response += f"**Line Count:** {line_count} (target: {target_min}-{target_max})\n"
    response += f"**Line Budget Status:** {line_status}\n\n"

    if errors:
        response += f"## Errors ({len(errors)})\n\n"
        for i, error in enumerate(errors, 1):
            response += f"{i}. {error}\n"
        response += "\n"

    if warnings:
        response += f"## Warnings ({len(warnings)})\n\n"
        for i, warning in enumerate(warnings, 1):
            response += f"{i}. {warning}\n"
        response += "\n"

    if not errors and not warnings:
        response += "✅ No issues found!\n\n"

    return response
