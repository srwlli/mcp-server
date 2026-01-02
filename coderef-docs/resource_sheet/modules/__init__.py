"""
Module Registry and Base Classes.

WO-RESOURCE-SHEET-MCP-TOOL-001

This module provides the registry for all documentation modules
and base classes for creating new modules.
"""

from typing import Dict, List
from ..types import DocumentationModule, CodeCharacteristics


class ModuleRegistry:
    """
    Central registry for all documentation modules.

    Manages registration, lookup, and selection of modules based
    on code characteristics.
    """

    def __init__(self):
        self._modules: Dict[str, DocumentationModule] = {}
        self._categories: Dict[str, List[str]] = {
            "universal": [],
            "ui": [],
            "state": [],
            "network": [],
            "hooks": [],
            "data": [],
            "testing": [],
        }

    def register(self, module: DocumentationModule) -> None:
        """Register a module in the registry."""
        self._modules[module.id] = module
        if module.category in self._categories:
            self._categories[module.category].append(module.id)

    def get(self, module_id: str) -> DocumentationModule | None:
        """Get a module by ID."""
        return self._modules.get(module_id)

    def get_by_category(self, category: str) -> List[DocumentationModule]:
        """Get all modules in a category."""
        module_ids = self._categories.get(category, [])
        return [self._modules[mid] for mid in module_ids if mid in self._modules]

    def get_all(self) -> List[DocumentationModule]:
        """Get all registered modules."""
        return list(self._modules.values())

    def select_modules(
        self, characteristics: CodeCharacteristics
    ) -> List[DocumentationModule]:
        """
        Select modules based on code characteristics.

        Args:
            characteristics: Detected code characteristics

        Returns:
            List of modules that should be included
        """
        selected = []

        for module in self._modules.values():
            # Check if any required characteristics are present
            if module.triggers["required_when"]:
                has_required = any(
                    characteristics.get(char, False)
                    for char in module.triggers["required_when"]
                )
                if has_required:
                    # Check incompatibilities
                    has_incompatible = any(
                        characteristics.get(char, False)
                        for char in module.triggers["incompatible_with"]
                    )
                    if not has_incompatible:
                        selected.append(module)

            # Check optional characteristics
            elif module.triggers["optional_when"]:
                has_optional = any(
                    characteristics.get(char, False)
                    for char in module.triggers["optional_when"]
                )
                if has_optional:
                    has_incompatible = any(
                        characteristics.get(char, False)
                        for char in module.triggers["incompatible_with"]
                    )
                    if not has_incompatible:
                        selected.append(module)

        return selected

    def count(self) -> int:
        """Get total number of registered modules."""
        return len(self._modules)


# Global registry instance
_registry = ModuleRegistry()


def get_registry() -> ModuleRegistry:
    """Get the global module registry instance."""
    return _registry
