"""
Base UDS Validator

Base class for all document-specific validators in the UDS system.
Extends the original UDSValidator with category-specific validation logic.
"""

from pathlib import Path
from typing import Optional, Union
import re
import yaml
from jsonschema import Draft7Validator, ValidationError as JsonSchemaValidationError

from ..validator import UDSValidator, ValidationResult, ValidationError, ValidationSeverity


class BaseUDSValidator(UDSValidator):
    """
    Base class for all UDS validators

    Provides common functionality:
    - YAML frontmatter extraction
    - JSON Schema validation
    - Base UDS field validation (agent, date, task)
    - Score calculation

    Subclasses should override:
    - schema_name: Name of JSON schema file in schemas/documentation/
    - doc_category: Category name (foundation, workorder, system, etc.)
    - validate_specific(): Category-specific validation logic
    """

    schema_name: Optional[str] = None
    doc_category: str = "unknown"

    def __init__(self, schemas_dir: Optional[Path] = None):
        """
        Initialize validator with schemas directory

        Args:
            schemas_dir: Path to schemas directory (default: package schemas/documentation/)
        """
        if schemas_dir is None:
            # Default to schemas/documentation/ for UDS schemas
            schemas_dir = Path(__file__).parent.parent.parent / "schemas" / "documentation"

        self.schemas_dir = schemas_dir
        self.schema = None

        if self.schema_name:
            self._load_schema()

    def _load_schema(self):
        """Load JSON schema for this validator and resolve $ref"""
        schema_path = self.schemas_dir / self.schema_name
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")

        import json
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        
        # Resolve $ref if schema uses allOf pattern
        if 'allOf' in self.schema:
            self._resolve_allof()
    
    def _resolve_allof(self):
        """Resolve allOf references by merging schemas"""
        if 'allOf' not in self.schema:
            return

        import json
        merged_required = []
        merged_properties = {}

        for item in self.schema['allOf']:
            # Handle $ref
            if '$ref' in item:
                ref_path = item['$ref']
                if ref_path.startswith('./'):
                    # Load referenced schema
                    ref_file = self.schemas_dir / ref_path[2:]
                    if ref_file.exists():
                        with open(ref_file, 'r', encoding='utf-8') as f:
                            ref_schema = json.load(f)

                        # Merge required fields
                        if 'required' in ref_schema:
                            merged_required.extend(ref_schema['required'])

                        # Merge properties
                        if 'properties' in ref_schema:
                            merged_properties.update(ref_schema['properties'])

            # Handle inline schema
            if 'required' in item:
                merged_required.extend(item['required'])

            if 'properties' in item:
                merged_properties.update(item['properties'])

        # Update schema with merged values
        self.schema['required'] = list(set(merged_required))
        self.schema['properties'] = merged_properties
        self.schema['type'] = 'object'

        # Remove allOf to prevent Draft7Validator from trying to resolve $ref
        del self.schema['allOf']

    def validate_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """
        Validate a markdown file against UDS schema

        Args:
            file_path: Path to markdown file

        Returns:
            ValidationResult with errors, warnings, and score
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return ValidationResult(
                valid=False,
                errors=[ValidationError(
                    severity=ValidationSeverity.CRITICAL,
                    message=f"File not found: {file_path}"
                )],
                warnings=[],
                score=0
            )

        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.validate_content(content, file_path)

    def validate_content(self, content: str, file_path: Optional[Path] = None) -> ValidationResult:
        """
        Validate document content against UDS schema

        Args:
            content: Document content (markdown with YAML frontmatter)
            file_path: Optional path for context

        Returns:
            ValidationResult with errors, warnings, and score
        """
        errors = []
        warnings = []

        # Extract YAML frontmatter
        frontmatter = self._extract_frontmatter(content)

        if frontmatter is None:
            return ValidationResult(
                valid=False,
                errors=[ValidationError(
                    severity=ValidationSeverity.CRITICAL,
                    message="Missing or invalid YAML frontmatter (must start with --- and end with ---)"
                )],
                warnings=[],
                score=0
            )

        # Validate against JSON schema if loaded
        if self.schema:
            schema_errors = self._validate_against_schema(frontmatter)
            errors.extend(schema_errors)

        # Validate required sections (POWER framework, etc.)
        section_errors = self._validate_sections(frontmatter, content)
        errors.extend(section_errors)

        # Category-specific validation
        specific_errors, specific_warnings = self.validate_specific(frontmatter, content, file_path)
        errors.extend(specific_errors)
        warnings.extend(specific_warnings)

        # Calculate score
        score = self._calculate_score(errors, warnings)

        # Calculate completeness
        completeness = self._calculate_completeness(frontmatter, content)

        # Valid if no CRITICAL errors
        valid = not any(e.severity == ValidationSeverity.CRITICAL for e in errors)

        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            score=score,
            completeness=completeness
        )

    def _extract_frontmatter(self, content: str) -> Optional[dict]:
        """Extract YAML frontmatter from markdown"""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None

        try:
            frontmatter = yaml.safe_load(match.group(1))
            return frontmatter if isinstance(frontmatter, dict) else None
        except yaml.YAMLError:
            return None

    def _validate_against_schema(self, frontmatter: dict) -> list[ValidationError]:
        """Validate frontmatter against JSON schema"""
        errors = []

        try:
            validator = Draft7Validator(self.schema)
            for error in validator.iter_errors(frontmatter):
                # Convert JSON schema error to ValidationError
                severity = ValidationSeverity.CRITICAL if error.validator in ['required', 'type'] else ValidationSeverity.MAJOR

                errors.append(ValidationError(
                    severity=severity,
                    message=error.message,
                    field='.'.join(str(p) for p in error.path) if error.path else None
                ))
        except Exception as e:
            errors.append(ValidationError(
                severity=ValidationSeverity.CRITICAL,
                message=f"Schema validation error: {str(e)}"
            ))

        return errors

    def _validate_sections(self, frontmatter: dict, content: str) -> list[ValidationError]:
        """
        Validate required sections based on doc_type from schema

        Checks if document contains required markdown sections based on
        doc_type field in frontmatter. Required sections are defined in
        the schema's required_sections field.

        Args:
            frontmatter: Parsed YAML frontmatter containing doc_type
            content: Full document content to search for sections

        Returns:
            List of ValidationError for missing required sections
        """
        errors = []

        # Get doc_type from frontmatter
        doc_type = frontmatter.get('doc_type')
        if not doc_type:
            # No doc_type means no section requirements
            return errors

        # Get required sections from schema
        if not self.schema or 'properties' not in self.schema:
            return errors

        required_sections_prop = self.schema.get('properties', {}).get('required_sections', {})
        if not required_sections_prop:
            return errors

        # Get sections for this specific doc_type
        doc_type_sections = required_sections_prop.get('properties', {}).get(doc_type, {})
        required_sections = doc_type_sections.get('default', [])

        if not required_sections:
            # No required sections defined for this doc_type
            return errors

        # Check each required section
        for section in required_sections:
            # Look for markdown headings: ## Section or # Section
            section_pattern = rf'^#+\s+{re.escape(section)}'
            if not re.search(section_pattern, content, re.MULTILINE | re.IGNORECASE):
                errors.append(ValidationError(
                    severity=ValidationSeverity.MAJOR,
                    message=f"Missing required {doc_type} section: {section}",
                    field="content"
                ))

        return errors

    def _extract_code_blocks(self, content: str) -> list[dict]:
        """
        Extract code blocks from markdown

        Args:
            content: Markdown content

        Returns:
            List of dicts with 'language' and 'code' keys
        """
        code_blocks = []

        # Pattern for fenced code blocks: ```language\ncode\n```
        pattern = r'```(\w+)\n(.*?)\n```'

        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1)
            code = match.group(2)
            code_blocks.append({
                'language': language,
                'code': code
            })

        return code_blocks

    def code_example_validation(self, frontmatter: dict, content: str, project_path: Optional[Path] = None) -> list[ValidationError]:
        """
        Validate code examples against actual code via coderef-context

        For API docs: Verifies endpoint examples match actual endpoints
        For COMPONENTS docs: Verifies component prop examples match actual props

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            project_path: Optional project path for .coderef/index.json lookup

        Returns:
            List of ValidationError for outdated examples (WARNING severity)
        """
        errors = []

        # Only validate for specific doc types
        doc_type = frontmatter.get('doc_type')
        if doc_type not in ['api', 'components']:
            return errors

        # Extract code blocks
        code_blocks = self._extract_code_blocks(content)
        if not code_blocks:
            # No code examples to validate
            return errors

        # For API docs, look for HTTP method + path patterns
        if doc_type == 'api':
            endpoint_pattern = r'(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/{}:-]+)'

            for block in code_blocks:
                code = block['code']

                # Find endpoint references in code examples
                for match in re.finditer(endpoint_pattern, code):
                    method = match.group(1)
                    path = match.group(2)
                    endpoint = f"{method} {path}"

                    # Try to verify endpoint exists
                    # This would call coderef-context in production
                    # For now, we'll add a placeholder that can be enhanced
                    # when coderef-context MCP integration is available

                    # NOTE: This is a simplified version. Full implementation
                    # would call coderef_query MCP tool:
                    # try:
                    #     result = await call_mcp_tool("coderef-context", "coderef_query", {
                    #         "project_path": str(project_path),
                    #         "query_type": "endpoints"
                    #     })
                    #     actual_endpoints = result.get('endpoints', [])
                    #     if endpoint not in actual_endpoints:
                    #         errors.append(ValidationError(
                    #             severity=ValidationSeverity.WARNING,
                    #             message=f"Code example references endpoint '{endpoint}' which may not exist. Verify against actual API.",
                    #             field="content"
                    #         ))
                    # except Exception:
                    #     # Graceful degradation if coderef-context unavailable
                    #     pass

                    pass  # Placeholder for MCP integration

        # For COMPONENTS docs, look for component prop usage
        elif doc_type == 'components':
            # Look for JSX/TSX component usage patterns
            component_pattern = r'<(\w+)\s+([^>]+)>'

            for block in code_blocks:
                if block['language'] not in ['jsx', 'tsx', 'javascript', 'typescript']:
                    continue

                code = block['code']

                # Find component usage
                for match in re.finditer(component_pattern, code):
                    component_name = match.group(1)
                    props_str = match.group(2)

                    # NOTE: Full implementation would call coderef_query
                    # to get actual component props and verify
                    pass  # Placeholder for MCP integration

        return errors

    def validate_specific(self, frontmatter: dict, content: str, file_path: Optional[Path] = None) -> tuple[list[ValidationError], list[str]]:
        """
        Category-specific validation logic

        Override this in subclasses to add custom validation.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content
            file_path: Optional file path for context

        Returns:
            Tuple of (errors, warnings)
        """
        return ([], [])

    def _calculate_score(self, errors: list[ValidationError], warnings: list[str]) -> int:
        """
        Calculate validation score (0-100)

        Scoring:
        - Start with 100
        - Deduct 50 for each CRITICAL error
        - Deduct 20 for each MAJOR error
        - Deduct 10 for each MINOR error
        - Deduct 5 for each WARNING
        - Deduct 2 for each warning message
        """
        score = 100

        for error in errors:
            if error.severity == ValidationSeverity.CRITICAL:
                score -= 50
            elif error.severity == ValidationSeverity.MAJOR:
                score -= 20
            elif error.severity == ValidationSeverity.MINOR:
                score -= 10
            elif error.severity == ValidationSeverity.WARNING:
                score -= 5

        score -= len(warnings) * 2

        return max(0, min(100, score))

    def _calculate_completeness(self, frontmatter: dict, content: str) -> Optional[int]:
        """
        Calculate completeness percentage (0-100) based on section coverage

        Completeness measures how many required sections are present.
        Only calculated if doc_type has required_sections defined.

        Args:
            frontmatter: Parsed YAML frontmatter
            content: Full document content

        Returns:
            Completeness percentage (0-100) or None if not applicable
        """
        # Get doc_type from frontmatter
        doc_type = frontmatter.get('doc_type')
        if not doc_type:
            return None

        # Get required sections from schema
        if not self.schema or 'properties' not in self.schema:
            return None

        required_sections_prop = self.schema.get('properties', {}).get('required_sections', {})
        if not required_sections_prop:
            return None

        # Get sections for this specific doc_type
        doc_type_sections = required_sections_prop.get('properties', {}).get(doc_type, {})
        required_sections = doc_type_sections.get('default', [])

        if not required_sections:
            # No required sections = 100% complete by default
            return 100

        # Count present sections
        present_count = 0
        for section in required_sections:
            # Look for markdown headings: ## Section or # Section
            section_pattern = rf'^#+\s+{re.escape(section)}'
            if re.search(section_pattern, content, re.MULTILINE | re.IGNORECASE):
                present_count += 1

        # Calculate percentage
        completeness = int((present_count / len(required_sections)) * 100)
        return completeness
