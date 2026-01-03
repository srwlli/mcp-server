"""
Module Registry - Tool 2 Checklist Integration

This module provides the ModuleRegistry class that maps element types to their
conditional module checklists from Tool 2 (resource-sheet-catalog.md).

Workorder: WO-RESOURCE-SHEET-CONSOLIDATION-001
Task: PORT-002
Author: Papertrail Agent
Date: 2026-01-03
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class ModuleRegistry:
    """Registry for element-specific checklists and conditional modules.

    This class provides access to the 20 element types' checklists from Tool 2,
    integrated into the template generation pipeline as conditional modules.
    """

    def __init__(self, mapping_file: Optional[Path] = None):
        """Initialize module registry.

        Args:
            mapping_file: Path to element-type-mapping.json
                         Defaults to mapping/element-type-mapping.json
        """
        if mapping_file is None:
            current_dir = Path(__file__).parent
            mapping_file = current_dir / "mapping" / "element-type-mapping.json"

        self.mapping = self._load_mapping(mapping_file)
        self.element_types = {e["element_type"]: e for e in self.mapping.get("element_types", [])}

    def _load_mapping(self, mapping_file: Path) -> Dict:
        """Load element type mapping from JSON file."""
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_checklist(self, element_type: str) -> List[str]:
        """Get checklist items for element type.

        Args:
            element_type: Element type name (e.g., "top_level_widgets", "custom_hooks")

        Returns:
            List of checklist items, or empty list if element type not found

        Example:
            >>> registry = ModuleRegistry()
            >>> checklist = registry.get_checklist("custom_hooks")
            >>> print(checklist)
            [
                "Side effects - Network, storage, subscriptions, timers",
                "Cleanup guarantees - What happens on unmount",
                ...
            ]
        """
        element_def = self.element_types.get(element_type)
        if not element_def:
            return []

        return element_def.get("checklist_items", [])

    def get_conditional_modules(self, element_type: str) -> List[str]:
        """Get conditional modules for element type.

        Args:
            element_type: Element type name

        Returns:
            List of conditional module names (e.g., ["ui/composition", "ui/events"])

        Example:
            >>> registry = ModuleRegistry()
            >>> modules = registry.get_conditional_modules("top_level_widgets")
            >>> print(modules)
            ["ui/composition", "ui/events", "ui/accessibility"]
        """
        element_def = self.element_types.get(element_type)
        if not element_def:
            return []

        return element_def.get("conditional_modules", [])

    def get_additional_sections(self, element_type: str) -> List[str]:
        """Get additional sections required for element type.

        Args:
            element_type: Element type name

        Returns:
            List of additional section names beyond the base 13 sections

        Example:
            >>> registry = ModuleRegistry()
            >>> sections = registry.get_additional_sections("stateful_containers")
            >>> print(sections)
            ["state_authority_table", "lifecycle_diagram", "persistence_contract", "event_subscriptions"]
        """
        element_def = self.element_types.get(element_type)
        if not element_def:
            return []

        return element_def.get("additional_sections", [])

    def get_required_sections(self, element_type: str) -> List[str]:
        """Get required sections for element type.

        Args:
            element_type: Element type name

        Returns:
            List of required section titles specific to this element type

        Example:
            >>> registry = ModuleRegistry()
            >>> sections = registry.get_required_sections("api_client")
            >>> print(sections)
            ["Endpoint Reference", "Auth Flow Diagram", "Error Taxonomy", ...]
        """
        element_def = self.element_types.get(element_type)
        if not element_def:
            return []

        return element_def.get("required_sections", [])

    def get_element_info(self, element_type: str) -> Optional[Dict]:
        """Get complete element definition.

        Args:
            element_type: Element type name

        Returns:
            Full element definition dict or None if not found

        Example:
            >>> registry = ModuleRegistry()
            >>> info = registry.get_element_info("global_state_layer")
            >>> print(info["display_name"])
            "Global State Layer (Redux/Zustand/Context)"
        """
        return self.element_types.get(element_type)

    def format_checklist_markdown(self, element_type: str) -> str:
        """Format checklist as markdown for injection into template.

        Args:
            element_type: Element type name

        Returns:
            Markdown-formatted checklist (H4 heading + bullet list)

        Example:
            >>> registry = ModuleRegistry()
            >>> markdown = registry.format_checklist_markdown("custom_hooks")
            >>> print(markdown)
            #### Checklist
            - [ ] Side effects - Network, storage, subscriptions, timers
            - [ ] Cleanup guarantees - What happens on unmount
            ...
        """
        checklist = self.get_checklist(element_type)
        if not checklist:
            return ""

        lines = ["#### Checklist"]
        for item in checklist:
            lines.append(f"- [ ] {item}")

        return "\n".join(lines)

    def get_all_element_types(self) -> List[str]:
        """Get list of all available element types.

        Returns:
            List of element type names

        Example:
            >>> registry = ModuleRegistry()
            >>> all_types = registry.get_all_element_types()
            >>> print(len(all_types))
            20
        """
        return list(self.element_types.keys())

    def get_element_display_name(self, element_type: str) -> str:
        """Get human-readable display name for element type.

        Args:
            element_type: Element type name (e.g., "top_level_widgets")

        Returns:
            Display name (e.g., "Top-Level Widgets/Pages")

        Example:
            >>> registry = ModuleRegistry()
            >>> name = registry.get_element_display_name("custom_hooks")
            >>> print(name)
            "Custom Hooks Library"
        """
        element_def = self.element_types.get(element_type)
        if not element_def:
            return element_type  # Fallback to type name

        return element_def.get("display_name", element_type)

    def get_maintenance_impact(self, element_type: str) -> str:
        """Get maintenance impact level for element type.

        Args:
            element_type: Element type name

        Returns:
            Impact level: "critical", "high", "medium", or "low"

        Example:
            >>> registry = ModuleRegistry()
            >>> impact = registry.get_maintenance_impact("global_state_layer")
            >>> print(impact)
            "critical"
        """
        element_def = self.element_types.get(element_type)
        if not element_def:
            return "medium"  # Default

        return element_def.get("maintenance_impact", "medium")


# Example usage
def main():
    """Demonstrate ModuleRegistry usage."""
    registry = ModuleRegistry()

    print("Module Registry - Tool 2 Checklist Integration")
    print("=" * 70)

    # Example 1: Get checklist for custom hooks
    print("\n1. Custom Hooks Checklist:")
    checklist = registry.get_checklist("custom_hooks")
    for item in checklist:
        print(f"   - {item}")

    # Example 2: Format checklist as markdown
    print("\n2. Custom Hooks Checklist (Markdown):")
    markdown = registry.format_checklist_markdown("custom_hooks")
    print(markdown)

    # Example 3: Get additional sections
    print("\n3. Stateful Containers - Additional Sections:")
    sections = registry.get_additional_sections("stateful_containers")
    for section in sections:
        print(f"   - {section}")

    # Example 4: Get conditional modules
    print("\n4. Top-Level Widgets - Conditional Modules:")
    modules = registry.get_conditional_modules("top_level_widgets")
    for module in modules:
        print(f"   - {module}")

    # Example 5: List all element types
    print("\n5. All Element Types:")
    all_types = registry.get_all_element_types()
    for i, element_type in enumerate(all_types, 1):
        display_name = registry.get_element_display_name(element_type)
        impact = registry.get_maintenance_impact(element_type)
        print(f"   {i:2}. {display_name:40} [{impact}]")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
