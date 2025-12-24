"""
Integration tests for archive feature workflow (ARCHIVE-009).

Tests the complete workflow from feature completion to archiving with index updates.
"""

import pytest
from pathlib import Path
import json
import tempfile
import subprocess
import tool_handlers
from tool_handlers import handle_archive_feature

# Initialize TEMPLATES_DIR for handlers
TEMPLATES_DIR = Path(__file__).parent.parent.parent / 'templates'
tool_handlers.set_templates_dir(TEMPLATES_DIR)


def extract_json_response(result):
    """Helper to extract JSON from format_success_response output."""
    text = result[0].text
    json_start = text.find('{')
    return json.loads(text[json_start:]) if json_start >= 0 else json.loads(text)


class TestArchiveWorkflow:
    """Integration tests for archive feature tool."""

    @pytest.fixture
    def test_project(self, tmp_path):
        """Create a test project with a completed feature."""
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=str(tmp_path), capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=str(tmp_path))
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=str(tmp_path))

        # Create project structure
        working_dir = tmp_path / 'coderef' / 'working' / 'test-feature'
        working_dir.mkdir(parents=True)

        # Create plan.json
        plan_data = {
            "META_DOCUMENTATION": {
                "feature_name": "test-feature",
                "version": "1.0.0"
            }
        }
        (working_dir / 'plan.json').write_text(json.dumps(plan_data, indent=2), encoding='utf-8')

        # Create DELIVERABLES.md with Complete status
        deliverables_content = """# Deliverables - Test Feature

**Status**: ✅ Complete

## Implementation Summary
Test feature completed successfully.
"""
        (working_dir / 'DELIVERABLES.md').write_text(deliverables_content, encoding='utf-8')

        # Create a couple of additional files
        (working_dir / 'README.md').write_text('# Test Feature\n', encoding='utf-8')
        (working_dir / 'notes.txt').write_text('Some implementation notes\n', encoding='utf-8')

        # Initial commit
        subprocess.run(['git', 'add', '.'], cwd=str(tmp_path))
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=str(tmp_path))

        return tmp_path

    @pytest.mark.asyncio
    async def test_archive_complete_feature(self, test_project):
        """Test archiving a feature with Complete status (should succeed immediately)."""
        # Archive the feature
        result = await handle_archive_feature({
            'project_path': str(test_project),
            'feature_name': 'test-feature'
        })

        # Verify result
        assert len(result) == 1
        response = extract_json_response(result)

        # Check success indicators
        assert response['archived'] is True
        assert response['feature_name'] == 'test-feature'
        assert response['previous_status'] == 'Complete'
        assert response['index_updated'] is True
        assert 'file_count' in response

        # Verify folder was moved
        working_dir = test_project / 'coderef' / 'working' / 'test-feature'
        archived_dir = test_project / 'coderef' / 'archived' / 'test-feature'

        assert not working_dir.exists(), "Working directory should be removed"
        assert archived_dir.exists(), "Archived directory should exist"

        # Verify all files were moved
        assert (archived_dir / 'plan.json').exists()
        assert (archived_dir / 'DELIVERABLES.md').exists()
        assert (archived_dir / 'README.md').exists()
        assert (archived_dir / 'notes.txt').exists()

        # Verify index.json was created
        index_path = test_project / 'coderef' / 'archived' / 'index.json'
        assert index_path.exists()

        index_data = json.loads(index_path.read_text())
        assert index_data['total_archived'] == 1
        assert len(index_data['archived_features']) == 1
        assert index_data['archived_features'][0]['folder_name'] == 'test-feature'
        assert 'archived_at' in index_data['archived_features'][0]

    @pytest.mark.asyncio
    async def test_archive_incomplete_feature_requires_force(self, test_project):
        """Test archiving a feature with In Progress status (should prompt for confirmation)."""
        # Update DELIVERABLES.md to In Progress
        working_dir = test_project / 'coderef' / 'working' / 'test-feature'
        deliverables_path = working_dir / 'DELIVERABLES.md'
        deliverables_path.write_text('**Status**: 🚧 In Progress\n', encoding='utf-8')

        # Try to archive without force
        result = await handle_archive_feature({
            'project_path': str(test_project),
            'feature_name': 'test-feature',
            'force': False
        })

        # Should return confirmation prompt
        assert len(result) == 1
        response = extract_json_response(result)

        assert response['action_required'] == 'USER_CONFIRMATION'
        assert response['current_status'] == 'In Progress'
        assert 'prompt' in response

        # Verify folder was NOT moved
        assert working_dir.exists(), "Working directory should still exist"
        archived_dir = test_project / 'coderef' / 'archived' / 'test-feature'
        assert not archived_dir.exists(), "Archived directory should not exist"

        # Now archive with force=True
        result = await handle_archive_feature({
            'project_path': str(test_project),
            'feature_name': 'test-feature',
            'force': True
        })

        # Should succeed
        response = extract_json_response(result)
        assert response['archived'] is True
        assert response['previous_status'] == 'In Progress'

        # Verify folder was moved
        assert not working_dir.exists()
        assert archived_dir.exists()

    @pytest.mark.asyncio
    async def test_archive_feature_not_found(self, test_project):
        """Test archiving a nonexistent feature (should return error)."""
        # With @mcp_error_handler, exceptions are caught and returned as ErrorResponse
        result = await handle_archive_feature({
            'project_path': str(test_project),
            'feature_name': 'nonexistent-feature'
        })

        # Check for error response
        assert len(result) == 1
        error_text = result[0].text.lower()
        assert 'nonexistent-feature' in error_text
        assert 'not found' in error_text

    @pytest.mark.asyncio
    async def test_archive_already_archived(self, test_project):
        """Test archiving a feature that's already archived (should return error)."""
        # First archive
        await handle_archive_feature({
            'project_path': str(test_project),
            'feature_name': 'test-feature'
        })

        # Recreate working directory with same name
        working_dir = test_project / 'coderef' / 'working' / 'test-feature'
        working_dir.mkdir(parents=True)
        (working_dir / 'plan.json').write_text('{}', encoding='utf-8')
        (working_dir / 'DELIVERABLES.md').write_text('**Status**: ✅ Complete\n', encoding='utf-8')

        # Try to archive again (should return error because archived dir exists)
        # With @mcp_error_handler, exceptions are caught and returned as ErrorResponse
        result = await handle_archive_feature({
            'project_path': str(test_project),
            'feature_name': 'test-feature'
        })

        # Check for error response
        assert len(result) == 1
        error_text = result[0].text.lower()
        assert 'already exists' in error_text

    @pytest.mark.asyncio
    async def test_multiple_features_archived(self, test_project):
        """Test archiving multiple features (index should track all)."""
        # Create second feature
        feature2_dir = test_project / 'coderef' / 'working' / 'feature-two'
        feature2_dir.mkdir(parents=True)
        plan_data = {
            "META_DOCUMENTATION": {
                "feature_name": "feature-two",
                "version": "1.0.0"
            }
        }
        (feature2_dir / 'plan.json').write_text(json.dumps(plan_data, indent=2), encoding='utf-8')
        (feature2_dir / 'DELIVERABLES.md').write_text('**Status**: ✅ Complete\n', encoding='utf-8')

        # Archive first feature
        await handle_archive_feature({
            'project_path': str(test_project),
            'feature_name': 'test-feature'
        })

        # Archive second feature
        await handle_archive_feature({
            'project_path': str(test_project),
            'feature_name': 'feature-two'
        })

        # Verify index tracks both
        index_path = test_project / 'coderef' / 'archived' / 'index.json'
        index_data = json.loads(index_path.read_text())

        assert index_data['total_archived'] == 2
        assert len(index_data['archived_features']) == 2

        # Verify both features are in index
        folder_names = [f['folder_name'] for f in index_data['archived_features']]
        assert 'test-feature' in folder_names
        assert 'feature-two' in folder_names

    @pytest.mark.asyncio
    async def test_archive_without_deliverables(self, test_project):
        """Test archiving a feature without DELIVERABLES.md (should prompt)."""
        # Remove DELIVERABLES.md
        working_dir = test_project / 'coderef' / 'working' / 'test-feature'
        deliverables_path = working_dir / 'DELIVERABLES.md'
        deliverables_path.unlink()

        # Try to archive without force
        result = await handle_archive_feature({
            'project_path': str(test_project),
            'feature_name': 'test-feature',
            'force': False
        })

        # Should prompt for confirmation
        response = extract_json_response(result)
        assert response['action_required'] == 'USER_CONFIRMATION'
        assert response['current_status'] == 'UNKNOWN'

        # Archive with force should succeed
        result = await handle_archive_feature({
            'project_path': str(test_project),
            'feature_name': 'test-feature',
            'force': True
        })

        response = extract_json_response(result)
        assert response['archived'] is True
        assert response['previous_status'] == 'UNKNOWN'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
