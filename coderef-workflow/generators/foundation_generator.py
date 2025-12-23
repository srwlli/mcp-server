"""Foundation documentation generator for 5-doc workflow."""

from pathlib import Path
from typing import List, Dict
from .base_generator import BaseGenerator
import sys

# Add parent directory to path for types import
sys.path.insert(0, str(Path(__file__).parent.parent))
from type_defs import WorkflowStepDict, TemplateDict


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
