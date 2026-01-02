"""
Comprehensive unit tests for workflow.py and engine.py template filters
Tests plan.json parsing and Jinja2 template filters
"""
import pytest
import json
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from papertrail.extensions.workflow import WorkflowExtension
from papertrail.engine import TemplateEngine


class TestWorkflowExtensionInitialization:
    """Test initialization and setup"""

    def test_init_with_default_workorder_dir(self):
        ext = WorkflowExtension()
        assert ext.workorder_dir is not None
        assert isinstance(ext.workorder_dir, Path)

    def test_init_with_custom_workorder_dir(self):
        custom_dir = Path("/custom/workorder")
        ext = WorkflowExtension(workorder_dir=custom_dir)
        assert ext.workorder_dir == custom_dir


class TestLoadPlan:
    """Test _load_plan helper method"""

    def test_loads_valid_plan(self):
        plan_data = {
            "META_DOCUMENTATION": {"version": "1.0.0"},
            "6_implementation_phases": []
        }
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        with patch('builtins.open', mock_open(read_data=json.dumps(plan_data))):
            ext = WorkflowExtension()
            result = ext._load_plan(mock_path)
            assert result['META_DOCUMENTATION']['version'] == "1.0.0"

    def test_handles_file_not_found(self):
        ext = WorkflowExtension()
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        result = ext._load_plan(mock_path)
        assert result == {}

    def test_handles_invalid_json(self):
        ext = WorkflowExtension()
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        with patch('builtins.open', mock_open(read_data="invalid json")):
            result = ext._load_plan(mock_path)
            assert result == {}


class TestGetPlanPhases:
    """Test get_plan_phases method"""

    @patch.object(WorkflowExtension, '_load_plan')
    def test_extracts_phases_from_plan(self, mock_load):
        plan_data = {
            "6_implementation_phases": {
                "phases": [
                    {
                        "name": "Setup",
                        "status": "completed",
                        "duration": "PT2H",
                        "deliverables": ["Config files", "Dependencies"]
                    },
                    {
                        "name": "Implementation",
                        "status": "in_progress",
                        "duration": "PT8H",
                        "deliverables": ["Core functionality"]
                    }
                ]
            }
        }
        mock_load.return_value = plan_data
        ext = WorkflowExtension()
        phases = ext.get_plan_phases("plan.json")

        assert len(phases) == 2
        assert phases[0]['name'] == 'Setup'
        assert phases[0]['status'] == 'completed'
        assert phases[1]['name'] == 'Implementation'

    @patch.object(WorkflowExtension, '_load_plan')
    def test_handles_missing_phases_section(self, mock_load):
        plan_data = {"META_DOCUMENTATION": {}}
        mock_load.return_value = plan_data
        ext = WorkflowExtension()
        phases = ext.get_plan_phases("plan.json")

        assert phases == []

    @patch.object(WorkflowExtension, '_load_plan')
    def test_handles_empty_phases(self, mock_load):
        plan_data = {"6_implementation_phases": {"phases": []}}
        mock_load.return_value = plan_data
        ext = WorkflowExtension()
        phases = ext.get_plan_phases("plan.json")

        assert phases == []


class TestGetPriorityChecklist:
    """Test get_priority_checklist method"""

    @patch.object(WorkflowExtension, '_load_plan')
    def test_extracts_and_sorts_tasks_by_priority(self, mock_load):
        plan_data = {
            "6_implementation_phases": {
                "phases": [
                    {
                        "tasks": [
                            {"task_id": "TASK-001", "description": "Low task", "priority": "low", "status": "pending"},
                            {"task_id": "TASK-002", "description": "Critical task", "priority": "critical", "status": "pending"},
                            {"task_id": "TASK-003", "description": "High task", "priority": "high", "status": "pending"},
                            {"task_id": "TASK-004", "description": "Medium task", "priority": "medium", "status": "pending"}
                        ]
                    }
                ]
            }
        }
        mock_load.return_value = plan_data
        ext = WorkflowExtension()
        tasks = ext.get_priority_checklist("plan.json")

        # Should be sorted: critical, high, medium, low
        assert len(tasks) == 4
        assert tasks[0]['priority'] == 'critical'
        assert tasks[1]['priority'] == 'high'
        assert tasks[2]['priority'] == 'medium'
        assert tasks[3]['priority'] == 'low'

    @patch.object(WorkflowExtension, '_load_plan')
    def test_handles_missing_tasks(self, mock_load):
        plan_data = {
            "6_implementation_phases": {
                "phases": [{"name": "Phase1"}]  # No tasks
            }
        }
        mock_load.return_value = plan_data
        ext = WorkflowExtension()
        tasks = ext.get_priority_checklist("plan.json")

        assert tasks == []

    @patch.object(WorkflowExtension, '_load_plan')
    def test_flattens_tasks_from_multiple_phases(self, mock_load):
        plan_data = {
            "6_implementation_phases": {
                "phases": [
                    {"tasks": [{"task_id": "T1", "priority": "high", "description": "Task 1", "status": "pending"}]},
                    {"tasks": [{"task_id": "T2", "priority": "high", "description": "Task 2", "status": "pending"}]}
                ]
            }
        }
        mock_load.return_value = plan_data
        ext = WorkflowExtension()
        tasks = ext.get_priority_checklist("plan.json")

        assert len(tasks) == 2


