"""
Template Engine - Jinja2-based templating with CodeRef extensions

Supports:
- Template inheritance ({% extends 'base.md' %})
- Conditionals ({% if condition %})
- Includes ({% include 'partial.md' %})
- Variable substitution ({{ variable }})
- CodeRef extensions ({% coderef.scan %}, {% git.stats %})
"""

from pathlib import Path
from typing import Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
import re

from .uds import UDSHeader, UDSFooter


class TemplateEngine:
    """
    Template engine with UDS injection and CodeRef extensions

    Features:
    - Jinja2-based template processing
    - UDS header/footer injection
    - Extension system for CodeRef integrations
    - Template inheritance and includes
    """

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize template engine

        Args:
            template_dir: Directory containing template files (optional)
        """
        self.template_dir = template_dir
        self.extensions = {}

        # Set up Jinja2 environment
        if template_dir and template_dir.exists():
            self.env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True
            )
        else:
            # No file loader, templates must be provided as strings
            self.env = Environment(
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True
            )

    def register_extension(self, name: str, extension: Any):
        """
        Register a CodeRef extension

        Args:
            name: Extension name (e.g., 'coderef', 'git', 'workflow')
            extension: Extension object with callable methods

        Example:
            engine.register_extension('git', GitExtension())
            # Now can use: {% git.stats feature_name %}
        """
        self.extensions[name] = extension

    def render(self, template_content: str, context: Dict[str, Any]) -> str:
        """
        Render template with context

        Args:
            template_content: Template string
            context: Variables to pass to template

        Returns:
            str: Rendered template

        Example:
            result = engine.render(
                "# {{ title }}\n{% if show_intro %}Intro{% endif %}",
                {"title": "My Doc", "show_intro": True}
            )
        """
        # Add extensions to context
        context.update(self.extensions)

        # Create template from string
        template = self.env.from_string(template_content)

        # Render template
        return template.render(**context)

    def render_file(self, template_path: str, context: Dict[str, Any]) -> str:
        """
        Render template from file

        Args:
            template_path: Path to template file (relative to template_dir)
            context: Variables to pass to template

        Returns:
            str: Rendered template

        Raises:
            TemplateNotFound: If template file doesn't exist
        """
        if not self.template_dir:
            raise ValueError("template_dir must be set to use render_file()")

        # Add extensions to context
        context.update(self.extensions)

        # Load and render template
        template = self.env.get_template(template_path)
        return template.render(**context)

    def inject_uds(
        self,
        content: str,
        header: UDSHeader,
        footer: Optional[UDSFooter] = None
    ) -> str:
        """
        Inject UDS header and footer into document

        Args:
            content: Document content
            header: UDS header to inject
            footer: Optional UDS footer to inject

        Returns:
            str: Content wrapped with UDS header/footer

        Example:
            doc = engine.inject_uds(
                content="# My Document\n...",
                header=UDSHeader(...),
                footer=UDSFooter(...)
            )
        """
        parts = [header.to_yaml(), content]

        if footer:
            parts.append(footer.to_yaml())

        return "\n".join(parts)

    def render_with_uds(
        self,
        template_content: str,
        context: Dict[str, Any],
        header: UDSHeader,
        footer: Optional[UDSFooter] = None
    ) -> str:
        """
        Render template and inject UDS header/footer in one step

        Args:
            template_content: Template string
            context: Variables to pass to template
            header: UDS header
            footer: Optional UDS footer

        Returns:
            str: Rendered template with UDS header/footer

        Example:
            doc = engine.render_with_uds(
                "# {{ title }}",
                {"title": "Architecture"},
                header=UDSHeader(...),
                footer=UDSFooter(...)
            )
        """
        # Render template
        rendered = self.render(template_content, context)

        # Inject UDS
        return self.inject_uds(rendered, header, footer)


def create_template_engine(
    template_dir: Optional[Path] = None,
    extensions: Optional[Dict[str, Any]] = None
) -> TemplateEngine:
    """
    Convenience function to create template engine with extensions

    Args:
        template_dir: Directory containing template files
        extensions: Dict of {name: extension_object} to register

    Returns:
        TemplateEngine: Configured engine

    Example:
        engine = create_template_engine(
            extensions={
                'git': GitExtension(),
                'coderef': CodeRefContextExtension()
            }
        )
    """
    engine = TemplateEngine(template_dir)

    if extensions:
        for name, ext in extensions.items():
            engine.register_extension(name, ext)

    return engine
