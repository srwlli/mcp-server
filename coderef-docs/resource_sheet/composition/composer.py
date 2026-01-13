"""
Document Composer - Assembles Modules into Final Documentation.

WO-RESOURCE-SHEET-MCP-TOOL-001

Composes selected modules into markdown, JSON schema, and JSDoc formats.
"""

from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

from ..types import DocumentationModule, CodeCharacteristics, ResourceSheetMetadata, GenerationMode
from utils.timestamp import get_date


class DocumentComposer:
    """
    Composes documentation modules into final output formats.

    Handles markdown assembly, schema generation, and JSDoc creation.
    """

    def compose_markdown(
        self,
        element_name: str,
        modules: List[DocumentationModule],
        extracted_data: Dict[str, Any],
        characteristics: CodeCharacteristics,
        mode: GenerationMode = "reverse-engineer",
    ) -> str:
        """
        Compose markdown documentation from modules.

        Args:
            element_name: Name of element being documented
            modules: Selected modules to include
            extracted_data: Data extracted from code analysis
            characteristics: Detected characteristics
            mode: Generation mode

        Returns:
            Complete markdown document
        """
        # Calculate auto-fill rate
        auto_fill_count = sum(1 for m in modules if m.auto_fill_capable)
        auto_fill_rate = (auto_fill_count / len(modules) * 100) if modules else 0

        # Build frontmatter
        frontmatter = self._build_frontmatter(
            element_name,
            modules,
            auto_fill_rate,
            mode,
        )

        # Build main content
        content_sections = []

        # Title
        content_sections.append(f"# {element_name} - Authoritative Documentation\n")

        # Characteristics summary
        if characteristics:
            content_sections.append(self._format_characteristics(characteristics))

        # Module sections
        for i, module in enumerate(modules, 1):
            section = self._compose_module_section(module, extracted_data, i)
            content_sections.append(section)

        # Combine all parts
        document = frontmatter + "\n\n" + "\n\n".join(content_sections)

        return document

    def compose_schema(
        self,
        element_name: str,
        modules: List[DocumentationModule],
        extracted_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compose JSON schema from modules.

        Args:
            element_name: Element name
            modules: Selected modules
            extracted_data: Extracted data

        Returns:
            JSON Schema object
        """
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": element_name,
            "type": "object",
            "properties": {},
        }

        # Merge module schemas
        for module in modules:
            module_schema = module.templates["schema"]["definition"]
            schema["properties"].update(module_schema)

        return schema

    def compose_jsdoc(
        self,
        element_name: str,
        modules: List[DocumentationModule],
        extracted_data: Dict[str, Any],
    ) -> List[str]:
        """
        Compose JSDoc comments from modules.

        Args:
            element_name: Element name
            modules: Selected modules
            extracted_data: Extracted data

        Returns:
            List of JSDoc comment lines
        """
        jsdoc_lines = [
            "/**",
            f" * {element_name}",
            f" * @see coderef/reference-sheets/{element_name.lower()}/{element_name.lower()}.md",
            " *",
        ]

        # Collect patterns from all modules
        for module in modules:
            patterns = module.templates["jsdoc"]["patterns"]
            for pattern in patterns:
                # Simple template substitution for Phase 1
                filled = pattern.replace("{{element_name}}", element_name)
                jsdoc_lines.append(f" * {filled}")

        jsdoc_lines.append(" */")

        return jsdoc_lines

    def _build_frontmatter(
        self,
        element: str,
        modules: List[DocumentationModule],
        auto_fill_rate: float,
        mode: GenerationMode,
    ) -> str:
        """Build YAML frontmatter for markdown document."""
        module_ids = [m.id for m in modules]
        module_list = ", ".join(module_ids)

        frontmatter = f"""---
element: {element}
type: Auto-detected
modules: [{module_list}]
auto_fill_rate: {auto_fill_rate:.1f}%
generated: {get_date()}
mode: {mode}
version: 1.0.0
---"""
        return frontmatter

    def _format_characteristics(self, characteristics: CodeCharacteristics) -> str:
        """Format characteristics as markdown section."""
        true_chars = [k.replace("_", " ").title() for k, v in characteristics.items() if v]

        if not true_chars:
            return ""

        content = "## Detected Characteristics\n\n"
        for char in true_chars:
            content += f"- ✓ {char}\n"

        return content

    def _compose_module_section(
        self,
        module: DocumentationModule,
        extracted_data: Dict[str, Any],
        section_number: int,
    ) -> str:
        """Compose a single module's section."""
        # Get module-specific data
        module_data = extracted_data.get(module.id, {})

        # Try auto-fill if capable
        content = ""
        if module.auto_fill_capable and module.templates["markdown"]["auto_fill"]:
            try:
                content = module.templates["markdown"]["auto_fill"](module_data)
            except Exception as e:
                content = f"⚠️ Auto-fill failed: {e}\n\n"

        # Add section title
        section = module.templates["markdown"]["section_title"]

        # If no auto-fill content, use template
        if not content:
            content = module.templates["markdown"]["content"]

        # Combine
        full_section = f"{section}\n\n{content}"

        # Add manual prompts if present
        prompts = module.templates["markdown"]["manual_prompts"]
        if prompts:
            full_section += "\n\n**Manual Review Required:**\n"
            for prompt in prompts:
                full_section += f"- {prompt}\n"

        return full_section

    def save_outputs(
        self,
        element_name: str,
        markdown: str,
        schema: Dict[str, Any],
        jsdoc: List[str],
        output_path: str,
        filename: str | None = None,
    ) -> Dict[str, str]:
        """
        Save all output formats to files.

        Args:
            element_name: Element name
            markdown: Markdown content
            schema: JSON schema
            jsdoc: JSDoc lines
            output_path: Output directory
            filename: Optional filename override (default: uses element_name.lower())

        Returns:
            Paths to created files
        """
        import json

        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Use provided filename or generate from element_name
        if filename:
            # Use provided filename (e.g., 'Auth-Service-RESOURCE-SHEET.md')
            file_base = filename.replace('-RESOURCE-SHEET.md', '')
        else:
            # Legacy: Use lowercase element name for all files
            file_base = element_name.lower()

        # Markdown - use full filename if provided
        if filename:
            md_path = output_dir / filename
        else:
            md_path = output_dir / f"{file_base}.md"
        md_path.write_text(markdown, encoding="utf-8")

        # Schema (save in same directory as markdown)
        schema_path = output_dir / f"{file_base}.schema.json"
        schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")

        # JSDoc (as snippet)
        jsdoc_path = output_dir / f"{file_base}.jsdoc.txt"
        jsdoc_path.write_text("\n".join(jsdoc), encoding="utf-8")

        return {
            "markdown": str(md_path),
            "schema": str(schema_path),
            "jsdoc": str(jsdoc_path),
        }
