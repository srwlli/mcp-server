"""
Test result aggregation module for normalizing and archiving test results.

Aggregates results from multiple test runs across different frameworks,
normalizes them to unified schema, and provides result archival with
timestamping for historical tracking.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.models import UnifiedTestResults, TestResult, TestStatus


logger = logging.getLogger(__name__)


class TestAggregator:
    """Aggregates and archives test results with timestamping."""

    def __init__(self, archive_dir: Optional[str] = None):
        """
        Initialize test aggregator.

        Args:
            archive_dir: Directory to store archived results. Defaults to .test-archive
        """
        if archive_dir is None:
            archive_dir = ".test-archive"
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def aggregate_results(
        self, results_list: List[UnifiedTestResults]
    ) -> UnifiedTestResults:
        """
        Aggregate multiple test results into single summary.

        Combines results from multiple frameworks/files into unified view
        with merged statistics.

        Args:
            results_list: List of UnifiedTestResults to aggregate

        Returns:
            Aggregated UnifiedTestResults with combined statistics
        """
        if not results_list:
            return UnifiedTestResults(
                project="unknown",
                framework="unknown",
                summary={"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                tests=[],
            )

        # Combine all tests
        all_tests: List[TestResult] = []
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_error = 0
        total_xfail = 0
        total_xpass = 0

        for result in results_list:
            all_tests.extend(result.tests)
            total_passed += result.summary.get("passed", 0)
            total_failed += result.summary.get("failed", 0)
            total_skipped += result.summary.get("skipped", 0)
            total_error += result.summary.get("error", 0)
            total_xfail += result.summary.get("xfail", 0)
            total_xpass += result.summary.get("xpass", 0)

        # Get project from first result
        project = results_list[0].project if results_list else "unknown"

        # Build summary
        summary = {
            "total": len(all_tests),
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
        }

        if total_error > 0:
            summary["error"] = total_error
        if total_xfail > 0:
            summary["xfail"] = total_xfail
        if total_xpass > 0:
            summary["xpass"] = total_xpass

        return UnifiedTestResults(
            project=project,
            framework="aggregated",
            summary=summary,
            tests=all_tests,
        )

    def archive_results(
        self,
        results: UnifiedTestResults,
        timestamp: Optional[datetime] = None,
        run_name: Optional[str] = None,
    ) -> Path:
        """
        Archive test results with timestamp.

        Saves results to archive directory with ISO 8601 timestamp.
        Useful for tracking test history and trends.

        Args:
            results: UnifiedTestResults to archive
            timestamp: Timestamp for archive. Defaults to current time.
            run_name: Optional name for the run (e.g., "nightly", "ci-build-123")

        Returns:
            Path to archived results file
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Create timestamped filename
        iso_time = timestamp.isoformat().replace(":", "-").replace(".", "-")
        framework = results.framework
        suffix = f"_{run_name}" if run_name else ""
        filename = f"{framework}_{iso_time}{suffix}.json"

        archive_path = self.archive_dir / filename

        # Prepare archive data
        archive_data = {
            "archived_at": timestamp.isoformat(),
            "run_name": run_name,
            "framework": results.framework,
            "project": results.project,
            "summary": results.summary,
            "tests": [
                {
                    "name": t.name,
                    "status": t.status.value,
                    "duration": t.duration,
                    "file": t.file,
                    "line": t.line,
                    "error_message": t.error_message,
                }
                for t in results.tests
            ],
        }

        # Write archive file
        archive_path.write_text(json.dumps(archive_data, indent=2))
        logger.info(f"Archived results to {archive_path}")

        return archive_path

    def get_archived_results(
        self, framework: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve archived results, optionally filtered by framework.

        Args:
            framework: Optional framework name to filter by

        Returns:
            List of archived result dictionaries sorted by date (newest first)
        """
        results = []

        for archive_file in sorted(
            self.archive_dir.glob("*.json"), reverse=True
        ):
            try:
                data = json.loads(archive_file.read_text())

                if framework is None or data.get("framework") == framework:
                    results.append(data)
            except Exception as e:
                logger.warning(f"Error reading archive file {archive_file}: {e}")

        return results

    def get_latest_result(self, framework: Optional[str] = None) -> Optional[Dict]:
        """
        Get the latest archived result, optionally for specific framework.

        Args:
            framework: Optional framework name

        Returns:
            Latest archived result dict or None if no results
        """
        results = self.get_archived_results(framework)
        return results[0] if results else None

    def compare_results(
        self,
        result1: UnifiedTestResults,
        result2: UnifiedTestResults,
    ) -> Dict:
        """
        Compare two test results and return differences.

        Useful for detecting regressions or improvements between runs.

        Args:
            result1: First test result (baseline)
            result2: Second test result (comparison)

        Returns:
            Dictionary with comparison metrics
        """
        summary1 = result1.summary
        summary2 = result2.summary

        diff_passed = summary2.get("passed", 0) - summary1.get("passed", 0)
        diff_failed = summary2.get("failed", 0) - summary1.get("failed", 0)
        diff_skipped = summary2.get("skipped", 0) - summary1.get("skipped", 0)
        diff_total = summary2.get("total", 0) - summary1.get("total", 0)

        # Build test name maps for comparison
        tests1 = {t.name: t for t in result1.tests}
        tests2 = {t.name: t for t in result2.tests}

        # Find status changes
        status_changes = {}
        for test_name in set(tests1.keys()) | set(tests2.keys()):
            test1 = tests1.get(test_name)
            test2 = tests2.get(test_name)

            if test1 and test2 and test1.status != test2.status:
                status_changes[test_name] = {
                    "old_status": test1.status.value,
                    "new_status": test2.status.value,
                    "old_duration": test1.duration,
                    "new_duration": test2.duration,
                }

        # Find new and removed tests
        new_tests = [name for name in tests2.keys() if name not in tests1]
        removed_tests = [name for name in tests1.keys() if name not in tests2]

        return {
            "total_change": diff_total,
            "passed_change": diff_passed,
            "failed_change": diff_failed,
            "skipped_change": diff_skipped,
            "status_changes": status_changes,
            "new_tests": new_tests,
            "removed_tests": removed_tests,
            "regression": diff_failed > 0,
            "improvement": diff_passed > 0 and diff_failed <= 0,
        }

    def get_result_history(
        self, framework: Optional[str] = None, limit: int = 10
    ) -> List[Dict]:
        """
        Get historical trend of test results.

        Args:
            framework: Optional framework filter
            limit: Maximum number of results to return

        Returns:
            List of result summaries with timestamps
        """
        archived = self.get_archived_results(framework)
        return [
            {
                "archived_at": r.get("archived_at"),
                "run_name": r.get("run_name"),
                "framework": r.get("framework"),
                "summary": r.get("summary"),
            }
            for r in archived[:limit]
        ]

    def export_results(
        self,
        results: UnifiedTestResults,
        export_path: str,
        format: str = "json",
    ) -> Path:
        """
        Export test results in specified format.

        Args:
            results: Results to export
            export_path: Path to export to
            format: Export format ('json', 'csv', 'html')

        Returns:
            Path to exported file

        Raises:
            ValueError: If unsupported format specified
        """
        export_path_obj = Path(export_path)
        export_path_obj.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            return self._export_json(results, export_path_obj)
        elif format == "csv":
            return self._export_csv(results, export_path_obj)
        elif format == "html":
            return self._export_html(results, export_path_obj)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_json(
        self, results: UnifiedTestResults, path: Path
    ) -> Path:
        """Export results as JSON."""
        data = {
            "framework": results.framework,
            "project": results.project,
            "summary": results.summary,
            "tests": [
                {
                    "name": t.name,
                    "status": t.status.value,
                    "duration": t.duration,
                    "file": t.file,
                    "line": t.line,
                    "error_message": t.error_message,
                }
                for t in results.tests
            ],
            "exported_at": datetime.utcnow().isoformat(),
        }
        path.write_text(json.dumps(data, indent=2))
        logger.info(f"Exported results to {path}")
        return path

    def _export_csv(
        self, results: UnifiedTestResults, path: Path
    ) -> Path:
        """Export results as CSV."""
        import csv

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["test_name", "status", "duration_seconds", "file", "line"]
            )

            for test in results.tests:
                writer.writerow(
                    [
                        test.name,
                        test.status.value,
                        test.duration,
                        test.file or "",
                        test.line or "",
                    ]
                )

        logger.info(f"Exported results to {path}")
        return path

    def _export_html(
        self, results: UnifiedTestResults, path: Path
    ) -> Path:
        """Export results as HTML report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Results - {results.framework}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .passed {{ color: green; font-weight: bold; }}
        .failed {{ color: red; font-weight: bold; }}
        .skipped {{ color: orange; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Test Results: {results.framework}</h1>
    <p>Project: {results.project}</p>
    <p>Generated: {datetime.utcnow().isoformat()}</p>

    <div class="summary">
        <h2>Summary</h2>
        <p>Total: {results.summary.get('total', 0)}</p>
        <p><span class="passed">Passed: {results.summary.get('passed', 0)}</span></p>
        <p><span class="failed">Failed: {results.summary.get('failed', 0)}</span></p>
        <p><span class="skipped">Skipped: {results.summary.get('skipped', 0)}</span></p>
    </div>

    <table>
        <thead>
            <tr>
                <th>Test Name</th>
                <th>Status</th>
                <th>Duration (s)</th>
                <th>File</th>
            </tr>
        </thead>
        <tbody>
"""

        for test in results.tests:
            status_class = (
                "passed"
                if test.status == TestStatus.PASSED
                else "failed"
                if test.status == TestStatus.FAILED
                else "skipped"
            )
            html += f"""            <tr>
                <td>{test.name}</td>
                <td><span class="{status_class}">{test.status.value}</span></td>
                <td>{test.duration:.2f}</td>
                <td>{test.file or ""}</td>
            </tr>
"""

        html += """        </tbody>
    </table>
</body>
</html>"""

        path.write_text(html)
        logger.info(f"Exported results to {path}")
        return path

    def cleanup_old_archives(self, keep_days: int = 30) -> int:
        """
        Clean up old archived results.

        Args:
            keep_days: Number of days of archives to keep

        Returns:
            Number of files deleted
        """
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=keep_days)
        deleted = 0

        for archive_file in self.archive_dir.glob("*.json"):
            try:
                file_mtime = datetime.fromtimestamp(archive_file.stat().st_mtime)
                if file_mtime < cutoff:
                    archive_file.unlink()
                    deleted += 1
                    logger.info(f"Deleted old archive: {archive_file}")
            except Exception as e:
                logger.warning(f"Error deleting archive {archive_file}: {e}")

        return deleted


# Singleton instance
_aggregator = TestAggregator()


def aggregate_results(results_list: List[UnifiedTestResults]) -> UnifiedTestResults:
    """Aggregate multiple test results (singleton wrapper)."""
    return _aggregator.aggregate_results(results_list)


def archive_results(
    results: UnifiedTestResults,
    timestamp: Optional[datetime] = None,
    run_name: Optional[str] = None,
) -> Path:
    """Archive test results (singleton wrapper)."""
    return _aggregator.archive_results(results, timestamp, run_name)