class TestTemplateFilters:
    """Test template filters in engine.py"""

    def test_file_status_icon_filter(self):
        engine = TemplateEngine()
        assert engine._file_status_icon('added') == '+'
        assert engine._file_status_icon('modified') == '~'
        assert engine._file_status_icon('deleted') == '-'
        assert engine._file_status_icon('unknown') == '?'

    def test_file_status_icon_case_insensitive(self):
        engine = TemplateEngine()
        assert engine._file_status_icon('ADDED') == '+'
        assert engine._file_status_icon('Modified') == '~'
        assert engine._file_status_icon('DELETED') == '-'

    def test_priority_color_filter(self):
        engine = TemplateEngine()
        assert '[CRITICAL]' in engine._priority_color('critical')
        assert '[HIGH]' in engine._priority_color('high')
        assert '[MEDIUM]' in engine._priority_color('medium')
        assert '[LOW]' in engine._priority_color('low')
        assert '[UNKNOWN]' in engine._priority_color('invalid')

    def test_priority_color_case_insensitive(self):
        engine = TemplateEngine()
        assert '[CRITICAL]' in engine._priority_color('CRITICAL')
        assert '[HIGH]' in engine._priority_color('High')

    def test_format_duration_filter(self):
        engine = TemplateEngine()
        assert engine._format_duration('PT2H') == '2 hours'
        assert engine._format_duration('PT30M') == '30 minutes'
        assert engine._format_duration('PT2H30M') == '2 hours 30 minutes'
        assert engine._format_duration('PT1H') == '1 hour'
        assert engine._format_duration('PT1M') == '1 minute'

    def test_format_duration_handles_invalid_input(self):
        engine = TemplateEngine()
        assert engine._format_duration('invalid') == 'invalid'
        assert engine._format_duration('') == ''
        assert engine._format_duration('P1D') == 'P1D'  # Days not supported

    def test_humanize_date_filter(self):
        engine = TemplateEngine()
        result = engine._humanize_date('2026-01-02T10:00:00Z')
        assert 'Jan' in result
        assert '2026' in result

    def test_humanize_date_handles_invalid_input(self):
        engine = TemplateEngine()
        result = engine._humanize_date('invalid')
        assert result == 'invalid'

    def test_filters_registered_in_jinja_env(self):
        engine = TemplateEngine()
        assert 'file_status_icon' in engine.env.filters
        assert 'priority_color' in engine.env.filters
        assert 'format_duration' in engine.env.filters
        assert 'humanize_date' in engine.env.filters

    def test_filters_work_in_template_rendering(self):
        engine = TemplateEngine()
        template = "{{ status | file_status_icon }} {{ priority | priority_color }}"
        result = engine.render(template, {'status': 'added', 'priority': 'high'})
        assert '+' in result
        assert '[HIGH]' in result


class TestWorkflowEdgeCases:
    """Test edge cases and error handling"""

    @patch.object(WorkflowExtension, '_load_plan')
    def test_get_plan_phases_with_empty_dict(self, mock_load):
        # Empty dict returns empty list
        mock_load.return_value = {}
        ext = WorkflowExtension()
        phases = ext.get_plan_phases("plan.json")
        assert phases == []

    @patch.object(WorkflowExtension, '_load_plan')
    def test_get_priority_checklist_with_empty_dict(self, mock_load):
        # Empty dict returns empty list
        mock_load.return_value = {}
        ext = WorkflowExtension()
        tasks = ext.get_priority_checklist("plan.json")
        assert tasks == []

    @patch.object(WorkflowExtension, '_load_plan')
    def test_get_plan_phases_missing_phases_key(self, mock_load):
        # Missing phases key returns empty list
        mock_load.return_value = {"6_implementation_phases": {}}
        ext = WorkflowExtension()
        phases = ext.get_plan_phases("plan.json")
        assert phases == []
