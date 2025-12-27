"""
Test orchestration coordinator for managing multi-project test execution.

Coordinates test discovery and execution across multiple projects,
aggregates results, and provides unified reporting.
"""

import asyncio
import logging
from typing import Dict, List, Optional

from src.models import UnifiedTestResults
from src.test_runner import TestRunner, TestRunRequest
from src.test_aggregator import TestAggregator
from src.result_analyzer import ResultAnalyzer


logger = logging.getLogger(__name__)


class TestCoordinator:
    """Coordinates test execution across multiple projects."""

    def __init__(
        self,
        max_parallel_projects: int = 4,
        max_parallel_tests: int = 8,
    ):
        """
        Initialize test coordinator.

        Args:
            max_parallel_projects: Maximum projects to run in parallel
            max_parallel_tests: Maximum tests per project to run in parallel
        """
        self.max_parallel_projects = max_parallel_projects
        self.max_parallel_tests = max_parallel_tests
        self.runner = TestRunner()
        self.aggregator = TestAggregator()
        self.analyzer = ResultAnalyzer()

    async def run_multi_project_tests(
        self,
        project_paths: List[str],
        verbose: bool = False,
        timeout_seconds: float = 300.0,
    ) -> Dict:
        """
        Run tests across multiple projects in parallel.

        Args:
            project_paths: List of project paths to test
            verbose: Enable verbose output
            timeout_seconds: Timeout per project

        Returns:
            Dictionary with aggregated results
        """
        logger.info(f"Starting multi-project test run for {len(project_paths)} projects")

        # Create tasks for each project
        tasks = [
            self._run_project_tests(path, verbose, timeout_seconds)
            for path in project_paths
        ]

        # Run with concurrency limit
        results = []
        for i in range(0, len(tasks), self.max_parallel_projects):
            batch = tasks[i : i + self.max_parallel_projects]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)

        # Filter out exceptions
        successful_results = [
            r for r in results if isinstance(r, UnifiedTestResults)
        ]
        errors = [r for r in results if isinstance(r, Exception)]

        if errors:
            logger.warning(f"Encountered {len(errors)} errors during test execution")

        # Aggregate results
        aggregated = self.aggregator.aggregate_results(successful_results)

        # Analyze aggregated results
        health = self.analyzer.validate_test_health(aggregated)
        performance = self.analyzer.analyze_performance(aggregated)

        return {
            "status": "success" if not errors else "partial",
            "total_projects": len(project_paths),
            "successful_projects": len(successful_results),
            "failed_projects": len(errors),
            "aggregated_results": {
                "framework": aggregated.framework,
                "summary": aggregated.summary,
                "test_count": len(aggregated.tests),
            },
            "health": health,
            "performance": performance,
            "errors": [str(e) for e in errors],
        }

    async def _run_project_tests(
        self,
        project_path: str,
        verbose: bool = False,
        timeout_seconds: float = 300.0,
    ) -> UnifiedTestResults:
        """Run tests for a single project."""
        try:
            logger.info(f"Running tests for {project_path}")
            req = TestRunRequest(
                project_path=project_path,
                timeout_seconds=timeout_seconds,
                max_workers=self.max_parallel_tests,
                verbose=verbose,
            )
            result = await self.runner.run_tests(req)
            logger.info(
                f"Completed tests for {project_path}: "
                f"{result.summary.get('passed', 0)} passed, "
                f"{result.summary.get('failed', 0)} failed"
            )
            return result
        except Exception as e:
            logger.error(f"Error running tests for {project_path}: {e}")
            raise

    async def run_tests_with_comparison(
        self,
        baseline_projects: List[str],
        current_projects: List[str],
    ) -> Dict:
        """
        Run tests and compare baseline vs current.

        Useful for CI/CD pipelines to detect regressions.

        Args:
            baseline_projects: Projects to establish baseline
            current_projects: Projects to test against baseline

        Returns:
            Dictionary with comparison metrics
        """
        logger.info("Running baseline and current test suites")

        # Run baseline
        baseline_results = await self.run_multi_project_tests(baseline_projects)

        # Run current
        current_results = await self.run_multi_project_tests(current_projects)

        # Compare
        comparison = self.analyzer.compare_results(
            self._create_unified_result(baseline_results),
            self._create_unified_result(current_results),
        )

        return {
            "baseline": baseline_results,
            "current": current_results,
            "comparison": comparison,
        }

    def _create_unified_result(self, multi_project_result: Dict) -> UnifiedTestResults:
        """Convert multi-project result to unified result for comparison."""
        aggregated = multi_project_result.get("aggregated_results", {})
        return UnifiedTestResults(
            framework=aggregated.get("framework", "unknown"),
            project="multi-project",
            summary=aggregated.get("summary", {}),
            tests=[],  # Simplified for comparison
        )

    async def run_tests_by_pattern(
        self,
        project_paths: List[str],
        test_pattern: str,
        verbose: bool = False,
    ) -> Dict:
        """
        Run tests matching pattern across multiple projects.

        Args:
            project_paths: List of project paths
            test_pattern: Test name pattern to match
            verbose: Enable verbose output

        Returns:
            Dictionary with results
        """
        logger.info(f"Running tests matching pattern '{test_pattern}'")

        tasks = [
            self._run_project_tests_with_pattern(path, test_pattern, verbose)
            for path in project_paths
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = [
            r for r in results if isinstance(r, UnifiedTestResults)
        ]

        aggregated = self.aggregator.aggregate_results(successful_results)

        return {
            "pattern": test_pattern,
            "projects_tested": len(project_paths),
            "tests_found": len(aggregated.tests),
            "summary": aggregated.summary,
        }

    async def _run_project_tests_with_pattern(
        self,
        project_path: str,
        test_pattern: str,
        verbose: bool = False,
    ) -> UnifiedTestResults:
        """Run tests matching pattern in a single project."""
        req = TestRunRequest(
            project_path=project_path,
            test_pattern=test_pattern,
            verbose=verbose,
        )
        return await self.runner.run_tests(req)

    async def run_tests_by_file(
        self,
        project_path: str,
        test_files: List[str],
        verbose: bool = False,
    ) -> Dict:
        """
        Run specific test files in a project.

        Args:
            project_path: Project path
            test_files: List of test files to run
            verbose: Enable verbose output

        Returns:
            Dictionary with aggregated results
        """
        logger.info(f"Running {len(test_files)} test files in {project_path}")

        tasks = [
            self._run_single_test_file(project_path, test_file, verbose)
            for test_file in test_files
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = [
            r for r in results if isinstance(r, UnifiedTestResults)
        ]

        aggregated = self.aggregator.aggregate_results(successful_results)
        health = self.analyzer.validate_test_health(aggregated)

        return {
            "project": project_path,
            "files_tested": len(test_files),
            "summary": aggregated.summary,
            "health": health,
        }

    async def _run_single_test_file(
        self,
        project_path: str,
        test_file: str,
        verbose: bool = False,
    ) -> UnifiedTestResults:
        """Run a single test file."""
        req = TestRunRequest(
            project_path=project_path,
            test_file=test_file,
            verbose=verbose,
        )
        return await self.runner.run_tests(req)

    def get_execution_summary(
        self, results: List[UnifiedTestResults]
    ) -> Dict:
        """
        Get high-level summary of test execution.

        Args:
            results: List of test results

        Returns:
            Summary dictionary
        """
        aggregated = self.aggregator.aggregate_results(results)
        health = self.analyzer.validate_test_health(aggregated)

        return {
            "total_projects": len(results),
            "total_tests": aggregated.summary.get("total", 0),
            "total_passed": aggregated.summary.get("passed", 0),
            "total_failed": aggregated.summary.get("failed", 0),
            "total_skipped": aggregated.summary.get("skipped", 0),
            "overall_health": health,
        }


# Singleton instance
_coordinator = TestCoordinator()


async def run_multi_project_tests(
    project_paths: List[str],
    verbose: bool = False,
    timeout_seconds: float = 300.0,
) -> Dict:
    """Run tests across multiple projects (singleton wrapper)."""
    return await _coordinator.run_multi_project_tests(
        project_paths, verbose, timeout_seconds
    )
