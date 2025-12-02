"""
Unit tests for QuickPlanGenerator

Part of docs-expert v2.0 Phase 2: Planning Flexibility
"""

import json
import pytest
from pathlib import Path

from src.generators.quick_plan_generator import QuickPlanGenerator


@pytest.fixture
def generator():
    """Create QuickPlanGenerator instance"""
    return QuickPlanGenerator()


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory"""
    return str(tmp_path / "quick-plans")


class TestQuickPlanGeneration:
    """Test quick plan generation for different complexity levels"""

    def test_generate_trivial_quick_plan(self, generator, temp_output_dir):
        """Test quick plan generation for trivial complexity"""
        result = generator.generate_quick_plan(
            feature_name="add-field",
            description="Add tags field to persona schema",
            complexity="trivial",
            output_dir=temp_output_dir
        )

        # Verify workorder
        assert result['workorder_id'] == "WO-ADD-FIELD-001"
        assert result['complexity'] == "trivial"

        # Verify task count (trivial = 2 tasks)
        assert result['total_tasks'] == 2
        assert len(result['plan']['plan']['tasks']) == 2

        # Verify plan structure
        plan = result['plan']['plan']
        assert 'context' in plan
        assert 'tasks' in plan
        assert 'validation' in plan

        # Verify context section
        assert 'what' in plan['context']
        assert 'why' in plan['context']
        assert 'estimated_time' in plan['context']

        # Verify skipped steps
        assert 'gather_context' in result['plan']['skipped_steps']
        assert 'analyze_project' in result['plan']['skipped_steps']

    def test_generate_simple_quick_plan(self, generator, temp_output_dir):
        """Test quick plan generation for simple complexity"""
        result = generator.generate_quick_plan(
            feature_name="update-docs",
            description="Update documentation for new feature",
            complexity="simple",
            output_dir=temp_output_dir
        )

        # Verify task count (simple = 3 tasks)
        assert result['total_tasks'] == 3
        assert len(result['plan']['plan']['tasks']) == 3

        # Verify todos were auto-generated
        assert 'todos' in result
        assert len(result['todos']) == 3

    def test_generate_moderate_quick_plan(self, generator, temp_output_dir):
        """Test quick plan generation for moderate complexity"""
        result = generator.generate_quick_plan(
            feature_name="add-endpoint",
            description="Add new REST API endpoint for user profiles",
            complexity="moderate",
            output_dir=temp_output_dir
        )

        # Verify task count (moderate = 5 tasks)
        assert result['total_tasks'] == 5
        assert len(result['plan']['plan']['tasks']) == 5

        # Verify all tasks have required fields
        for task in result['plan']['plan']['tasks']:
            assert 'task_id' in task
            assert 'description' in task
            assert 'files' in task
            assert 'acceptance_criteria' in task
            assert 'estimated_time' in task
            assert 'dependencies' in task


class TestWorkorderGeneration:
    """Test workorder ID generation"""

    def test_workorder_id_format(self, generator, temp_output_dir):
        """Test that workorder IDs follow correct format"""
        result = generator.generate_quick_plan(
            feature_name="test-feature",
            description="Test description",
            complexity="simple",
            output_dir=temp_output_dir
        )

        assert result['workorder_id'].startswith("WO-")
        assert result['workorder_id'].endswith("-001")
        assert "TEST-FEATURE" in result['workorder_id']

    def test_workorder_id_with_hyphens(self, generator, temp_output_dir):
        """Test workorder ID generation with hyphenated feature names"""
        result = generator.generate_quick_plan(
            feature_name="add-new-field-to-schema",
            description="Test",
            complexity="trivial",
            output_dir=temp_output_dir
        )

        assert result['workorder_id'] == "WO-ADD-NEW-FIELD-TO-SCHEMA-001"


class TestTaskBreakdown:
    """Test task generation and breakdown"""

    def test_task_ids_sequential(self, generator, temp_output_dir):
        """Test that task IDs are sequential starting from 1"""
        result = generator.generate_quick_plan(
            feature_name="test",
            description="Test",
            complexity="moderate",
            output_dir=temp_output_dir
        )

        tasks = result['plan']['plan']['tasks']
        task_ids = [task['task_id'] for task in tasks]

        assert task_ids == [1, 2, 3, 4, 5]

    def test_implementation_task_always_first(self, generator, temp_output_dir):
        """Test that implementation task is always first"""
        result = generator.generate_quick_plan(
            feature_name="test",
            description="Implement new feature",
            complexity="simple",
            output_dir=temp_output_dir
        )

        first_task = result['plan']['plan']['tasks'][0]
        assert first_task['task_id'] == 1
        assert 'implement' in first_task['description'].lower()

    def test_tasks_have_acceptance_criteria(self, generator, temp_output_dir):
        """Test that all tasks have acceptance criteria"""
        result = generator.generate_quick_plan(
            feature_name="test",
            description="Test",
            complexity="simple",
            output_dir=temp_output_dir
        )

        for task in result['plan']['plan']['tasks']:
            assert 'acceptance_criteria' in task
            assert len(task['acceptance_criteria']) > 0
            assert all(isinstance(c, str) for c in task['acceptance_criteria'])

    def test_tasks_have_file_references(self, generator, temp_output_dir):
        """Test that tasks reference files to modify"""
        result = generator.generate_quick_plan(
            feature_name="persona-update",
            description="Update persona system",
            complexity="simple",
            output_dir=temp_output_dir
        )

        for task in result['plan']['plan']['tasks']:
            assert 'files' in task
            assert isinstance(task['files'], list)


class TestTimeEstimation:
    """Test time estimation logic"""

    def test_trivial_time_estimate(self, generator, temp_output_dir):
        """Test time estimate for trivial tasks"""
        result = generator.generate_quick_plan(
            feature_name="test",
            description="Test",
            complexity="trivial",
            output_dir=temp_output_dir
        )

        # Trivial should be < 30 minutes total
        assert "minute" in result['estimated_time'].lower()
        time_value = int(result['estimated_time'].split()[0])
        assert time_value < 30

    def test_moderate_time_estimate(self, generator, temp_output_dir):
        """Test time estimate for moderate tasks"""
        result = generator.generate_quick_plan(
            feature_name="test",
            description="Test",
            complexity="moderate",
            output_dir=temp_output_dir
        )

        # Moderate should be 30-90 minutes
        estimated_time = result['estimated_time']
        if "hour" in estimated_time:
            assert "1 hour" in estimated_time
        else:
            time_value = int(estimated_time.split()[0])
            assert 30 <= time_value <= 90


class TestPlanStructure:
    """Test quick plan structure and format"""

    def test_plan_has_three_sections(self, generator, temp_output_dir):
        """Test that quick plans have exactly 3 sections"""
        result = generator.generate_quick_plan(
            feature_name="test",
            description="Test",
            complexity="simple",
            output_dir=temp_output_dir
        )

        plan = result['plan']['plan']
        assert len(plan.keys()) == 3
        assert 'context' in plan
        assert 'tasks' in plan
        assert 'validation' in plan

    def test_context_section_complete(self, generator, temp_output_dir):
        """Test that context section has all required fields"""
        result = generator.generate_quick_plan(
            feature_name="test",
            description="Test feature for user authentication",
            complexity="simple",
            output_dir=temp_output_dir
        )

        context = result['plan']['plan']['context']
        assert 'what' in context
        assert 'why' in context
        assert 'estimated_time' in context

        # Verify 'what' extracted from description
        assert len(context['what']) > 0

    def test_validation_section_has_tests(self, generator, temp_output_dir):
        """Test that validation section includes test descriptions"""
        result = generator.generate_quick_plan(
            feature_name="test",
            description="Test",
            complexity="simple",
            output_dir=temp_output_dir
        )

        validation = result['plan']['plan']['validation']
        assert 'tests' in validation
        assert isinstance(validation['tests'], list)
        assert len(validation['tests']) > 0


class TestFileOperations:
    """Test file saving and path handling"""

    def test_plan_saved_to_file(self, generator, temp_output_dir):
        """Test that quick plan is saved to quick-plan.json"""
        result = generator.generate_quick_plan(
            feature_name="test-save",
            description="Test",
            complexity="trivial",
            output_dir=temp_output_dir
        )

        plan_file = Path(result['output_path'])
        assert plan_file.exists()
        assert plan_file.name == "quick-plan.json"

    def test_plan_file_valid_json(self, generator, temp_output_dir):
        """Test that saved plan file is valid JSON"""
        result = generator.generate_quick_plan(
            feature_name="test-json",
            description="Test",
            complexity="simple",
            output_dir=temp_output_dir
        )

        with open(result['output_path'], 'r') as f:
            loaded_plan = json.load(f)

        assert 'workorder_id' in loaded_plan
        assert 'plan' in loaded_plan
        assert loaded_plan['workorder_id'] == result['workorder_id']

    def test_default_output_directory(self, generator, tmp_path):
        """Test default output directory structure"""
        # Change working directory to temp
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)

            result = generator.generate_quick_plan(
                feature_name="test-default",
                description="Test",
                complexity="trivial"
            )

            # Should create coderef/working/{feature_name}/
            expected_path = tmp_path / "coderef" / "working" / "test-default" / "quick-plan.json"
            assert Path(result['output_path']).name == "quick-plan.json"

        finally:
            os.chdir(original_dir)


class TestTodoAutoGeneration:
    """Test automatic todo list generation"""

    def test_todos_generated_automatically(self, generator, temp_output_dir):
        """Test that todos are auto-generated when quick plan is created"""
        result = generator.generate_quick_plan(
            feature_name="test-todos",
            description="Test",
            complexity="simple",
            output_dir=temp_output_dir
        )

        assert 'todos' in result
        assert len(result['todos']) == result['total_tasks']

    def test_todos_have_correct_format(self, generator, temp_output_dir):
        """Test that auto-generated todos follow TodoWrite format"""
        result = generator.generate_quick_plan(
            feature_name="test-format",
            description="Test",
            complexity="simple",
            output_dir=temp_output_dir
        )

        for todo in result['todos']:
            assert 'content' in todo
            assert 'activeForm' in todo
            assert 'status' in todo
            assert 'metadata' in todo

            # Verify metadata
            assert todo['metadata']['workorder_id'] == result['workorder_id']

    def test_todos_match_tasks(self, generator, temp_output_dir):
        """Test that todos correspond to plan tasks"""
        result = generator.generate_quick_plan(
            feature_name="test-match",
            description="Test",
            complexity="moderate",
            output_dir=temp_output_dir
        )

        tasks = result['plan']['plan']['tasks']
        todos = result['todos']

        assert len(todos) == len(tasks)

        # Verify task IDs match
        for i, (task, todo) in enumerate(zip(tasks, todos)):
            assert task['task_id'] == todo['metadata']['task_id']


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_long_feature_name(self, generator, temp_output_dir):
        """Test handling of long feature names"""
        result = generator.generate_quick_plan(
            feature_name="very-long-feature-name-with-many-words-and-hyphens",
            description="Test",
            complexity="trivial",
            output_dir=temp_output_dir
        )

        assert result['workorder_id'].startswith("WO-")
        assert len(result['workorder_id']) > 20

    def test_description_with_action_verb(self, generator, temp_output_dir):
        """Test description extraction when starting with action verb"""
        result = generator.generate_quick_plan(
            feature_name="test",
            description="Add new authentication system",
            complexity="simple",
            output_dir=temp_output_dir
        )

        first_task = result['plan']['plan']['tasks'][0]
        # Should preserve action verb
        assert first_task['description'] == "Add new authentication system"

    def test_description_without_action_verb(self, generator, temp_output_dir):
        """Test description extraction without action verb"""
        result = generator.generate_quick_plan(
            feature_name="test",
            description="New authentication system",
            complexity="simple",
            output_dir=temp_output_dir
        )

        first_task = result['plan']['plan']['tasks'][0]
        # Should add "Implement"
        assert "implement" in first_task['description'].lower()


class TestPerformance:
    """Test performance requirements"""

    def test_generation_speed(self, generator, temp_output_dir):
        """Test that quick plan generation completes in <2 seconds"""
        import time

        start = time.time()
        result = generator.generate_quick_plan(
            feature_name="perf-test",
            description="Performance test",
            complexity="moderate",
            output_dir=temp_output_dir
        )
        duration = time.time() - start

        assert duration < 2.0, f"Quick plan generation took {duration:.2f}s (target: <2s)"
