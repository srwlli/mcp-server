"""
Audit generator for audit_codebase tool.

Scans codebase for standards violations and generates comprehensive audit reports
with compliance scores, violation details, and fix suggestions.
"""

import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from constants import (
    Paths, Files, AuditSeverity, AuditScope,
    EXCLUDE_DIRS, MAX_FILE_SIZE, ALLOWED_FILE_EXTENSIONS
)
from type_defs import (
    StandardsDataDict, AuditViolationDict, ComplianceScoreDict,
    ViolationStatsDict, AuditResultDict, UIPatternDict,
    BehaviorPatternDict, UXPatternDict
)
from logger_config import logger, log_security_event


class AuditGenerator:
    """
    Generator for auditing codebases against established standards.

    Parses standards documents, scans codebase for violations, calculates
    compliance scores, and generates detailed audit reports.
    """

    def __init__(self, project_path: Path, standards_dir: Path):
        """
        Initialize audit generator.

        Args:
            project_path: Absolute path to project directory
            standards_dir: Path to standards directory containing markdown docs
        """
        self.project_path = project_path.resolve()  # SEC-001: Canonicalize path
        self.standards_dir = standards_dir.resolve()

        # Compile regex patterns once for performance
        self._button_pattern = re.compile(r'<Button[^>]*>', re.DOTALL)
        self._modal_pattern = re.compile(r'<Modal[^>]*>|<Dialog[^>]*>', re.DOTALL)
        self._color_pattern = re.compile(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}')
        self._error_pattern = re.compile(r'throw new Error\([\'"](.+?)[\'"]\)|toast\.error\([\'"](.+?)[\'"]\)')
        self._loading_pattern = re.compile(r'isLoading|loading\s*[:=]|<Spinner|<Loading')

        logger.debug(f"Initialized AuditGenerator for {project_path} with standards from {standards_dir}")

    def parse_standards_documents(self, standards_dir: Path) -> StandardsDataDict:
        """
        Parse all 4 standards documents into structured data model.

        Reads UI-STANDARDS.md, BEHAVIOR-STANDARDS.md, UX-PATTERNS.md, and
        COMPONENT-INDEX.md from the standards directory.

        Args:
            standards_dir: Directory containing standards markdown files

        Returns:
            StandardsDataDict with parsed standards data

        Raises:
            FileNotFoundError: If standards directory or required files don't exist
        """
        logger.info("Parsing standards documents", extra={'standards_dir': str(standards_dir)})

        if not standards_dir.exists():
            raise FileNotFoundError(f"Standards directory not found: {standards_dir}")

        standards: StandardsDataDict = {
            'ui_patterns': {},
            'behavior_patterns': {},
            'ux_patterns': {},
            'components': {},
            'source_files': [],
            'parse_errors': []
        }

        # Parse UI standards
        ui_file = standards_dir / Files.UI_STANDARDS
        if ui_file.exists():
            content = ui_file.read_text(encoding='utf-8')
            standards['ui_patterns'] = self.parse_ui_standards(content)
            standards['source_files'].append(str(ui_file))
        else:
            logger.warning(f"UI standards file not found: {ui_file}")
            standards['parse_errors'].append(f"Missing {Files.UI_STANDARDS}")

        # Parse behavior standards
        behavior_file = standards_dir / Files.BEHAVIOR_STANDARDS
        if behavior_file.exists():
            content = behavior_file.read_text(encoding='utf-8')
            standards['behavior_patterns'] = self.parse_behavior_standards(content)
            standards['source_files'].append(str(behavior_file))
        else:
            logger.warning(f"Behavior standards file not found: {behavior_file}")
            standards['parse_errors'].append(f"Missing {Files.BEHAVIOR_STANDARDS}")

        # Parse UX standards
        ux_file = standards_dir / Files.UX_PATTERNS
        if ux_file.exists():
            content = ux_file.read_text(encoding='utf-8')
            standards['ux_patterns'] = self.parse_ux_standards(content)
            standards['source_files'].append(str(ux_file))
        else:
            logger.warning(f"UX patterns file not found: {ux_file}")
            standards['parse_errors'].append(f"Missing {Files.UX_PATTERNS}")

        logger.info(f"Standards parsing complete", extra={
            'files_parsed': len(standards['source_files']),
            'parse_errors': len(standards['parse_errors'])
        })

        return standards

    def parse_ui_standards(self, content: str) -> dict:
        """
        Parse UI-STANDARDS.md to extract UI patterns.

        Args:
            content: Raw markdown content from UI-STANDARDS.md

        Returns:
            Dictionary with buttons, modals, colors patterns
        """
        patterns = {
            'buttons': {'allowed_sizes': [], 'allowed_variants': []},
            'modals': {'allowed_sizes': []},
            'colors': {'allowed_hex_codes': []}
        }

        # Extract button sizes
        sizes_match = re.search(r'\*\*Discovered Sizes\*\*:\s*(.+?)\n', content)
        if sizes_match:
            sizes_str = sizes_match.group(1).strip()
            patterns['buttons']['allowed_sizes'] = [s.strip() for s in sizes_str.split(',')]

        # Extract button variants
        variants_match = re.search(r'\*\*Discovered Variants\*\*:\s*(.+?)\n', content)
        if variants_match:
            variants_str = variants_match.group(1).strip()
            patterns['buttons']['allowed_variants'] = [v.strip() for v in variants_str.split(',')]

        # Extract colors
        color_matches = re.findall(r'-\s*`(#[0-9a-fA-F]{6})`', content)
        patterns['colors']['allowed_hex_codes'] = color_matches

        logger.debug(f"Parsed UI standards: {len(patterns['buttons']['allowed_sizes'])} button sizes, "
                    f"{len(patterns['buttons']['allowed_variants'])} variants, "
                    f"{len(patterns['colors']['allowed_hex_codes'])} colors")

        return patterns

    def parse_behavior_standards(self, content: str) -> dict:
        """
        Parse BEHAVIOR-STANDARDS.md to extract behavior patterns.

        Args:
            content: Raw markdown content from BEHAVIOR-STANDARDS.md

        Returns:
            Dictionary with error_handling, loading_states patterns
        """
        patterns = {
            'error_handling': {'expected_patterns': []},
            'loading_states': {'required': False}
        }

        # Extract error messages
        error_section = re.search(r'## Error Handling\n\n\*\*Discovered Error Messages\*\*:(.*?)(?=\n##|\n---|\Z)', content, re.DOTALL)
        if error_section:
            messages = re.findall(r'-\s*(.+?)\n', error_section.group(1))
            patterns['error_handling']['expected_patterns'] = messages

        # Check if loading states are mentioned
        if 'Loading state patterns detected' in content:
            patterns['loading_states']['required'] = True

        logger.debug(f"Parsed behavior standards: {len(patterns['error_handling']['expected_patterns'])} error patterns")

        return patterns

    def parse_ux_standards(self, content: str) -> dict:
        """
        Parse UX-PATTERNS.md to extract UX patterns.

        Args:
            content: Raw markdown content from UX-PATTERNS.md

        Returns:
            Dictionary with navigation, accessibility patterns
        """
        patterns = {
            'navigation': {'routing_detected': False},
            'accessibility': {'aria_required': False}
        }

        # Check if routing library is detected
        if 'Routing library detected' in content:
            patterns['navigation']['routing_detected'] = True

        # Check if ARIA attributes are required
        if 'ARIA attributes detected' in content:
            patterns['accessibility']['aria_required'] = True

        logger.debug(f"Parsed UX standards: routing={patterns['navigation']['routing_detected']}, "
                    f"aria={patterns['accessibility']['aria_required']}")

        return patterns

    def scan_for_violations(self, standards: StandardsDataDict) -> List[AuditViolationDict]:
        """
        Scan codebase and detect all violations.

        Main orchestrator that coordinates all violation detection.

        Args:
            standards: Parsed standards data

        Returns:
            List of all detected violations
        """
        logger.info("Starting violation detection scan")

        violations: List[AuditViolationDict] = []
        files_scanned = 0

        # Scan all source files (reuse logic from StandardsGenerator)
        excluded_paths = [Path(self.project_path / d).resolve() for d in EXCLUDE_DIRS]

        for ext in ALLOWED_FILE_EXTENSIONS:
            pattern = f"**/*{ext}"
            for file_path in self.project_path.glob(pattern):
                file_resolved = file_path.resolve()

                # Check excluded directories
                if any(file_resolved.is_relative_to(exc_path) for exc_path in excluded_paths if exc_path.exists()):
                    continue

                # Check symlinks (SEC-008)
                if file_path.is_symlink():
                    if not file_resolved.is_relative_to(self.project_path.resolve()):
                        log_security_event(
                            'symlink_outside_project',
                            f"Skipping symlink: {file_path}",
                            file_path=str(file_path)
                        )
                        continue

                # Check file size (SEC-007)
                try:
                    if file_path.stat().st_size > MAX_FILE_SIZE:
                        logger.warning(f"Skipping large file: {file_path}")
                        continue
                except OSError:
                    continue

                # Read file and detect violations
                try:
                    content = file_path.read_text(encoding='utf-8')
                    files_scanned += 1

                    # Detect UI violations
                    ui_violations = self.detect_ui_violations(content, file_path, standards.get('ui_patterns', {}))
                    violations.extend(ui_violations)

                    # Detect behavior violations
                    behavior_violations = self.detect_behavior_violations(content, file_path, standards.get('behavior_patterns', {}))
                    violations.extend(behavior_violations)

                    # Detect UX violations
                    ux_violations = self.detect_ux_violations(content, file_path, standards.get('ux_patterns', {}))
                    violations.extend(ux_violations)

                except Exception as e:
                    logger.debug(f"Error scanning {file_path}: {e}")
                    continue

        # Re-number violation IDs to ensure uniqueness across all files
        for i, violation in enumerate(violations):
            violation['id'] = f'V-{i + 1:03d}'

        logger.info(f"Violation detection complete: scanned {files_scanned} files, found {len(violations)} violations")

        # Store files_scanned for later use (attach to violations list as metadata)
        # This is a bit of a hack but allows us to pass the count through
        if violations:
            violations[0]['_files_scanned'] = files_scanned
        else:
            # If no violations, create a dummy entry to carry metadata
            violations.append({'_files_scanned': files_scanned, '_is_metadata': True})

        return violations

    def detect_ui_violations(self, file_content: str, file_path: Path, standards: dict) -> List[AuditViolationDict]:
        """
        Detect UI pattern violations (buttons, modals, colors).

        Args:
            file_content: Content of source file
            file_path: Path to source file
            standards: UI standards dictionary

        Returns:
            List of UI violations found
        """
        violations: List[AuditViolationDict] = []

        # Get relative path for reporting
        try:
            rel_path = str(file_path.relative_to(self.project_path))
        except ValueError:
            rel_path = str(file_path)

        # Check button sizes
        allowed_sizes = standards.get('buttons', {}).get('allowed_sizes', [])
        if allowed_sizes:
            # Find all button size attributes
            button_size_pattern = re.compile(r'<Button[^>]*\ssize=["\'"]([^"\']+)["\'"][^>]*>', re.DOTALL)
            for match in button_size_pattern.finditer(file_content):
                size = match.group(1)
                if size not in allowed_sizes:
                    line_num = file_content[:match.start()].count('\n') + 1
                    violations.append({
                        'id': f'V-{len(violations) + 1:03d}',
                        'type': 'non_standard_button_size',
                        'severity': 'major',
                        'category': 'ui_patterns',
                        'file_path': rel_path,
                        'line_number': line_num,
                        'message': f"Button uses non-standard size '{size}'",
                        'actual_value': size,
                        'expected_value': f"One of: {', '.join(allowed_sizes)}",
                        'fix_suggestion': f"Change size='{size}' to one of the approved sizes: {', '.join(allowed_sizes)}",
                        'code_snippet': self._extract_code_snippet(file_content, match.start(), 3)
                    })

        # Check button variants
        allowed_variants = standards.get('buttons', {}).get('allowed_variants', [])
        if allowed_variants:
            button_variant_pattern = re.compile(r'<Button[^>]*\svariant=["\'"]([^"\']+)["\'"][^>]*>', re.DOTALL)
            for match in button_variant_pattern.finditer(file_content):
                variant = match.group(1)
                if variant not in allowed_variants:
                    line_num = file_content[:match.start()].count('\n') + 1
                    violations.append({
                        'id': f'V-{len(violations) + 1:03d}',
                        'type': 'non_standard_button_variant',
                        'severity': 'major',
                        'category': 'ui_patterns',
                        'file_path': rel_path,
                        'line_number': line_num,
                        'message': f"Button uses non-standard variant '{variant}'",
                        'actual_value': variant,
                        'expected_value': f"One of: {', '.join(allowed_variants)}",
                        'fix_suggestion': f"Change variant='{variant}' to one of the approved variants: {', '.join(allowed_variants)}",
                        'code_snippet': self._extract_code_snippet(file_content, match.start(), 3)
                    })

        # Check colors
        allowed_colors = standards.get('colors', {}).get('allowed_hex_codes', [])
        if allowed_colors:
            # Normalize allowed colors to lowercase for comparison
            allowed_colors_lower = [c.lower() for c in allowed_colors]

            for match in self._color_pattern.finditer(file_content):
                color = match.group(0).lower()
                if color not in allowed_colors_lower:
                    line_num = file_content[:match.start()].count('\n') + 1
                    violations.append({
                        'id': f'V-{len(violations) + 1:03d}',
                        'type': 'non_standard_color',
                        'severity': 'minor',
                        'category': 'ui_patterns',
                        'file_path': rel_path,
                        'line_number': line_num,
                        'message': f"Uses undocumented color '{color}'",
                        'actual_value': color,
                        'expected_value': f"One of: {', '.join(allowed_colors[:5])}{'...' if len(allowed_colors) > 5 else ''}",
                        'fix_suggestion': f"Use an approved color from the design system instead of '{color}'",
                        'code_snippet': self._extract_code_snippet(file_content, match.start(), 3)
                    })

        return violations

    def detect_behavior_violations(self, file_content: str, file_path: Path, standards: dict) -> List[AuditViolationDict]:
        """
        Detect behavior pattern violations (errors, loading states).

        Args:
            file_content: Content of source file
            file_path: Path to source file
            standards: Behavior standards dictionary

        Returns:
            List of behavior violations found
        """
        violations: List[AuditViolationDict] = []

        # Get relative path for reporting
        try:
            rel_path = str(file_path.relative_to(self.project_path))
        except ValueError:
            rel_path = str(file_path)

        # Check error messages against expected patterns
        expected_patterns = standards.get('error_handling', {}).get('expected_patterns', [])
        if expected_patterns:
            for match in self._error_pattern.finditer(file_content):
                error_msg = match.group(1) or match.group(2)  # From throw Error or toast.error
                if error_msg:
                    # Check if message matches any expected pattern
                    matches_expected = any(pattern.lower() in error_msg.lower() for pattern in expected_patterns)

                    if not matches_expected:
                        line_num = file_content[:match.start()].count('\n') + 1
                        violations.append({
                            'id': f'V-{len(violations) + 1:03d}',
                            'type': 'non_standard_error_message',
                            'severity': 'major',
                            'category': 'behavior_patterns',
                            'file_path': rel_path,
                            'line_number': line_num,
                            'message': f"Error message doesn't follow expected patterns",
                            'actual_value': error_msg,
                            'expected_value': f"Should contain one of: {', '.join(expected_patterns[:3])}{'...' if len(expected_patterns) > 3 else ''}",
                            'fix_suggestion': f"Update error message to match project standards. Consider: '{expected_patterns[0] if expected_patterns else 'standard error format'}'",
                            'code_snippet': self._extract_code_snippet(file_content, match.start(), 3)
                        })

        # Check for loading states in async operations
        loading_required = standards.get('loading_states', {}).get('required', False)
        if loading_required:
            # Check if file has async operations
            has_async = bool(re.search(r'\basync\s+(?:function|\w+\s*\()|await\s+', file_content))

            if has_async:
                # Check if there are loading indicators
                has_loading = bool(self._loading_pattern.search(file_content))

                if not has_loading:
                    violations.append({
                        'id': f'V-{len(violations) + 1:03d}',
                        'type': 'missing_loading_state',
                        'severity': 'major',
                        'category': 'behavior_patterns',
                        'file_path': rel_path,
                        'line_number': 1,
                        'message': "File contains async operations but no loading state indicators",
                        'actual_value': "No loading state found",
                        'expected_value': "isLoading, loading state, Spinner, or Loading component",
                        'fix_suggestion': "Add loading state indicators (e.g., isLoading flag, <Spinner/>, or <Loading/>) for async operations",
                        'code_snippet': "// Async operations detected without loading states"
                    })

        return violations

    def detect_ux_violations(self, file_content: str, file_path: Path, standards: dict) -> List[AuditViolationDict]:
        """
        Detect UX pattern violations (accessibility, navigation).

        Args:
            file_content: Content of source file
            file_path: Path to source file
            standards: UX standards dictionary

        Returns:
            List of UX violations found
        """
        violations: List[AuditViolationDict] = []

        # Get relative path for reporting
        try:
            rel_path = str(file_path.relative_to(self.project_path))
        except ValueError:
            rel_path = str(file_path)

        # Check for missing ARIA attributes on interactive elements
        aria_required = standards.get('accessibility', {}).get('aria_required', False)
        if aria_required:
            # Find interactive elements without ARIA labels
            interactive_elements = [
                (r'<button[^>]*>', 'button'),
                (r'<a\s+[^>]*href[^>]*>', 'link'),
                (r'<input[^>]*>', 'input'),
                (r'<select[^>]*>', 'select'),
            ]

            for pattern_str, element_type in interactive_elements:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                for match in pattern.finditer(file_content):
                    element_tag = match.group(0)

                    # Check if element has ARIA label or aria-labelledby
                    has_aria = bool(re.search(r'aria-label(?:ledby)?=', element_tag))

                    # For buttons and links, also check for visible text content
                    has_text_content = False
                    if element_type in ['button', 'link']:
                        # Simple check: if tag closes with >, likely has text content
                        # More sophisticated: would need to parse to closing tag
                        has_text_content = '>' in element_tag and not element_tag.strip().endswith('/>')

                    if not has_aria and not has_text_content:
                        line_num = file_content[:match.start()].count('\n') + 1
                        violations.append({
                            'id': f'V-{len(violations) + 1:03d}',
                            'type': 'missing_aria_label',
                            'severity': 'critical',
                            'category': 'ux_patterns',
                            'file_path': rel_path,
                            'line_number': line_num,
                            'message': f"Interactive {element_type} missing ARIA label",
                            'actual_value': "No aria-label or aria-labelledby",
                            'expected_value': "aria-label or aria-labelledby attribute",
                            'fix_suggestion': f"Add aria-label='descriptive text' to this {element_type} for screen reader accessibility",
                            'code_snippet': self._extract_code_snippet(file_content, match.start(), 3)
                        })

        # Check navigation consistency (if routing is detected in standards)
        routing_detected = standards.get('navigation', {}).get('routing_detected', False)
        if routing_detected:
            # Check for inconsistent navigation patterns
            # Look for direct <a href> tags when routing library should be used
            direct_links = re.compile(r'<a\s+href=["\']/(?!http)', re.IGNORECASE)
            for match in direct_links.finditer(file_content):
                line_num = file_content[:match.start()].count('\n') + 1
                violations.append({
                    'id': f'V-{len(violations) + 1:03d}',
                    'type': 'inconsistent_navigation',
                    'severity': 'major',
                    'category': 'ux_patterns',
                    'file_path': rel_path,
                    'line_number': line_num,
                    'message': "Direct <a href> link instead of routing library",
                    'actual_value': "<a href> with internal path",
                    'expected_value': "Router Link component (e.g., <Link to=...>)",
                    'fix_suggestion': "Use the project's routing library (Link component) instead of plain <a> tags for internal navigation",
                    'code_snippet': self._extract_code_snippet(file_content, match.start(), 3)
                })

        return violations

    def _extract_code_snippet(self, content: str, position: int, context_lines: int = 3) -> str:
        """
        Extract code snippet around a specific position.

        Args:
            content: Full file content
            position: Character position of the violation
            context_lines: Number of lines of context to include

        Returns:
            Code snippet string
        """
        lines = content.split('\n')
        violation_line = content[:position].count('\n')

        # Calculate start and end lines
        start_line = max(0, violation_line - context_lines)
        end_line = min(len(lines), violation_line + context_lines + 1)

        # Extract snippet
        snippet_lines = lines[start_line:end_line]

        # Add line numbers
        numbered_lines = []
        for i, line in enumerate(snippet_lines):
            line_num = start_line + i + 1
            marker = '>' if (start_line + i) == violation_line else ' '
            numbered_lines.append(f"{marker} {line_num:4d} | {line}")

        return '\n'.join(numbered_lines)

    def assign_severity(self, violation_type: str, context: dict) -> str:
        """
        Assign severity level (critical/major/minor) based on impact.

        Args:
            violation_type: Type of violation
            context: Additional context for severity determination

        Returns:
            Severity level string
        """
        # Critical: Missing ARIA, security issues, broken flows
        # Major: Non-standard UI components, missing loading states
        # Minor: Undocumented colors, inconsistent messages

        # TODO: Implement in Phase 3
        return AuditSeverity.MINOR.value

    def generate_fix_suggestion(self, violation: AuditViolationDict) -> str:
        """
        Generate actionable fix suggestion for violation.

        Args:
            violation: Violation dictionary

        Returns:
            Fix suggestion string
        """
        # TODO: Implement in Phase 3
        return "Fix suggestion to be implemented"

    def calculate_compliance_score(self, violations: List[AuditViolationDict], total_patterns: int) -> ComplianceScoreDict:
        """
        Calculate compliance percentage (0-100) based on violations.

        Uses weighted scoring:
        - Critical: 10 points per violation
        - Major: 5 points per violation
        - Minor: 1 point per violation

        Args:
            violations: List of all violations
            total_patterns: Total number of checkable patterns

        Returns:
            ComplianceScoreDict with scores and grade
        """
        # Start from perfect score
        base_score = 100

        # Calculate deductions by severity
        critical_count = sum(1 for v in violations if v.get('severity') == AuditSeverity.CRITICAL.value)
        major_count = sum(1 for v in violations if v.get('severity') == AuditSeverity.MAJOR.value)
        minor_count = sum(1 for v in violations if v.get('severity') == AuditSeverity.MINOR.value)

        # Weighted deductions
        total_deduction = (critical_count * 10) + (major_count * 5) + (minor_count * 1)

        # Calculate overall score (minimum 0)
        overall_score = max(0, base_score - total_deduction)

        # Calculate category-specific scores
        ui_violations = [v for v in violations if v.get('category') == 'ui_patterns']
        ui_deduction = sum(
            10 if v.get('severity') == AuditSeverity.CRITICAL.value else
            5 if v.get('severity') == AuditSeverity.MAJOR.value else 1
            for v in ui_violations
        )
        ui_compliance = max(0, base_score - ui_deduction)

        behavior_violations = [v for v in violations if v.get('category') == 'behavior_patterns']
        behavior_deduction = sum(
            10 if v.get('severity') == AuditSeverity.CRITICAL.value else
            5 if v.get('severity') == AuditSeverity.MAJOR.value else 1
            for v in behavior_violations
        )
        behavior_compliance = max(0, base_score - behavior_deduction)

        ux_violations = [v for v in violations if v.get('category') == 'ux_patterns']
        ux_deduction = sum(
            10 if v.get('severity') == AuditSeverity.CRITICAL.value else
            5 if v.get('severity') == AuditSeverity.MAJOR.value else 1
            for v in ux_violations
        )
        ux_compliance = max(0, base_score - ux_deduction)

        # Determine letter grade
        if overall_score >= 90:
            grade = 'A'
        elif overall_score >= 80:
            grade = 'B'
        elif overall_score >= 70:
            grade = 'C'
        elif overall_score >= 60:
            grade = 'D'
        else:
            grade = 'F'

        # Passing threshold: 80 or above
        passing = overall_score >= 80

        return {
            'overall_score': overall_score,
            'ui_compliance': ui_compliance,
            'behavior_compliance': behavior_compliance,
            'ux_compliance': ux_compliance,
            'grade': grade,
            'passing': passing
        }

    def generate_audit_report(self, violations: List[AuditViolationDict], compliance: ComplianceScoreDict, scan_metadata: dict) -> str:
        """
        Generate markdown audit report with all sections.

        Args:
            violations: List of violations
            compliance: Compliance score details
            scan_metadata: Scan timing and file counts

        Returns:
            Markdown formatted audit report
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        project_name = self.project_path.name

        # Build report sections
        report_sections = []

        # Header
        report_sections.append(f"""# Codebase Audit Report

