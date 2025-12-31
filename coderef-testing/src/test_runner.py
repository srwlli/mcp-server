"""
Test execution engine for running tests across all supported frameworks.

Provides async/parallel execution with timeout handling, error management,
and result collection for pytest, jest, vitest, cargo, and mocha.
"""

import asyncio
import json
import logging
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil

# Add coderef/ utilities to path for wrapper functions
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from coderef.utils import check_coderef_available, read_coderef_output

from src.models import TestFramework, TestResult, TestStatus, UnifiedTestResults, FrameworkInfo, TestSummary


logger = logging.getLogger(__name__)


@dataclass
class TestRunRequest:
    """Request to run tests."""

    project_path: str
    framework: Optional[TestFramework] = None
    test_file: Optional[str] = None
    test_pattern: Optional[str] = None
    timeout_seconds: float = 300.0
    max_workers: int = 4
    verbose: bool = False
    use_impact_analysis: bool = False  # Use coderef impact analysis for selective testing


class TestRunner:
    """Executes tests for supported frameworks with async/parallel support."""

    def __init__(self):
        """Initialize test runner."""
        self.timeout_seconds = 300.0
        self.max_workers = 4

    def _get_impacted_test_files(self, project_path: Path) -> Optional[List[str]]:
        """
        Use .coderef/ data to determine which test files need to run based on code changes.

        Strategy:
        1. Check if .coderef/ data exists (uses check_coderef_available)
        2. Read drift.json or index.json to find recently changed files
        3. Map changed files to test files using common patterns:
           - src/foo.py → tests/test_foo.py
           - lib/bar.js → tests/bar.test.js
           - components/Button.tsx → tests/Button.spec.tsx
        4. Return list of test files to run (or None if no impact data available)

        Returns:
            List of test file paths, or None if impact analysis unavailable
        """
        try:
            if not check_coderef_available(str(project_path)):
                logger.debug("No .coderef/ data available, skipping impact analysis")
                return None

            # Try to read drift data (shows what changed since last scan)
            try:
                drift = read_coderef_output(str(project_path), 'drift')
                changed_files = drift.get('changed_files', [])
                logger.info(f"Found {len(changed_files)} changed files from drift analysis")
            except Exception:
                # Fallback: use index to find all files, assume all need testing
                logger.debug("Drift data unavailable, using index for all files")
                return None

            if not changed_files:
                logger.info("No changed files detected, running all tests")
                return None

            # Map changed source files to test files
            test_files = set()
            for file_path in changed_files:
                # Common test file patterns
                path = Path(file_path)
                stem = path.stem
                suffix = path.suffix

                # Pattern 1: src/foo.py → tests/test_foo.py
                test_files.add(str(project_path / "tests" / f"test_{stem}{suffix}"))

                # Pattern 2: lib/bar.js → tests/bar.test.js
                test_files.add(str(project_path / "tests" / f"{stem}.test{suffix}"))

                # Pattern 3: components/Button.tsx → tests/Button.spec.tsx
                test_files.add(str(project_path / "tests" / f"{stem}.spec{suffix}"))

                # Pattern 4: Same directory test files (e.g., foo.py + test_foo.py in same dir)
                if path.parent != project_path:
                    test_files.add(str(path.parent / f"test_{stem}{suffix}"))

            # Filter to only existing test files
            existing_test_files = [f for f in test_files if Path(f).exists()]

            if existing_test_files:
                logger.info(f"Impact analysis identified {len(existing_test_files)} test files to run")
                return existing_test_files
            else:
                logger.warning("No matching test files found for changed files, running all tests")
                return None

        except Exception as e:
            logger.debug(f"Impact analysis failed: {e}, running all tests")
            return None

    def _create_results(
        self,
        project: str,
        framework: TestFramework,
        tests: List[TestResult],
        duration: float = 0.0,
        error: Optional[str] = None,
    ) -> UnifiedTestResults:
        """Helper to create properly formatted UnifiedTestResults."""
        passed = sum(1 for t in tests if t.status == TestStatus.PASSED)
        failed = sum(1 for t in tests if t.status == TestStatus.FAILED)
        skipped = sum(1 for t in tests if t.status == TestStatus.SKIPPED)
        errors = sum(1 for t in tests if t.status == TestStatus.ERROR)
        total = len(tests)

        summary = TestSummary(
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration=duration,
            success_rate=100.0 if total == 0 else (passed / (total - skipped) * 100.0) if (total - skipped) > 0 else 100.0,
        )

        return UnifiedTestResults(
            project=project,
            framework=FrameworkInfo(framework=framework),
            summary=summary,
            tests=tests,
            error=error,
        )

    async def run_tests(self, request: TestRunRequest) -> UnifiedTestResults:
        """
        Run tests according to request specification.

        Supports filtering by test file or pattern, parallel execution,
        and timeout handling. Optionally uses impact analysis to run only
        tests affected by recent code changes.

        Args:
            request: TestRunRequest with project path and options

        Returns:
            UnifiedTestResults with collected and parsed test results
        """
        project_path = Path(request.project_path).resolve()

        # Detect framework if not specified
        framework = request.framework
        if framework is None:
            from src.framework_detector import detect_frameworks
            frameworks = detect_frameworks(str(project_path))
            if not frameworks:
                return self._create_results(
                    str(project_path),
                    TestFramework.UNKNOWN,
                    [],
                )
            framework = frameworks[0].framework

        # Apply impact analysis if requested (only if no explicit test_file/pattern specified)
        if request.use_impact_analysis and not request.test_file and not request.test_pattern:
            impacted_files = self._get_impacted_test_files(project_path)
            if impacted_files and len(impacted_files) > 0:
                # Run only impacted test files
                logger.info(f"Running {len(impacted_files)} impacted test files (impact analysis enabled)")
                # For pytest, we can pass multiple files
                if framework == TestFramework.PYTEST:
                    # Store impacted files in request for pytest runner
                    request.test_file = " ".join(impacted_files)  # pytest accepts multiple files
                # For other frameworks, run tests for each file and aggregate results
                # (simplified implementation - could be improved with parallel execution)

        # Run tests based on framework
        if framework == TestFramework.PYTEST:
            return await self._run_pytest(project_path, request)
        elif framework == TestFramework.JEST:
            return await self._run_jest(project_path, request)
        elif framework == TestFramework.VITEST:
            return await self._run_vitest(project_path, request)
        elif framework == TestFramework.CARGO:
            return await self._run_cargo(project_path, request)
        elif framework == TestFramework.MOCHA:
            return await self._run_mocha(project_path, request)
        else:
            return self._create_results(
                str(project_path),
                TestFramework.UNKNOWN,
                [],
            )

    # ========================================================================
    # Pytest Execution
    # ========================================================================

    async def _run_pytest(self, project_path: Path, request: TestRunRequest) -> UnifiedTestResults:
        """Run pytest tests."""
        cmd = ["python", "-m", "pytest", "-v", "--tb=short"]

        if request.test_file:
            # Handle multiple test files (from impact analysis)
            if " " in request.test_file:
                # Split and add each file
                test_files = request.test_file.split(" ")
                cmd.extend(test_files)
            else:
                cmd.append(str(request.test_file))
        elif request.test_pattern:
            cmd.extend(["-k", request.test_pattern])

        if request.verbose:
            cmd.append("-vv")

        try:
            result = await self._execute_command(
                cmd, project_path, request.timeout_seconds
            )
            return await self._parse_pytest_output(project_path, result)
        except asyncio.TimeoutError:
            return self._create_results(
                str(project_path),
                TestFramework.PYTEST,
                [],
                error="Test execution timed out",
            )
        except Exception as e:
            logger.error(f"Error running pytest: {e}")
            return self._create_results(
                str(project_path),
                TestFramework.PYTEST,
                [],
                error=str(e),
            )

    async def _parse_pytest_output(
        self, project_path: Path, stdout: str
    ) -> UnifiedTestResults:
        """Parse pytest output and return unified results."""
        tests: List[TestResult] = []

        # Parse text output from pytest -v
        tests, passed, failed, skipped = self._parse_pytest_text(stdout)

        return self._create_results(
            str(project_path),
            TestFramework.PYTEST,
            tests,
            duration=sum(t.duration for t in tests),
        )

    def _map_pytest_status(self, outcome: str) -> TestStatus:
        """Map pytest outcome to TestStatus."""
        mapping = {
            "passed": TestStatus.PASSED,
            "failed": TestStatus.FAILED,
            "skipped": TestStatus.SKIPPED,
            "error": TestStatus.ERROR,
            "xfail": TestStatus.XFAIL,
            "xpass": TestStatus.XPASS,
        }
        return mapping.get(outcome, TestStatus.ERROR)

    def _parse_pytest_text(self, stdout: str) -> Tuple[List[TestResult], int, int, int]:
        """Parse pytest text output as fallback."""
        tests: List[TestResult] = []
        passed = failed = skipped = 0

        # Extract test results from output
        for line in stdout.split("\n"):
            if " PASSED" in line:
                test_name = line.split(" ")[0]
                tests.append(TestResult(name=test_name, status=TestStatus.PASSED, duration=0))
                passed += 1
            elif " FAILED" in line:
                test_name = line.split(" ")[0]
                tests.append(TestResult(name=test_name, status=TestStatus.FAILED, duration=0))
                failed += 1
            elif " SKIPPED" in line:
                test_name = line.split(" ")[0]
                tests.append(TestResult(name=test_name, status=TestStatus.SKIPPED, duration=0))
                skipped += 1

        return tests, passed, failed, skipped

    # ========================================================================
    # Jest Execution
    # ========================================================================

    async def _run_jest(self, project_path: Path, request: TestRunRequest) -> UnifiedTestResults:
        """Run jest tests."""
        cmd = ["npm", "test", "--"]

        if request.test_file:
            cmd.append(str(request.test_file))
        elif request.test_pattern:
            cmd.extend(["-t", request.test_pattern])

        if request.verbose:
            cmd.append("--verbose")

        cmd.extend(["--json", "--outputFile=.jest-results.json"])

        try:
            result = await self._execute_command(
                cmd, project_path, request.timeout_seconds
            )
            return await self._parse_jest_output(project_path, result)
        except asyncio.TimeoutError:
            return self._create_results(
                str(project_path),
                TestFramework.JEST,
                [],
                error="Test execution timed out",
            )
        except Exception as e:
            logger.error(f"Error running jest: {e}")
            return self._create_results(
                str(project_path),
                TestFramework.JEST,
                [],
                error=str(e),
            )

    async def _parse_jest_output(
        self, project_path: Path, stdout: str
    ) -> UnifiedTestResults:
        """Parse jest output and return unified results."""
        tests: List[TestResult] = []
        passed = failed = skipped = 0

        # Try to parse JSON results if they exist
        result_file = project_path / ".jest-results.json"
        if result_file.exists():
            try:
                results = json.loads(result_file.read_text())
                for suite in results.get("testResults", []):
                    for test in suite.get("assertionResults", []):
                        status_str = test.get("status", "failed")
                        status = (
                            TestStatus.PASSED
                            if status_str == "passed"
                            else TestStatus.SKIPPED
                            if status_str == "skipped"
                            else TestStatus.FAILED
                        )
                        result = TestResult(
                            name=test.get("fullName", "unknown"),
                            status=status,
                            duration=float(test.get("duration", 0)) / 1000.0,
                            file=suite.get("name", ""),
                        )
                        tests.append(result)
                        if status == TestStatus.PASSED:
                            passed += 1
                        elif status == TestStatus.FAILED:
                            failed += 1
                        elif status == TestStatus.SKIPPED:
                            skipped += 1
                result_file.unlink()
            except Exception as e:
                logger.warning(f"Error parsing jest JSON results: {e}")

        return self._create_results(
            str(project_path),
            TestFramework.JEST,
            tests,
            duration=sum(t.duration for t in tests),
        )

    # ========================================================================
    # Vitest Execution
    # ========================================================================

    async def _run_vitest(self, project_path: Path, request: TestRunRequest) -> UnifiedTestResults:
        """Run vitest tests."""
        cmd = ["npm", "run", "test", "--"]

        if request.test_file:
            cmd.append(str(request.test_file))

        if request.verbose:
            cmd.append("--reporter=verbose")

        cmd.extend(["--reporter=json", "--outputFile=.vitest-results.json"])

        try:
            result = await self._execute_command(
                cmd, project_path, request.timeout_seconds
            )
            return await self._parse_vitest_output(project_path, result)
        except asyncio.TimeoutError:
            return UnifiedTestResults(
                project=str(project_path),
                framework=TestFramework.VITEST,
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0, "timeout": 1},
                tests=[],
                error="Test execution timed out",
            )
        except Exception as e:
            logger.error(f"Error running vitest: {e}")
            return UnifiedTestResults(
                project=str(project_path),
                framework=TestFramework.VITEST,
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                tests=[],
                error=str(e),
            )

    async def _parse_vitest_output(
        self, project_path: Path, stdout: str
    ) -> UnifiedTestResults:
        """Parse vitest output and return unified results."""
        # Similar to jest output parsing
        tests: List[TestResult] = []
        passed = failed = skipped = 0

        result_file = project_path / ".vitest-results.json"
        if result_file.exists():
            try:
                results = json.loads(result_file.read_text())
                for suite in results.get("testSuites", []):
                    for test in suite.get("tests", []):
                        status_str = test.get("state", "fail")
                        status = (
                            TestStatus.PASSED
                            if status_str == "pass"
                            else TestStatus.SKIPPED
                            if status_str == "skip"
                            else TestStatus.FAILED
                        )
                        result = TestResult(
                            name=test.get("name", "unknown"),
                            status=status,
                            duration=float(test.get("duration", 0)) / 1000.0,
                        )
                        tests.append(result)
                        if status == TestStatus.PASSED:
                            passed += 1
                        elif status == TestStatus.FAILED:
                            failed += 1
                        elif status == TestStatus.SKIPPED:
                            skipped += 1
                result_file.unlink()
            except Exception as e:
                logger.warning(f"Error parsing vitest JSON results: {e}")

        return UnifiedTestResults(
            project=str(project_path),
            framework=TestFramework.VITEST,
            summary={
                "total": len(tests),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            },
            tests=tests,
        )

    # ========================================================================
    # Cargo (Rust) Execution
    # ========================================================================

    async def _run_cargo(self, project_path: Path, request: TestRunRequest) -> UnifiedTestResults:
        """Run cargo tests."""
        cmd = ["cargo", "test", "--", "--format=json"]

        if request.test_pattern:
            cmd.extend([request.test_pattern, "--"])

        if request.verbose:
            cmd.append("--nocapture")

        try:
            result = await self._execute_command(
                cmd, project_path, request.timeout_seconds
            )
            return await self._parse_cargo_output(project_path, result)
        except asyncio.TimeoutError:
            return UnifiedTestResults(
                project=str(project_path),
                framework=TestFramework.CARGO,
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0, "timeout": 1},
                tests=[],
                error="Test execution timed out",
            )
        except Exception as e:
            logger.error(f"Error running cargo: {e}")
            return UnifiedTestResults(
                project=str(project_path),
                framework=TestFramework.CARGO,
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                tests=[],
                error=str(e),
            )

    async def _parse_cargo_output(self, project_path: Path, stdout: str) -> UnifiedTestResults:
        """Parse cargo test output and return unified results."""
        tests: List[TestResult] = []
        passed = failed = skipped = 0

        for line in stdout.split("\n"):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "test":
                    name = data.get("name", "unknown")
                    event = data.get("event", {})
                    if event.get("ok") is True:
                        status = TestStatus.PASSED
                        passed += 1
                    elif event.get("ok") is False:
                        status = TestStatus.FAILED
                        failed += 1
                    else:
                        status = TestStatus.SKIPPED
                        skipped += 1

                    result = TestResult(
                        name=name,
                        status=status,
                        duration=float(event.get("execution_time", 0)),
                    )
                    tests.append(result)
            except json.JSONDecodeError:
                continue

        return UnifiedTestResults(
            project=str(project_path),
            framework=TestFramework.CARGO,
            summary={
                "total": len(tests),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            },
            tests=tests,
        )

    # ========================================================================
    # Mocha Execution
    # ========================================================================

    async def _run_mocha(self, project_path: Path, request: TestRunRequest) -> UnifiedTestResults:
        """Run mocha tests."""
        cmd = ["npm", "test", "--"]

        if request.test_file:
            cmd.append(str(request.test_file))

        if request.verbose:
            cmd.append("--reporter=spec")

        cmd.extend(["--reporter=json", "--reporter=tap"])

        try:
            result = await self._execute_command(
                cmd, project_path, request.timeout_seconds
            )
            return await self._parse_mocha_output(project_path, result)
        except asyncio.TimeoutError:
            return UnifiedTestResults(
                project=str(project_path),
                framework=TestFramework.MOCHA,
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0, "timeout": 1},
                tests=[],
                error="Test execution timed out",
            )
        except Exception as e:
            logger.error(f"Error running mocha: {e}")
            return UnifiedTestResults(
                project=str(project_path),
                framework=TestFramework.MOCHA,
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                tests=[],
                error=str(e),
            )

    async def _parse_mocha_output(self, project_path: Path, stdout: str) -> UnifiedTestResults:
        """Parse mocha output and return unified results."""
        tests: List[TestResult] = []
        passed = failed = skipped = 0

        # Parse TAP or JSON output
        for line in stdout.split("\n"):
            if line.startswith("ok "):
                match = re.match(r"ok \d+ (.*)", line)
                if match:
                    tests.append(
                        TestResult(name=match.group(1), status=TestStatus.PASSED, duration=0)
                    )
                    passed += 1
            elif line.startswith("not ok "):
                match = re.match(r"not ok \d+ (.*)", line)
                if match:
                    tests.append(
                        TestResult(name=match.group(1), status=TestStatus.FAILED, duration=0)
                    )
                    failed += 1

        return UnifiedTestResults(
            project=str(project_path),
            framework=TestFramework.MOCHA,
            summary={
                "total": len(tests),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            },
            tests=tests,
        )

    # ========================================================================
    # Command Execution Helpers
    # ========================================================================

    async def _execute_command(
        self, cmd: List[str], cwd: Path, timeout_seconds: float
    ) -> str:
        """Execute a command and return stdout."""
        # Check if command exists
        if not shutil.which(cmd[0]):
            raise FileNotFoundError(f"Command not found: {cmd[0]}")

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout_seconds
            )
            return stdout.decode("utf-8", errors="replace")
        except asyncio.TimeoutError:
            process.kill()
            raise
        except Exception as e:
            logger.error(f"Error executing command {cmd}: {e}")
            raise


# Singleton instance
_runner = TestRunner()


async def run_tests(request: TestRunRequest) -> UnifiedTestResults:
    """Run tests according to request (singleton wrapper)."""
    return await _runner.run_tests(request)
