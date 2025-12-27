"""Planning generator for creating implementation plans."""

from pathlib import Path
from typing import Optional, Dict, Any
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import Paths, Files
from logger_config import logger, log_error, log_security_event


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
            return {
                "purpose": context.get("description", f"Implement {feature_name} feature"),
                "value_proposition": context.get("goal", "Enhance system capabilities"),
                "real_world_analogy": "TODO: Add real-world analogy",
                "use_case": "TODO: Add use case workflow",
                "output": "TODO: List tangible artifacts"
            }

        return {
            "purpose": f"Implement {feature_name} feature",
            "value_proposition": "TODO: Define value proposition",
            "real_world_analogy": "TODO: Add real-world analogy",
            "use_case": "TODO: Add use case workflow",
            "output": "TODO: List tangible artifacts"
        }

    def _generate_risk_assessment(
        self,
        context: Optional[Dict[str, Any]],
        analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate Section 2: Risk Assessment."""
        return {
            "overall_risk": "medium",
            "complexity": "medium (TODO: estimate file count and lines)",
            "scope": "Medium - TODO files, TODO components affected",
            "file_system_risk": "low",
            "dependencies": context.get("constraints", []) if context else [],
            "performance_concerns": ["TODO: identify performance concerns"],
            "security_considerations": ["TODO: identify security considerations"],
            "breaking_changes": "none"
        }

    def _generate_current_state(self, analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Section 3: Current State Analysis."""
        return {
            "affected_files": ["TODO: List all files to create/modify"],
            "dependencies": {
                "existing_internal": [],
                "existing_external": [],
                "new_external": [],
                "new_internal": []
            },
            "architecture_context": "TODO: Describe architecture layer and patterns"
        }

    def _generate_key_features(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Section 4: Key Features."""
        if context and "requirements" in context:
            return {
                "primary_features": context["requirements"][:5],
                "secondary_features": context["requirements"][5:] if len(context["requirements"]) > 5 else [],
                "edge_case_handling": ["TODO: Define edge cases"],
                "configuration_options": ["None"]
            }

        return {
            "primary_features": ["TODO: List 3-5 primary features"],
            "secondary_features": ["TODO: List 2-3 secondary features"],
            "edge_case_handling": ["TODO: List 2-3 edge cases"],
            "configuration_options": ["None"]
        }

    def _generate_tasks(
        self,
        context: Optional[Dict[str, Any]],
        analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, list]:
        """Generate Section 5: Task ID System."""
        return {
            "tasks": [
                "SETUP-001: TODO: Initial setup task",
                "LOGIC-001: TODO: Core logic task",
                "TEST-001: TODO: Testing task",
                "DOC-001: TODO: Documentation task"
            ]
        }

    def _generate_phases(self) -> Dict[str, Any]:
        """Generate Section 6: Implementation Phases."""
        return {
            "phases": [
                {
                    "title": "Phase 1: Foundation",
                    "purpose": "Setup and scaffolding",
                    "complexity": "low",
                    "effort_level": 2,
                    "tasks": ["SETUP-001"],
                    "completion_criteria": "All files exist, dependencies installed"
                },
                {
                    "title": "Phase 2: Core Implementation",
                    "purpose": "Implement primary features",
                    "complexity": "high",
                    "effort_level": 4,
                    "tasks": ["LOGIC-001"],
                    "completion_criteria": "Happy path works end-to-end"
                },
                {
                    "title": "Phase 3: Testing",
                    "purpose": "Comprehensive testing",
                    "complexity": "medium",
                    "effort_level": 3,
                    "tasks": ["TEST-001"],
                    "completion_criteria": "All tests passing"
                },
                {
                    "title": "Phase 4: Documentation",
                    "purpose": "Complete documentation",
                    "complexity": "low",
                    "effort_level": 2,
                    "tasks": ["DOC-001"],
                    "completion_criteria": "All docs complete"
                }
            ]
        }

    def _generate_testing_strategy(self) -> Dict[str, Any]:
        """Generate Section 7: Testing Strategy."""
        return {
            "unit_tests": ["TODO: List unit tests"],
            "integration_tests": ["TODO: List integration tests"],
            "end_to_end_tests": ["Not applicable" ],
            "edge_case_scenarios": [
                {
                    "scenario": "TODO: Edge case 1",
                    "setup": "TODO: How to create",
                    "expected_behavior": "TODO: What should happen",
                    "verification": "TODO: How to verify",
                    "error_handling": "TODO: Error type or 'No error'"
                }
            ]
        }

    def _generate_success_criteria(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Section 8: Success Criteria."""
        return {
            "functional_requirements": [
                {"requirement": "TODO", "metric": "TODO", "target": "TODO", "validation": "TODO"}
            ],
            "quality_requirements": [
                {"requirement": "Code coverage", "metric": "Line coverage", "target": ">80%", "validation": "Run coverage tool"}
            ],
            "performance_requirements": [],
            "security_requirements": []
        }

    def _generate_checklist(self) -> Dict[str, list]:
        """Generate Section 9: Implementation Checklist."""
        return {
            "pre_implementation": [
                "☐ Review complete plan for gaps",
                "☐ Get stakeholder approval",
                "☐ Set up development environment"
            ],
            "phase_1": ["☐ SETUP-001: TODO"],
            "phase_2": ["☐ LOGIC-001: TODO"],
            "phase_3": ["☐ TEST-001: TODO"],
            "phase_4": ["☐ DOC-001: TODO"],
            "finalization": [
                "☐ All tests passing",
                "☐ Code review completed",
                "☐ Documentation updated",
                "☐ Changelog entry created"
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
        Save plan to coderef/workorder/<feature-name>/plan.json.

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
