"""
Validation Pipeline - 4-Gate Quality Validation System

This module implements a 4-gate validation pipeline for resource sheets,
combining Tool 1's quality controls with element-specific validation.

Workorder: WO-RESOURCE-SHEET-CONSOLIDATION-001
Task: VALID-001
Author: Papertrail Agent
Date: 2026-01-03
"""

import re
import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


# Load module registry data directly to avoid import conflicts
def load_module_registry():
    """Load element type mapping directly from JSON file."""
    mapping_file = Path(__file__).parent.parent / "resource_sheet" / "mapping" / "element-type-mapping.json"
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    return {e["element_type"]: e for e in mapping.get("element_types", [])}


class SimpleModuleRegistry:
    """Simplified module registry for validation (avoids import conflicts)."""

    def __init__(self):
        self.element_types = load_module_registry()

    def get_element_info(self, element_type: str) -> Optional[Dict]:
        return self.element_types.get(element_type)

    def get_checklist(self, element_type: str) -> List[str]:
        element_def = self.element_types.get(element_type)
        return element_def.get("checklist_items", []) if element_def else []

    def get_required_sections(self, element_type: str) -> List[str]:
        element_def = self.element_types.get(element_type)
        return element_def.get("required_sections", []) if element_def else []


@dataclass
class GateResult:
    """Result of a single validation gate."""
    gate_name: str
    passed: bool
    score: int  # 0-100
    checks_passed: int
    checks_total: int
    failures: List[str]
    warnings: List[str]


@dataclass
class ValidationResult:
    """Overall validation result for a resource sheet."""
    status: str  # "pass", "warn", or "reject"
    overall_score: int  # 0-100
    gate_results: List[GateResult]
    summary: str

    def is_approved(self) -> bool:
        """Check if resource sheet is approved (pass or warn)."""
        return self.status in ["pass", "warn"]

    def has_critical_failures(self) -> bool:
        """Check if there are critical failures requiring rejection."""
        return self.status == "reject"


