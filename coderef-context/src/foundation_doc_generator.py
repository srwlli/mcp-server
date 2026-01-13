"""
Foundation Documentation Generator

Generates foundation docs (API.md, SCHEMA.md, COMPONENTS.md, README.md) from .coderef/index.json.
Simple list-based templates (not full POWER framework).
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class FoundationDocGenerator:
    """Generates foundation documentation from CodeRef index"""

    def __init__(self, project_path: str, index_data: List[Dict[str, Any]]):
        self.project_path = Path(project_path)
        self.index_data = index_data
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _group_by_type(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group elements by type"""
        grouped = {}
        for element in self.index_data:
            elem_type = element.get("type", "unknown")
            if elem_type not in grouped:
                grouped[elem_type] = []
            grouped[elem_type].append(element)
        return grouped

    def _group_by_file(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group elements by file"""
        grouped = {}
        for element in self.index_data:
            file_path = element.get("file", "unknown")
            if file_path not in grouped:
                grouped[file_path] = []
            grouped[file_path].append(element)
        return grouped

    def generate_api_md(self) -> str:
        """Generate API.md with all functions/methods"""
        grouped = self._group_by_type()
        functions = grouped.get("function", [])
        methods = grouped.get("method", [])

        lines = [
            "# API Reference",
            "",
            f"**Generated:** {self.timestamp}",
            f"**Total Functions:** {len(functions)}",
            f"**Total Methods:** {len(methods)}",
            "",
            "---",
            ""
        ]

        if functions:
            lines.extend([
                "## Functions",
                ""
            ])
            for func in sorted(functions, key=lambda x: x.get("name", "")):
                name = func.get("name")
                file = func.get("file")
                line = func.get("line")
                params = func.get("parameters", [])
                is_async = func.get("isAsync", False)

                async_prefix = "async " if is_async else ""
                params_str = ", ".join(params) if params else ""

                lines.append(f"### {async_prefix}`{name}({params_str})`")
                lines.append(f"**Location:** `{file}:{line}`")

                if func.get("docstring"):
                    lines.append(f"**Description:** {func.get('docstring').split('\\n')[0]}")

                lines.append("")

        if methods:
            lines.extend([
                "## Methods",
                ""
            ])
            # Group methods by class (if available in parent context)
            by_file = {}
            for method in methods:
                file_key = method.get("file", "unknown")
                if file_key not in by_file:
                    by_file[file_key] = []
                by_file[file_key].append(method)

            for file_path in sorted(by_file.keys()):
                lines.append(f"### From `{file_path}`")
                lines.append("")
                for method in sorted(by_file[file_path], key=lambda x: x.get("name", "")):
                    name = method.get("name")
                    line_num = method.get("line")
                    params = method.get("parameters", [])
                    is_async = method.get("isAsync", False)

                    async_prefix = "async " if is_async else ""
                    params_str = ", ".join(params) if params else ""

                    lines.append(f"- **{async_prefix}`{name}({params_str})`** (line {line_num})")

                lines.append("")

        return "\\n".join(lines)

    def generate_schema_md(self) -> str:
        """Generate SCHEMA.md with all classes/interfaces"""
        grouped = self._group_by_type()
        classes = grouped.get("class", [])

        lines = [
            "# Schema Reference",
            "",
            f"**Generated:** {self.timestamp}",
            f"**Total Classes:** {len(classes)}",
            "",
            "---",
            ""
        ]

        if classes:
            lines.extend([
                "## Classes",
                ""
            ])
            for cls in sorted(classes, key=lambda x: x.get("name", "")):
                name = cls.get("name")
                file = cls.get("file")
                line = cls.get("line")
                methods = cls.get("methods", [])
                bases = cls.get("bases", [])

                lines.append(f"### `{name}`")
                lines.append(f"**Location:** `{file}:{line}`")

                if bases:
                    lines.append(f"**Extends:** {', '.join(bases)}")

                if cls.get("docstring"):
                    lines.append(f"**Description:** {cls.get('docstring').split('\\n')[0]}")

                if methods:
                    lines.append(f"**Methods:** {len(methods)}")
                    lines.append("")
                    for method in methods:
                        method_name = method.get("name")
                        method_line = method.get("line")
                        method_params = method.get("parameters", [])
                        method_async = method.get("isAsync", False)

                        async_prefix = "async " if method_async else ""
                        params_str = ", ".join(method_params) if method_params else ""

                        lines.append(f"  - {async_prefix}`{method_name}({params_str})` (line {method_line})")

                lines.append("")

        return "\\n".join(lines)

    def generate_components_md(self) -> str:
        """Generate COMPONENTS.md with all components/hooks"""
        grouped = self._group_by_type()
        components = grouped.get("component", [])
        hooks = grouped.get("hook", [])

        lines = [
            "# Components Reference",
            "",
            f"**Generated:** {self.timestamp}",
            f"**Total Components:** {len(components)}",
            f"**Total Hooks:** {len(hooks)}",
            "",
            "---",
            ""
        ]

        if components:
            lines.extend([
                "## Components",
                ""
            ])
            for comp in sorted(components, key=lambda x: x.get("name", "")):
                name = comp.get("name")
                file = comp.get("file")
                line = comp.get("line")
                params = comp.get("parameters", [])

                lines.append(f"### `<{name} />`")
                lines.append(f"**Location:** `{file}:{line}`")

                if params:
                    lines.append(f"**Props:** {', '.join(params)}")

                lines.append("")

        if hooks:
            lines.extend([
                "## Hooks",
                ""
            ])
            for hook in sorted(hooks, key=lambda x: x.get("name", "")):
                name = hook.get("name")
                file = hook.get("file")
                line = hook.get("line")

                lines.append(f"### `{name}()`")
                lines.append(f"**Location:** `{file}:{line}`")
                lines.append("")

        return "\\n".join(lines)

    def generate_readme_md(self) -> str:
        """Generate simple README.md overview"""
        grouped = self._group_by_type()
        by_file = self._group_by_file()

        type_counts = {t: len(elems) for t, elems in grouped.items()}
        total_elements = len(self.index_data)
        total_files = len(by_file)

        lines = [
            f"# {self.project_path.name}",
            "",
            f"**Generated:** {self.timestamp}",
            "",
            "## Project Overview",
            "",
            f"- **Total Elements:** {total_elements}",
            f"- **Total Files:** {total_files}",
            "",
            "## Element Distribution",
            ""
        ]

        for elem_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            lines.append(f"- **{elem_type.capitalize()}:** {count}")

        lines.extend([
            "",
            "## Documentation",
            "",
            "- [API Reference](API.md) - All functions and methods",
            "- [Schema Reference](SCHEMA.md) - All classes and interfaces",
            "- [Components Reference](COMPONENTS.md) - All components and hooks",
            ""
        ])

        return "\\n".join(lines)

    def generate_all(self, doc_types: List[str], output_dir: Path) -> Dict[str, Any]:
        """
        Generate all requested docs and write to output directory

        Args:
            doc_types: List of doc types to generate (api, schema, components, readme)
            output_dir: Output directory path

        Returns:
            {"success": bool, "generated_files": List[str], "errors": List[str]}
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []
        errors = []

        doc_generators = {
            "api": ("API.md", self.generate_api_md),
            "schema": ("SCHEMA.md", self.generate_schema_md),
            "components": ("COMPONENTS.md", self.generate_components_md),
            "readme": ("README.md", self.generate_readme_md),
        }

        for doc_type in doc_types:
            if doc_type not in doc_generators:
                errors.append(f"Unknown doc type: {doc_type}")
                continue

            filename, generator_func = doc_generators[doc_type]
            output_path = output_dir / filename

            try:
                content = generator_func()
                output_path.write_text(content, encoding='utf-8')
                generated_files.append(str(output_path))
            except Exception as e:
                errors.append(f"Error generating {filename}: {str(e)}")

        return {
            "success": len(errors) == 0,
            "generated_files": generated_files,
            "errors": errors
        }


def generate_foundation_docs(
    project_path: str,
    index_data: List[Dict[str, Any]],
    doc_types: List[str],
    output_dir: str
) -> Dict[str, Any]:
    """
    Main entry point for foundation doc generation

    Args:
        project_path: Project root path
        index_data: Array of elements from index.json
        doc_types: Doc types to generate (api, schema, components, readme)
        output_dir: Output directory for generated docs

    Returns:
        {"success": bool, "generated_files": List[str], "errors": List[str]}
    """
    generator = FoundationDocGenerator(project_path, index_data)
    return generator.generate_all(doc_types, Path(output_dir))
