#!/usr/bin/env python3
"""
Add changelog entry for v1.3.0 - audit_codebase tool implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import tool_handlers

async def add_changelog():
    """Add changelog entry for v1.3.0."""

    # Set templates dir
    project_path = str(Path(__file__).parent.resolve())
    tool_handlers.set_templates_dir(Path(project_path) / "templates" / "power")

    result = await tool_handlers.handle_add_changelog_entry({
        "project_path": project_path,
        "version": "1.3.0",
        "change_type": "feature",
        "severity": "major",
        "title": "Implemented audit_codebase tool for compliance auditing",
        "description": "Added comprehensive codebase auditing tool that scans for UI/behavior/UX violations against established standards. Includes weighted compliance scoring (critical=-10pts, major=-5pts, minor=-1pt), detailed violation reporting with code snippets, fix suggestions, and markdown report generation.",
        "files": [
            "generators/audit_generator.py",
            "tool_handlers.py",
            "server.py",
            "constants.py",
            "validation.py",
            "type_defs.py",
            "CLAUDE.md",
            "README.md"
        ],
        "reason": "Complete the Consistency Trilogy pattern by adding Tool #9 (audit_codebase) to enable compliance auditing against established standards",
        "impact": "Users can now audit codebases for standards violations, get actionable compliance scores (0-100 with A-F grading), and receive detailed reports with fix suggestions. Enables iterative quality improvement and technical debt tracking.",
        "breaking": False,
        "contributors": ["willh", "Claude Code AI"]
    })

    print(result[0].text)

if __name__ == "__main__":
    asyncio.run(add_changelog())
