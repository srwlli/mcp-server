"""
Schema Synchronization Tool

Provides utilities for keeping JSON schemas in sync with documentation requirements.
Helps prevent drift between schema definitions and actual validation rules.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SchemaSyncTool:
    """
    Tool for synchronizing and validating JSON schemas

    Purpose:
    - Report on schema consistency across doc types
    - Validate that required_sections are defined for all doc_types
    - Generate schema update suggestions
    - Detect schema drift
    """

    def __init__(self, schemas_dir: Optional[Path] = None):
        """
        Initialize schema sync tool

        Args:
            schemas_dir: Path to schemas/documentation/ directory
        """
        if schemas_dir is None:
            # Default to schemas/documentation/
            schemas_dir = Path(__file__).parent.parent.parent / "schemas" / "documentation"

        self.schemas_dir = Path(schemas_dir)

        if not self.schemas_dir.exists():
            raise FileNotFoundError(f"Schemas directory not found: {self.schemas_dir}")

    def load_schema(self, schema_name: str) -> dict:
        """
        Load a JSON schema file

        Args:
            schema_name: Name of schema file (e.g., 'foundation-doc-frontmatter-schema.json')

        Returns:
            Parsed JSON schema
        """
        schema_path = self.schemas_dir / schema_name

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")

        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_required_sections(self, schema: dict) -> Dict[str, List[str]]:
        """
        Extract required_sections from schema

        Args:
            schema: Parsed JSON schema

        Returns:
            Dict mapping doc_type to list of required sections
        """
        # Handle allOf pattern
        if 'allOf' in schema:
            for item in schema['allOf']:
                if 'properties' in item and 'required_sections' in item['properties']:
                    required_sections_prop = item['properties']['required_sections']
                    break
            else:
                return {}
        else:
            if 'properties' not in schema or 'required_sections' not in schema['properties']:
                return {}

            required_sections_prop = schema['properties']['required_sections']

        # Extract doc_type -> sections mapping
        result = {}
        if 'properties' in required_sections_prop:
            for doc_type, config in required_sections_prop['properties'].items():
                if 'default' in config:
                    result[doc_type] = config['default']

        return result

    def get_doc_types(self, schema: dict) -> List[str]:
        """
        Extract valid doc_type enum values from schema

        Args:
            schema: Parsed JSON schema

        Returns:
            List of valid doc_type values
        """
        # Handle allOf pattern
        if 'allOf' in schema:
            for item in schema['allOf']:
                if 'properties' in item and 'doc_type' in item['properties']:
                    doc_type_prop = item['properties']['doc_type']
                    if 'enum' in doc_type_prop:
                        return doc_type_prop['enum']
            return []
        else:
            if 'properties' not in schema or 'doc_type' not in schema['properties']:
                return []

            doc_type_prop = schema['properties']['doc_type']
            return doc_type_prop.get('enum', [])

    def validate_schema_completeness(self, schema_name: str) -> Tuple[bool, List[str]]:
        """
        Validate that schema has required_sections for all doc_types

        Args:
            schema_name: Name of schema file

        Returns:
            Tuple of (is_complete, list_of_issues)
        """
        schema = self.load_schema(schema_name)
        doc_types = self.get_doc_types(schema)
        required_sections = self.get_required_sections(schema)

        issues = []

        if not doc_types:
            issues.append("Schema does not define doc_type enum")
            return (False, issues)

        if not required_sections:
            issues.append("Schema does not define required_sections")
            return (False, issues)

        # Check each doc_type has required_sections
        for doc_type in doc_types:
            if doc_type not in required_sections:
                issues.append(f"Doc type '{doc_type}' missing required_sections definition")
            elif not required_sections[doc_type]:
                issues.append(f"Doc type '{doc_type}' has empty required_sections array")

        is_complete = len(issues) == 0
        return (is_complete, issues)

    def generate_schema_report(self, schema_name: str) -> str:
        """
        Generate a human-readable report for a schema

        Args:
            schema_name: Name of schema file

        Returns:
            Formatted report string
        """
        try:
            schema = self.load_schema(schema_name)
            doc_types = self.get_doc_types(schema)
            required_sections = self.get_required_sections(schema)
            is_complete, issues = self.validate_schema_completeness(schema_name)

            report_lines = [
                f"# Schema Report: {schema_name}",
                "",
                f"**Complete:** {'Yes' if is_complete else 'No'}",
                f"**Doc Types:** {len(doc_types)}",
                f"**Required Sections Defined:** {len(required_sections)}",
                "",
            ]

            if issues:
                report_lines.extend([
                    "## Issues",
                    ""
                ])
                for issue in issues:
                    report_lines.append(f"- {issue}")
                report_lines.append("")

            if doc_types:
                report_lines.extend([
                    "## Doc Types",
                    ""
                ])
                for doc_type in doc_types:
                    sections = required_sections.get(doc_type, [])
                    section_count = len(sections)
                    status = "✅" if sections else "❌"
                    report_lines.append(f"{status} **{doc_type}** - {section_count} required sections")

                    if sections:
                        for section in sections:
                            report_lines.append(f"  - {section}")

                    report_lines.append("")

            return "\n".join(report_lines)

        except Exception as e:
            return f"# Error generating report\n\n{str(e)}"

    def compare_schemas(self, schema1_name: str, schema2_name: str) -> str:
        """
        Compare required_sections between two schemas

        Args:
            schema1_name: First schema file name
            schema2_name: Second schema file name

        Returns:
            Comparison report
        """
        schema1 = self.load_schema(schema1_name)
        schema2 = self.load_schema(schema2_name)

        sections1 = self.get_required_sections(schema1)
        sections2 = self.get_required_sections(schema2)

        doc_types1 = set(sections1.keys())
        doc_types2 = set(sections2.keys())

        report_lines = [
            f"# Schema Comparison",
            "",
            f"**Schema 1:** {schema1_name}",
            f"**Schema 2:** {schema2_name}",
            "",
        ]

        # Doc types only in schema1
        only_in_1 = doc_types1 - doc_types2
        if only_in_1:
            report_lines.extend([
                f"## Doc types only in {schema1_name}",
                ""
            ])
            for doc_type in sorted(only_in_1):
                report_lines.append(f"- {doc_type}")
            report_lines.append("")

        # Doc types only in schema2
        only_in_2 = doc_types2 - doc_types1
        if only_in_2:
            report_lines.extend([
                f"## Doc types only in {schema2_name}",
                ""
            ])
            for doc_type in sorted(only_in_2):
                report_lines.append(f"- {doc_type}")
            report_lines.append("")

        # Common doc types with different sections
        common = doc_types1 & doc_types2
        if common:
            report_lines.extend([
                "## Common doc types",
                ""
            ])

            for doc_type in sorted(common):
                s1 = set(sections1[doc_type])
                s2 = set(sections2[doc_type])

                if s1 == s2:
                    report_lines.append(f"✅ **{doc_type}** - Identical ({len(s1)} sections)")
                else:
                    report_lines.append(f"❌ **{doc_type}** - Different sections")

                    only_s1 = s1 - s2
                    if only_s1:
                        report_lines.append(f"  Only in {schema1_name}:")
                        for section in sorted(only_s1):
                            report_lines.append(f"    - {section}")

                    only_s2 = s2 - s1
                    if only_s2:
                        report_lines.append(f"  Only in {schema2_name}:")
                        for section in sorted(only_s2):
                            report_lines.append(f"    - {section}")

                report_lines.append("")

        return "\n".join(report_lines)

    def list_all_schemas(self) -> List[str]:
        """
        List all JSON schemas in schemas directory

        Returns:
            List of schema file names
        """
        return [
            f.name
            for f in self.schemas_dir.glob("*.json")
            if f.is_file()
        ]

    def validate_all_schemas(self) -> str:
        """
        Validate all schemas in directory

        Returns:
            Summary report of all schemas
        """
        schemas = self.list_all_schemas()

        report_lines = [
            "# All Schemas Validation Report",
            "",
            f"**Total Schemas:** {len(schemas)}",
            ""
        ]

        complete_count = 0
        incomplete_schemas = []

        for schema_name in sorted(schemas):
            try:
                is_complete, issues = self.validate_schema_completeness(schema_name)

                if is_complete:
                    complete_count += 1
                    report_lines.append(f"✅ {schema_name}")
                else:
                    incomplete_schemas.append((schema_name, issues))
                    issue_count = len(issues)
                    report_lines.append(f"❌ {schema_name} ({issue_count} issues)")

            except Exception as e:
                report_lines.append(f"⚠️ {schema_name} (error: {str(e)})")

        report_lines.extend([
            "",
            f"**Complete:** {complete_count}/{len(schemas)}",
            ""
        ])

        if incomplete_schemas:
            report_lines.extend([
                "## Issues by Schema",
                ""
            ])

            for schema_name, issues in incomplete_schemas:
                report_lines.append(f"### {schema_name}")
                report_lines.append("")
                for issue in issues:
                    report_lines.append(f"- {issue}")
                report_lines.append("")

        return "\n".join(report_lines)
