"""
Type definitions for Resource Sheet module system.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

from typing import TypedDict, Literal, Callable, Any
from dataclasses import dataclass


# Code Characteristics Detection
class CodeCharacteristics(TypedDict, total=False):
    """Detected characteristics of a code element."""

    # Structure
    is_class: bool
    is_function: bool
    is_component: bool
    is_hook: bool

    # Behavior
    makes_network_calls: bool
    manages_state: bool
    handles_auth: bool
    has_error_handling: bool
    has_retry_logic: bool

    # UI
    has_jsx: bool
    has_props: bool
    has_events: bool

    # Storage
    uses_local_storage: bool
    uses_indexed_db: bool
    uses_global_state: bool

    # Data
    has_types: bool
    has_schema: bool
    has_validation: bool

    # Testing
    has_tests: bool
    has_mocks: bool


# Module Trigger Conditions
class ModuleTriggers(TypedDict):
    """Conditions for when a module should be included."""
    required_when: list[str]        # Must include if these characteristics present
    optional_when: list[str]        # May include if these characteristics present
    incompatible_with: list[str]    # Cannot include if these characteristics present


# Template Components
class MarkdownTemplate(TypedDict):
    """Markdown template definition."""
    section_title: str
    content: str
    auto_fill: Callable[[dict], str]
    manual_prompts: list[str]


class SchemaTemplate(TypedDict):
    """JSON Schema template definition."""
    definition: dict
    validation_rules: dict


class JSDocTemplate(TypedDict):
    """JSDoc template definition."""
    patterns: list[str]
    examples: list[str]


class ModuleTemplates(TypedDict):
    """All template types for a module."""
    markdown: MarkdownTemplate
    schema: SchemaTemplate
    jsdoc: JSDocTemplate


# Extraction Configuration
class ModuleExtraction(TypedDict):
    """How to extract data for a module."""
    from_coderef_scan: Callable[[dict], dict]
    from_ast: Callable[[Any], dict]
    from_user: list[dict]
    validation: Callable[[dict], dict]


# Complete Module Definition
@dataclass
class DocumentationModule:
    """
    Complete definition of a documentation module.

    Modules are composable units that generate specific sections
    of documentation based on detected code characteristics.
    """

    # Identity
    id: str
    name: str
    description: str
    category: Literal["universal", "ui", "state", "network", "hooks", "data", "testing"]

    # When to include
    triggers: ModuleTriggers

    # What to generate
    templates: ModuleTemplates

    # How to extract data
    extraction: ModuleExtraction

    # Metadata
    version: str = "1.0.0"
    auto_fill_capable: bool = True


# Module Selection Result
@dataclass
class ModuleSelection:
    """Result of module selection process."""
    selected_modules: list[str]
    characteristics: CodeCharacteristics
    auto_fill_percentage: float
    warnings: list[str]


# Generation Mode
GenerationMode = Literal["reverse-engineer", "template", "refresh"]


# Tool Parameters
class GenerateResourceSheetParams(TypedDict):
    """Parameters for generate_resource_sheet MCP tool."""
    element_name: str
    project_path: str
    element_type: str | None
    mode: GenerationMode
    auto_analyze: bool
    output_path: str | None
    validate_against_code: bool


# Output Metadata
@dataclass
class ResourceSheetMetadata:
    """Metadata for generated resource sheet."""
    element: str
    type: str
    modules: list[str]
    auto_fill_rate: float
    generated: str
    mode: GenerationMode
    version: str = "1.0.0"