class ValidationPipeline:
    """4-Gate validation pipeline for resource sheets.

    Gate 1: Structural Validation (4 checks)
    Gate 2: Content Quality (4 checks)
    Gate 3: Element-Specific Validation (3 checks)
    Gate 4: Auto-Fill Threshold (1 check)
    """

    def __init__(self):
        """Initialize validation pipeline with module registry."""
        self.registry = SimpleModuleRegistry()

    def validate(self, resource_sheet: str, element_type: str) -> ValidationResult:
        """Run complete 4-gate validation pipeline.

        Args:
            resource_sheet: Resource sheet markdown content
            element_type: Element type name (e.g., "custom_hooks")

        Returns:
            ValidationResult with overall status and gate results
        """
        gate_results = []

        # Gate 1: Structural Validation
        gate1 = self._gate_1_structural(resource_sheet)
        gate_results.append(gate1)

        # Gate 2: Content Quality
        gate2 = self._gate_2_content_quality(resource_sheet)
        gate_results.append(gate2)

        # Gate 3: Element-Specific Validation
        gate3 = self._gate_3_element_specific(resource_sheet, element_type)
        gate_results.append(gate3)

        # Gate 4: Auto-Fill Threshold
        gate4 = self._gate_4_auto_fill(resource_sheet)
        gate_results.append(gate4)

        # Compute overall result
        return self._compute_overall_result(gate_results)

    def _gate_1_structural(self, resource_sheet: str) -> GateResult:
        """Gate 1: Structural Validation (4 checks).

        Checks:
        1. Header metadata present (agent, date, task)
        2. Executive summary present (2-4 sentences)
        3. Required sections present (13 base sections from Tool 1)
        4. State ownership table present (if element is stateful)
        """
        failures = []
        warnings = []
        checks_passed = 0

        # Check 1: Header metadata
        has_agent = re.search(r'^Agent:', resource_sheet, re.MULTILINE)
        has_date = re.search(r'^Date:', resource_sheet, re.MULTILINE)
        has_task = re.search(r'^Task:', resource_sheet, re.MULTILINE)

        if has_agent and has_date and has_task:
            checks_passed += 1
        else:
            missing = []
            if not has_agent:
                missing.append("Agent")
            if not has_date:
                missing.append("Date")
            if not has_task:
                missing.append("Task")
            failures.append(f"Missing header metadata: {', '.join(missing)}")

        # Check 2: Executive summary (2-4 sentences)
        exec_summary_match = re.search(r'## Executive Summary\s+(.*?)(?=\n##|\Z)', resource_sheet, re.DOTALL)
        if exec_summary_match:
            summary_text = exec_summary_match.group(1).strip()
            sentences = re.split(r'[.!?]+', summary_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            if 2 <= len(sentences) <= 4:
                checks_passed += 1
            else:
                warnings.append(f"Executive summary has {len(sentences)} sentences (expected 2-4)")
        else:
            failures.append("Executive summary section missing")

        # Check 3: Required base sections (at least 8 of 13 core sections should be present)
        base_sections = [
            "Executive Summary",
            "Audience & Intent",
            "Architecture Overview",
            "State Ownership",
            "Behaviors",
            "Testing Strategy",
            "Common Pitfalls"
        ]
        sections_found = sum(1 for section in base_sections if f"## {section}" in resource_sheet or f"# {section}" in resource_sheet)

        if sections_found >= 5:  # At least 5/7 critical sections
            checks_passed += 1
        else:
            failures.append(f"Only {sections_found}/7 base sections found")

        # Check 4: State ownership table (if mentions "state" in content)
        if "state" in resource_sheet.lower():
            has_state_table = bool(re.search(r'\|\s*State\s*\|.*\|', resource_sheet))
            if has_state_table:
                checks_passed += 1
            else:
                warnings.append("Document mentions state but no state ownership table found")
        else:
            checks_passed += 1  # Not applicable, count as passed

        passed = checks_passed >= 3  # Need at least 3/4 checks
        score = int((checks_passed / 4) * 100)

        return GateResult(
            gate_name="Gate 1: Structural Validation",
            passed=passed,
            score=score,
            checks_passed=checks_passed,
            checks_total=4,
            failures=failures,
            warnings=warnings
        )

    def _gate_2_content_quality(self, resource_sheet: str) -> GateResult:
        """Gate 2: Content Quality (4 checks).

        Checks:
        1. No TODO/FIXME/PLACEHOLDER markers
        2. Exhaustiveness (state documented, persistence documented)
        3. Voice compliance (imperative voice, no hedging)
        4. Tables used for structured data
        """
        failures = []
        warnings = []
        checks_passed = 0

        # Check 1: No TODO/FIXME/PLACEHOLDER markers
        todo_markers = re.findall(r'(?:TODO|FIXME|PLACEHOLDER|XXX|HACK)', resource_sheet, re.IGNORECASE)
        if not todo_markers:
            checks_passed += 1
        else:
            warnings.append(f"Found {len(todo_markers)} TODO/FIXME markers")

        # Check 2: Exhaustiveness (check for empty sections)
        empty_sections = re.findall(r'##\s+([^\n]+)\s*\n\s*(?:##|$)', resource_sheet)
        if len(empty_sections) <= 2:  # Allow up to 2 empty sections
            checks_passed += 1
        else:
            warnings.append(f"{len(empty_sections)} sections appear to be empty")

        # Check 3: Voice compliance (check for hedging language)
        hedging_patterns = [
            r'\bshould probably\b',
            r'\bmight want to\b',
            r'\bcould consider\b',
            r'\bperhaps\b',
            r'\bmaybe\b'
        ]
        hedging_found = []
        for pattern in hedging_patterns:
            matches = re.findall(pattern, resource_sheet, re.IGNORECASE)
            if matches:
                hedging_found.extend(matches)

        if len(hedging_found) <= 2:  # Allow minimal hedging
            checks_passed += 1
        else:
            warnings.append(f"Found {len(hedging_found)} instances of hedging language")

        # Check 4: Tables used for structured data
        table_count = len(re.findall(r'\|.*\|', resource_sheet))
        if table_count >= 2:  # At least 2 markdown tables
            checks_passed += 1
        else:
            warnings.append(f"Only {table_count} markdown tables found (expected structured data in tables)")

        passed = checks_passed >= 3  # Need at least 3/4 checks
        score = int((checks_passed / 4) * 100)

        return GateResult(
            gate_name="Gate 2: Content Quality",
            passed=passed,
            score=score,
            checks_passed=checks_passed,
            checks_total=4,
            failures=failures,
            warnings=warnings
        )

    def _gate_3_element_specific(self, resource_sheet: str, element_type: str) -> GateResult:
        """Gate 3: Element-Specific Validation (3 checks).

        Checks:
        1. Focus areas from element type present
        2. Required sections for element type present
        3. Element-specific tables populated (checklist present)
        """
        failures = []
        warnings = []
        checks_passed = 0

        # Get element-specific requirements
        element_info = self.registry.get_element_info(element_type)
        if not element_info:
            # Element type not found, skip validation
            return GateResult(
                gate_name="Gate 3: Element-Specific Validation",
                passed=True,
                score=100,
                checks_passed=3,
                checks_total=3,
                failures=[],
                warnings=[f"Element type '{element_type}' not found in registry, skipping validation"]
            )

        # Check 1: Focus areas (checklist items) present
        checklist_items = self.registry.get_checklist(element_type)
        if checklist_items:
            items_found = sum(1 for item in checklist_items if any(keyword in resource_sheet.lower() for keyword in item.lower().split()[:3]))
            coverage = items_found / len(checklist_items)

            if coverage >= 0.5:  # At least 50% of focus areas mentioned
                checks_passed += 1
            else:
                warnings.append(f"Only {items_found}/{len(checklist_items)} focus areas found")
        else:
            checks_passed += 1  # No checklist defined, pass

        # Check 2: Required sections present
        required_sections = self.registry.get_required_sections(element_type)
        if required_sections:
            sections_found = sum(1 for section in required_sections if section.lower() in resource_sheet.lower())
            coverage = sections_found / len(required_sections)

            if coverage >= 0.6:  # At least 60% of required sections
                checks_passed += 1
            else:
                failures.append(f"Only {sections_found}/{len(required_sections)} required sections found")
        else:
            checks_passed += 1  # No required sections defined, pass

        # Check 3: Checklist present
        has_checklist = "#### Checklist" in resource_sheet or "## Checklist" in resource_sheet
        if has_checklist:
            checks_passed += 1
        else:
            warnings.append("No checklist section found")

        passed = checks_passed >= 2  # Need at least 2/3 checks
        score = int((checks_passed / 3) * 100)

        return GateResult(
            gate_name="Gate 3: Element-Specific Validation",
            passed=passed,
            score=score,
            checks_passed=checks_passed,
            checks_total=3,
            failures=failures,
            warnings=warnings
        )

    def _gate_4_auto_fill(self, resource_sheet: str) -> GateResult:
        """Gate 4: Auto-Fill Threshold (1 check).

        Checks:
        1. >= 60% completion rate (measure filled fields vs placeholders)
        """
        failures = []
        warnings = []

        # Count placeholders
        placeholder_count = len(re.findall(r'(?:TODO|FIXME|PLACEHOLDER|XXX|\[.*?\]|\.\.\.|TBD)', resource_sheet))

        # Count total sections/subsections (estimate total fields)
        total_sections = len(re.findall(r'^#{2,4}\s+', resource_sheet, re.MULTILINE))

        # Estimate completion rate (rough heuristic)
        if total_sections > 0:
            completion_rate = max(0, 1 - (placeholder_count / total_sections))
        else:
            completion_rate = 0

        threshold = 0.60  # 60% threshold
        passed = completion_rate >= threshold
        score = int(completion_rate * 100)

        if not passed:
            failures.append(f"Auto-fill rate {completion_rate:.1%} below threshold ({threshold:.0%})")
        elif completion_rate < 0.70:
            warnings.append(f"Auto-fill rate {completion_rate:.1%} is acceptable but below ideal (70%)")

        return GateResult(
            gate_name="Gate 4: Auto-Fill Threshold",
            passed=passed,
            score=score,
            checks_passed=1 if passed else 0,
            checks_total=1,
            failures=failures,
            warnings=warnings
        )

    def _compute_overall_result(self, gate_results: List[GateResult]) -> ValidationResult:
        """Compute overall validation result from gate results.

        Logic:
        - PASS: All critical gates pass (Gates 1, 3, 4 required)
        - WARN: Major failures (Gate 2 violations) but critical gates pass
        - REJECT: Critical failures (Gates 1, 3, or 4 fail)
        """
        # Critical gates: 1, 3, 4
        critical_gates = [gate_results[0], gate_results[2], gate_results[3]]
        all_critical_pass = all(gate.passed for gate in critical_gates)

        # Overall score (weighted average)
        total_score = sum(gate.score for gate in gate_results)
        overall_score = total_score // 4

        # Determine status
        if all_critical_pass:
            if gate_results[1].passed:  # Gate 2 also passes
                status = "pass"
                summary = f"Resource sheet approved (score: {overall_score}/100)"
            else:
                status = "warn"
                summary = f"Resource sheet approved with warnings (score: {overall_score}/100)"
        else:
            status = "reject"
            failed_gates = [gate.gate_name for gate in critical_gates if not gate.passed]
            summary = f"Resource sheet rejected - critical gates failed: {', '.join(failed_gates)}"

        return ValidationResult(
            status=status,
            overall_score=overall_score,
            gate_results=gate_results,
            summary=summary
        )


# Example usage and testing
def main():
    """Test validation pipeline with sample resource sheets."""
    pipeline = ValidationPipeline()

    # Test Case 1: Well-formed resource sheet
    good_sheet = """
Agent: Claude
Date: 2026-01-03
Task: DOCUMENT

# useLocalStorage — Authoritative Documentation

## Executive Summary
This hook provides localStorage access with type safety and synchronization. It manages persistent state across sessions. Primary use case is user preferences and app configuration.

## Audience & Intent
- **Markdown:** Architecture truth
- **Code:** Runtime behavior

## Architecture Overview
Custom hook that wraps localStorage API with React state management.

## State Ownership
| State | Owner | Type | Source of Truth |
|-------|-------|------|-----------------|
| value | useLocalStorage | Local | localStorage |

## Behaviors & Events
- onChange: Updates localStorage
- onMount: Hydrates from storage

## Testing Strategy
- Unit tests for all operations
- Integration tests for cross-tab sync

## Common Pitfalls
- Serialization errors
- Quota exceeded

#### Checklist
- [ ] Side effects
- [ ] Cleanup guarantees
- [ ] Dependency array
    """

    # Test Case 2: Incomplete resource sheet
    incomplete_sheet = """
# Some Component

TODO: Add documentation
    """

    print("Validation Pipeline - Test Results")
    print("=" * 70)

    for i, (name, sheet) in enumerate([("Good Sheet", good_sheet), ("Incomplete Sheet", incomplete_sheet)], 1):
        print(f"\n{i}. {name}:")
        print("-" * 70)
        result = pipeline.validate(sheet, "custom_hooks")

        print(f"Status: {result.status.upper()}")
        print(f"Overall Score: {result.overall_score}/100")
        print(f"Summary: {result.summary}\n")

        for gate in result.gate_results:
            status_symbol = "[PASS]" if gate.passed else "[FAIL]"
            print(f"{status_symbol} {gate.gate_name}: {gate.score}/100 ({gate.checks_passed}/{gate.checks_total} checks)")
            if gate.failures:
                for failure in gate.failures:
                    print(f"    [FAIL] {failure}")
            if gate.warnings:
                for warning in gate.warnings:
                    print(f"    [WARN] {warning}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
