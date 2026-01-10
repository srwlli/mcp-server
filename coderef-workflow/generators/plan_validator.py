"""
Plan validation for implementation plans (QUA-001).

Validates implementation plans against:
1. plan.schema.json - Single source of truth for plan structure
2. Quality checklist - Completeness, quality, and autonomy checks

Scores plans 0-100 based on completeness, quality, and autonomy.
Enables iterative review loop until score >= 90.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import re
import time
from type_defs import ValidationResultDict, ValidationIssueDict
from logger_config import logger

# Schema path relative to project root
SCHEMA_PATH = Path(__file__).parent.parent / "coderef" / "schemas" / "plan.schema.json"


class PlanValidator:
    """Validates implementation plans against schema and quality checklist."""

    # Required fields from schema (cached for performance)
    REQUIRED_SECTIONS = [
        "0_preparation",
        "1_executive_summary",
        "2_risk_assessment",
        "3_current_state_analysis",
        "4_key_features",
        "5_task_id_system",
        "6_implementation_phases",
        "7_testing_strategy",
        "8_success_criteria",
        "9_implementation_checklist"
    ]

    # Executive summary required fields (NEW format from schema)
    EXECUTIVE_SUMMARY_REQUIRED = ["goal", "description", "scope"]

    # OLD format fields (for backward compatibility)
    EXECUTIVE_SUMMARY_LEGACY = ["feature_overview", "value_proposition", "real_world_analogy", "primary_use_cases", "success_metrics"]

    def __init__(self, plan_path: Path):
        """Initialize validator with path to plan file.

        Args:
            plan_path: Path to plan JSON file
        """
        self.plan_path = plan_path
        self.plan_data = None
        self.issues: List[ValidationIssueDict] = []
        self._schema: Optional[Dict[str, Any]] = None

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """Load plan schema from coderef/schemas/plan.schema.json.

        Returns:
            Schema dict or None if not found
        """
        if self._schema is not None:
            return self._schema

        try:
            if SCHEMA_PATH.exists():
                with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                    self._schema = json.load(f)
                    logger.debug(f"Loaded plan schema v{self._schema.get('version', 'unknown')}")
                    return self._schema
        except Exception as e:
            logger.warning(f"Could not load plan schema: {e}")

        return None

    def validate(self) -> ValidationResultDict:
        """Validate plan and return results.

        Returns:
            ValidationResultDict with score, issues, and checklist results
        """
        start_time = time.time()
        logger.info(f'Starting validation of plan: {self.plan_path}')

        # Load plan JSON
        self._load_plan()

        # Run validators
        self.validate_structure()
        self.validate_completeness()
        self.validate_quality()
        self.validate_workorder()  # F6.4: Optional validation (only runs if workorder exists)
        self.validate_autonomy()
        self.validate_no_time_estimates()  # NEW: Enforce agentic constraint (no timelines)

        # Check for circular dependencies
        if 'UNIVERSAL_PLANNING_STRUCTURE' in self.plan_data:
            structure = self.plan_data['UNIVERSAL_PLANNING_STRUCTURE']
            if '6_implementation_phases' in structure:
                self._validate_no_circular_dependencies(structure['6_implementation_phases'])

        # Calculate score and determine result
        score = self.calculate_score()
        result = self.determine_result(score)
        approved = score >= 90

        # Build checklist results
        checklist_results = self._build_checklist_results()

        # Track performance
        duration = time.time() - start_time
        logger.info(f'Validation complete: score={score}, result={result}, issues={len(self.issues)}, duration={duration:.2f}s')

        return ValidationResultDict(
            validation_result=result,
            score=score,
            issues=self.issues,
            checklist_results=checklist_results,
            approved=approved
        )

    def _load_plan(self):
        """Load and parse plan JSON file."""
        try:
            with open(self.plan_path, 'r', encoding='utf-8') as f:
                self.plan_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON in plan file: {str(e)}')
        except FileNotFoundError:
            raise FileNotFoundError(f'Plan file not found: {self.plan_path}')

    def validate_structure(self):
        """Validate plan has all required sections."""
        logger.debug('Validating structure...')

        required_sections = [
            '0_preparation',
            '1_executive_summary',
            '2_risk_assessment',
            '3_current_state_analysis',
            '4_key_features',
            '5_task_id_system',
            '6_implementation_phases',
            '7_testing_strategy',
            '8_success_criteria',
            '9_implementation_checklist'
        ]

        # Check META_DOCUMENTATION
        if 'META_DOCUMENTATION' not in self.plan_data:
            self.issues.append({
                'severity': 'critical',
                'section': 'structure',
                'issue': 'Missing META_DOCUMENTATION section',
                'suggestion': 'Add META_DOCUMENTATION section with plan_id, plan_name, status, estimated_effort'
            })

        # Check UNIVERSAL_PLANNING_STRUCTURE
        if 'UNIVERSAL_PLANNING_STRUCTURE' not in self.plan_data:
            self.issues.append({
                'severity': 'critical',
                'section': 'structure',
                'issue': 'Missing UNIVERSAL_PLANNING_STRUCTURE section',
                'suggestion': 'Add UNIVERSAL_PLANNING_STRUCTURE section containing sections 0-9'
            })
            return  # Can't check subsections if parent missing

        # Check each required section 0-9
        structure = self.plan_data['UNIVERSAL_PLANNING_STRUCTURE']
        for section in required_sections:
            if section not in structure:
                self.issues.append({
                    'severity': 'critical',
                    'section': 'structure',
                    'issue': f'Missing section {section}',
                    'suggestion': f'Add section {section} to UNIVERSAL_PLANNING_STRUCTURE'
                })

    def validate_completeness(self):
        """Validate no placeholders, all task IDs valid."""
        logger.debug('Validating completeness...')

        # Check for placeholder text
        plan_json_str = json.dumps(self.plan_data)
        placeholder_pattern = r'\b(TBD|TODO|\[placeholder\]|Coming soon|Fill this in|to be determined)\b'
        matches = re.finditer(placeholder_pattern, plan_json_str, re.IGNORECASE)
        for match in matches:
            self.issues.append({
                'severity': 'major',
                'section': 'completeness',
                'issue': f'Placeholder text found: "{match.group()}"',
                'suggestion': 'Replace placeholder with actual content'
            })

        # Validate task IDs if implementation_phases exists
        if 'UNIVERSAL_PLANNING_STRUCTURE' in self.plan_data:
            structure = self.plan_data['UNIVERSAL_PLANNING_STRUCTURE']
            if '6_implementation_phases' in structure:
                self._validate_task_ids(structure['6_implementation_phases'])

    def _validate_task_ids(self, phases_data):
        """Validate task IDs are unique and dependencies are valid."""
        task_ids = set()
        dependencies = []

        # Extract all task IDs and dependencies
        for phase_key, phase in phases_data.items():
            if isinstance(phase, dict) and 'tasks' in phase:
                for task in phase['tasks']:
                    if isinstance(task, dict) and 'id' in task:
                        task_id = task['id']

                        # Check uniqueness
                        if task_id in task_ids:
                            self.issues.append({
                                'severity': 'critical',
                                'section': 'completeness',
                                'issue': f'Duplicate task ID: {task_id}',
                                'suggestion': 'Each task ID must be unique'
                            })
                        task_ids.add(task_id)

                        # Collect dependencies
                        if 'depends_on' in task and task['depends_on']:
                            for dep in task['depends_on']:
                                dependencies.append((task_id, dep))

        # Validate dependencies reference existing tasks
        for task_id, dep_id in dependencies:
            if dep_id not in task_ids:
                self.issues.append({
                    'severity': 'critical',
                    'section': 'completeness',
                    'issue': f'Task {task_id} depends on non-existent task {dep_id}',
                    'suggestion': f'Ensure task {dep_id} exists or remove dependency'
                })

    def _validate_no_circular_dependencies(self, phases_data):
        """Detect circular dependencies using DFS."""
        # Build adjacency list
        graph = {}
        task_ids = set()

        for phase_key, phase in phases_data.items():
            if isinstance(phase, dict) and 'tasks' in phase:
                for task in phase['tasks']:
                    if isinstance(task, dict) and 'id' in task:
                        task_id = task['id']
                        task_ids.add(task_id)
                        graph[task_id] = task.get('depends_on', [])

        # DFS cycle detection
        visited = set()
        rec_stack = set()

        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Cycle detected
                    self.issues.append({
                        'severity': 'critical',
                        'section': 'completeness',
                        'issue': f'Circular dependency detected involving task {node} and {neighbor}',
                        'suggestion': 'Remove circular dependency to create valid execution order'
                    })
                    return True

            rec_stack.remove(node)
            return False

        for task_id in task_ids:
            if task_id not in visited:
                has_cycle(task_id)

    def validate_quality(self):
        """Validate task descriptions clear, success criteria measurable."""
        logger.debug('Validating quality...')

        if 'UNIVERSAL_PLANNING_STRUCTURE' not in self.plan_data:
            return

        structure = self.plan_data['UNIVERSAL_PLANNING_STRUCTURE']

        # Validate task descriptions
        if '6_implementation_phases' in structure:
            self._validate_task_descriptions(structure['6_implementation_phases'])
            self._validate_phase_fields(structure['6_implementation_phases'])

        # Validate success criteria
        if '8_success_criteria' in structure:
            self._validate_success_criteria(structure['8_success_criteria'])

        # Validate edge cases
        if '7_testing_strategy' in structure:
            self._validate_edge_cases(structure['7_testing_strategy'])

    def _validate_task_descriptions(self, phases_data):
        """Check task descriptions are clear and specific."""
        for phase_key, phase in phases_data.items():
            if isinstance(phase, dict) and 'tasks' in phase:
                for task in phase['tasks']:
                    if isinstance(task, dict) and 'description' in task:
                        desc = task['description']
                        word_count = len(desc.split())
                        task_id = task.get('id', 'unknown')

                        if word_count < 10:
                            self.issues.append({
                                'severity': 'major',
                                'section': 'quality',
                                'issue': f'Task {task_id} description too short ({word_count} words)',
                                'suggestion': 'Expand description to at least 10 words with specific details'
                            })
                        elif word_count < 20:
                            self.issues.append({
                                'severity': 'minor',
                                'section': 'quality',
                                'issue': f'Task {task_id} description could be more detailed ({word_count} words)',
                                'suggestion': 'Consider expanding description to 20+ words for clarity'
                            })

    def _validate_phase_fields(self, phases_data):
        """Check phases have required fields.

        Supports both formats:
        - OLD format: phase_1, phase_2 keys with complexity/effort_level
        - NEW format: phases array with phase/name/tasks/deliverables
        """
        # Handle NEW format: phases array
        if 'phases' in phases_data and isinstance(phases_data['phases'], list):
            for phase in phases_data['phases']:
                if isinstance(phase, dict):
                    phase_name = phase.get('name', f"Phase {phase.get('phase', '?')}")

                    # NEW format required fields
                    required_new = ['phase', 'name', 'tasks', 'deliverables']
                    for field in required_new:
                        if field not in phase:
                            self.issues.append({
                                'severity': 'major',
                                'section': 'quality',
                                'issue': f'Phase "{phase_name}" missing required "{field}" field',
                                'suggestion': f'Add {field} field to phase'
                            })
            return  # Don't check OLD format if NEW format detected

        # Handle OLD format: phase_1, phase_2 keys
        for phase_key, phase in phases_data.items():
            if isinstance(phase, dict) and phase_key.startswith('phase_'):
                phase_name = phase.get('title', phase_key)

                # OLD format: complexity and effort_level are optional but validated if present
                if 'complexity' in phase:
                    if phase['complexity'] not in ['low', 'medium', 'high', 'very_high']:
                        self.issues.append({
                            'severity': 'minor',
                            'section': 'quality',
                            'issue': f'Phase {phase_name} has invalid complexity value: {phase["complexity"]}',
                            'suggestion': 'Use one of: low, medium, high, very_high'
                        })

                if 'effort_level' in phase:
                    if not isinstance(phase['effort_level'], int) or phase['effort_level'] < 1 or phase['effort_level'] > 5:
                        self.issues.append({
                            'severity': 'minor',
                            'section': 'quality',
                            'issue': f'Phase {phase_name} has invalid effort_level: {phase.get("effort_level")}',
                            'suggestion': 'Use integer 1-5 (1=trivial, 5=major undertaking)'
                        })

                # Warn if old "duration" field is still present
                if 'duration' in phase:
                    self.issues.append({
                        'severity': 'minor',
                        'section': 'quality',
                        'issue': f'Phase {phase_name} contains deprecated "duration" field',
                        'suggestion': 'Consider removing "duration" field'
                    })

    def _validate_success_criteria(self, criteria_data):
        """Check success criteria are measurable."""
        criteria_json = json.dumps(criteria_data)
        # Look for numbers, percentages, time units
        measurable_pattern = r'\d+|\b(\d+\.\d+|percent|%|seconds?|ms|minutes?|hours?|>=|<=|>|<)\b'
        matches = re.findall(measurable_pattern, criteria_json, re.IGNORECASE)

        if len(matches) < 3:  # Should have several measurable criteria
            self.issues.append({
                'severity': 'major',
                'section': 'quality',
                'issue': 'Success criteria lack measurable metrics',
                'suggestion': 'Add specific metrics (numbers, percentages, thresholds) to success criteria'
            })

    def _validate_edge_cases(self, testing_data):
        """Check edge cases are documented."""
        edge_case_json = json.dumps(testing_data)
        # Look for edge case mentions
        edge_case_pattern = r'edge.?case|scenario|boundary|invalid|empty|null|error|exception'
        matches = re.findall(edge_case_pattern, edge_case_json, re.IGNORECASE)

        if len(matches) < 5:
            self.issues.append({
                'severity': 'major',
                'section': 'quality',
                'issue': f'Insufficient edge case coverage (found {len(matches)} mentions, need 5+)',
                'suggestion': 'Document at least 5-10 edge case scenarios in testing strategy'
            })

    def validate_workorder(self):
        """Validate workorder metadata if present (optional - for backward compatibility)."""
        logger.debug('Validating workorder metadata...')

        if 'UNIVERSAL_PLANNING_STRUCTURE' not in self.plan_data:
            return

        structure = self.plan_data['UNIVERSAL_PLANNING_STRUCTURE']

        # Only validate if section 5 exists
        if '5_task_id_system' not in structure:
            return

        task_system = structure['5_task_id_system']

        # If workorder field exists, validate it (optional field for backward compatibility)
        if 'workorder' in task_system:
            workorder = task_system['workorder']

            # F6.1: Validate workorder ID format
            if 'id' not in workorder:
                self.issues.append({
                    'severity': 'critical',
                    'section': 'workorder',
                    'issue': 'Workorder missing required "id" field',
                    'suggestion': 'Add workorder.id field with format WO-{FEATURE-NAME}-001'
                })
            else:
                workorder_id = workorder['id']
                # Validate format: WO-{FEATURE-NAME}-001
                if not re.match(r'^WO-[A-Z0-9_-]+-001$', workorder_id):
                    self.issues.append({
                        'severity': 'major',
                        'section': 'workorder',
                        'issue': f'Invalid workorder ID format: {workorder_id}',
                        'suggestion': 'Use format WO-{FEATURE-NAME}-001 (uppercase, hyphens preserved, ends with -001)'
                    })

            # F6.3: Validate workorder metadata completeness
            required_fields = ['id', 'name', 'feature_dir']
            for field in required_fields:
                if field not in workorder:
                    self.issues.append({
                        'severity': 'major',
                        'section': 'workorder',
                        'issue': f'Workorder missing required "{field}" field',
                        'suggestion': f'Add workorder.{field} field'
                    })

            # F6.2: Validate all tasks reference the workorder
            if 'tasks' in task_system and 'id' in workorder:
                workorder_id = workorder['id']
                tasks = task_system.get('tasks', [])

                for task in tasks:
                    if isinstance(task, dict):
                        task_id = task.get('id', 'unknown')

                        # Check task has workorder_id field
                        if 'workorder_id' not in task:
                            self.issues.append({
                                'severity': 'major',
                                'section': 'workorder',
                                'issue': f'Task {task_id} missing workorder_id field',
                                'suggestion': f'Add "workorder_id": "{workorder_id}" to task {task_id}'
                            })
                        # Check task workorder_id matches plan's workorder
                        elif task['workorder_id'] != workorder_id:
                            self.issues.append({
                                'severity': 'critical',
                                'section': 'workorder',
                                'issue': f'Task {task_id} workorder_id mismatch: {task["workorder_id"]} != {workorder_id}',
                                'suggestion': f'Change task workorder_id to "{workorder_id}"'
                            })

    def validate_autonomy(self):
        """Validate no ambiguity, implementable without clarification."""
        logger.debug('Validating autonomy...')

        plan_json_str = json.dumps(self.plan_data)

        # Check for ambiguous phrases
        ambiguous_pattern = r'\b(might|could|maybe|possibly|perhaps|unclear|TBD|to be determined|needs clarification)\b'
        matches = list(re.finditer(ambiguous_pattern, plan_json_str, re.IGNORECASE))

        for match in matches[:5]:  # Limit to first 5 to avoid spam
            self.issues.append({
                'severity': 'major',
                'section': 'autonomy',
                'issue': f'Ambiguous phrase found: "{match.group()}"',
                'suggestion': 'Replace with definitive language - make clear decisions'
            })

        # Check for questions
        question_pattern = r'(Should we|What about|What if|How do we|Which|\?)'
        matches = list(re.finditer(question_pattern, plan_json_str, re.IGNORECASE))

        for match in matches[:5]:  # Limit to first 5
            self.issues.append({
                'severity': 'major',
                'section': 'autonomy',
                'issue': f'Question found in plan: "{match.group()}"',
                'suggestion': 'Answer the question in the plan - no unresolved questions'
            })

    def calculate_score(self) -> int:
        """Calculate 0-100 score based on issues."""
        score = 100
        for issue in self.issues:
            if issue['severity'] == 'critical':
                score -= 10
            elif issue['severity'] == 'major':
                score -= 5
            elif issue['severity'] == 'minor':
                score -= 1
        return max(0, score)

    def determine_result(self, score: int) -> str:
        """Determine validation result from score."""
        if score >= 90:
            return 'PASS'
        elif score >= 85:
            return 'PASS_WITH_WARNINGS'
        elif score >= 70:
            return 'NEEDS_REVISION'
        else:
            return 'FAIL'

    def _build_checklist_results(self) -> dict:
        """Build checklist results dict mapping all 23 checklist items to pass/fail."""
        results = {}

        # Completeness checklist items (9 items)
        results['executive_summary_complete'] = self._check_executive_summary_complete()
        results['risk_assessment_present'] = self._check_section_present('2_risk_assessment')
        results['current_state_documented'] = self._check_section_present('3_current_state_analysis')
        results['key_features_defined'] = self._check_section_present('4_key_features')
        results['all_tasks_have_ids'] = not self._has_issues_matching('task.*without.*id', ignore_case=True)
        results['phases_defined'] = self._check_section_present('6_implementation_phases')
        results['testing_strategy_present'] = self._check_section_present('7_testing_strategy')
        results['success_criteria_defined'] = self._check_section_present('8_success_criteria')
        results['implementation_checklist_present'] = self._check_section_present('9_implementation_checklist')

        # Quality checklist items (8 items)
        results['no_placeholder_text'] = not self._has_issues_matching('Placeholder text found')
        results['task_descriptions_imperative'] = not self._has_issues_matching('description.*not.*imperative', ignore_case=True)
        results['success_criteria_measurable'] = not self._has_issues_matching('Success criteria lack')
        results['edge_cases_comprehensive'] = not self._has_issues_matching('Insufficient edge case')
        results['effort_estimates_realistic'] = not self._has_issues_matching('effort.*unrealistic', ignore_case=True)
        results['dependencies_valid'] = not self._has_issues_matching('depends on non-existent')
        results['security_addressed'] = not self._has_issues_matching('security.*not.*addressed', ignore_case=True)
        results['performance_targets_specified'] = not self._has_issues_matching('performance.*not.*specified', ignore_case=True)

        # Autonomy checklist items (6 items)
        results['no_ambiguous_phrases'] = not self._has_issues_matching('Ambiguous phrase')
        results['no_questions'] = not self._has_issues_matching('Question found')
        results['edge_case_behavior_defined'] = not self._has_issues_matching('edge case.*undefined', ignore_case=True)
        results['acceptance_criteria_clear'] = not self._has_issues_matching('acceptance.*unclear', ignore_case=True)
        results['review_gates_specified'] = not self._has_issues_matching('review.*gate.*missing', ignore_case=True)
        results['technical_decisions_documented'] = not self._has_issues_matching('decision.*not.*documented', ignore_case=True)

        # Additional validation
        results['no_circular_dependencies'] = not self._has_issues_matching('Circular dependency')

        return results

    def _check_executive_summary_complete(self) -> bool:
        """Check if executive summary has all required fields.

        Uses class constants from plan.schema.json:
        - EXECUTIVE_SUMMARY_REQUIRED: NEW format (goal, description, scope)
        - EXECUTIVE_SUMMARY_LEGACY: OLD format (for backward compatibility)
        """
        if 'UNIVERSAL_PLANNING_STRUCTURE' not in self.plan_data:
            return False
        structure = self.plan_data['UNIVERSAL_PLANNING_STRUCTURE']
        if '1_executive_summary' not in structure:
            return False
        summary = structure['1_executive_summary']

        # Accept either NEW format (from schema) or OLD format (legacy)
        has_new_format = all(field in summary for field in self.EXECUTIVE_SUMMARY_REQUIRED)
        has_old_format = all(field in summary for field in self.EXECUTIVE_SUMMARY_LEGACY)

        return has_new_format or has_old_format

    def _check_section_present(self, section_name: str) -> bool:
        """Check if a specific section is present."""
        if 'UNIVERSAL_PLANNING_STRUCTURE' not in self.plan_data:
            return False
        return section_name in self.plan_data['UNIVERSAL_PLANNING_STRUCTURE']

    def _has_issues_in_section(self, section: str) -> bool:
        """Check if any issues in given section."""
        return any(issue['section'] == section for issue in self.issues)

    def _has_critical_in_section(self, section: str) -> bool:
        """Check if any critical issues in given section."""
        return any(issue['section'] == section and issue['severity'] == 'critical'
                   for issue in self.issues)

    def _has_issues_matching(self, pattern: str, ignore_case: bool = False) -> bool:
        """Check if any issues match pattern."""
        flags = re.IGNORECASE if ignore_case else 0
        regex = re.compile(pattern, flags)
        return any(regex.search(issue['issue']) for issue in self.issues)

    def validate_no_time_estimates(self):
        """
        Enforce agentic constraint: Plans must not contain time estimates.

        Plans are complexity-based, not time-based. AI agents work autonomously
        without deadlines. Focus on WHAT and HOW COMPLEX, never WHEN or HOW LONG.

        Rejects plans containing:
        - hours, minutes, duration (explicit time references)
        - timeline, schedule, deadline (temporal planning)
        - estimated_time, time_estimate (time field names)

        Allows:
        - "real-time" (technical term)
        - "runtime" (technical term)
        - "estimated_effort: low/medium/high" (complexity enum, not time)
        """
        logger.debug('Validating no time estimates (agentic constraint)...')

        plan_str = json.dumps(self.plan_data).lower()

        # Time keywords that violate agentic constraint
        time_keywords = [
            'hours', 'minutes', 'duration', 'timeline',
            'schedule', 'deadline', 'estimated_time', 'time_estimate'
        ]

        # Exceptions (technical terms that contain "time")
        exceptions = ['real-time', 'realtime', 'runtime', 'run-time']

        found_keywords = []
        for keyword in time_keywords:
            # Check if keyword exists
            if keyword in plan_str:
                # Skip if it's part of an exception
                is_exception = any(exc in plan_str for exc in exceptions if keyword in exc)
                if not is_exception:
                    found_keywords.append(keyword)

        if found_keywords:
            self.issues.append({
                'severity': 'major',
                'section': 'autonomy',
                'issue': f'Plan contains time estimates: {", ".join(found_keywords)}',
                'suggestion': 'Remove time references. Use complexity levels (trivial/low/medium/high/very_high) instead. Plans describe WHAT and HOW COMPLEX, not WHEN or HOW LONG.'
            })
