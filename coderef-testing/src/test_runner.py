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
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil

from src.models import TestFramework, TestResult, TestStatus, UnifiedTestResults, FrameworkInfo


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


class TestRunner:
    """Executes tests for supported frameworks with async/parallel support."""

    def __init__(self):
        """Initialize test runner."""
        self.timeout_seconds = 300.0
        self.max_workers = 4

    async def run_tests(self, request: TestRunRequest) -> UnifiedTestResults:
        """
        Run tests according to request specification.

        Supports filtering by test file or pattern, parallel execution,
        and timeout handling.

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
                return UnifiedTestResults(
                    project=str(project_path),
                    framework=TestFramework.UNKNOWN,
                    summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                    tests=[],
                )
            framework = frameworks[0].framework

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
            return UnifiedTestResults(
                project=str(project_path),
                framework=TestFramework.UNKNOWN,
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                tests=[],
            )

    # ========================================================================
    # Pytest Execution
    # ========================================================================

    async def _run_pytest(self, project_path: Path, request: TestRunRequest) -> UnifiedTestResults:
        """Run pytest tests."""
        cmd = ["pytest", "--json-report", "--json-report-file=.pytest-report.json"]

        if request.test_file:
            cmd.append(str(request.test_file))
        elif request.test_pattern:
            cmd.extend(["-k", request.test_pattern])

        if request.verbose:
            cmd.append("-v")

        cmd.append("--tb=short")

        try:
            result = await self._execute_command(
                cmd, project_path, request.timeout_seconds
            )
            return await self._parse_pytest_output(project_path, result)
        except asyncio.TimeoutError:
            return UnifiedTestResults(
                project=str(project_path),
                framework=TestFramework.PYTEST,
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0, "timeout": 1},
                tests=[],
                error="Test execution timed out",
            )
        except Exception as e:
            logger.error(f"Error running pytest: {e}")
            return UnifiedTestResults(
                project=str(project_path),
                framework=TestFramework.PYTEST,
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                tests=[],
                error=str(e),
            )

    async def _parse_pytest_output(
        self, project_path: Path, stdout: str
    ) -> UnifiedTestResults:
        """Parse pytest output and return unified results."""
        tests: List[TestResult] = []
        passed = failed = skipped = 0

        # Try to parse JSON report if it exists
        report_file = project_path / ".pytest-report.json"
        if report_file.exists():
            try:
                report = json.loads(report_file.read_text())
                for test in report.get("tests", []):
                    status = self._map_pytest_status(test.get("outcome", "failed"))
                    result = TestResult(
                        name=test.get("nodeid", "unknown"),
                        status=status,
                        duration=float(test.get("duration", 0)),
                        file=test.get("nodeid", "").split("::")[0],
                    )
                    tests.append(result)
                    if status == TestStatus.PASSED:
                        passed += 1
                    elif status == TestStatus.FAILED:
                        failed += 1
                    elif status == TestStatus.SKIPPED:
                        skipped += 1
                report_file.unlink()
            except Exception as e:
                logger.warning(f"Error parsing pytest JSON report: {e}")

        # Fallback: parse text output
        if not tests:
            tests, passed, failed, skipped = self._parse_pytest_text(stdout)

        return UnifiedTestResults(
            project=str(project_path),
            framework=TestFramework.PYTEST,
            summary={
                "total": len(tests),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            },
            tests=tests,
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
            return UnifiedTestResults(
                project=str(project_path),
                framework=TestFramework.JEST,
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0, "timeout": 1},
                tests=[],
                error="Test execution timed out",
            )
        except Exception as e:
            logger.error(f"Error running jest: {e}")
            return UnifiedTestResults(
                project=str(project_path),
                framework=TestFramework.JEST,
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                tests=[],
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

        return UnifiedTestResults(
            project=str(project_path),
            framework=TestFramework.JEST,
            summary={
                "total": len(tests),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            },
            tests=tests,
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
