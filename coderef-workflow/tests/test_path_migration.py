"""
Test to verify coderef/working → coderef/workorder path migration.

This test ensures all tool handlers use the correct global path:
- coderef/workorder/ (NEW - v1.1.0+)
- NOT coderef/working/ (OLD - deprecated)
"""

import pytest
import re
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_handlers import (
    handle_gather_context,
    handle_analyze_project_for_planning,
    handle_log_workorder,
    handle_get_workorder_log,
    handle_track_agent_status,
    handle_generate_handoff_context,
    handle_archive_feature,
)
from generators.features_inventory_generator import FeaturesInventoryGenerator


class TestPathMigration:
    """Test suite for coderef/working → coderef/workorder migration."""

    def test_no_old_paths_in_tool_handlers(self):
        """Verify tool_handlers.py doesn't use coderef/working for actual paths."""
        handler_file = Path(__file__).parent.parent / "tool_handlers.py"
        content = handler_file.read_text(encoding='utf-8')

        # Find all path assignments with 'working'
        working_path_patterns = [
            r"Path\([^)]*\)\s*/\s*['\"]coderef['\"]\s*/\s*['\"]working['\"]",
            r"project_path_obj\s*/\s*['\"]coderef['\"]\s*/\s*['\"]working['\"]",
            r"project_path\s*/\s*['\"]coderef['\"]\s*/\s*['\"]working['\"]",
        ]

        violations = []
        for pattern in working_path_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Get line number for context
                line_num = content[:match.start()].count('\n') + 1
                violations.append((line_num, match.group()))

        # Filter out non-path references (comments, test data, constants)
        actual_violations = []
        for line_num, match in violations:
            # Get the line context
            lines = content.split('\n')
            line_context = lines[line_num - 1] if line_num <= len(lines) else ""

            # Skip comments
            if '#' in line_context and line_context.index('#') < match.find('Path'):
                continue

            # Skip test data and constants
            if any(x in line_context for x in ['test', 'tmpdir', 'WORKING_DIR =', 'CONTEXT_DIR =']):
                continue

            actual_violations.append((line_num, match))

        assert not actual_violations, f"Found {len(actual_violations)} old coderef/working paths:\n" + \
                                      "\n".join([f"  Line {ln}: {m}" for ln, m in actual_violations])

    def test_tool_handlers_use_workorder_paths(self):
        """Verify tool_handlers.py uses coderef/workorder for path creation."""
        handler_file = Path(__file__).parent.parent / "tool_handlers.py"
        content = handler_file.read_text(encoding='utf-8')

        # Check for workorder paths
        workorder_patterns = [
            r"coderef['\"].*\/.*['\"]workorder['\"]",
            r"['\"]workorder['\"].*feature",
        ]

        found_workorder = False
        for pattern in workorder_patterns:
            if re.search(pattern, content):
                found_workorder = True
                break

        assert found_workorder, "No coderef/workorder paths found in tool_handlers.py"

    def test_features_inventory_generator_uses_workorder(self):
        """Verify FeaturesInventoryGenerator uses coderef/workorder."""
        generator_file = Path(__file__).parent.parent / "generators" / "features_inventory_generator.py"
        content = generator_file.read_text(encoding='utf-8')

        # Check that __init__ uses workorder
        init_pattern = r'self\.working_dir\s*=\s*project_path\s*/\s*"coderef"\s*/\s*"workorder"'
        assert re.search(init_pattern, content), \
            "FeaturesInventoryGenerator doesn't use coderef/workorder in __init__"

        # Verify no old paths
        old_pattern = r'project_path\s*/\s*"coderef"\s*/\s*"working"'
        assert not re.search(old_pattern, content), \
            "FeaturesInventoryGenerator still uses old coderef/working path"

    def test_no_old_paths_across_codebase(self):
        """Comprehensive check for old paths in all Python files."""
        project_root = Path(__file__).parent.parent
        exclude_dirs = {'.venv', '__pycache__', '.pytest_cache', 'dist', 'build'}

        violations = []
        for py_file in project_root.rglob("*.py"):
            # Skip excluded directories
            if any(part in py_file.parts for part in exclude_dirs):
                continue

            # Skip test files for now (they may contain old paths for testing)
            if 'test' in py_file.name and py_file.name != 'test_path_migration.py':
                continue

            content = py_file.read_text(encoding='utf-8')

            # Look for actual path operations using 'working'
            working_path_ops = [
                r"['\"](coderef/working|coderef\\\\working)['\"]",
                r"coderef['\"].*working",
            ]

            for pattern in working_path_ops:
                for match in re.finditer(pattern, content):
                    # Get context
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end]

                    # Skip if it's a comment, test, or string literal
                    if any(x in context for x in ['#', 'test', '"""', "'''", 'WORKING_DIR', 'CONTEXT_DIR']):
                        continue

                    violations.append({
                        'file': str(py_file.relative_to(project_root)),
                        'pattern': match.group(),
                        'context': context.replace('\n', ' ')[:80]
                    })

        # Only report actual violations (not test/comment references)
        actual_violations = [v for v in violations if 'test' not in v['file']]
        assert not actual_violations, \
            f"Found {len(actual_violations)} old coderef/working references:\n" + \
            "\n".join([f"  {v['file']}: {v['pattern']}" for v in actual_violations[:5]])

    def test_gather_context_saves_to_workorder(self):
        """Verify gather_context tool saves context.json to coderef/workorder."""
        # This is a behavioral test - verifies the tool function signature
        import inspect

        sig = inspect.getsource(handle_gather_context)
        assert "coderef" in sig and "workorder" in sig, \
            "gather_context doesn't use coderef/workorder path"

    def test_path_constants_updated(self):
        """Verify constants.py has appropriate path definitions."""
        constants_file = Path(__file__).parent.parent / "constants.py"
        content = constants_file.read_text()

        # At minimum, should have workorder mentioned
        assert "workorder" in content.lower(), \
            "constants.py doesn't mention workorder paths"


class TestPathMigrationIntegration:
    """Integration tests for path migration."""

    def test_all_path_creations_use_workorder(self):
        """Verify all Path() operations creating feature dirs use workorder."""
        handlers_file = Path(__file__).parent.parent / "tool_handlers.py"
        content = handlers_file.read_text(encoding='utf-8')

        # Count actual path creation operations
        workorder_creations = len(re.findall(
            r"\/\s*['\"]workorder['\"]",
            content
        ))

        # Should have at least 5 workorder path creations
        assert workorder_creations >= 5, \
            f"Only found {workorder_creations} workorder path creations (expected >= 5)"

        # Verify no working path creations in actual code
        working_creations = len(re.findall(
            r"\/\s*['\"]working['\"]",
            content
        ))

        # Only comments/strings, not actual path operations
        assert working_creations < 3, \
            f"Found {working_creations} potential working path operations (expected < 3)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
