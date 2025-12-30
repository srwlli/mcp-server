"""Foundation documentation generator for 5-doc workflow."""

from pathlib import Path
from typing import List, Dict, Optional
from .base_generator import BaseGenerator
import sys
import os
from datetime import datetime

# Add parent directory to path for types import
sys.path.insert(0, str(Path(__file__).parent.parent))
from type_defs import WorkflowStepDict, TemplateDict

# Papertrail imports (Phase 3 integration)
try:
    from papertrail import (
        UDSHeader,
        UDSFooter,
        TemplateEngine,
        create_template_engine,
        validate_uds,
        calculate_health
    )
    from papertrail.extensions import (
        CodeRefContextExtension,
        GitExtension,
        WorkflowExtension
    )
    PAPERTRAIL_AVAILABLE = True
except ImportError:
    PAPERTRAIL_AVAILABLE = False

# Feature flag (defaults to OFF for safety)
PAPERTRAIL_ENABLED = os.getenv("PAPERTRAIL_ENABLED", "false").lower() == "true"


class FoundationGenerator(BaseGenerator):
    """
    Generator for foundation documentation workflow.

    Creates 5 core documentation files in sequential order:
    1. README.md
    2. ARCHITECTURE.md
    3. API.md
    4. COMPONENTS.md
    5. SCHEMA.md

    Each document references previous documents for context.
    """

    # Define the 5-doc workflow order
    FOUNDATION_TEMPLATES = [
        'readme',
        'architecture',
        'api',
        'components',
        'schema'
    ]

    def __init__(self, templates_dir: Path):
        """
        Initialize foundation generator.

        Args:
            templates_dir: Path to templates directory
        """
        super().__init__(templates_dir)

    def get_workflow_info(self) -> List[WorkflowStepDict]:
        """
        Get information about all templates in the foundation workflow.

        Returns:
            List of dictionaries with template metadata
        """
        workflow = []

        for template_name in self.FOUNDATION_TEMPLATES:
            try:
                info = self.get_template_info(template_name)
                info['template_name'] = template_name
                workflow.append(info)
            except Exception as e:
                workflow.append({
                    'template_name': template_name,
                    'error': str(e)
                })

        return workflow

    def get_generation_plan(self, project_path: str) -> str:
        """
        Generate a human-readable plan for documentation generation.

        Args:
            project_path: Path to project directory

        Returns:
            Formatted string describing the generation plan
        """
        try:
            paths = self.prepare_generation(project_path)
            workflow = self.get_workflow_info()

            plan = f"Foundation Documentation Generation Plan\n"
            plan += f"=" * 50 + "\n\n"
            plan += f"Project: {paths['project_path']}\n"
            plan += f"Output: {paths['output_dir']}\n\n"
            plan += f"Documents to generate ({len(workflow)}):\n\n"

            for i, template in enumerate(workflow, 1):
                if 'error' in template:
                    plan += f"{i}. {template['template_name'].upper()}: ERROR - {template['error']}\n"
                else:
                    save_as = template.get('save_as', f"{template['template_name'].upper()}.md")
                    plan += f"{i}. {save_as}\n"
                    plan += f"   Purpose: {template.get('purpose', 'N/A')}\n"
                    plan += f"   Template: {template['template_name']}\n\n"

            plan += f"\nGeneration Order:\n"
            plan += f"Each document will reference previous documents for context.\n"
            plan += f"Total: {len(workflow)} documents\n"

            return plan

        except Exception as e:
            return f"Error creating generation plan: {str(e)}"

    def get_templates_for_generation(self) -> List[TemplateDict]:
        """
        Get all template contents for the foundation workflow.

        Returns:
            List of dictionaries with template_name and template_content
        """
        templates = []

        for template_name in self.FOUNDATION_TEMPLATES:
            try:
                content = self.read_template(template_name)
                templates.append({
                    'template_name': template_name,
                    'template_content': content,
                    'status': 'success'
                })
            except Exception as e:
                templates.append({
                    'template_name': template_name,
                    'template_content': '',
                    'status': 'error',
                    'error': str(e)
                })

        return templates

    def generate_with_uds(
        self,
        template_name: str,
        context: Dict,
        workorder_id: str,
        feature_id: str,
        version: str = "1.0.0"
    ) -> str:
        """
        Generate document with UDS headers/footers using Papertrail.

        Phase 3: Papertrail integration with feature flag support.

        Args:
            template_name: Name of template (readme, architecture, etc.)
            context: Template variables
            workorder_id: WO-{FEATURE}-{CATEGORY}-###
            feature_id: Feature identifier
            version: Document version (default: 1.0.0)

        Returns:
            Generated document with UDS wrapping
        """
        # Fallback to legacy if Papertrail unavailable or disabled
        if not PAPERTRAIL_ENABLED or not PAPERTRAIL_AVAILABLE:
            return self.generate(template_name, context)

        try:
            # Create UDS header
            header = UDSHeader(
                workorder_id=workorder_id,
                generated_by="coderef-docs v2.0.0",
                feature_id=feature_id,
                timestamp=datetime.utcnow().isoformat() + "Z",
                title=context.get("title", template_name.upper()),
                version=version,
                status="draft"
            )

            # Create UDS footer
            footer = UDSFooter(
                copyright_year=datetime.utcnow().year,
                organization="CodeRef",
                generated_by="coderef-docs v2.0.0",
                workorder_id=workorder_id,
                feature_id=feature_id,
                last_updated=datetime.utcnow().strftime("%Y-%m-%d")
            )

            # Setup template engine with CodeRef extensions
            project_path = context.get("project_path")
            engine = create_template_engine(extensions={
                "git": GitExtension(project_path),
                "workflow": WorkflowExtension(),
                "coderef": CodeRefContextExtension(project_path)
            })

            # Read template
            template_content = self.read_template(template_name)

            # Render with extensions
            rendered = engine.render(template_content, context)

            # Wrap with UDS
            final_doc = engine.inject_uds(rendered, header, footer)

            return final_doc

        except Exception as e:
            # Log error and fallback to legacy
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Papertrail generation failed: {e}, falling back to legacy")
            return self.generate(template_name, context)
