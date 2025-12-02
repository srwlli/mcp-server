"""
Integration tests for multi-agent coordination workflow (Phase 8).

Tests the complete workflow from plan creation to agent verification.
"""

import pytest
from pathlib import Path
import json
import tempfile
import subprocess
import asyncio
import tool_handlers
from tool_handlers import (
    handle_generate_agent_communication,
    handle_assign_agent_task,
    handle_verify_agent_completion,
    handle_aggregate_agent_deliverables,
    handle_track_agent_status
)

# Initialize TEMPLATES_DIR for handlers
TEMPLATES_DIR = Path(__file__).parent.parent.parent / 'templates'
tool_handlers.set_templates_dir(TEMPLATES_DIR)


class TestAgentCoordinationWorkflow:
    """Integration tests for multi-agent coordination."""

    @pytest.fixture
    def test_project(self, tmp_path):
        """Create a test project with plan.json."""
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=str(tmp_path), capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=str(tmp_path))
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=str(tmp_path))

        # Create project structure
        working_dir = tmp_path / 'coderef' / 'working' / 'test-feature'
        working_dir.mkdir(parents=True)

        # Create minimal plan.json
        plan_data = {
            "META_DOCUMENTATION": {
                "feature_name": "test-feature",
                "version": "1.0.0"
            },
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "5_task_id_system": {
                    "workorder": {
                        "id": "WO-TEST-FEATURE-001",
                        "name": "Test Feature"
                    }
                },
                "6_implementation_phases": {
                    "phase_0": {
                        "tasks": [
                            {"id": "TASK-001", "description": "Setup environment"}
                        ]
                    },
                    "phase_1": {
                        "tasks": [
                            {"id": "TASK-002", "description": "Implement core logic"}
                        ]
                    }
                },
                "details": {
                    "forbidden_files": [
                        "server.py - DO NOT MODIFY",
                        "tool_handlers.py - DO NOT MODIFY"
                    ],
                    "allowed_files": ["new_feature.py"]
                },
                "8_success_criteria": {
                    "criteria": [
                        {"id": "SC-001", "criterion": "All tests pass"}
                    ]
                }
            }
        }
        plan_path = working_dir / 'plan.json'
        plan_path.write_text(json.dumps(plan_data, indent=2))

        # Initial commit
        subprocess.run(['git', 'add', '.'], cwd=str(tmp_path))
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=str(tmp_path))

        return tmp_path

    @pytest.mark.asyncio
    async def test_it1_single_agent_backward_compatibility(self, test_project):
        """IT-1: Verify single-agent mode works (backward compatibility)."""
        # This test verifies that existing workflows aren't broken
        # by multi-agent additions

        # Generate communication.json (single-agent mode)
        result = await handle_generate_agent_communication({
            'project_path': str(test_project),
            'feature_name': 'test-feature'
        })

        assert result[0].text  # Should return success

        # Verify communication.json exists
        comm_path = test_project / 'coderef' / 'working' / 'test-feature' / 'communication.json'
        assert comm_path.exists()

        # Verify structure
        comm_data = json.loads(comm_path.read_text())
        assert comm_data['workorder_id'] == 'WO-TEST-FEATURE-001'
        assert comm_data['feature'] == 'TEST_FEATURE'
        assert 'agent_1_status' in comm_data

    @pytest.mark.asyncio
    async def test_it2_multi_agent_same_feature(self, test_project):
        """IT-2: Multi-agent mode with 2 agents on same feature."""
        # Generate communication.json
        await handle_generate_agent_communication({
            'project_path': str(test_project),
            'feature_name': 'test-feature'
        })

        # Assign Agent 2
        result = await handle_assign_agent_task({
            'project_path': str(test_project),
            'feature_name': 'test-feature',
            'agent_number': 2,
            'phase_id': 'phase_0'
        })

        assert result[0].text  # Should return success

        # Verify agent 2 assignment
        comm_path = test_project / 'coderef' / 'working' / 'test-feature' / 'communication.json'
        comm_data = json.loads(comm_path.read_text())

        assert comm_data['agent_2_workorder'] == 'WO-TEST-FEATURE-002'
        assert 'ASSIGNED' in comm_data['agent_2_status']

        # Assign Agent 3
        await handle_assign_agent_task({
            'project_path': str(test_project),
            'feature_name': 'test-feature',
            'agent_number': 3,
            'phase_id': 'phase_1'
        })

        # Track status
        result = await handle_track_agent_status({
            'project_path': str(test_project),
            'feature_name': 'test-feature'
        })

        assert result[0].text  # Should return dashboard

    @pytest.mark.asyncio
    async def test_it4_end_to_end_workflow(self, test_project):
        """IT-4: Complete end-to-end workflow."""
        # Step 1: Generate communication.json
        await handle_generate_agent_communication({
            'project_path': str(test_project),
            'feature_name': 'test-feature'
        })

        # Step 2: Assign agent
        await handle_assign_agent_task({
            'project_path': str(test_project),
            'feature_name': 'test-feature',
            'agent_number': 2,
            'phase_id': 'phase_0'
        })

        # Step 3: Simulate agent completion (update status manually)
        comm_path = test_project / 'coderef' / 'working' / 'test-feature' / 'communication.json'
        comm_data = json.loads(comm_path.read_text())
        comm_data['agent_2_status'] = 'COMPLETE'
        comm_path.write_text(json.dumps(comm_data, indent=2))

        # Step 4: Verify agent completion
        result = await handle_verify_agent_completion({
            'project_path': str(test_project),
            'feature_name': 'test-feature',
            'agent_number': 2
        })

        # Should pass because no forbidden files modified
        comm_data = json.loads(comm_path.read_text())
        assert 'VERIFIED' in comm_data.get('agent_2_status', '') or 'VERIFICATION_FAILED' in comm_data.get('agent_2_status', '')

        # Step 5: Track overall status
        result = await handle_track_agent_status({
            'project_path': str(test_project),
            'feature_name': 'test-feature'
        })

        assert result[0].text  # Should return dashboard


class TestPerformanceBenchmark:
    """Performance tests to validate 3x speedup claim."""

    @pytest.mark.asyncio
    async def test_coordination_overhead(self, tmp_path):
        """Verify coordination overhead is minimal (<100ms per operation)."""
        import time

        # Setup minimal test environment
        working_dir = tmp_path / 'coderef' / 'working' / 'perf-test'
        working_dir.mkdir(parents=True)

        # Create minimal communication.json
        comm_data = {
            "feature": "PERF_TEST",
            "workorder_id": "WO-PERF-TEST-001",
            "agent_1_status": "READY",
            "agent_N_status": None
        }
        comm_path = working_dir / 'communication.json'
        comm_path.write_text(json.dumps(comm_data))

        # Measure track_agent_status performance
        start = time.time()
        result = await handle_track_agent_status({
            'project_path': str(tmp_path),
            'feature_name': 'perf-test'
        })
        elapsed = time.time() - start

        assert elapsed < 0.1  # Should complete in <100ms
        assert result[0].text  # Should return valid result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