**Project**: {project_name}
**Generated**: {timestamp}
**Scan Duration**: {scan_metadata.get('duration', 0):.2f} seconds
**Files Scanned**: {scan_metadata.get('files_scanned', 0)}

---
""")

        # Executive Summary
        status_emoji = '✅' if compliance['passing'] else '❌'
        report_sections.append(f"""## Executive Summary

**Overall Compliance Score**: {compliance['overall_score']}/100 ({compliance['grade']})
**Status**: {status_emoji} {'PASSING' if compliance['passing'] else 'FAILING'} (threshold: 80)

### Compliance by Category

| Category | Score | Status |
|----------|-------|--------|
| UI Patterns | {compliance['ui_compliance']}/100 | {'✅' if compliance['ui_compliance'] >= 80 else '⚠️'} |
| Behavior Patterns | {compliance['behavior_compliance']}/100 | {'✅' if compliance['behavior_compliance'] >= 80 else '⚠️'} |
| UX Patterns | {compliance['ux_compliance']}/100 | {'✅' if compliance['ux_compliance'] >= 80 else '⚠️'} |

### Violations Summary

| Severity | Count | Weight |
|----------|-------|--------|
| 🔴 Critical | {sum(1 for v in violations if v.get('severity') == 'critical')} | -10 pts each |
| 🟠 Major | {sum(1 for v in violations if v.get('severity') == 'major')} | -5 pts each |
| 🟡 Minor | {sum(1 for v in violations if v.get('severity') == 'minor')} | -1 pt each |
| **Total** | **{len(violations)}** | |

