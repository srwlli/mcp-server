"""
Writing Standards Post-Processor (Tool 1 Quality Controls)

Applies Tool 1 writing guidelines to generated resource sheets:
- Voice & Tone enforcement (imperative, precise, no hedging, active voice)
- Structural validation (tables over prose, code blocks for sequences)
- Exhaustiveness checks (all state/failures/contracts documented)
- Refactor safety validation

WO-RESOURCE-SHEET-CONSOLIDATION-001 / PORT-001
Source: .claude/commands/create-resource-sheet.md sections 5-6
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """Represents a writing standards violation."""
    severity: str  # 'critical', 'major', 'minor'
    category: str  # 'voice', 'tone', 'structure', 'exhaustiveness', 'refactor_safety'
    line_number: int
    issue: str
    suggestion: str


class WritingStandardsProcessor:
    """Post-processor that enforces Tool 1 writing standards."""

    # Voice & Tone Patterns
    HEDGING_PATTERNS = [
        r'\bshould probably\b',
        r'\bmight want to\b',
        r'\bcould potentially\b',
        r'\bperhaps\b',
        r'\bmaybe\b',
        r'\bkind of\b',
        r'\bsort of\b',
    ]

    CONVERSATIONAL_PATTERNS = [
        r'\bwe persist\b',
        r'\bwe manage\b',
        r'\bwe handle\b',
        r'\blet\'s\b',
        r'\byou should\b',
        r'\byou can\b',
    ]

    PASSIVE_VOICE_PATTERNS = [
        r'is managed by',
        r'is handled by',
        r'is controlled by',
        r'is owned by',
        r'are managed by',
        r'are handled by',
    ]

    # Structural Patterns
    STATE_TABLE_REQUIRED = r'(?i)(state|ownership|persistence)'
    EVENT_TABLE_REQUIRED = r'(?i)(event|callback|handler)'

    # Exhaustiveness Requirements
    STORAGE_KEYWORDS = r'localStorage|sessionStorage|indexedDB|storage'
    FAILURE_KEYWORDS = r'error|failure|exception|crash'
    INTEGRATION_KEYWORDS = r'external|api|integration|service'

    def __init__(self):
        self.issues: List[ValidationIssue] = []

    def process(self, markdown_content: str) -> Tuple[str, List[ValidationIssue]]:
        """
        Process markdown content and apply writing standards.

        Args:
            markdown_content: Raw generated markdown

        Returns:
            Tuple of (processed_content, validation_issues)
        """
        self.issues = []
        lines = markdown_content.split('\n')
        processed_lines = []

        for line_num, line in enumerate(lines, start=1):
            processed_line = self._process_line(line, line_num)
            processed_lines.append(processed_line)

        # Run structural validation
        self._validate_structure('\n'.join(processed_lines))

        # Run exhaustiveness validation
        self._validate_exhaustiveness('\n'.join(processed_lines))

        # Run refactor safety validation
        self._validate_refactor_safety('\n'.join(processed_lines))

        return '\n'.join(processed_lines), self.issues

    def _process_line(self, line: str, line_num: int) -> str:
        """Process a single line for voice & tone violations."""
        original_line = line

        # Check for hedging
        for pattern in self.HEDGING_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    severity='major',
                    category='voice',
                    line_number=line_num,
                    issue=f'Hedging detected: "{line.strip()}"',
                    suggestion='Use definitive language: "must" instead of "should probably"'
                ))
                # Auto-fix common patterns
                line = re.sub(r'\bshould probably\b', 'must', line, flags=re.IGNORECASE)
                line = re.sub(r'\bmight want to\b', 'should', line, flags=re.IGNORECASE)

        # Check for conversational tone
        for pattern in self.CONVERSATIONAL_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    severity='major',
                    category='tone',
                    line_number=line_num,
                    issue=f'Conversational tone detected: "{line.strip()}"',
                    suggestion='Use imperative voice: "Component persists" not "We persist"'
                ))
                # Auto-fix common patterns
                line = re.sub(r'\bwe persist\b', 'Component persists', line, flags=re.IGNORECASE)
                line = re.sub(r'\bwe manage\b', 'System manages', line, flags=re.IGNORECASE)

        # Check for passive voice
        for pattern in self.PASSIVE_VOICE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    severity='minor',
                    category='voice',
                    line_number=line_num,
                    issue=f'Passive voice detected: "{line.strip()}"',
                    suggestion='Use active voice: "Component manages state" not "State is managed by component"'
                ))
                # Auto-fix common patterns
                line = re.sub(r'is managed by (\w+)', r'\1 manages', line, flags=re.IGNORECASE)
                line = re.sub(r'is handled by (\w+)', r'\1 handles', line, flags=re.IGNORECASE)

        # Only return modified line if auto-fixes were applied
        if line != original_line:
            return line
        return original_line

    def _validate_structure(self, content: str):
        """Validate structural requirements (tables over prose)."""
        # Check for state ownership table
        if re.search(self.STATE_TABLE_REQUIRED, content, re.IGNORECASE):
            # Look for markdown table with state/owner columns
            if not re.search(r'\|.*State.*\|.*Owner.*\|', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    severity='major',
                    category='structure',
                    line_number=0,
                    issue='State ownership mentioned but no table found',
                    suggestion='Use table format: | State | Owner | Type | Persistence | Source of Truth |'
                ))

        # Check for event/callback table
        if re.search(self.EVENT_TABLE_REQUIRED, content, re.IGNORECASE):
            # Look for markdown table with event/callback columns
            if not re.search(r'\|.*Event.*\|.*Trigger.*\|.*Payload.*\|', content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    severity='minor',
                    category='structure',
                    line_number=0,
                    issue='Events mentioned but no callback contract table found',
                    suggestion='Use table format: | Event | Trigger | Payload | Side Effects |'
                ))

        # Check for diagram disclaimer (if diagrams present)
        if re.search(r'```mermaid|!\[.*\]\(.*\)', content):
            if 'illustrative' not in content.lower():
                self.issues.append(ValidationIssue(
                    severity='minor',
                    category='structure',
                    line_number=0,
                    issue='Diagram present but no illustrative disclaimer',
                    suggestion='Add: > Diagrams are illustrative, not authoritative. Text defines truth.'
                ))

    def _validate_exhaustiveness(self, content: str):
        """Validate exhaustiveness requirements (all state/failures/contracts documented)."""
        # Check for storage without keys catalog
        if re.search(self.STORAGE_KEYWORDS, content, re.IGNORECASE):
            if 'storage keys' not in content.lower() and 'keys catalog' not in content.lower():
                self.issues.append(ValidationIssue(
                    severity='major',
                    category='exhaustiveness',
                    line_number=0,
                    issue='Storage mentioned but no keys catalog found',
                    suggestion='Document ALL persisted state keys in a catalog table'
                ))

        # Check for failures without recovery paths
        if re.search(self.FAILURE_KEYWORDS, content, re.IGNORECASE):
            if 'recovery' not in content.lower() and 'fallback' not in content.lower():
                self.issues.append(ValidationIssue(
                    severity='major',
                    category='exhaustiveness',
                    line_number=0,
                    issue='Failures/errors mentioned but no recovery paths documented',
                    suggestion='Document ALL failure modes with recovery strategies'
                ))

        # Check for integrations without contracts
        if re.search(self.INTEGRATION_KEYWORDS, content, re.IGNORECASE):
            if 'contract' not in content.lower() and 'interface' not in content.lower():
                self.issues.append(ValidationIssue(
                    severity='major',
                    category='exhaustiveness',
                    line_number=0,
                    issue='External integrations mentioned but no contracts documented',
                    suggestion='Document ALL external integration contracts explicitly'
                ))

        # Check for non-goals section
        if 'non-goals' not in content.lower() and 'out of scope' not in content.lower():
            self.issues.append(ValidationIssue(
                severity='minor',
                category='exhaustiveness',
                line_number=0,
                issue='No non-goals section found',
                suggestion='Add explicit non-goals to prevent scope creep'
            ))

    def _validate_refactor_safety(self, content: str):
        """Validate refactor safety checklist requirements."""
        refactor_checks = [
            ('state ownership', 'State ownership rules must be unambiguous'),
            ('failure', 'Failure modes must have documented recovery paths'),
            ('non-goals', 'Non-goals must be explicit to prevent scope creep'),
        ]

        for keyword, message in refactor_checks:
            if keyword in content.lower():
                # Validated - keyword present
                continue
            else:
                # Only warn if related content exists but keyword missing
                if keyword == 'state ownership' and 'state' in content.lower():
                    self.issues.append(ValidationIssue(
                        severity='major',
                        category='refactor_safety',
                        line_number=0,
                        issue=message,
                        suggestion=f'Add explicit {keyword} documentation'
                    ))

    def generate_report(self) -> Dict:
        """Generate validation report with issue counts and recommendations."""
        critical = [i for i in self.issues if i.severity == 'critical']
        major = [i for i in self.issues if i.severity == 'major']
        minor = [i for i in self.issues if i.severity == 'minor']

        return {
            'total_issues': len(self.issues),
            'critical_count': len(critical),
            'major_count': len(major),
            'minor_count': len(minor),
            'status': self._determine_status(len(critical), len(major), len(minor)),
            'issues': [
                {
                    'severity': i.severity,
                    'category': i.category,
                    'line': i.line_number,
                    'issue': i.issue,
                    'suggestion': i.suggestion
                }
                for i in self.issues
            ]
        }

    def _determine_status(self, critical: int, major: int, minor: int) -> str:
        """Determine validation status based on issue counts."""
        if critical > 0:
            return 'REJECTED'
        elif major > 2:
            return 'APPROVED_WITH_WARNINGS'
        elif minor > 5:
            return 'APPROVED_WITH_WARNINGS'
        else:
            return 'APPROVED'


def apply_writing_standards(markdown_content: str) -> Tuple[str, Dict]:
    """
    Apply Tool 1 writing standards to generated resource sheet.

    Args:
        markdown_content: Raw generated markdown from resource sheet generator

    Returns:
        Tuple of (processed_markdown, validation_report)

    Example:
        >>> content = "We should probably persist state..."
        >>> processed, report = apply_writing_standards(content)
        >>> print(report['status'])
        'APPROVED_WITH_WARNINGS'
    """
    processor = WritingStandardsProcessor()
    processed_content, _ = processor.process(markdown_content)
    report = processor.generate_report()

    return processed_content, report
