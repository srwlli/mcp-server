"""
Performance tests for query operations.

Tests filtering, searching, and retrieval performance across generators.
Part of WO-COMPREHENSIVE-TESTING-SUITE-002.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import pytest
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ============================================================================
# FIXTURES FOR QUERY TESTING
# ============================================================================

@pytest.fixture
def project_with_changelog_history(tmp_path: Path) -> Path:
    """
    Create a project with extensive changelog history for query testing.

    Creates 100+ changelog entries across multiple versions.
    """
    project_dir = tmp_path / "changelog-history-project"
    project_dir.mkdir()

    # Create coderef structure
    coderef_dir = project_dir / "coderef"
    coderef_dir.mkdir()
    changelog_dir = coderef_dir / "changelog"
    changelog_dir.mkdir()

    # Create schema
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["project_name", "versions"],
        "properties": {
            "project_name": {"type": "string"},
            "versions": {"type": "array"}
        }
    }
    (changelog_dir / "schema.json").write_text(json.dumps(schema, indent=2))

    # Create changelog with 100 entries across 20 versions
    versions = []
    change_types = ["bugfix", "enhancement", "feature", "breaking_change", "security"]
    severities = ["critical", "major", "minor", "patch"]

    for major in range(2):  # v1.x and v2.x
        for minor in range(5):  # 5 minor versions each
            for patch in range(2):  # 2 patches each
                version_num = f"{major + 1}.{minor}.{patch}"
                changes = []

                # Add 2-5 changes per version
                for change_idx in range(3):
                    change_type = change_types[(major * 10 + minor * 2 + change_idx) % len(change_types)]
                    severity = severities[(major * 5 + minor + change_idx) % len(severities)]

                    changes.append({
                        "id": f"CHG-{major + 1}{minor}{patch}-{change_idx}",
                        "type": change_type,
                        "severity": severity,
                        "title": f"Change {change_idx} for v{version_num}",
                        "description": f"This is change {change_idx} with type {change_type}",
                        "files": [f"src/module_{minor}/file_{patch}.py"],
                        "reason": "Testing query performance",
                        "impact": "No production impact",
                        "breaking": change_type == "breaking_change",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })

                versions.append({
                    "version": version_num,
                    "date": datetime.now(timezone.utc).isoformat(),
                    "summary": f"Release {version_num}",
                    "changes": changes
                })

    changelog = {
        "project_name": "changelog-history-project",
        "versions": versions
    }
    (changelog_dir / "CHANGELOG.json").write_text(json.dumps(changelog, indent=2))

    return project_dir


@pytest.fixture
def project_with_many_experts(tmp_path: Path) -> Path:
    """
    Create a project with many context experts for query testing.
    """
    project_dir = tmp_path / "many-experts-project"
    project_dir.mkdir()

    # Create source files
    src_dir = project_dir / "src"
    src_dir.mkdir()

    for i in range(30):
        (src_dir / f"module_{i}.py").write_text(f'''"""Module {i}."""

def function_{i}():
    return {i}

class Class_{i}:
    pass
''')

    # Create coderef structure
    coderef_dir = project_dir / "coderef"
    coderef_dir.mkdir()

    experts_dir = coderef_dir / "context-experts"
    experts_dir.mkdir()
    (experts_dir / "experts").mkdir()
    (experts_dir / "cache").mkdir()

    # Create index with many experts
    domains = ["core", "api", "ui", "db", "test", "infra"]
    experts = []

    for i in range(30):
        domain = domains[i % len(domains)]
        expert = {
            "expert_id": f"CE-src-module_{i}_py-{str(i).zfill(3)}",
            "name": f"{domain.upper()}: src/module_{i}.py",
            "resource_path": f"src/module_{i}.py",
            "resource_type": "file",
            "domain": domain,
            "capabilities": ["answer_questions", "review_changes"],
            "status": "active" if i % 3 != 0 else "stale",
            "staleness_score": (i * 3) % 100,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        experts.append(expert)

        # Also save individual expert files
        expert_file = experts_dir / "experts" / f"{expert['expert_id']}.json"
        full_expert = {
            **expert,
            "code_structure": {
                "functions": [f"function_{i}"],
                "classes": [f"Class_{i}"],
                "functions_count": 1,
                "classes_count": 1
            },
            "git_history": [],
            "relationships": {},
            "usage_patterns": {}
        }
        expert_file.write_text(json.dumps(full_expert, indent=2))

    index = {
        "experts": experts,
        "total_count": len(experts),
        "by_domain": {},
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

    # Count by domain
    for domain in domains:
        index["by_domain"][domain] = sum(1 for e in experts if e["domain"] == domain)

    (experts_dir / "index.json").write_text(json.dumps(index, indent=2))

    return project_dir


@pytest.fixture
def project_with_plans(tmp_path: Path) -> Path:
    """Create a project with multiple feature plans for query testing."""
    project_dir = tmp_path / "plans-project"
    project_dir.mkdir()

    # Create coderef structure
    coderef_dir = project_dir / "coderef"
    coderef_dir.mkdir()
    working_dir = coderef_dir / "working"
    working_dir.mkdir()

    # Create 10 feature plans
    features = [
        "auth-system", "user-dashboard", "api-v2", "payment-integration",
        "notification-service", "search-feature", "analytics-module",
        "caching-layer", "rate-limiting", "audit-logging"
    ]

    for i, feature in enumerate(features):
        feature_dir = working_dir / feature
        feature_dir.mkdir()

        # Create context.json
        context = {
            "feature_name": feature,
            "description": f"Description for {feature}",
            "goal": f"Implement {feature}",
            "requirements": [f"Req {j}" for j in range(3)],
            "workorder_id": f"WO-{feature.upper().replace('-', '-')}-001",
            "gathered_at": datetime.now(timezone.utc).isoformat()
        }
        (feature_dir / "context.json").write_text(json.dumps(context, indent=2))

        # Create plan.json
        plan = {
            "META_DOCUMENTATION": {
                "feature_name": feature,
                "schema_version": "1.0.0",
                "status": "complete" if i % 2 == 0 else "partial",
                "generated_at": datetime.now(timezone.utc).isoformat()
            },
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "1_executive_summary": {
                    "feature_name": feature.replace("-", " ").title(),
                    "description": f"Implementation of {feature}",
                    "goal": f"Deliver {feature} functionality"
                },
                "5_task_id_system": {
                    "workorder": {
                        "id": f"WO-{feature.upper().replace('-', '-')}-001",
                        "name": feature.replace("-", " ").title()
                    },
                    "tasks": [
                        {"id": f"TASK-{i}-{j}", "description": f"Task {j}"}
                        for j in range(5)
                    ]
                }
            }
        }
        (feature_dir / "plan.json").write_text(json.dumps(plan, indent=2))

    return project_dir


# ============================================================================
# CHANGELOG QUERY PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
class TestChangelogQueryPerformance:
    """Performance tests for changelog query operations."""

    def test_get_all_changelog_performance(self, project_with_changelog_history: Path):
        """Get all changelog entries should be fast even with many entries."""
        from generators.changelog_generator import ChangelogGenerator

        generator = ChangelogGenerator(project_with_changelog_history)

        start_time = time.time()
        result = generator.get_changelog()
        elapsed = time.time() - start_time

        assert "versions" in result
        assert len(result["versions"]) >= 20
        assert elapsed < 0.5, f"Get all changelog took {elapsed:.3f}s, expected < 0.5s"

    def test_get_specific_version_performance(self, project_with_changelog_history: Path):
        """Retrieving a specific version should be O(n) at worst."""
        from generators.changelog_generator import ChangelogGenerator

        generator = ChangelogGenerator(project_with_changelog_history)

        # Test multiple version lookups
        versions_to_test = ["1.0.0", "1.2.1", "2.3.0", "2.4.1"]
        total_time = 0

        for version in versions_to_test:
            start_time = time.time()
            result = generator.get_changelog(version=version)
            elapsed = time.time() - start_time
            total_time += elapsed

            assert result.get("version") == version or "versions" in result

        avg_time = total_time / len(versions_to_test)
        assert avg_time < 0.1, f"Average version lookup took {avg_time:.3f}s, expected < 0.1s"

    def test_filter_by_change_type_performance(self, project_with_changelog_history: Path):
        """Filtering by change type should be efficient."""
        from generators.changelog_generator import ChangelogGenerator

        generator = ChangelogGenerator(project_with_changelog_history)

        change_types = ["bugfix", "enhancement", "feature", "breaking_change", "security"]

        for change_type in change_types:
            start_time = time.time()
            result = generator.get_changelog(change_type=change_type)
            elapsed = time.time() - start_time

            assert elapsed < 0.2, f"Filter by {change_type} took {elapsed:.3f}s, expected < 0.2s"

    def test_filter_breaking_changes_performance(self, project_with_changelog_history: Path):
        """Filtering breaking changes should be efficient."""
        from generators.changelog_generator import ChangelogGenerator

        generator = ChangelogGenerator(project_with_changelog_history)

        start_time = time.time()
        result = generator.get_changelog(breaking_only=True)
        elapsed = time.time() - start_time

        assert elapsed < 0.2, f"Breaking changes filter took {elapsed:.3f}s, expected < 0.2s"


# ============================================================================
# CONTEXT EXPERT QUERY PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
class TestExpertQueryPerformance:
    """Performance tests for context expert query operations."""

    def test_list_all_experts_performance(self, project_with_many_experts: Path):
        """Listing all experts should be fast."""
        from generators.context_expert_generator import ContextExpertGenerator

        generator = ContextExpertGenerator(project_with_many_experts)

        start_time = time.time()
        result = generator.list_experts()
        elapsed = time.time() - start_time

        assert result.get("success", False)
        assert len(result.get("experts", [])) >= 30
        assert elapsed < 0.3, f"List experts took {elapsed:.3f}s, expected < 0.3s"

    def test_filter_by_domain_performance(self, project_with_many_experts: Path):
        """Filtering experts by domain should be efficient."""
        from generators.context_expert_generator import ContextExpertGenerator

        generator = ContextExpertGenerator(project_with_many_experts)

        domains = ["core", "api", "ui", "db", "test", "infra"]

        for domain in domains:
            start_time = time.time()
            result = generator.list_experts(domain=domain)
            elapsed = time.time() - start_time

            assert elapsed < 0.2, f"Filter by {domain} took {elapsed:.3f}s, expected < 0.2s"

    def test_filter_by_status_performance(self, project_with_many_experts: Path):
        """Filtering experts by status should be efficient."""
        from generators.context_expert_generator import ContextExpertGenerator

        generator = ContextExpertGenerator(project_with_many_experts)

        for status in ["active", "stale"]:
            start_time = time.time()
            result = generator.list_experts(status=status)
            elapsed = time.time() - start_time

            assert elapsed < 0.2, f"Filter by {status} took {elapsed:.3f}s, expected < 0.2s"

    def test_get_expert_by_id_performance(self, project_with_many_experts: Path):
        """Getting a specific expert by ID should be O(1)."""
        from generators.context_expert_generator import ContextExpertGenerator

        generator = ContextExpertGenerator(project_with_many_experts)

        # Test multiple ID lookups
        expert_ids = [f"CE-src-module_{i}_py-{str(i).zfill(3)}" for i in range(10)]
        total_time = 0

        for expert_id in expert_ids:
            start_time = time.time()
            result = generator.get_expert(expert_id)
            elapsed = time.time() - start_time
            total_time += elapsed

        avg_time = total_time / len(expert_ids)
        assert avg_time < 0.05, f"Average expert lookup took {avg_time:.3f}s, expected < 0.05s"


# ============================================================================
# PLANNING QUERY PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
class TestPlanningQueryPerformance:
    """Performance tests for planning-related queries."""

    def test_load_context_performance(self, project_with_plans: Path):
        """Loading context should be fast for any feature."""
        from generators.planning_generator import PlanningGenerator

        generator = PlanningGenerator(project_with_plans)

        features = ["auth-system", "api-v2", "caching-layer"]
        total_time = 0

        for feature in features:
            start_time = time.time()
            result = generator.load_context(feature)
            elapsed = time.time() - start_time
            total_time += elapsed

        avg_time = total_time / len(features)
        assert avg_time < 0.05, f"Average context load took {avg_time:.3f}s, expected < 0.05s"

    def test_validate_plan_performance(self, project_with_plans: Path):
        """Plan validation should complete quickly."""
        from generators.planning_generator import PlanningGenerator

        generator = PlanningGenerator(project_with_plans)

        features = ["auth-system", "user-dashboard", "api-v2"]
        total_time = 0

        for feature in features:
            plan_path = project_with_plans / "coderef" / "working" / feature / "plan.json"

            start_time = time.time()
            result = generator.validate_plan(str(plan_path))
            elapsed = time.time() - start_time
            total_time += elapsed

        avg_time = total_time / len(features)
        assert avg_time < 0.2, f"Average plan validation took {avg_time:.3f}s, expected < 0.2s"


# ============================================================================
# BATCH QUERY PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
class TestBatchQueryPerformance:
    """Performance tests for batch query operations."""

    def test_sequential_expert_queries(self, project_with_many_experts: Path):
        """Sequential expert queries should not degrade."""
        from generators.context_expert_generator import ContextExpertGenerator

        generator = ContextExpertGenerator(project_with_many_experts)

        # Run 20 sequential queries
        start_time = time.time()
        for i in range(20):
            if i % 3 == 0:
                generator.list_experts()
            elif i % 3 == 1:
                generator.list_experts(domain="core")
            else:
                generator.get_expert(f"CE-src-module_{i % 10}_py-{str(i % 10).zfill(3)}")
        elapsed = time.time() - start_time

        avg_per_query = elapsed / 20
        assert avg_per_query < 0.1, f"Average query time {avg_per_query:.3f}s, expected < 0.1s"

    def test_mixed_generator_queries(
        self,
        project_with_changelog_history: Path,
        project_with_many_experts: Path
    ):
        """Mixed queries across generators should not interfere."""
        from generators.changelog_generator import ChangelogGenerator
        from generators.context_expert_generator import ContextExpertGenerator

        changelog_gen = ChangelogGenerator(project_with_changelog_history)
        expert_gen = ContextExpertGenerator(project_with_many_experts)

        start_time = time.time()

        # Interleave queries
        for i in range(10):
            changelog_gen.get_changelog(version=f"1.{i % 5}.0")
            expert_gen.list_experts(domain=["core", "api", "ui"][i % 3])

        elapsed = time.time() - start_time

        avg_per_query = elapsed / 20
        assert avg_per_query < 0.1, f"Mixed query avg {avg_per_query:.3f}s, expected < 0.1s"


# ============================================================================
# INDEX PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
class TestIndexPerformance:
    """Tests for index-based query optimization."""

    def test_expert_index_load_time(self, project_with_many_experts: Path):
        """Expert index should load quickly."""
        from generators.context_expert_generator import ContextExpertGenerator

        # Create fresh generator (forces index load)
        start_time = time.time()
        generator = ContextExpertGenerator(project_with_many_experts)
        # Access experts to trigger index load
        _ = generator.list_experts()
        elapsed = time.time() - start_time

        assert elapsed < 0.5, f"Index load took {elapsed:.3f}s, expected < 0.5s"

    def test_changelog_parse_time(self, project_with_changelog_history: Path):
        """Changelog JSON parsing should be efficient."""
        from generators.changelog_generator import ChangelogGenerator

        # Create fresh generator
        start_time = time.time()
        generator = ChangelogGenerator(project_with_changelog_history)
        # Access to trigger parse
        _ = generator.get_changelog()
        elapsed = time.time() - start_time

        assert elapsed < 0.3, f"Changelog parse took {elapsed:.3f}s, expected < 0.3s"


# ============================================================================
# CACHING PERFORMANCE TESTS
# ============================================================================

@pytest.mark.performance
class TestCachingPerformance:
    """Tests for caching effectiveness."""

    def test_repeated_expert_queries_use_cache(self, project_with_many_experts: Path):
        """Repeated queries should benefit from caching."""
        from generators.context_expert_generator import ContextExpertGenerator

        generator = ContextExpertGenerator(project_with_many_experts)

        # First query (cold)
        start_cold = time.time()
        generator.get_expert("CE-src-module_0_py-000")
        cold_time = time.time() - start_cold

        # Repeated queries (should use cache or be equally fast)
        warm_times = []
        for _ in range(5):
            start_warm = time.time()
            generator.get_expert("CE-src-module_0_py-000")
            warm_times.append(time.time() - start_warm)

        avg_warm = sum(warm_times) / len(warm_times)

        # Warm queries should be at least as fast as cold
        assert avg_warm <= cold_time * 1.5, f"Warm queries ({avg_warm:.3f}s) slower than cold ({cold_time:.3f}s)"

    def test_repeated_changelog_queries(self, project_with_changelog_history: Path):
        """Repeated changelog queries should be consistent."""
        from generators.changelog_generator import ChangelogGenerator

        generator = ChangelogGenerator(project_with_changelog_history)

        times = []
        for _ in range(10):
            start = time.time()
            generator.get_changelog()
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        # Times should be consistent (no major variance)
        variance = max_time - min_time
        assert variance < 0.2, f"Query time variance {variance:.3f}s too high"
        assert avg_time < 0.3, f"Average query time {avg_time:.3f}s too high"


# ============================================================================
# QUERY BASELINE METRICS
# ============================================================================

@pytest.mark.performance
class TestQueryBaselines:
    """Establish query performance baselines."""

    def test_record_query_baselines(
        self,
        project_with_changelog_history: Path,
        project_with_many_experts: Path
    ):
        """Record query performance baselines for regression testing."""
        from generators.changelog_generator import ChangelogGenerator
        from generators.context_expert_generator import ContextExpertGenerator

        metrics = {}

        # Changelog queries
        cgen = ChangelogGenerator(project_with_changelog_history)

        start = time.time()
        cgen.get_changelog()
        metrics["changelog_get_all"] = time.time() - start

        start = time.time()
        cgen.get_changelog(version="1.2.0")
        metrics["changelog_get_version"] = time.time() - start

        start = time.time()
        cgen.get_changelog(change_type="feature")
        metrics["changelog_filter_type"] = time.time() - start

        # Expert queries
        egen = ContextExpertGenerator(project_with_many_experts)

        start = time.time()
        egen.list_experts()
        metrics["expert_list_all"] = time.time() - start

        start = time.time()
        egen.list_experts(domain="core")
        metrics["expert_filter_domain"] = time.time() - start

        start = time.time()
        egen.get_expert("CE-src-module_0_py-000")
        metrics["expert_get_by_id"] = time.time() - start

        # Log metrics
        print("\n=== Query Performance Baselines ===")
        for op, elapsed in metrics.items():
            print(f"  {op}: {elapsed:.4f}s")
        print("===================================\n")

        # All queries should be fast
        for op, elapsed in metrics.items():
            assert elapsed < 0.5, f"{op} took {elapsed:.3f}s, expected < 0.5s"
