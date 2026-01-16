"""
Resource Sheet Generator - Main Orchestration.

WO-RESOURCE-SHEET-MCP-TOOL-001

Orchestrates the complete resource sheet generation workflow:
1. Analyze code
2. Detect characteristics
3. Select modules
4. Extract data
5. Compose documentation
"""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from resource_sheet.types import GenerationMode, CodeCharacteristics, ResourceSheetMetadata
from resource_sheet.detection import CodeAnalyzer, CharacteristicsDetector
from resource_sheet.composition import DocumentComposer
from resource_sheet.modules import get_registry

# Import universal modules to register them
from resource_sheet.modules.universal import (
    architecture_module,
    integration_module,
    testing_module,
    performance_module,
)

# Import conditional modules
from resource_sheet.modules.conditional import (
    props_module,
    events_module,
    accessibility_module,
    state_module,
    lifecycle_module,
    endpoints_module,
    auth_module,
    retry_module,
    error_handling_module,
    hook_signature_module,
    hook_side_effects_module,
)


def convert_subject_to_filename(subject: str) -> str:
    """
    Convert subject field to proper resource sheet filename.

    Converts 'Auth Service' or 'AuthService' to 'Auth-Service-RESOURCE-SHEET.md'
    following PascalCase-with-hyphens format.

    Args:
        subject: Subject string (e.g., 'Auth Service', 'AuthService', 'Widget System')

    Returns:
        Properly formatted filename (e.g., 'Auth-Service-RESOURCE-SHEET.md')

    Examples:
        >>> convert_subject_to_filename('Auth Service')
        'Auth-Service-RESOURCE-SHEET.md'
        >>> convert_subject_to_filename('AuthService')
        'Auth-Service-RESOURCE-SHEET.md'
        >>> convert_subject_to_filename('Widget System')
        'Widget-System-RESOURCE-SHEET.md'
        >>> convert_subject_to_filename('File API Route')
        'File-Api-Route-RESOURCE-SHEET.md'
    """
    import re

    # Handle empty/invalid input
    if not subject or not subject.strip():
        raise ValueError("Subject cannot be empty")

    subject = subject.strip()

    # If subject has spaces, split by spaces and capitalize each word
    if ' ' in subject:
        words = subject.split()
        # Capitalize first letter of each word, lowercase the rest
        pascal_words = [word.capitalize() for word in words]
        component_name = '-'.join(pascal_words)
    else:
        # Handle camelCase or PascalCase: insert hyphens before capital letters
        # e.g., 'AuthService' -> 'Auth-Service', 'FileAPIRoute' -> 'File-API-Route'

        # Insert hyphen before uppercase letters that follow lowercase or are followed by lowercase
        result = re.sub(r'([a-z])([A-Z])', r'\1-\2', subject)  # lowercase followed by uppercase
        result = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', result)  # multiple caps followed by cap+lowercase

        # Ensure first letter is capitalized
        if result and result[0].islower():
            result = result[0].upper() + result[1:]

        component_name = result

    return f"{component_name}-RESOURCE-SHEET.md"


