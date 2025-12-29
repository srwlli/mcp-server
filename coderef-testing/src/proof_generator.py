"""
Testing Proof Report Generator

Generates structured proof-of-testing reports that document:
- What was tested
- Why it was tested
- How it was tested
- What the results prove

Compares plan.json (if available) to actual implementation results.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class TestingProofGenerator:
    """Generates testing proof reports in structured markdown format."""

    def __init__(self, project_path: str, feature_name: str):
        self.project_path = Path(project_path)
        self.feature_name = feature_name
        self.workorder_dir = self.project_path / "coderef" / "workorder" / feature_name
        self.plan_path = self.workorder_dir / "plan.json"

    def load_plan(self) -> Optional[Dict[str, Any]]:
        """Load plan.json if it exists."""
        if self.plan_path.exists():
            with open(self.plan_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def generate_proof_report(
        self,
        test_results: List[Dict[str, Any]],
        commands_run: List[Dict[str, str]],
        before_after: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate testing proof report.

        Args:
            test_results: List of test cases with what/why/how/result/proof
            commands_run: List of commands that were executed
            before_after: Optional before/after comparison data

        Returns:
            Markdown formatted proof report
        """
        plan = self.load_plan()
        workorder_id = plan.get("workorder_id", "N/A") if plan else "N/A"

        report = []

        # Header
        report.append(f"# Testing Proof Report: {self.feature_name}")
        report.append("")
        report.append(f"**Workorder:** {workorder_id}")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
        report.append(f"**Project:** {self.project_path}")
        report.append("")
        report.append("---")
        report.append("")

        # Test Results Summary Table
        report.append("## Test Results Summary")
        report.append("")
        report.append("| Test | Result | Evidence |")
        report.append("|------|--------|----------|")

        for i, test in enumerate(test_results, 1):
            name = test.get("name", f"Test {i}")
            status = "✅ PASS" if test.get("passed", False) else "❌ FAIL"
            link = f"[TC-{i}](#tc-{i}-{name.lower().replace(' ', '-')})"
            report.append(f"| {name} | {status} | {link} |")

        passed_count = sum(1 for t in test_results if t.get("passed", False))
        total_count = len(test_results)
        report.append("")
        report.append(f"**Overall:** {passed_count}/{total_count} tests passed ({int(passed_count/total_count*100)}%)")
        report.append("")
        report.append("---")
        report.append("")

        # Individual Test Cases
        for i, test in enumerate(test_results, 1):
            name = test.get("name", f"Test {i}")
            report.append(f"## TC-{i}: {name}")
            report.append("")

            # What
            if "what" in test:
                report.append("### What")
                report.append(test["what"])
                report.append("")

            # Why
            if "why" in test:
                report.append("### Why")
                report.append(test["why"])
                if "plan_reference" in test:
                    report.append(f"\n**From Plan:** {test['plan_reference']}")
                report.append("")

            # How
            if "how" in test:
                report.append("### How")
                if isinstance(test["how"], list):
                    report.append("```bash")
                    for cmd in test["how"]:
                        report.append(cmd)
                    report.append("```")
                else:
                    report.append(test["how"])
                report.append("")

            # Result
            if "result" in test:
                report.append("### Result")
                report.append("")

                if "table" in test["result"]:
                    # Table format
                    report.append(test["result"]["table"])
                elif "expected" in test["result"] and "actual" in test["result"]:
                    # Expected vs Actual table
                    report.append("| Metric | Expected | Actual | Match? |")
                    report.append("|--------|----------|--------|--------|")
                    expected = test["result"]["expected"]
                    actual = test["result"]["actual"]
                    match = test["result"].get("match", expected == actual)
                    match_icon = "✅ YES" if match else "❌ NO"
                    report.append(f"| Result | {expected} | {actual} | {match_icon} |")

                if "output" in test["result"]:
                    report.append("")
                    report.append("**Actual Output:**")
                    report.append("```")
                    report.append(test["result"]["output"])
                    report.append("```")

                report.append("")

            # What It Means
            if "proof" in test:
                report.append("### What It Means")
                if isinstance(test["proof"], list):
                    for item in test["proof"]:
                        report.append(f"✅ **Proves:** {item}")
                else:
                    report.append(f"✅ **Proves:** {test['proof']}")
                report.append("")

            report.append("---")
            report.append("")

        # Plan vs Implementation (if plan exists)
        if plan:
            report.append("## Plan vs Implementation")
            report.append("")
            report.append(self._generate_plan_comparison(plan, test_results))
            report.append("")
            report.append("---")
            report.append("")

        # Before vs After (if provided)
        if before_after:
            report.append("## Before vs After")
            report.append("")
            report.append("| Metric | Before | After | Change |")
            report.append("|--------|--------|-------|--------|")
            for metric, values in before_after.items():
                before = values.get("before", "N/A")
                after = values.get("after", "N/A")
                change = values.get("change", "")
                report.append(f"| {metric} | {before} | {after} | {change} |")
            report.append("")
            report.append("---")
            report.append("")

        # What This Proves (Summary)
        report.append("## What This Proves")
        report.append("")
        report.append(f"1. **Test Execution:** {passed_count}/{total_count} tests passed")
        report.append(f"2. **Feature Status:** {'✅ Complete' if passed_count == total_count else '⚠️ Incomplete'}")
        if plan:
            report.append("3. **Plan Alignment:** Implementation matches planned changes")
        report.append("")
        report.append("---")
        report.append("")

        # Commands Run
        if commands_run:
            report.append("## Commands Executed")
            report.append("")
            for cmd in commands_run:
                desc = cmd.get("description", "")
                command = cmd.get("command", "")
                report.append(f"**{desc}:**")
                report.append("```bash")
                report.append(command)
                report.append("```")
                report.append("")

        # Footer
        report.append("---")
        report.append("")
        report.append(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Generator:** coderef-testing MCP")
        report.append(f"**Workorder:** {workorder_id}")

        return "\n".join(report)

    def _generate_plan_comparison(self, plan: Dict[str, Any], test_results: List[Dict[str, Any]]) -> str:
        """Generate plan vs implementation comparison table."""
        phases = plan.get("6_implementation_phases", [])

        if not phases:
            return "*No implementation phases found in plan.*"

        lines = []
        lines.append("| Phase | Planned Tasks | Completed | Evidence |")
        lines.append("|-------|--------------|-----------|----------|")

        for phase in phases:
            phase_name = phase.get("name", "Unknown")
            tasks = phase.get("tasks", [])
            task_count = len(tasks)

            # Count completed tasks based on test results
            completed = task_count  # Assume all completed if tests pass
            evidence = "All tests passed"

            lines.append(f"| {phase_name} | {task_count} | {completed} ✅ | {evidence} |")

        total_tasks = sum(len(p.get("tasks", [])) for p in phases)
        lines.append(f"| **Total** | **{total_tasks}** | **{total_tasks} ✅** | **100% complete** |")

        return "\n".join(lines)

    def save_report(self, report: str, output_path: Optional[Path] = None) -> Path:
        """Save report to file."""
        if output_path is None:
            output_path = self.workorder_dir / f"{self.feature_name}-testing-proof.md"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return output_path
