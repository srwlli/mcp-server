"""
Consistency Checker Generator for Tool #10 (check_consistency).

Provides lightweight, fast quality gate for checking code changes against established
standards. Designed for pre-commit hooks and CI/CD pipelines with <1s performance target.
"""

from pathlib import Path
from typing import List
import subprocess
import time

# Import types
from type_defs import StandardsDataDict, AuditViolationDict, ConsistencyResultDict

# Import AuditGenerator for composition (reuse violation detection)
from generators.audit_generator import AuditGenerator

# Import logger
from logger_config import logger


class ConsistencyChecker:
    """
    Consistency checker for validating code changes against standards.

    Uses composition with AuditGenerator to reuse violation detection logic.
    Adds git integration for auto-detecting changed files and terminal-friendly output.
    """

    def __init__(self, project_path: Path, standards_dir: Path):
        """
        Initialize ConsistencyChecker.

        Args:
            project_path: Path to project root
            standards_dir: Path to standards directory
        """
        self.project_path = project_path
        self.standards_dir = standards_dir

        # Create AuditGenerator instance for composition
        self.audit_generator = AuditGenerator(project_path, standards_dir)

        logger.debug(f"ConsistencyChecker initialized", extra={
            'project_path': str(project_path),
            'standards_dir': str(standards_dir)
        })

    # Git Integration Methods (Phase 2)

    def is_git_repository(self) -> bool:
        """
        Check if project is a git repository.

        Returns:
            True if git repo, False otherwise
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            is_repo = result.returncode == 0
            logger.debug(f"Git repository check: {is_repo}", extra={'project_path': str(self.project_path)})
            return is_repo
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            logger.debug(f"Git check failed: {str(e)}", extra={'error_type': type(e).__name__})
            return False

    def detect_changed_files(self, mode: str = 'staged') -> List[Path]:
        """
        Detect changed files using git diff.

        Args:
            mode: Detection mode - 'staged', 'unstaged', or 'all'

        Returns:
            List of Path objects (relative to project root)
        """
        logger.debug(f"Detecting changed files", extra={'mode': mode})

        if not self.is_git_repository():
            logger.warning("Not a git repository, cannot auto-detect files")
            return []

        try:
            # Determine git command based on mode
            if mode == 'staged':
                cmd = ['git', 'diff', '--name-only', '--cached']
            elif mode == 'unstaged':
                cmd = ['git', 'diff', '--name-only']
            elif mode == 'all':
                # Get both staged and unstaged
                staged = self.detect_changed_files('staged')
                unstaged = self.detect_changed_files('unstaged')
                return list(set(staged + unstaged))  # Deduplicate
            else:
                raise ValueError(f"Invalid mode: {mode}")

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                logger.warning(f"Git diff failed: {result.stderr}")
                return []

            # Parse output
            files = [
                Path(line.strip())
                for line in result.stdout.splitlines()
                if line.strip()
            ]

            # Filter out deleted files (they don't exist on filesystem)
            existing_files = [
                f for f in files
                if (self.project_path / f).exists()
            ]

            logger.info(f"Detected {len(existing_files)} changed files", extra={
                'mode': mode,
                'total_changed': len(files),
                'existing': len(existing_files)
            })

            return existing_files

        except subprocess.TimeoutExpired:
            logger.error("Git diff timed out after 10 seconds")
            return []
        except (subprocess.SubprocessError, OSError) as e:
            logger.error(f"Git operation failed: {str(e)}", extra={'error_type': type(e).__name__})
            return []

    def get_file_content_from_git(self, file_path: Path, ref: str = 'HEAD') -> str:
        """
        Get file content from git at specific ref.

        Args:
            file_path: Relative path to file
            ref: Git reference (default: HEAD)

        Returns:
            File content as string (empty string if not in git)
        """
        try:
            result = subprocess.run(
                ['git', 'show', f'{ref}:{file_path}'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return ""  # File not in git

            return result.stdout

        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            return ""

    # Violation Detection Methods (Phase 3)

    def check_files(self, files: List[Path], standards: StandardsDataDict, scope: List[str]) -> List[AuditViolationDict]:
        """
        Check specific files for violations using AuditGenerator.

        Args:
            files: List of file paths to check (relative to project root)
            standards: Parsed standards data
            scope: Which standards to check ('ui_patterns', 'behavior_patterns', 'ux_patterns', 'all')

        Returns:
            List of violations found
        """
        violations = []

        logger.info(f"Checking {len(files)} files", extra={'scope': scope})

        for file_path in files:
            file_start = time.time()

            # Read file content
            full_path = self.project_path / file_path
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError) as e:
                logger.warning(f"Skipping file {file_path}: {str(e)}")
                continue

            # Check only relevant file types (tsx, jsx, ts, js)
            if not str(file_path).endswith(('.tsx', '.jsx', '.ts', '.js')):
                logger.debug(f"Skipping non-code file: {file_path}")
                continue

            # Call appropriate AuditGenerator methods based on scope
            file_violations = []

            if 'all' in scope or 'ui_patterns' in scope:
                ui_violations = self.audit_generator.detect_ui_violations(
                    content, file_path, standards.get('ui_patterns', {})
                )
                file_violations.extend(ui_violations)

            if 'all' in scope or 'behavior_patterns' in scope:
                behavior_violations = self.audit_generator.detect_behavior_violations(
                    content, file_path, standards.get('behavior_patterns', {})
                )
                file_violations.extend(behavior_violations)

            if 'all' in scope or 'ux_patterns' in scope:
                ux_violations = self.audit_generator.detect_ux_violations(
                    content, file_path, standards.get('ux_patterns', {})
                )
                file_violations.extend(ux_violations)

            violations.extend(file_violations)

            file_duration = time.time() - file_start
            logger.debug(f"Checked {file_path} in {file_duration:.3f}s", extra={
                'file_path': str(file_path),
                'violations_found': len(file_violations),
                'duration': file_duration
            })

        logger.info(f"Check complete: {len(violations)} violations found", extra={
            'files_checked': len(files),
            'total_violations': len(violations)
        })

        return violations

    def filter_by_severity_threshold(self, violations: List[AuditViolationDict], threshold: str) -> List[AuditViolationDict]:
        """
        Filter violations to only those >= severity threshold.

        Args:
            violations: List of all violations
            threshold: Severity threshold ('critical', 'major', or 'minor')

        Returns:
            Filtered list of violations
        """
        # Severity hierarchy: critical > major > minor
        severity_order = {'critical': 3, 'major': 2, 'minor': 1}
        threshold_level = severity_order.get(threshold, 1)

        filtered = [
            v for v in violations
            if severity_order.get(v.get('severity', 'minor'), 1) >= threshold_level
        ]

        logger.debug(f"Severity filtering: {len(violations)} -> {len(filtered)}", extra={
            'threshold': threshold,
            'original_count': len(violations),
            'filtered_count': len(filtered)
        })

        return filtered

    # Output Formatting Methods (Phase 4)

    def generate_check_summary(self, violations: List[AuditViolationDict], files_checked: int, duration: float) -> str:
        """
        Generate concise terminal-friendly summary.

        Args:
            violations: List of violations found
            files_checked: Number of files that were checked
            duration: Check duration in seconds

        Returns:
            Formatted summary string
        """
        # Count violations by severity
        critical_count = sum(1 for v in violations if v.get('severity') == 'critical')
        major_count = sum(1 for v in violations if v.get('severity') == 'major')
        minor_count = sum(1 for v in violations if v.get('severity') == 'minor')

        # Determine status
        status = "PASSED" if len(violations) == 0 else "FAILED"
        status_symbol = "[PASS]" if len(violations) == 0 else "[FAIL]"

        # Build summary
        lines = []
        lines.append(f"{status_symbol} Consistency check {status}\n")
        lines.append(f"{len(violations)} violations found ({critical_count} critical, {major_count} major, {minor_count} minor)")
        lines.append(f"Files checked: {files_checked}")
        lines.append(f"Duration: {duration:.2f}s\n")

        if len(violations) == 0:
            lines.append("All files comply with established standards.")
        else:
            lines.append("Violations:")
            for violation in violations:
                lines.append("  " + self.format_violation_for_terminal(violation))

        return '\n'.join(lines)

    def format_violation_for_terminal(self, violation: AuditViolationDict) -> str:
        """
        Format single violation for terminal display.

        Args:
            violation: Violation dictionary

        Returns:
            Formatted string (file:line - [severity] message)
        """
        file_path = violation.get('file_path', 'unknown')
        line = violation.get('line_number', 0)
        severity = violation.get('severity', 'minor')
        message = violation.get('message', 'Unknown violation')

        return f"{file_path}:{line} - [{severity}] {message}"
