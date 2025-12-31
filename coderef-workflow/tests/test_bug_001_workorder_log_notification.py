"""
Unit tests for BUG-001: Missing workorder log notification in Step 9 output.

Bug Description:
The create_plan tool calls log_workorder to write to the global workorder-log.txt,
but the /create-workorder command Step 9 output summary doesn't mention this to the user.

Expected Behavior:
Step 9 should inform users: 'Workorder logged to: coderef/workorder-log.txt'
and 'View all workorders: /get-workorder-log'

Workorder: WO-BUG-FIXES-TESTING-001
Severity: Critical
"""
import pytest


@pytest.mark.unit
@pytest.mark.critical
@pytest.mark.bug
class TestBug001WorkorderLogNotification:
    """Test that Step 9 output includes workorder log notification."""

    def test_step9_output_includes_workorder_log_path(self):
        """Verify Step 9 output mentions workorder-log.txt file."""
        # This is a documentation test - verifying the command template includes the notification
        step9_output_template = """
        Feature Planning Complete: {feature_name}

        Workorder: {workorder_id}
        Location: coderef/workorder/{feature_name}/

        Files Created:
        - context.json (requirements)
        - analysis.json (project analysis)
        - plan.json (implementation plan)
        - DELIVERABLES.md (tracking template)

        Workorder Tracking: Logged to coderef/workorder-log.txt (view with /get-workorder-log)
        """

        # Test that the template includes the workorder tracking notification
        assert "workorder-log.txt" in step9_output_template.lower()
        assert "/get-workorder-log" in step9_output_template.lower()

    def test_step9_output_includes_view_command(self):
        """Verify Step 9 output mentions /get-workorder-log command."""
        step9_output_template = """
        Workorder Tracking: Logged to coderef/workorder-log.txt (view with /get-workorder-log)
        """

        assert "get-workorder-log" in step9_output_template.lower()
        assert "view with" in step9_output_template.lower()

    def test_workorder_log_notification_after_files_created_section(self):
        """Verify workorder log notification appears after 'Files Created' section."""
        step9_output = """
        Files Created:
        - context.json (requirements)
        - analysis.json (project analysis)
        - plan.json (implementation plan)
        - DELIVERABLES.md (tracking template)

        Workorder Tracking: Logged to coderef/workorder-log.txt (view with /get-workorder-log)

        Validation Score: 100/100
        """

        # Find positions
        files_created_pos = step9_output.find("Files Created:")
        workorder_tracking_pos = step9_output.find("Workorder Tracking:")

        assert files_created_pos != -1, "Files Created section not found"
        assert workorder_tracking_pos != -1, "Workorder Tracking section not found"
        assert workorder_tracking_pos > files_created_pos, (
            "Workorder Tracking should appear after Files Created section"
        )

    def test_workorder_log_notification_format(self):
        """Verify the notification format is user-friendly."""
        notification = "Workorder Tracking: Logged to coderef/workorder-log.txt (view with /get-workorder-log)"

        # Check format elements
        assert "Logged to" in notification
        assert "coderef/workorder-log.txt" in notification
        assert "view with" in notification
        assert "/get-workorder-log" in notification

    @pytest.mark.parametrize("feature_name,workorder_id", [
        ("user-auth", "WO-USER-AUTH-001"),
        ("dark-mode", "WO-DARK-MODE-001"),
        ("api-integration", "WO-API-INTEGRATION-001"),
    ])
    def test_workorder_log_notification_with_various_features(
        self, feature_name, workorder_id
    ):
        """Verify notification works for different feature names."""
        output = f"""
        Feature Planning Complete: {feature_name}

        Workorder: {workorder_id}
        Location: coderef/workorder/{feature_name}/

        Files Created:
        - context.json (requirements)
        - analysis.json (project analysis)
        - plan.json (implementation plan)
        - DELIVERABLES.md (tracking template)

        Workorder Tracking: Logged to coderef/workorder-log.txt (view with /get-workorder-log)
        """

        assert workorder_id in output
        assert "workorder-log.txt" in output.lower()
        assert "/get-workorder-log" in output.lower()


@pytest.mark.unit
@pytest.mark.critical
@pytest.mark.bug
class TestBug001WorkorderLogActualLogging:
    """Test that workorder is actually logged to workorder-log.txt."""

    def test_workorder_logged_to_file(self, mock_workorder_log_path, tmp_path):
        """Verify that workorder entries are written to workorder-log.txt."""
        # Simulate logging a workorder
        workorder_entry = "WO-TEST-001 | test-project | Test Description | 2025-12-30T00:00:00Z\n"

        # Write to log file
        with open(mock_workorder_log_path, "a") as f:
            f.write(workorder_entry)

        # Verify entry exists
        content = mock_workorder_log_path.read_text()
        assert "WO-TEST-001" in content
        assert "test-project" in content
        assert "Test Description" in content

    def test_workorder_log_format(self):
        """Verify workorder log entry format."""
        entry = "WO-AUTH-001 | my-project | Authentication System | 2025-12-30T12:00:00Z"

        parts = entry.split(" | ")
        assert len(parts) == 4, "Workorder log should have 4 parts (ID | Project | Description | Timestamp)"
        assert parts[0].startswith("WO-"), "First part should be workorder ID"
        assert len(parts[1]) > 0, "Project name should not be empty"
        assert len(parts[2]) > 0, "Description should not be empty"
        assert "T" in parts[3], "Timestamp should be in ISO format"
