"""Planning generator for creating implementation plans."""

from pathlib import Path
from typing import Optional, Dict, Any
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import Paths, Files
from logger_config import logger, log_error, log_security_event
from uds_helpers import get_server_version


class PlanningGenerator:
    """
    Generates implementation plans by synthesizing context, analysis, and template.

    Workflow:
    1. Load context.json (if exists) - feature requirements
    2. Load analysis data (if exists) - project structure/standards
    3. Load AI-optimized template - planning structure
    4. Generate complete plan (10 sections) in batch mode
    5. Save to coderef/workorder/<feature-name>/plan.json
    6. On failure: save partial plan with TODOs marking incomplete sections
    """

    def __init__(self, project_path: Path):
        """
        Initialize planning generator.

        Args:
            project_path: Validated project root directory
        """
        self.project_path = project_path

        # Use MCP server's installation directory for templates (not user's project)
        server_root = Path(__file__).parent.parent  # Up to docs-mcp/ directory
        self.context_dir = server_root / "coderef" / "context"
        self.template_file = self.context_dir / "planning-template-for-ai.json"

        logger.info(f"PlanningGenerator initialized for project: {project_path}")
        logger.debug(f"Template path: {self.template_file}")

    def validate_feature_name(self, feature_name: str) -> str:
        """
        Validate and sanitize feature name to prevent path traversal.

        Args:
            feature_name: Feature name provided by user

        Returns:
            Sanitized feature name

        Raises:
            ValueError: If feature name contains invalid characters
        """
        import re
        # Allow alphanumeric, hyphens, underscores only (no path separators)
        if not feature_name or not re.match(r'^[a-zA-Z0-9_-]+$', feature_name):
            log_security_event(
                'invalid_feature_name',
                f"Feature name contains invalid characters: {feature_name}",
                feature_name=feature_name
            )
            raise ValueError(
                f"Invalid feature name: '{feature_name}'. "
                "Only alphanumeric characters, hyphens, and underscores allowed."
            )
        return feature_name

    def load_context(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """
        Load context.json for the feature (if exists).

        Args:
            feature_name: Name of feature

        Returns:
            Context data dict or None if file doesn't exist

        Raises:
            ValueError: If context file exists but is malformed
        """
        context_file = self.project_path / Paths.CONTEXT_DIR / "working" / feature_name / "context.json"

        if not context_file.exists():
            logger.warning(f"Context file not found: {context_file}")
            return None

        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                context = json.load(f)
            logger.info(f"Context loaded from: {context_file}")
            return context
        except json.JSONDecodeError as e:
            log_error('malformed_context', f"Context file is malformed: {str(e)}", path=str(context_file))
            raise ValueError(f"Context file is malformed JSON: {str(e)}")
        except Exception as e:
            log_error('context_load_error', str(e), path=str(context_file))
            raise ValueError(f"Error loading context file: {str(e)}")

    def load_analysis(self, feature_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Load project analysis data from analyze_project_for_planning.

        Args:
            feature_name: Optional feature name to load feature-specific analysis

        Returns:
            Analysis data dict or None if not available

        Note:
            If feature_name provided, looks in coderef/workorder/{feature_name}/analysis.json
            Otherwise returns None (analysis must be run first).
        """
        if not feature_name:
            logger.debug("No feature_name provided for analysis loading")
            return None

        # Look for analysis.json in feature workorder directory
        analysis_file = self.project_path / 'coderef' / 'workorder' / feature_name / 'analysis.json'

        if not analysis_file.exists():
            logger.debug(f"Analysis file not found: {analysis_file}")
            return None

        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            logger.info(f"Analysis loaded from: {analysis_file}")
            return analysis
        except json.JSONDecodeError as e:
            log_error('malformed_analysis', f"Analysis file is malformed: {str(e)}", path=str(analysis_file))
            return None
        except Exception as e:
            log_error('analysis_load_error', str(e), path=str(analysis_file))
            return None

    def load_template(self) -> Dict[str, Any]:
        """
        Load AI-optimized planning template.

        Returns:
            Template data dict

        Raises:
            FileNotFoundError: If template file doesn't exist
            ValueError: If template file is malformed
        """
        if not self.template_file.exists():
            log_error('template_not_found', f"Template file not found: {self.template_file}")
            raise FileNotFoundError(
                f"Planning template not found: {self.template_file}. "
                f"Expected AI-optimized template in MCP server directory at: "
                f"coderef/context/planning-template-for-ai.json"
            )

        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                template = json.load(f)
            logger.info(f"Template loaded from: {self.template_file}")
            return template
        except json.JSONDecodeError as e:
            log_error('malformed_template', f"Template file is malformed: {str(e)}")
            raise ValueError(f"Template file is malformed JSON: {str(e)}")
        except Exception as e:
            log_error('template_load_error', str(e))
            raise ValueError(f"Error loading template file: {str(e)}")

    def generate_plan(
        self,
        feature_name: str,
        context: Optional[Dict[str, Any]] = None,
        analysis: Optional[Dict[str, Any]] = None,
        workorder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete implementation plan.

        This is the main method that synthesizes context, analysis, and template
        into a complete 10-section implementation plan.

        Args:
            feature_name: Name of feature to plan
            context: Context data from gather-context (optional)
            analysis: Analysis data from analyze-for-planning (optional)
            workorder_id: Optional workorder ID for tracking

        Returns:
            Complete plan dict with all 10 sections

        Raises:
            ValueError: If plan generation fails
        """
        logger.info(f"Generating plan for feature: {feature_name}")

        # Validate feature name
        feature_name = self.validate_feature_name(feature_name)

        # Load inputs
        if context is None:
            context = self.load_context(feature_name)
            if context is None:
                logger.warning("No context.json found - generating plan without requirements context")

        if analysis is None:
            analysis = self.load_analysis()
            if analysis is None:
                logger.warning("No analysis data available - generating plan without codebase analysis")

        template = self.load_template()

        # Generate plan (with single retry on failure)
        try:
            plan = self._generate_plan_internal(feature_name, context, analysis, template, workorder_id)
            logger.info(f"Plan generated successfully for: {feature_name}")
            return plan
        except Exception as e:
            logger.warning(f"First attempt failed: {str(e)}. Retrying once...")
            try:
                plan = self._generate_plan_internal(feature_name, context, analysis, template, workorder_id)
                logger.info(f"Plan generated successfully on retry for: {feature_name}")
                return plan
            except Exception as retry_error:
                log_error('plan_generation_failed', f"Plan generation failed after retry: {str(retry_error)}")
                # Save partial plan
                partial_plan = self._create_partial_plan(feature_name, str(retry_error))
                self.save_plan(feature_name, partial_plan)
                raise ValueError(f"Plan generation failed: {str(retry_error)}. Partial plan saved.")

    def _generate_plan_internal(
        self,
        feature_name: str,
        context: Optional[Dict[str, Any]],
        analysis: Optional[Dict[str, Any]],
        template: Dict[str, Any],
        workorder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Internal plan generation logic.

        NOTE: This is a simplified implementation. In production, this would use
        an AI model (like Claude) to actually synthesize the inputs into a complete plan.
        For now, it creates a skeleton plan structure.

        Args:
            feature_name: Feature name
            context: Context data
            analysis: Analysis data
            template: Template data
            workorder_id: Optional workorder ID for tracking

        Returns:
            Plan dict with all 10 sections
        """
        logger.debug(f"Generating plan internal for: {feature_name}")

        # In a full implementation, this would call an AI model to generate the plan
        # For now, create skeleton structure following template
        plan = {
            "META_DOCUMENTATION": {
                "feature_name": feature_name,
                "workorder_id": workorder_id,
                "version": template.get("_AI_INSTRUCTIONS", {}).get("version", "1.0.0"),
                "status": "planning",
                "generated_by": "PlanningGenerator",
                "has_context": context is not None,
                "has_analysis": analysis is not None,
            },
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "0_preparation": self._generate_preparation_section(context, analysis),
                "1_executive_summary": self._generate_executive_summary(feature_name, context),
                "2_risk_assessment": self._generate_risk_assessment(context, analysis),
                "3_current_state_analysis": self._generate_current_state(analysis),
                "4_key_features": self._generate_key_features(context),
                "5_task_id_system": self._generate_tasks(context, analysis),
                "6_implementation_phases": self._generate_phases(),
                "7_testing_strategy": self._generate_testing_strategy(),
                "8_success_criteria": self._generate_success_criteria(context),
                "9_implementation_checklist": self._generate_checklist()
            }
        }

        return plan

    def _generate_preparation_section(
        self,
        context: Optional[Dict[str, Any]],
        analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate Section 0: Preparation."""
        if analysis:
            return analysis.get("preparation_summary", {})

        return {
            "foundation_docs": {"available": [], "missing": ["Run /analyze-for-planning to discover docs"]},
            "coding_standards": {"available": [], "missing": ["Run /analyze-for-planning to discover standards"]},
            "reference_components": {"primary": "Unknown", "secondary": []},
            "key_patterns_identified": ["Run /analyze-for-planning to identify patterns"],
            "technology_stack": {"languages": [], "frameworks": [], "key_libraries": []},
            "gaps_and_risks": ["Missing project analysis - run /analyze-for-planning first"]
        }

    def _generate_executive_summary(
        self,
        feature_name: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate Section 1: Executive Summary."""
        if context:
            description = context.get("description", f"Implement {feature_name} feature")
            goal = context.get("goal", "Enhance system capabilities")
            requirements = context.get("requirements", [])

            # Generate use case from requirements
            use_case = "User requests feature"
            if requirements:
                use_case = f"User requests {feature_name} → System implements: {', '.join(requirements[:3])} → Feature is functional"

            # Generate output list from requirements
            output = "New feature implementation"
            if requirements:
                output = f"Implemented {len(requirements)} requirements: {', '.join(requirements[:3])}"

            return {
                "purpose": description,
                "value_proposition": goal,
                "real_world_analogy": f"Similar to building {feature_name} - systematically implementing each requirement to deliver complete functionality",
                "use_case": use_case,
                "output": output
            }

        # Without context, provide minimal structure
        feature_title = feature_name.replace("-", " ").replace("_", " ").title()
        return {
            "purpose": f"Implement {feature_title} feature to extend system capabilities",
            "value_proposition": f"Enables users to {feature_title.lower()} functionality",
            "real_world_analogy": f"Building {feature_title} from scratch following established patterns",
            "use_case": f"User triggers {feature_name} → System processes request → Feature delivers result",
            "output": f"{feature_title} implementation with tests and documentation"
        }

    def _generate_risk_assessment(
        self,
        context: Optional[Dict[str, Any]],
        analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate Section 2: Risk Assessment."""
        requirements_count = len(context.get("requirements", [])) if context else 0

        # Estimate complexity based on requirements count
        if requirements_count <= 3:
            complexity = "low (estimated 3-5 files, <200 lines)"
            overall_risk = "low"
        elif requirements_count <= 8:
            complexity = "medium (estimated 5-15 files, 200-1000 lines)"
            overall_risk = "medium"
        else:
            complexity = "high (estimated 15+ files, 1000+ lines)"
            overall_risk = "medium"

        # Get constraints as dependencies
        constraints = context.get("constraints", []) if context else []
        dependencies = constraints if constraints else ["None identified - may require discovery during implementation"]

        return {
            "overall_risk": overall_risk,
            "complexity": complexity,
            "scope": f"Estimated {requirements_count} requirements affecting multiple components",
            "file_system_risk": "low (standard code changes only)",
            "dependencies": dependencies,
            "performance_concerns": ["No significant performance concerns identified - monitor during implementation"],
            "security_considerations": ["Follow existing security patterns - review during implementation"],
            "breaking_changes": "none (extending existing functionality)"
        }

    def _generate_current_state(self, analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Section 3: Current State Analysis."""
        if analysis:
            # Extract from analysis if available
            tech_stack = analysis.get("preparation_summary", {}).get("technology_stack", {})
            patterns = analysis.get("preparation_summary", {}).get("key_patterns_identified", [])

            return {
                "affected_files": ["Identify during implementation based on feature scope"],
                "dependencies": {
                    "existing_internal": ["Existing modules and components - identify during implementation"],
                    "existing_external": tech_stack.get("key_libraries", []),
                    "new_external": [],
                    "new_internal": []
                },
                "architecture_context": f"Follows existing patterns: {', '.join(patterns[:3]) if patterns else 'Standard implementation patterns'}"
            }

        return {
            "affected_files": ["Identify during implementation based on feature scope"],
            "dependencies": {
                "existing_internal": ["Existing modules and components - identify during implementation"],
                "existing_external": ["Standard project dependencies"],
                "new_external": [],
                "new_internal": []
            },
            "architecture_context": "Standard implementation following existing project architecture and patterns"
        }

    def _generate_key_features(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Section 4: Key Features."""
        if context and "requirements" in context:
            requirements = context["requirements"]
            primary_count = min(5, len(requirements))

            return {
                "primary_features": requirements[:primary_count],
                "secondary_features": requirements[primary_count:] if len(requirements) > primary_count else [],
                "edge_case_handling": [
                    "Empty or null input validation",
                    "Invalid input error handling",
                    "Boundary conditions and limits"
                ],
                "configuration_options": ["None"]
            }

        return {
            "primary_features": [
                "Implement core functionality",
                "Add error handling",
                "Integrate with existing system"
            ],
            "secondary_features": [
                "Add logging and monitoring",
                "Optimize performance"
            ],
            "edge_case_handling": [
                "Empty or null input validation",
                "Invalid input error handling",
                "Boundary conditions and limits"
            ],
            "configuration_options": ["None"]
        }

    def _generate_tasks(
        self,
        context: Optional[Dict[str, Any]],
        analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, list]:
        """Generate Section 5: Task ID System."""
        tasks = []

        # Setup tasks
        tasks.append("SETUP-001: Create initial project structure and setup development environment with required dependencies")

        # Logic tasks based on requirements
        if context and "requirements" in context:
            requirements = context["requirements"]
            for idx, req in enumerate(requirements[:5], start=1):
                tasks.append(f"LOGIC-{idx:03d}: Implement {req} following existing project patterns and architecture")
        else:
            tasks.append("LOGIC-001: Implement core feature functionality following existing project patterns and architecture")

        # Testing tasks
        tasks.append("TEST-001: Write unit tests for all new functionality with minimum 80% code coverage")
        tasks.append("TEST-002: Write integration tests to verify end-to-end functionality and component interactions")

        # Documentation tasks
        tasks.append("DOC-001: Update documentation including README, API docs, and inline code comments for all public interfaces")

        return {"tasks": tasks}

    def _generate_phases(self) -> Dict[str, Any]:
        """Generate Section 6: Implementation Phases with NEW schema format."""
        return {
            "phases": [
                {
                    "phase": 1,
                    "name": "Phase 1: Foundation",
                    "description": "Setup and scaffolding - create initial structure, install dependencies, configure environment",
                    "tasks": ["SETUP-001"],
                    "deliverables": ["All files exist", "Dependencies installed", "Environment configured"]
                },
                {
                    "phase": 2,
                    "name": "Phase 2: Core Implementation",
                    "description": "Implement primary features and business logic following existing patterns",
                    "tasks": ["LOGIC-001"],
                    "deliverables": ["Happy path works end-to-end", "Core functionality complete"]
                },
                {
                    "phase": 3,
                    "name": "Phase 3: Testing",
                    "description": "Comprehensive testing at unit, integration, and end-to-end levels",
                    "tasks": ["TEST-001"],
                    "deliverables": ["All tests passing", "Coverage meets requirements"]
                },
                {
                    "phase": 4,
                    "name": "Phase 4: Documentation",
                    "description": "Complete documentation for users and developers",
                    "tasks": ["DOC-001"],
                    "deliverables": ["All documentation complete", "Examples provided"]
                }
            ]
        }

    def _generate_testing_strategy(self) -> Dict[str, Any]:
        """Generate Section 7: Testing Strategy."""
        return {
            "unit_tests": [
                "Test individual functions and methods in isolation",
                "Verify input validation and error handling",
                "Test edge cases and boundary conditions",
                "Achieve minimum 80% code coverage"
            ],
            "integration_tests": [
                "Test component interactions and data flow",
                "Verify end-to-end functionality",
                "Test integration with existing systems"
            ],
            "end_to_end_tests": ["Not applicable"],
            "edge_case_scenarios": [
                {
                    "scenario": "Empty or null input provided",
                    "setup": "Call function with None or empty string",
                    "expected_behavior": "Function validates input and returns appropriate error",
                    "verification": "Assert error message and status code",
                    "error_handling": "ValueError or ValidationError"
                },
                {
                    "scenario": "Invalid input format provided",
                    "setup": "Call function with malformed or incorrect data type",
                    "expected_behavior": "Function validates input type and returns error",
                    "verification": "Assert error message indicates invalid format",
                    "error_handling": "TypeError or ValidationError"
                },
                {
                    "scenario": "Boundary conditions at limits",
                    "setup": "Test with minimum and maximum allowed values",
                    "expected_behavior": "Function handles boundary values correctly",
                    "verification": "Assert results are within expected range",
                    "error_handling": "No error expected for valid boundaries"
                }
            ]
        }

    def _generate_success_criteria(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Section 8: Success Criteria."""
        functional = [
            {
                "requirement": "Feature implementation complete",
                "metric": "All requirements implemented",
                "target": "100% of specified requirements",
                "validation": "Manual verification against requirements list"
            },
            {
                "requirement": "Integration successful",
                "metric": "Feature works with existing system",
                "target": "No breaking changes to existing functionality",
                "validation": "Run full test suite"
            }
        ]

        # Add requirement-specific criteria if context available
        if context and "requirements" in context:
            requirements = context["requirements"]
            for idx, req in enumerate(requirements[:3], start=1):
                functional.append({
                    "requirement": req,
                    "metric": "Functionality verified",
                    "target": "Works as specified",
                    "validation": f"Test cases for: {req}"
                })

        return {
            "functional_requirements": functional,
            "quality_requirements": [
                {"requirement": "Code coverage", "metric": "Line coverage", "target": ">80%", "validation": "Run coverage tool"},
                {"requirement": "Code quality", "metric": "Linter passes", "target": "Zero linting errors", "validation": "Run linter"},
                {"requirement": "Type safety", "metric": "Type checker passes", "target": "Zero type errors", "validation": "Run type checker"}
            ],
            "performance_requirements": [
                {"requirement": "Response time", "metric": "Execution time", "target": "< 1 second for typical operations", "validation": "Performance tests"}
            ],
            "security_requirements": [
                {"requirement": "Input validation", "metric": "All inputs validated", "target": "100% validation coverage", "validation": "Security review"}
            ]
        }

    def _generate_checklist(self) -> Dict[str, list]:
        """Generate Section 9: Implementation Checklist."""
        return {
            "pre_implementation": [
                "☐ Review complete plan for gaps or ambiguities",
                "☐ Verify all requirements are clear and testable",
                "☐ Set up development environment with required dependencies"
            ],
            "phase_1": [
                "☐ SETUP-001: Create initial project structure and setup development environment with required dependencies"
            ],
            "phase_2": [
                "☐ LOGIC-001: Implement core feature functionality following existing project patterns and architecture"
            ],
            "phase_3": [
                "☐ TEST-001: Write unit tests for all new functionality with minimum 80% code coverage",
                "☐ TEST-002: Write integration tests to verify end-to-end functionality and component interactions"
            ],
            "phase_4": [
                "☐ DOC-001: Update documentation including README, API docs, and inline code comments for all public interfaces"
            ],
            "finalization": [
                "☐ All tests passing (unit + integration)",
                "☐ Code review completed and approved",
                "☐ Documentation updated and complete",
                "☐ Changelog entry created with version bump",
                "☐ Final verification against success criteria"
            ]
        }

    def _create_partial_plan(self, feature_name: str, error_message: str) -> Dict[str, Any]:
        """
        Create partial plan with error markers when generation fails.

        Args:
            feature_name: Feature name
            error_message: Error that caused failure

        Returns:
            Partial plan dict with incomplete sections marked
        """
        return {
            "META_DOCUMENTATION": {
                "feature_name": feature_name,
                "status": "partial",
                "version": "1.0.0",
                "generated_by": "PlanningGenerator",
                "error": error_message,
                "note": "Plan generation failed. Complete missing sections and re-validate."
            },
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "0_preparation": {"status": "TODO", "error": error_message},
                "1_executive_summary": {"status": "TODO", "note": "Complete this section manually"},
                "2_risk_assessment": {"status": "TODO", "note": "Complete this section manually"},
                "3_current_state_analysis": {"status": "TODO", "note": "Complete this section manually"},
                "4_key_features": {"status": "TODO", "note": "Complete this section manually"},
                "5_task_id_system": {"status": "TODO", "note": "Complete this section manually"},
                "6_implementation_phases": {"status": "TODO", "note": "Complete this section manually"},
                "7_testing_strategy": {"status": "TODO", "note": "Complete this section manually"},
                "8_success_criteria": {"status": "TODO", "note": "Complete this section manually"},
                "9_implementation_checklist": {"status": "TODO", "note": "Complete this section manually"}
            }
        }

    def save_plan(self, feature_name: str, plan: Dict[str, Any]) -> str:
        """
        Save plan to coderef/workorder/<feature-name>/plan.json with UDS metadata.

        Args:
            feature_name: Feature name
            plan: Plan data dict

        Returns:
            Path to saved plan file

        Raises:
            IOError: If file cannot be written
        """
        # Validate feature name (security check)
        feature_name = self.validate_feature_name(feature_name)

        # Inject UDS metadata into META_DOCUMENTATION if workorder_id exists (WO-UDS-INTEGRATION-001)
        if 'META_DOCUMENTATION' in plan and 'workorder_id' in plan['META_DOCUMENTATION']:
            from datetime import datetime, timedelta

            workorder_id = plan['META_DOCUMENTATION']['workorder_id']
            status = plan['META_DOCUMENTATION'].get('status', 'DRAFT')

            # Add UDS fields to META_DOCUMENTATION
            plan['META_DOCUMENTATION']['uds'] = {
                'generated_by': get_server_version(),
                'document_type': 'Implementation Plan',
                'last_updated': datetime.utcnow().strftime("%Y-%m-%d"),
                'ai_assistance': True,
                'next_review': (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
            }
            logger.info(f"UDS metadata injected into plan for workorder: {workorder_id}")

        # Create workorder directory
        working_dir = self.project_path / Paths.CONTEXT_DIR / "workorder" / feature_name
        working_dir.mkdir(parents=True, exist_ok=True)

        # Save plan
        plan_file = working_dir / "plan.json"
        try:
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2)
            logger.info(f"Plan saved to: {plan_file}")
            return str(plan_file)
        except Exception as e:
            log_error('plan_save_error', str(e), path=str(plan_file))
            raise IOError(f"Error saving plan to {plan_file}: {str(e)}")
