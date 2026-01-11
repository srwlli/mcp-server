"""Generator for universal quickref guides for any application type."""

from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import Paths
from logger_config import logger

# Import base generator
from generators.base_generator import BaseGenerator


class QuickrefGenerator(BaseGenerator):
    """Generate scannable quickref guides for any application type."""

    # App types supported
    APP_TYPES = {
        'cli': 'CLI Tool',
        'web': 'Web Application',
        'api': 'API/Service',
        'desktop': 'Desktop Application',
        'library': 'Library/Framework'
    }

    def __init__(self):
        """Initialize quickref generator."""
        # Don't need templates_dir since we generate dynamically
        self.templates_dir = None

    def get_interview_questions(self, app_type: Optional[str] = None) -> Dict[str, any]:
        """
        Get interview questions for gathering app information.

        Args:
            app_type: Type of application (cli/web/api/desktop/library)

        Returns:
            Dictionary with interview steps and questions
        """
        logger.info("Generating interview questions", extra={'app_type': app_type})

        # Determine app type if not provided
        if app_type and app_type.lower() not in self.APP_TYPES:
            app_type = None

        return {
            "workflow": "interview",
            "total_steps": 9,
            "steps": [
                {
                    "step": 1,
                    "name": "Basic Info",
                    "questions": [
                        "What is the name of your application?",
                        "Provide a brief one-sentence description:",
                        "What type of application is it? (CLI/Web App/API/Desktop/Library)"
                    ]
                },
                {
                    "step": 2,
                    "name": "Core Capabilities",
                    "questions": [
                        "What are the 4-5 main things this application does?",
                        "What problems does it solve for users?"
                    ]
                },
                {
                    "step": 3,
                    "name": "Actions/Commands",
                    "questions": [
                        "What actions or commands are available to users?",
                        "For each action: What does it do? How long does it take?"
                    ],
                    "format": "Table: action | purpose | time/speed"
                },
                {
                    "step": 4,
                    "name": "Features/Tools",
                    "questions": [
                        "What are the main features or tools?",
                        "How should they be grouped? (by category)"
                    ]
                },
                {
                    "step": 5,
                    "name": "Common Workflows",
                    "questions": [
                        "What are 3-5 common use cases?",
                        "Walk me through the steps for each workflow"
                    ],
                    "format": "Numbered step-by-step sequences"
                },
                {
                    "step": 6,
                    "name": "Outputs/Results",
                    "questions": [
                        "Where do outputs go? (files, directories, screens)",
                        "What gets created or modified?"
                    ],
                    "format": "Table: type | location | files"
                },
                {
                    "step": 7,
                    "name": "Key Concepts",
                    "questions": [
                        "Are there 2-4 important patterns or concepts users should know?",
                        "Any unique workflows or design patterns?"
                    ],
                    "optional": True
                },
                {
                    "step": 8,
                    "name": "Generate",
                    "action": "AI generates quickref.md following universal pattern",
                    "output_location": "coderef/quickref.md"
                },
                {
                    "step": 9,
                    "name": "Review",
                    "action": "Show preview and ask: 'Review this quickref. Any changes needed?'"
                }
            ],
            "instructions_for_ai": self._get_ai_instructions(app_type)
        }

    def _get_ai_instructions(self, app_type: Optional[str]) -> str:
        """
        Get instructions for AI on how to conduct the interview.

        Args:
            app_type: Type of application

        Returns:
            Instructions string for AI
        """
        app_specific = ""
        if app_type == 'cli':
            app_specific = "\n- Focus on commands, flags, and terminal workflows"
        elif app_type == 'web':
            app_specific = "\n- Focus on pages, navigation, and user flows"
        elif app_type == 'api':
            app_specific = "\n- Focus on endpoints, HTTP methods, and response formats"
        elif app_type == 'desktop':
            app_specific = "\n- Focus on menu items, shortcuts, and UI workflows"
        elif app_type == 'library':
            app_specific = "\n- Focus on functions, classes, and code examples"

        return f"""
**AI Instructions for Quickref Interview:**

1. Guide the user through all 9 steps sequentially
2. Ask questions in natural language - user answers conversationally
3. Parse responses and build app_info dictionary
4. After gathering all info, generate quickref.md using the universal pattern
5. Show preview and ask for feedback{app_specific}

**Universal Quickref Pattern (8 sections):**

1. **At a Glance**: 4-5 core capabilities (bullet list)
2. **Actions/Commands**: What users can DO (table format)
3. **Features/Tools**: Grouped by category (tables)
4. **Common Workflows**: Step-by-step sequences (numbered lists)
5. **Reference Format**: Copy-paste examples (code blocks)
6. **Output Locations**: Where files go (table)
7. **Key Concepts**: Important patterns (2-4 items)
8. **Summary**: Total counts and links

**Design Principles:**
- Scannable: Tables over paragraphs
- Hierarchical: Category → Feature → Details
- Actionable: Every line = something user can do
- Minimal: Remove all fluff, keep only essentials
- Target length: 150-250 lines

**Save Location:** coderef/quickref.md
        """.strip()

    def generate_quickref_template(self, app_info: Dict[str, any]) -> str:
        """
        Generate quickref markdown from gathered app information.

        Args:
            app_info: Dictionary with app name, type, capabilities, actions, etc.

        Returns:
            Quickref markdown content
        """
        logger.info("Generating quickref", extra={'app_name': app_info.get('name', 'unknown')})

        sections = []

        # Header
        app_name = app_info.get('name', 'Application')
        app_description = app_info.get('description', '')
        sections.append(f"# {app_name} Quick Reference")
        sections.append("")
        if app_description:
            sections.append(f"**{app_description}**")
            sections.append("")
        sections.append("---")
        sections.append("")

        # 1. At a Glance
        sections.append("## At a Glance")
        sections.append("")
        capabilities = app_info.get('capabilities', [])
        if capabilities:
            for cap in capabilities:
                sections.append(f"- {cap}")
        sections.append("")
        sections.append("---")
        sections.append("")

        # 2. Actions/Commands
        actions_header = self._get_actions_header(app_info.get('type', 'cli'))
        sections.append(f"## {actions_header}")
        sections.append("")
        actions = app_info.get('actions', [])
        if actions:
            sections.append("| Action | Purpose | Time/Speed |")
            sections.append("|--------|---------|------------|")
            for action in actions:
                name = action.get('name', '')
                purpose = action.get('purpose', '')
                time = action.get('time', '')
                sections.append(f"| {name} | {purpose} | {time} |")
        sections.append("")
        sections.append("---")
        sections.append("")

        # 3. Features/Tools
        sections.append("## Features/Tools")
        sections.append("")
        features = app_info.get('features', {})
        if features:
            for category, items in features.items():
                sections.append(f"### {category}")
                sections.append("")
                sections.append("| Feature | Description |")
                sections.append("|---------|-------------|")
                for item in items:
                    name = item.get('name', '')
                    desc = item.get('description', '')
                    sections.append(f"| {name} | {desc} |")
                sections.append("")
        sections.append("---")
        sections.append("")

        # 4. Common Workflows
        sections.append("## Common Workflows")
        sections.append("")
        workflows = app_info.get('workflows', [])
        if workflows:
            for workflow in workflows:
                title = workflow.get('title', '')
                steps = workflow.get('steps', [])
                sections.append(f"### {title}")
                sections.append("```")
                for i, step in enumerate(steps, 1):
                    sections.append(f"{i}. {step}")
                sections.append("```")
                sections.append("")
        sections.append("---")
        sections.append("")

        # 5. Reference Format
        sections.append("## Reference Format")
        sections.append("")
        examples = app_info.get('examples', [])
        if examples:
            for example in examples:
                sections.append("```")
                sections.append(example)
                sections.append("```")
                sections.append("")
        sections.append("---")
        sections.append("")

        # 6. Output Locations
        sections.append("## Output Locations")
        sections.append("")
        outputs = app_info.get('outputs', [])
        if outputs:
            sections.append("| Type | Location | Files |")
            sections.append("|------|----------|-------|")
            for output in outputs:
                type_name = output.get('type', '')
                location = output.get('location', '')
                files = output.get('files', '')
                sections.append(f"| {type_name} | {location} | {files} |")
        sections.append("")
        sections.append("---")
        sections.append("")

        # 7. Key Concepts (optional)
        concepts = app_info.get('concepts', [])
        if concepts:
            sections.append("## Key Concepts")
            sections.append("")
            for concept in concepts:
                title = concept.get('title', '')
                description = concept.get('description', '')
                sections.append(f"**{title}**")
                sections.append(f"{description}")
                sections.append("")
            sections.append("---")
            sections.append("")

        # 8. Summary
        sections.append("## Summary")
        sections.append("")
        summary_items = app_info.get('summary', [])
        if summary_items:
            for item in summary_items:
                sections.append(f"- {item}")
        sections.append("")

        # Footer with links
        related_docs = app_info.get('related_docs', [])
        if related_docs:
            sections.append("---")
            sections.append("")
            for doc in related_docs:
                sections.append(f"**{doc}**")
            sections.append("")

        return "\n".join(sections)

    def _get_actions_header(self, app_type: str) -> str:
        """
        Get the appropriate header for actions section based on app type.

        Args:
            app_type: Type of application

        Returns:
            Header string
        """
        headers = {
            'cli': 'Commands',
            'web': 'Pages/Features',
            'api': 'Endpoints',
            'desktop': 'Menu Items/Shortcuts',
            'library': 'Functions/Classes'
        }
        return headers.get(app_type.lower(), 'Actions')

    def save_quickref(self, content: str, project_path: str) -> str:
        """
        Save quickref to project directory.

        Args:
            content: Quickref markdown content
            project_path: Project root directory

        Returns:
            Path to saved quickref file

        Raises:
            ValueError: If project path is invalid
            IOError: If file cannot be written
        """
        # Validate project path
        validated_path = self.validate_project_path(project_path)

        # Create coderef directory if needed
        coderef_dir = validated_path / Paths.CODEREF
        coderef_dir.mkdir(parents=True, exist_ok=True)

        # Save quickref.md
        quickref_path = coderef_dir / "quickref.md"
        try:
            with open(quickref_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # GAP-004 + GAP-005: Validate quickref.md with ValidatorFactory and centralized error handling
            try:
                from papertrail.validators.factory import ValidatorFactory
                from utils.validation_helpers import handle_validation_result

                validator = ValidatorFactory.get_validator(str(quickref_path))
                result = validator.validate_file(str(quickref_path))
                handle_validation_result(result, "quickref.md")
            except ImportError:
                pass  # Papertrail not available
            except ValueError:
                # Critical validation failure - but continue with graceful degradation
                logger.error("quickref.md validation failed critically - continuing with partial data")
            except Exception:
                pass  # Validation error - continue

            logger.info(f"Quickref saved to: {quickref_path}")
            return str(quickref_path)
        except Exception as e:
            raise IOError(f"Error saving quickref to {quickref_path}: {str(e)}")

    def validate_completeness(self, app_info: Dict[str, any]) -> Dict[str, any]:
        """
        Validate that app_info has all required fields.

        Args:
            app_info: App information dictionary

        Returns:
            Validation result with missing fields and warnings
        """
        required_fields = ['name', 'description', 'capabilities', 'actions']
        missing = [field for field in required_fields if not app_info.get(field)]

        recommended_fields = ['workflows', 'outputs', 'examples']
        missing_recommended = [field for field in recommended_fields if not app_info.get(field)]

        return {
            'complete': len(missing) == 0,
            'missing_required': missing,
            'missing_recommended': missing_recommended,
            'warnings': [
                f"Missing required field: {field}" for field in missing
            ] + [
                f"Recommended field missing: {field}" for field in missing_recommended
            ]
        }
