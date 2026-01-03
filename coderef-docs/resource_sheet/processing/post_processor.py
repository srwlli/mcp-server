"""
Document Post-Processor - Writing Standards Enforcement.

WO-RESOURCE-SHEET-MCP-TOOL-001 Phase 3C (PORT-001)

Implements automated checks for 5 writing guideline categories from
legacy Tool 1 template (.claude/commands/create-resource-sheet.md).

Violations are returned as structured warnings, with optional auto-fix mode.
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ViolationSeverity(Enum):
    """Severity levels for writing violations."""
    ERROR = "error"      # Must fix before publication
    WARNING = "warning"  # Should fix for quality
    INFO = "info"        # Suggestion for improvement


@dataclass
class Violation:
    """A writing guideline violation."""
    category: str          # e.g., "voice_tone", "precision", "active_voice"
    severity: ViolationSeverity
    line_number: int       # 0-indexed
    text: str              # Problematic text
    message: str           # Human-readable explanation
    suggestion: Optional[str] = None  # Recommended fix


class DocumentPostProcessor:
    """
    Post-processes generated resource sheets to enforce writing standards.

    Implements 5 guideline categories:
    1. Voice & Tone - Imperative, not conversational
    2. Precision - No hedging words
    3. Active Voice - Prefer active over passive
    4. Table Usage - Structured data in tables
    5. Ambiguity - "Must" vs "Should" clarity

    Usage:
        processor = DocumentPostProcessor()
        violations = processor.check_all(markdown_content)

        if violations:
            for v in violations:
                print(f"{v.severity.value}: {v.message}")

        # Optional auto-fix
        fixed_markdown = processor.apply_fixes(markdown_content, violations)
    """

    def __init__(self):
        """Initialize post-processor with pattern definitions."""
        # Conversational patterns to avoid
        self.conversational_patterns = [
            (r'\bwe\s+(\w+)', "Use imperative: 'Component {verb}' not 'We {verb}'"),
            (r'\byou\s+can\s+(\w+)', "Use imperative: 'Users can {verb}' or 'Component allows {verb}'"),
            (r'\blet\'s\s+', "Use imperative, not conversational"),
            (r'\bokay\b', "Remove conversational filler"),
            (r'\bbasically\b', "Remove conversational filler"),
        ]

        # Hedging words that weaken precision
        self.hedging_patterns = [
            r'\bshould probably\b',
            r'\bmight want to\b',
            r'\bcould consider\b',
            r'\bperhaps\b',
            r'\bmaybe\b',
            r'\bkind of\b',
            r'\bsort of\b',
            r'\bsomewhat\b',
            r'\bpossibly\b',
            r'\bpotentially\b',
        ]

        # Passive voice patterns
        self.passive_voice_patterns = [
            (r'is\s+(\w+ed)\s+by', "Passive voice: 'is {verb} by' → Use active voice"),
            (r'was\s+(\w+ed)\s+by', "Passive voice: 'was {verb} by' → Use active voice"),
            (r'are\s+(\w+ed)\s+by', "Passive voice: 'are {verb} by' → Use active voice"),
            (r'were\s+(\w+ed)\s+by', "Passive voice: 'were {verb} by' → Use active voice"),
            (r'been\s+(\w+ed)', "Passive voice: 'been {verb}' → Consider active alternative"),
        ]

        # Ambiguous "should" usage (should be "must" or "may")
        self.ambiguous_should_pattern = r'\bshould\b'

    def check_all(self, markdown: str) -> List[Violation]:
        """
        Run all writing guideline checks on markdown content.

        Args:
            markdown: Resource sheet markdown content

        Returns:
            List of violations sorted by line number
        """
        violations = []
        violations.extend(self.check_voice_tone(markdown))
        violations.extend(self.check_precision(markdown))
        violations.extend(self.check_active_voice(markdown))
        violations.extend(self.check_table_usage(markdown))
        violations.extend(self.check_ambiguity(markdown))

        # Sort by line number for easier review
        return sorted(violations, key=lambda v: v.line_number)

    def check_voice_tone(self, markdown: str) -> List[Violation]:
        """
        Check for conversational language (imperative required).

        Detects:
        - "We persist" → "Component persists"
        - "You can add" → "Users can add" or "Component allows"
        - "Let's start" → "Start with"

        Args:
            markdown: Markdown content

        Returns:
            List of voice & tone violations
        """
        violations = []
        lines = markdown.split('\n')

        for i, line in enumerate(lines):
            # Skip code blocks and headers
            if line.strip().startswith('```') or line.strip().startswith('#'):
                continue

            for pattern, message_template in self.conversational_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    verb = match.group(1) if match.lastindex >= 1 else ""
                    violations.append(Violation(
                        category="voice_tone",
                        severity=ViolationSeverity.WARNING,
                        line_number=i,
                        text=match.group(0),
                        message=message_template.format(verb=verb),
                        suggestion=None  # Context-dependent, can't auto-fix
                    ))

        return violations

    def check_precision(self, markdown: str) -> List[Violation]:
        """
        Check for hedging language (precision required).

        Detects:
        - "should probably" → "must" or "will"
        - "might want to" → "should" or "can"
        - "perhaps", "maybe" → Remove or rephrase

        Args:
            markdown: Markdown content

        Returns:
            List of precision violations
        """
        violations = []
        lines = markdown.split('\n')

        for i, line in enumerate(lines):
            # Skip code blocks
            if line.strip().startswith('```'):
                continue

            for pattern in self.hedging_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    violations.append(Violation(
                        category="precision",
                        severity=ViolationSeverity.WARNING,
                        line_number=i,
                        text=match.group(0),
                        message=f"Hedging language: '{match.group(0)}' weakens precision",
                        suggestion="Use 'must', 'will', 'can', or remove entirely"
                    ))

        return violations

    def check_active_voice(self, markdown: str) -> List[Violation]:
        """
        Check for passive voice (active voice preferred).

        Detects:
        - "is managed by" → "Component manages"
        - "was created by" → "Developer creates"
        - "are processed by" → "System processes"

        Args:
            markdown: Markdown content

        Returns:
            List of active voice violations
        """
        violations = []
        lines = markdown.split('\n')

        for i, line in enumerate(lines):
            # Skip code blocks and tables
            if line.strip().startswith('```') or '|' in line:
                continue

            for pattern, message_template in self.passive_voice_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    verb = match.group(1) if match.lastindex >= 1 else ""
                    violations.append(Violation(
                        category="active_voice",
                        severity=ViolationSeverity.INFO,
                        line_number=i,
                        text=match.group(0),
                        message=message_template.format(verb=verb),
                        suggestion=None  # Context-dependent
                    ))

        return violations

    def check_table_usage(self, markdown: str) -> List[Violation]:
        """
        Check for structured data that should be in tables.

        Detects patterns like:
        - "State: X, Owner: Y, Type: Z" → Should be table
        - List with consistent structure → Consider table

        Args:
            markdown: Markdown content

        Returns:
            List of table usage violations
        """
        violations = []
        lines = markdown.split('\n')

        # Detect list items with key-value patterns
        structured_list_items = []
        in_list = False
        list_start = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detect list start
            if stripped.startswith('- ') or stripped.startswith('* '):
                if not in_list:
                    in_list = True
                    list_start = i
                    structured_list_items = []

                # Check if line has key-value structure
                # e.g., "- State: X, Owner: Y" or "- **Name:** Value"
                if ':' in stripped and (',' in stripped or '**' in stripped):
                    structured_list_items.append(i)

            # Detect list end
            elif in_list and not stripped.startswith('- ') and stripped:
                # If we found 3+ structured items, suggest table
                if len(structured_list_items) >= 3:
                    violations.append(Violation(
                        category="table_usage",
                        severity=ViolationSeverity.INFO,
                        line_number=list_start,
                        text=f"List items {list_start}-{i-1}",
                        message=f"Found {len(structured_list_items)} list items with key-value structure. Consider using a table for better readability.",
                        suggestion="Convert to markdown table with columns for each key"
                    ))

                in_list = False
                structured_list_items = []

        return violations

    def check_ambiguity(self, markdown: str) -> List[Violation]:
        """
        Check for ambiguous "should" statements.

        "Should" is ambiguous - use:
        - "must" for requirements
        - "may" for optional actions
        - "will" for definite future actions

        Args:
            markdown: Markdown content

        Returns:
            List of ambiguity violations
        """
        violations = []
        lines = markdown.split('\n')

        for i, line in enumerate(lines):
            # Skip code blocks, comments, and quotes
            if line.strip().startswith('```') or line.strip().startswith('>'):
                continue

            matches = re.finditer(self.ambiguous_should_pattern, line, re.IGNORECASE)
            for match in matches:
                violations.append(Violation(
                    category="ambiguity",
                    severity=ViolationSeverity.WARNING,
                    line_number=i,
                    text=match.group(0),
                    message="Ambiguous 'should' - use 'must' (requirement), 'may' (optional), or 'will' (definite)",
                    suggestion="Replace with 'must', 'may', or 'will' depending on context"
                ))

        return violations

    def apply_fixes(self, markdown: str, violations: List[Violation]) -> str:
        """
        Apply automatic fixes to violations where possible.

        Only fixes violations with non-None suggestions that are safe
        to auto-apply (e.g., removing filler words).

        Args:
            markdown: Original markdown content
            violations: List of violations to fix

        Returns:
            Fixed markdown content
        """
        lines = markdown.split('\n')

        # Group violations by line number (reverse order to preserve indices)
        violations_by_line = {}
        for v in violations:
            if v.line_number not in violations_by_line:
                violations_by_line[v.line_number] = []
            violations_by_line[v.line_number].append(v)

        # Apply fixes (only for safe auto-fixable patterns)
        for line_num in sorted(violations_by_line.keys(), reverse=True):
            line = lines[line_num]

            for violation in violations_by_line[line_num]:
                # Auto-fix: Remove conversational filler words
                if violation.category == "precision" and violation.text in ["basically", "okay"]:
                    line = line.replace(violation.text, "")

                # Auto-fix: Common hedge word removals
                elif violation.category == "precision" and violation.text in ["perhaps", "maybe"]:
                    line = re.sub(r'\b' + re.escape(violation.text) + r'\b\s*,?\s*', '', line, flags=re.IGNORECASE)

            lines[line_num] = line

        return '\n'.join(lines)

    def get_report(self, violations: List[Violation]) -> str:
        """
        Generate a human-readable report of violations.

        Args:
            violations: List of violations

        Returns:
            Formatted report string
        """
        if not violations:
            return "✅ No writing guideline violations detected!"

        report = [f"Found {len(violations)} writing guideline violations:\n"]

        # Group by category
        by_category = {}
        for v in violations:
            if v.category not in by_category:
                by_category[v.category] = []
            by_category[v.category].append(v)

        for category, viols in sorted(by_category.items()):
            report.append(f"\n## {category.replace('_', ' ').title()} ({len(viols)} issues)")
            for v in viols:
                severity_icon = {
                    ViolationSeverity.ERROR: "❌",
                    ViolationSeverity.WARNING: "⚠️",
                    ViolationSeverity.INFO: "ℹ️"
                }[v.severity]

                report.append(f"  {severity_icon} Line {v.line_number + 1}: {v.message}")
                report.append(f"     Text: \"{v.text}\"")
                if v.suggestion:
                    report.append(f"     Suggestion: {v.suggestion}")

        return '\n'.join(report)


# Example usage
if __name__ == "__main__":
    # Test document with intentional violations
    test_doc = """
# Test Resource Sheet

## Overview

We persist the state to localStorage. You can add custom handlers.
The component should probably validate inputs. Maybe we could use Zod.

State is managed by the parent component. Data was created by the API.

- State: active, Owner: Component, Type: boolean
- State: value, Owner: Component, Type: string
- State: error, Owner: Component, Type: Error | null

Basically, this is how it works.
"""

    processor = DocumentPostProcessor()
    violations = processor.check_all(test_doc)

    print(processor.get_report(violations))

    if violations:
        print("\n" + "="*60)
        print("APPLYING FIXES...")
        print("="*60)
        fixed = processor.apply_fixes(test_doc, violations)
        print(fixed)