---
""")

        # Violations by Severity
        if violations:
            report_sections.append("## Violations by Severity\n\n")

            # Critical violations
            critical = [v for v in violations if v.get('severity') == 'critical']
            if critical:
                report_sections.append("### 🔴 Critical Violations\n\n")
                for v in critical:
                    report_sections.append(self._format_violation(v))

            # Major violations
            major = [v for v in violations if v.get('severity') == 'major']
            if major:
                report_sections.append("### 🟠 Major Violations\n\n")
                for v in major:
                    report_sections.append(self._format_violation(v))

            # Minor violations
            minor = [v for v in violations if v.get('severity') == 'minor']
            if minor:
                report_sections.append("### 🟡 Minor Violations\n\n")
                for v in minor:
                    report_sections.append(self._format_violation(v))

            report_sections.append("---\n\n")

        # Violations by File
        if violations:
            report_sections.append("## Violations by File\n\n")

            # Group by file
            violations_by_file = {}
            for v in violations:
                file_path = v.get('file_path', 'unknown')
                if file_path not in violations_by_file:
                    violations_by_file[file_path] = []
                violations_by_file[file_path].append(v)

            # Sort by count (descending)
            sorted_files = sorted(violations_by_file.items(), key=lambda x: len(x[1]), reverse=True)

            for file_path, file_violations in sorted_files:
                critical_count = sum(1 for v in file_violations if v.get('severity') == 'critical')
                major_count = sum(1 for v in file_violations if v.get('severity') == 'major')
                minor_count = sum(1 for v in file_violations if v.get('severity') == 'minor')

                report_sections.append(f"### `{file_path}`\n\n")
                report_sections.append(f"**Total**: {len(file_violations)} violations ")
                report_sections.append(f"({critical_count} critical, {major_count} major, {minor_count} minor)\n\n")

                for v in file_violations:
                    report_sections.append(f"- [{v.get('id')}] Line {v.get('line_number')}: {v.get('message')}\n")

                report_sections.append("\n")

            report_sections.append("---\n\n")

        # Fix Recommendations
        if violations:
            report_sections.append("## Fix Recommendations\n\n")
            report_sections.append("### Priority Order\n\n")
            report_sections.append("1. **Critical violations** - Fix immediately (accessibility, security)\n")
            report_sections.append("2. **Major violations** - Fix soon (UX consistency, standards compliance)\n")
            report_sections.append("3. **Minor violations** - Fix when convenient (style, optimization)\n\n")

            report_sections.append("### Quick Fixes\n\n")

            # Group by type for common fixes
            violations_by_type = {}
            for v in violations:
                v_type = v.get('type', 'unknown')
                if v_type not in violations_by_type:
                    violations_by_type[v_type] = []
                violations_by_type[v_type].append(v)

            for v_type, type_violations in violations_by_type.items():
                if len(type_violations) > 1:
                    report_sections.append(f"**{v_type.replace('_', ' ').title()}** ({len(type_violations)} occurrences)\n")
                    report_sections.append(f"- {type_violations[0].get('fix_suggestion', 'No suggestion available')}\n\n")

            report_sections.append("---\n\n")

        # Scan Metadata
        report_sections.append("## Scan Metadata\n\n")
        report_sections.append(f"- **Duration**: {scan_metadata.get('duration', 0):.2f} seconds\n")
        report_sections.append(f"- **Files Scanned**: {scan_metadata.get('files_scanned', 0)}\n")
        report_sections.append(f"- **Standards Files**: {len(scan_metadata.get('standards_files', []))}\n")

        if scan_metadata.get('parse_errors'):
            report_sections.append(f"- **Parse Warnings**: {len(scan_metadata.get('parse_errors'))}\n")

        report_sections.append("\n")

        # Footer
        report_sections.append("---\n\n")
        report_sections.append("*Generated by coderef-docs audit_codebase tool*\n")

        return ''.join(report_sections)

    def _format_violation(self, violation: AuditViolationDict) -> str:
        """Format a single violation for the report."""
        output = []
        output.append(f"#### [{violation.get('id')}] {violation.get('message')}\n\n")
        output.append(f"**File**: `{violation.get('file_path')}:{violation.get('line_number')}`  \n")
        output.append(f"**Type**: {violation.get('type', 'unknown').replace('_', ' ').title()}  \n")
        output.append(f"**Actual**: {violation.get('actual_value')}  \n")
        output.append(f"**Expected**: {violation.get('expected_value')}  \n\n")

        if violation.get('fix_suggestion'):
            output.append(f"**Fix**: {violation.get('fix_suggestion')}\n\n")

        if violation.get('code_snippet'):
            output.append("```\n")
            output.append(violation.get('code_snippet'))
            output.append("\n```\n\n")

        return ''.join(output)

    def save_audit_report(self, report_content: str, audits_dir: Path, violations: List[AuditViolationDict],
                          compliance: ComplianceScoreDict, scan_metadata: dict) -> AuditResultDict:
        """
        Save audit report to timestamped file.

        Args:
            report_content: Markdown report content
            audits_dir: Directory to save report
            violations: List of violations (for stats)
            compliance: Compliance score details
            scan_metadata: Scan metadata

        Returns:
            AuditResultDict with report path and summary
        """
        logger.info(f"Saving audit report to {audits_dir}")

        # Ensure directory exists
        audits_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamped filename
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        filename = f"AUDIT-REPORT-{timestamp}.md"
        report_path = audits_dir / filename

        # Save report
        report_path.write_text(report_content, encoding='utf-8')

        # Build violation stats
        violation_stats: ViolationStatsDict = {
            'total_violations': len(violations),
            'critical_count': sum(1 for v in violations if v.get('severity') == AuditSeverity.CRITICAL.value),
            'major_count': sum(1 for v in violations if v.get('severity') == AuditSeverity.MAJOR.value),
            'minor_count': sum(1 for v in violations if v.get('severity') == AuditSeverity.MINOR.value),
            'violations_by_file': {},
            'violations_by_type': {},
            'most_violated_file': '',
            'most_common_violation': ''
        }

        result: AuditResultDict = {
            'report_path': str(report_path),
            'compliance_score': compliance['overall_score'],
            'compliance_details': compliance,
            'violation_stats': violation_stats,
            'violations': violations,
            'scan_metadata': scan_metadata,
            'success': True
        }

        logger.info("Audit report saved successfully", extra={'report_path': str(report_path)})

        return result
