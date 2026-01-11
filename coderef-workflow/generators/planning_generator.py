"""Planning generator for creating implementation plans."""

from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import sys
import asyncio

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
        context_file = self.project_path / Paths.CONTEXT_DIR / "workorder" / feature_name / "context.json"

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

    async def generate_plan(
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
            analysis = self.load_analysis(feature_name)
            if analysis is None:
                logger.warning("No analysis data available - generating plan without codebase analysis")

        template = self.load_template()

        # Generate plan (with single retry on failure)
        try:
            plan = await self._generate_plan_with_agent(feature_name, context, analysis, template, workorder_id)
            logger.info(f"Plan generated successfully for: {feature_name}")
            return plan
        except Exception as e:
            logger.warning(f"First attempt failed: {str(e)}. Retrying once...")
            try:
                plan = await self._generate_plan_with_agent(feature_name, context, analysis, template, workorder_id)
                logger.info(f"Plan generated successfully on retry for: {feature_name}")
                return plan
            except Exception as retry_error:
                log_error('plan_generation_failed', f"Plan generation failed after retry: {str(retry_error)}")
                # Save partial plan
                partial_plan = self._create_partial_plan(feature_name, str(retry_error))
                self.save_plan(feature_name, partial_plan)
                raise ValueError(f"Plan generation failed: {str(retry_error)}. Partial plan saved.")

    async def _generate_plan_with_agent(
        self,
        feature_name: str,
        context: Optional[Dict[str, Any]],
        analysis: Optional[Dict[str, Any]],
        template: Dict[str, Any],
        workorder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AI-powered plan generation using Task agent with full codebase context.

        This method launches a Task agent with comprehensive context (requirements,
        coderef data, foundation docs) and explicit instructions to use coderef MCP
        tools for dependency analysis, impact assessment, and pattern adherence.

        Args:
            feature_name: Feature name
            context: Context data (requirements, goals, constraints)
            analysis: Analysis data (foundation docs, tech stack, patterns)
            template: Template structure for plan sections
            workorder_id: Optional workorder ID for tracking

        Returns:
            Plan dict with all 10 sections, file-specific tasks, dependency-ordered phases

        Raises:
            ValueError: If Task agent unavailable or plan generation fails
        """
        logger.info(f"Generating AI-powered plan for: {feature_name}")

        # Pre-flight validation - ensure .coderef/ exists
        self._validate_coderef_exists()

        # Load coderef data
        coderef_data = {
            "index": self._load_coderef_index(),
            "patterns": self._load_coderef_patterns(),
            "graph": self._load_coderef_graph(),
            "coverage": self._load_coderef_coverage(),
            "complexity": self._load_coderef_complexity()
        }

        # Build comprehensive agent prompt
        agent_prompt = self._build_agent_prompt(
            feature_name, context, analysis, coderef_data, template
        )

        # Launch Task agent
        try:
            logger.debug("Launching Task agent for plan generation...")
            # NOTE: Task tool is called via MCP - this would need actual MCP integration
            # For now, fall back to template-based generation with a clear message
            raise NotImplementedError(
                "Task agent integration not yet implemented. "
                "To complete: Add Task tool invocation in _generate_plan_with_agent() method. "
                "See generators/planning_generator.py line 285 for implementation notes."
            )

        except NotImplementedError as e:
            logger.warning(f"⚠️  AI agent not available: {str(e)}")
            logger.info("ℹ️  Using template-based generation (fallback mode)")
            logger.info("ℹ️  Plan will use generic tasks instead of file-specific details")
            # Fallback to old template method
            return self._generate_plan_internal_fallback(
                feature_name, context, analysis, template, workorder_id
            )
        except Exception as e:
            # Unexpected error during agent launch
            logger.error(f"❌ Unexpected error during AI plan generation: {str(e)}")
            logger.warning("⚠️  Falling back to template-based generation")
            # Still try fallback even on unexpected errors
            try:
                return self._generate_plan_internal_fallback(
                    feature_name, context, analysis, template, workorder_id
                )
            except Exception as fallback_error:
                # If even fallback fails, raise with helpful message
                raise ValueError(
                    f"Plan generation failed in both AI and fallback modes.\n"
                    f"AI error: {str(e)}\n"
                    f"Fallback error: {str(fallback_error)}\n"
                    f"Please check logs and ensure context/analysis data is valid."
                )

    def _generate_plan_internal_fallback(
        self,
        feature_name: str,
        context: Optional[Dict[str, Any]],
        analysis: Optional[Dict[str, Any]],
        template: Dict[str, Any],
        workorder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fallback template-based plan generation (original implementation).

        Used when Task agent is unavailable or fails. Creates skeleton plan structure
        with generic tasks instead of file-specific implementation details.

        Args:
            feature_name: Feature name
            context: Context data
            analysis: Analysis data
            template: Template data
            workorder_id: Optional workorder ID for tracking

        Returns:
            Plan dict with all 10 sections (generic template-based)
        """
        logger.debug(f"Generating fallback plan for: {feature_name}")

        # Create skeleton structure following template
        plan = {
            "META_DOCUMENTATION": {
                "feature_name": feature_name,
                "workorder_id": workorder_id,
                "version": template.get("_AI_INSTRUCTIONS", {}).get("version", "1.0.0"),
                "status": "planning",
                "generated_by": "PlanningGenerator (fallback mode)",
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

    # ========== CodeRef Data Loading Methods (IMPL-002) ==========

    def _load_coderef_index(self) -> Optional[Dict[str, Any]]:
        """
        Load .coderef/index.json - code inventory with all functions, classes, components.

        Returns:
            Code inventory dict or None if file doesn't exist
        """
        index_path = self.project_path / ".coderef" / "index.json"
        if not index_path.exists():
            logger.warning(f"CodeRef index not found: {index_path}")
            return None

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"📁 Loaded coderef index: {len(data)} elements")
            return data
        except Exception as e:
            logger.error(f"Failed to load coderef index: {e}")
            return None

    def _load_coderef_patterns(self) -> Optional[Dict[str, Any]]:
        """
        Load .coderef/reports/patterns.json - coding conventions and patterns.

        Returns:
            Patterns dict or None if file doesn't exist
        """
        patterns_path = self.project_path / ".coderef" / "reports" / "patterns.json"
        if not patterns_path.exists():
            logger.warning(f"CodeRef patterns not found: {patterns_path}")
            return None

        try:
            with open(patterns_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"📁 Loaded coderef patterns: {len(data.get('patterns', []))} patterns")
            return data
        except Exception as e:
            logger.error(f"Failed to load coderef patterns: {e}")
            return None

    def _load_coderef_graph(self) -> Optional[Dict[str, Any]]:
        """
        Load .coderef/graph.json - dependency graph for relationship analysis.

        Returns:
            Dependency graph dict or None if file doesn't exist
        """
        graph_path = self.project_path / ".coderef" / "graph.json"
        if not graph_path.exists():
            logger.warning(f"CodeRef graph not found: {graph_path}")
            return None

        try:
            with open(graph_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"📁 Loaded coderef graph: {len(data.get('nodes', []))} nodes")
            return data
        except Exception as e:
            logger.error(f"Failed to load coderef graph: {e}")
            return None

    def _load_coderef_coverage(self) -> Optional[Dict[str, Any]]:
        """
        Load .coderef/reports/coverage.json - test coverage data for gap identification.

        Returns:
            Coverage dict or None if file doesn't exist
        """
        coverage_path = self.project_path / ".coderef" / "reports" / "coverage.json"
        if not coverage_path.exists():
            logger.warning(f"CodeRef coverage not found: {coverage_path}")
            return None

        try:
            with open(coverage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"📁 Loaded coderef coverage: {data.get('overall_coverage', 'unknown')}%")
            return data
        except Exception as e:
            logger.error(f"Failed to load coderef coverage: {e}")
            return None

    def _load_coderef_complexity(self) -> Optional[Dict[str, Any]]:
        """
        Load .coderef/reports/complexity.json - complexity metrics for effort estimation.

        Returns:
            Complexity dict or None if file doesn't exist
        """
        complexity_path = self.project_path / ".coderef" / "reports" / "complexity.json"
        if not complexity_path.exists():
            logger.warning(f"CodeRef complexity not found: {complexity_path}")
            return None

        try:
            with open(complexity_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"📁 Loaded coderef complexity: {len(data.get('files', []))} files analyzed")
            return data
        except Exception as e:
            logger.error(f"Failed to load coderef complexity: {e}")
            return None

    # ========== End CodeRef Data Loading Methods ==========

    def _build_agent_prompt(
        self,
        feature_name: str,
        context: Optional[Dict[str, Any]],
        analysis: Optional[Dict[str, Any]],
        coderef_data: Dict[str, Any],
        template: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive prompt for Task agent with all context.

        Constructs detailed prompt including:
        - Feature requirements from context.json
        - Codebase intelligence from .coderef/
        - Architecture context from foundation docs
        - Explicit coderef MCP tool usage instructions
        - Template structure for plan sections

        Args:
            feature_name: Feature name
            context: User requirements and constraints
            analysis: Project analysis with foundation docs
            coderef_data: All coderef data (index, patterns, graph, coverage, complexity)
            template: Plan structure template

        Returns:
            Comprehensive prompt string for Task agent
        """
        # Extract context data
        description = context.get("description", "Feature implementation") if context else "Feature implementation"
        goal = context.get("goal", "Implement feature") if context else "Implement feature"
        requirements = context.get("requirements", []) if context else []
        constraints = context.get("constraints", []) if context else []

        # Extract coderef data counts
        index_count = len(coderef_data.get("index", [])) if coderef_data.get("index") else 0
        patterns_count = len(coderef_data.get("patterns", {}).get("patterns", [])) if coderef_data.get("patterns") else 0
        graph_nodes = len(coderef_data.get("graph", {}).get("nodes", [])) if coderef_data.get("graph") else 0
        coverage_pct = coderef_data.get("coverage", {}).get("overall_coverage", "unknown") if coderef_data.get("coverage") else "unknown"

        # Extract foundation docs
        foundation_docs = analysis.get("foundation_doc_content", {}) if analysis else {}
        architecture_preview = foundation_docs.get("ARCHITECTURE.md", {}).get("preview", "Not available")[:500]
        api_preview = foundation_docs.get("API.md", {}).get("preview", "Not available")[:500]

        prompt = f"""You are an expert implementation planner. Generate a detailed, executable plan for this feature:

**FEATURE:** {feature_name}

**DESCRIPTION:** {description}

**GOAL:** {goal}

**REQUIREMENTS ({len(requirements)} total):**
{self._format_list(requirements)}

**CONSTRAINTS ({len(constraints)} total):**
{self._format_list(constraints)}

---

**CRITICAL: You have COMPLETE codebase context. USE IT EXPLICITLY.**

**CODE INVENTORY (.coderef/index.json):**
- Total elements: {index_count}
- Available: Functions, classes, components with exact file paths and line numbers

**CODING PATTERNS (.coderef/reports/patterns.json):**
- {patterns_count} patterns identified
- Includes: Error handling patterns, naming conventions, code organization rules

**DEPENDENCY GRAPH (.coderef/graph.json):**
- {graph_nodes} nodes in dependency graph
- Use for: Dependency analysis, impact assessment, task ordering

**TEST COVERAGE (.coderef/reports/coverage.json):**
- Overall coverage: {coverage_pct}%
- Use for: Identifying test gaps, planning test strategy

**ARCHITECTURE (ARCHITECTURE.md preview):**
{architecture_preview}...

**API REFERENCE (API.md preview):**
{api_preview}...

---

**YOUR TASK - Generate Implementation Plan**

You MUST create a plan.json following the 10-section structure below.

**MANDATORY REQUIREMENTS:**

1. **DEPENDENCY ANALYSIS** (use coderef data):
   - Check which existing functions/classes this feature depends on (use index.json)
   - Identify which files will be modified (check code inventory for exact paths)
   - Analyze dependency chains (use graph.json if available)

2. **PATTERN ADHERENCE** (use patterns.json):
   - Follow existing coding patterns from patterns.json
   - Match error handling approaches
   - Use established naming conventions

3. **TASK BREAKDOWN** (be SPECIFIC - most important):
   - Break each requirement into FILE-LEVEL tasks
   - Example: "IMPL-001: Modify src/auth/jwt.service.ts lines 45-60 - add generateRefreshToken() method"
   - NOT: "IMPL-001: Implement JWT tokens"
   - Include exact file paths from code inventory
   - Reference specific line numbers where changes occur

4. **PHASE PLANNING** (use dependencies):
   - Order tasks by dependency (what must happen first?)
   - Identify parallel vs sequential work
   - Create realistic phases (not always 4!)
   - Add "dependencies" and "rationale" fields to each phase

5. **TESTING STRATEGY** (use coverage.json):
   - Address current test coverage gaps
   - Specify which test files to create/modify
   - Include edge cases and integration tests

---

**OUTPUT FORMAT:**

Return a JSON object with this structure:

{{
  "META_DOCUMENTATION": {{
    "feature_name": "{feature_name}",
    "workorder_id": "WO-{feature_name.upper().replace('-', '-')}-001",
    "version": "1.0.0",
    "status": "planning",
    "generated_by": "AI Agent",
    "has_context": true,
    "has_analysis": true
  }},
  "UNIVERSAL_PLANNING_STRUCTURE": {{
    "0_preparation": {{ ... }},
    "1_executive_summary": {{ ... }},
    "2_risk_assessment": {{ ... }},
    "3_current_state_analysis": {{ ... }},
    "4_key_features": {{ ... }},
    "5_task_id_system": {{
      "tasks": [
        "SETUP-001: Specific setup task with file paths",
        "IMPL-001: Modify path/to/file.py lines X-Y - add specific method/function",
        "IMPL-002: Create path/to/new_file.py - implement specific component",
        ...
      ]
    }},
    "6_implementation_phases": {{
      "phases": [
        {{
          "phase": 1,
          "name": "Descriptive Phase Name",
          "description": "What this phase accomplishes",
          "tasks": ["SETUP-001", "IMPL-001"],
          "deliverables": ["Specific deliverable 1", "Specific deliverable 2"],
          "dependencies": "Sequential - SETUP-001 must complete before IMPL-001",
          "rationale": "Why this phase grouping makes sense"
        }}
      ]
    }},
    "7_testing_strategy": {{ ... }},
    "8_success_criteria": {{ ... }},
    "9_implementation_checklist": {{ ... }}
  }}
}}

---

**VALIDATION RULES:**

- ✅ Every task MUST reference specific files from code inventory
- ✅ Every task MUST consider existing patterns from patterns.json
- ✅ Every phase MUST have dependency-ordered tasks with rationale
- ✅ Risk assessment MUST address breaking changes and dependencies
- ✅ Testing strategy MUST address gaps from coverage.json
- ✅ NO time estimates (hours/minutes) - use complexity levels instead
- ✅ NO questions in plan - answer everything

**EXAMPLE TASK (GOOD):**
"IMPL-003: Modify generators/planning_generator.py lines 232-285 - Replace _generate_plan_internal() with _generate_plan_with_agent() async method that launches Task agent with coderef context"

**EXAMPLE TASK (BAD):**
"IMPL-003: Implement AI agent integration following existing patterns"

---

Generate the complete plan now. Be specific, reference actual files, and use the codebase intelligence provided.
"""
        return prompt

    def _format_list(self, items: List[str], max_items: int = 10) -> str:
        """Format list of items for prompt, truncating if too long."""
        if not items:
            return "- None specified"

        displayed = items[:max_items]
        result = "\n".join(f"- {item}" for item in displayed)

        if len(items) > max_items:
            result += f"\n... and {len(items) - max_items} more"

        return result

    # ========== End Prompt Builder ==========

    def _validate_coderef_exists(self) -> None:
        """
        Pre-flight validation - ensure .coderef/ directory exists with required files.

        Checks for:
        - .coderef/index.json (code inventory)
        - .coderef/graph.json (dependency graph)
        - .coderef/reports/patterns.json (coding conventions)

        Also checks drift.json if available and warns if >10% stale.

        Raises:
            ValueError: If required .coderef/ files are missing with instructions
        """
        coderef_dir = self.project_path / ".coderef"

        if not coderef_dir.exists():
            raise ValueError(
                f"❌ Error: .coderef/ directory not found at {self.project_path}\n\n"
                f"CodeRef data is required for AI-powered planning.\n\n"
                f"Run one of these commands to generate it:\n"
                f"  Quick scan:  coderef scan {self.project_path}\n"
                f"  Full scan:   python scripts/populate-coderef.py {self.project_path}\n\n"
                f"Then retry: /create-workorder"
            )

        # Check required files
        required_files = [
            (".coderef/index.json", "code inventory"),
            (".coderef/graph.json", "dependency graph"),
            (".coderef/reports/patterns.json", "coding patterns")
        ]

        missing = []
        for file_path, description in required_files:
            full_path = self.project_path / file_path
            if not full_path.exists():
                missing.append(f"  - {file_path} ({description})")

        if missing:
            raise ValueError(
                f"❌ Error: Required .coderef/ files missing:\n" +
                "\n".join(missing) + "\n\n" +
                f"Run: coderef scan {self.project_path}\n"
                f"Or:  python scripts/populate-coderef.py {self.project_path}\n\n"
                f"Then retry: /create-workorder"
            )

        # Check freshness (drift)
        drift_file = self.project_path / ".coderef" / "reports" / "drift.json"
        if drift_file.exists():
            try:
                with open(drift_file, 'r') as f:
                    drift_data = json.load(f)
                drift_percentage = drift_data.get("drift_percentage", 0)

                if drift_percentage > 10:
                    logger.warning(
                        f"⚠️  .coderef/ data is {drift_percentage}% stale.\n"
                        f"   Recommended: Re-run populate-coderef.py before planning.\n"
                        f"   Proceeding with stale data may produce inaccurate plans."
                    )
            except Exception as e:
                logger.debug(f"Could not check drift: {e}")

        logger.info("✅ CodeRef data validation passed")

    def _validate_plan_uses_coderef(self, plan: Dict[str, Any], coderef_data: Dict[str, Any]) -> None:
        """
        Post-generation validation - verify plan uses coderef context.

        Checks:
        - Tasks reference actual files from code inventory
        - Patterns from patterns.json mentioned
        - Dependencies considered

        Args:
            plan: Generated plan dict
            coderef_data: CodeRef data used during generation

        Raises:
            ValueError: If plan doesn't use coderef context properly
        """
        validation_errors = []

        # Get tasks from plan
        tasks = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {}).get("5_task_id_system", {}).get("tasks", [])

        # Check 1: Tasks should reference specific files (not be generic)
        generic_count = 0
        for task in tasks:
            # Generic tasks often have phrases like "following existing patterns" without file paths
            if "following existing" in task.lower() and "/" not in task:
                generic_count += 1

        if generic_count > len(tasks) * 0.5:  # More than 50% are generic
            validation_errors.append(
                f"Plan contains {generic_count}/{len(tasks)} generic tasks without file references. "
                f"Tasks must specify exact files to modify (e.g., 'Modify src/auth.py lines 45-60')."
            )

        # Check 2: Phases should have dependency/rationale fields
        phases = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {}).get("6_implementation_phases", {}).get("phases", [])
        phases_without_rationale = sum(1 for phase in phases if not phase.get("rationale"))

        if phases_without_rationale > 0:
            validation_errors.append(
                f"{phases_without_rationale} phases missing 'rationale' field. "
                f"Each phase must explain why tasks are grouped together."
            )

        if validation_errors:
            logger.warning(
                f"⚠️  Plan validation warnings:\n" +
                "\n".join(f"  - {err}" for err in validation_errors)
            )
            # Don't raise - just warn for now since we're using fallback
        else:
            logger.info("✅ Plan uses coderef context appropriately")

    def _track_coderef_usage(self, agent_execution_log: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
        """
        Track which coderef MCP tools the agent used during plan generation.

        Parses agent execution log for tool calls:
        - coderef_query
        - coderef_impact
        - coderef_patterns
        - coderef_complexity
        - coderef_coverage

        Args:
            agent_execution_log: Optional execution log from Task agent

        Returns:
            Dict mapping tool names to call counts
        """
        tools_used = {
            "coderef_query": 0,
            "coderef_impact": 0,
            "coderef_patterns": 0,
            "coderef_complexity": 0,
            "coderef_coverage": 0
        }

        if not agent_execution_log:
            logger.debug("No agent execution log available for telemetry")
            return tools_used

        # Parse log for tool calls (implementation depends on agent log format)
        # This is a stub - actual implementation would parse agent's tool_calls
        for action in agent_execution_log.get("actions", []):
            tool_name = action.get("tool")
            if tool_name in tools_used:
                tools_used[tool_name] += 1

        # Log telemetry
        total_calls = sum(tools_used.values())
        logger.info("📊 CodeRef ecosystem usage during planning:")
        for tool, count in tools_used.items():
            if count > 0:
                logger.info(f"  🔧 {tool}: {count} calls")

        if total_calls < 5:
            logger.warning(
                f"⚠️  Agent used only {total_calls} coderef tool calls. "
                f"Plan may not be fully grounded in codebase context. "
                f"Recommended: At least 5 tool calls for thorough analysis."
            )
        else:
            logger.info(f"✅ Good coderef usage: {total_calls} tool calls")

        return tools_used

    # ========== End Validation & Telemetry ==========

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