class ResourceSheetGenerator:
    """
    Main generator for resource sheet documentation.

    Implements the 3-step workflow:
    1. WHAT IS THIS? - Analyze code and detect characteristics
    2. PICK VARIABLES - Select appropriate modules
    3. ASSEMBLE - Compose final documentation
    """

    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.detector = CharacteristicsDetector()
        self.composer = DocumentComposer()
        self.registry = get_registry()

        # Register universal modules
        self._register_modules()

    def _register_modules(self):
        """Register all available modules with the registry."""
        # Universal modules (always included)
        self.registry.register(architecture_module)
        self.registry.register(integration_module)
        self.registry.register(testing_module)
        self.registry.register(performance_module)

        # Conditional modules (triggered by code characteristics)
        # UI modules
        self.registry.register(props_module)
        self.registry.register(events_module)
        self.registry.register(accessibility_module)

        # State modules
        self.registry.register(state_module)
        self.registry.register(lifecycle_module)

        # Network modules
        self.registry.register(endpoints_module)
        self.registry.register(auth_module)
        self.registry.register(retry_module)
        self.registry.register(error_handling_module)

        # Hook modules
        self.registry.register(hook_signature_module)
        self.registry.register(hook_side_effects_module)

    def calculate_complexity_stats(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate complexity statistics from ElementData with complexity field.

        WO-DOCS-SCANNER-INTEGRATION-001: IMPL-003
        Reads ElementData.complexity field (from Phase 1 scanner task_5) and calculates:
        - Average complexity
        - Max complexity
        - Hotspot elements (complexity > 10)

        Args:
            elements: List of ElementData dicts with optional 'complexity' field

        Returns:
            Dict with avg, max, hotspots, and refactoring recommendations

        Graceful degradation: Returns sensible defaults if complexity field missing.
        """
        # Extract complexity values (filter out None/0)
        complexities = [e.get('complexity', 0) for e in elements if e.get('complexity')]

        if not complexities:
            # No complexity data - return defaults
            return {
                'avg': 0,
                'max': 0,
                'hotspots': [],
                'total_elements': len(elements),
                'elements_with_complexity': 0,
                'has_complexity_data': False
            }

        # Calculate statistics
        avg_complexity = sum(complexities) / len(complexities)
        max_complexity = max(complexities)

        # Identify hotspots (complexity > 10)
        hotspots = [
            {
                'name': e['name'],
                'complexity': e.get('complexity'),
                'file': e.get('file', 'unknown'),
                'line': e.get('line', 0),
                'recommendation': self._get_complexity_recommendation(e.get('complexity', 0))
            }
            for e in elements
            if e.get('complexity', 0) > 10
        ]

        # Sort hotspots by complexity (highest first)
        hotspots.sort(key=lambda x: x['complexity'], reverse=True)

        return {
            'avg': avg_complexity,
            'max': max_complexity,
            'hotspots': hotspots,
            'total_elements': len(elements),
            'elements_with_complexity': len(complexities),
            'has_complexity_data': True
        }

    def _get_complexity_recommendation(self, complexity: int) -> str:
        """
        Get refactoring recommendation based on complexity threshold.

        Thresholds:
        - 1-10: Acceptable
        - 11-15: MEDIUM priority - Consider simplifying
        - 16+: HIGH priority - Refactor into smaller functions
        """
        if complexity <= 10:
            return "Acceptable complexity"
        elif complexity <= 15:
            return "MEDIUM - Consider simplifying control flow"
        else:
            return "HIGH - Refactor into smaller functions"

    async def generate(
        self,
        element_name: str,
        project_path: str,
        element_type: str | None = None,
        mode: GenerationMode = "reverse-engineer",
        auto_analyze: bool = True,
        output_path: str | None = None,
        validate_against_code: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate resource sheet documentation for a code element.

        Args:
            element_name: Name of element to document (will be converted to PascalCase-with-hyphens)
            project_path: Path to project root
            element_type: Optional manual element type override
            mode: Generation mode (reverse-engineer, template, refresh)
            auto_analyze: Use coderef_scan for auto-fill (default: True)
            output_path: Where to save output (default: coderef/resources-sheets/)
            validate_against_code: Compare docs to code (default: True)

        Returns:
            Generation result with paths, metadata, and warnings
        """
        # Generate proper filename from element_name (subject field)
        filename = convert_subject_to_filename(element_name)

        # Set default output directory to coderef/resources-sheets/
        if output_path is None:
            output_path = f"{project_path}/coderef/resources-sheets"

        # Step 1: WHAT IS THIS? - Analyze and detect
        analysis = await self._analyze_element(
            element_name, project_path, auto_analyze, element_type
        )

        # Step 2: PICK VARIABLES - Select modules
        modules = self._select_modules(analysis["characteristics"])

        # Step 3: ASSEMBLE - Compose documentation
        outputs = await self._compose_documentation(
            element_name,
            modules,
            analysis,
            mode,
            output_path,
            filename,
        )

        # Build result
        result = {
            "element_name": element_name,
            "generated_filename": filename,
            "output_directory": output_path,
            "mode": mode,
            "characteristics": analysis["characteristics"],
            "selected_modules": [m.id for m in modules],
            "module_count": len(modules),
            "auto_fill_rate": self._calculate_auto_fill_rate(modules),
            "outputs": outputs,
            "warnings": analysis.get("warnings", []),
            "generated_at": datetime.now().isoformat(),
            "validation_note": "Generated files should be validated using papertrail's ResourceSheetValidator MCP tool",
        }

        return result

    async def _analyze_element(
        self,
        element_name: str,
        project_path: str,
        auto_analyze: bool,
        element_type: str | None,
    ) -> Dict[str, Any]:
        """Step 1: Analyze code and detect characteristics."""
        if auto_analyze:
            # Use code analysis
            analysis = await self.analyzer.analyze_element(
                element_name, project_path, use_coderef_scan=False
            )
        else:
            # Template mode - no analysis
            analysis = {
                "element_name": element_name,
                "scan_data": {},
                "characteristics": {},
                "analysis_method": "manual",
            }

        return analysis

    def _select_modules(self, characteristics: CodeCharacteristics) -> List:
        """Step 2: Select appropriate modules based on characteristics."""
        # For Phase 1, always include universal modules
        # Future: Use registry.select_modules(characteristics)

        modules = [
            architecture_module,
            integration_module,
            testing_module,
            performance_module,
        ]

        return modules

    async def _compose_documentation(
        self,
        element_name: str,
        modules: List,
        analysis: Dict[str, Any],
        mode: GenerationMode,
        output_path: str,
        filename: str,
    ) -> Dict[str, str]:
        """Step 3: Compose and save documentation in all formats."""
        # Extract module-specific data
        extracted_data = self._extract_module_data(modules, analysis["scan_data"])

        # Compose markdown
        markdown = self.composer.compose_markdown(
            element_name,
            modules,
            extracted_data,
            analysis["characteristics"],
            mode,
        )

        # Compose schema
        schema = self.composer.compose_schema(
            element_name,
            modules,
            extracted_data,
        )

        # Compose JSDoc
        jsdoc = self.composer.compose_jsdoc(
            element_name,
            modules,
            extracted_data,
        )

        # Save all outputs using the proper filename
        output_paths = self.composer.save_outputs(
            element_name,
            markdown,
            schema,
            jsdoc,
            output_path,
            filename,
        )

        return output_paths

    def _extract_module_data(self, modules: List, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract module-specific data from scan results."""
        extracted = {}

        for module in modules:
            try:
                module_data = module.extraction["from_coderef_scan"](scan_data)
                extracted[module.id] = module_data
            except Exception as e:
                # Graceful failure - module gets empty data
                extracted[module.id] = {}

        return extracted

    def _calculate_auto_fill_rate(self, modules: List) -> float:
        """Calculate percentage of modules that can auto-fill."""
        if not modules:
            return 0.0

        auto_fill_count = sum(1 for m in modules if m.auto_fill_capable)
        return (auto_fill_count / len(modules)) * 100
