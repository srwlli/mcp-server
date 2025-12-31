"""
Persona management - loading, activation, and state tracking.
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

# Add coderef/ utilities to path for wrapper functions
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from coderef.utils import read_coderef_output, check_coderef_available

from src.models import PersonaDefinition, PersonaState


class PersonaManager:
    """Manages persona loading and activation."""

    def __init__(self, personas_dir: Path):
        """
        Initialize persona manager.

        Args:
            personas_dir: Root directory containing persona JSON files
        """
        self.personas_dir = personas_dir
        self.state = PersonaState()
        self._persona_cache: Dict[str, PersonaDefinition] = {}

    def load_persona(self, name: str) -> PersonaDefinition:
        """
        Load a persona definition from JSON file.

        Args:
            name: Persona name (e.g., 'mcp-expert', 'docs-expert', 'coderef-expert')

        Returns:
            PersonaDefinition object

        Raises:
            FileNotFoundError: If persona JSON file doesn't exist
            ValueError: If JSON is invalid or doesn't match schema
        """
        # Check cache first
        if name in self._persona_cache:
            return self._persona_cache[name]

        # Check base/, custom/, and coderef-personas/ directories
        persona_file = self.personas_dir / "base" / f"{name}.json"

        # If not in base/, check custom/
        if not persona_file.exists():
            persona_file = self.personas_dir / "custom" / f"{name}.json"

        # If not in custom/, check coderef-personas/
        if not persona_file.exists():
            persona_file = self.personas_dir / "coderef-personas" / f"{name}.json"

        if not persona_file.exists():
            raise FileNotFoundError(
                f"Persona '{name}' not found in base/, custom/, or coderef-personas/ directories. "
                f"Available personas: {self.list_available_personas()}"
            )

        # Load and validate JSON
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona_data = json.load(f)

            # Validate against Pydantic schema
            persona = PersonaDefinition(**persona_data)

            # Cache for future use
            self._persona_cache[name] = persona

            return persona

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {persona_file}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load persona '{name}': {e}")

    def load_coderef_patterns(self, project_path: Optional[Path] = None) -> Optional[Dict]:
        """
        Load code patterns from .coderef/patterns.json for enhanced persona context.

        Args:
            project_path: Path to project directory (default: use current directory)

        Returns:
            Dict with pattern data or None if not available

        Example pattern data:
            {
                'handlers': [...],
                'decorators': [...],
                'error_handling': [...]
            }
        """
        if project_path is None:
            project_path = Path.cwd()

        try:
            if check_coderef_available(str(project_path)):
                patterns = read_coderef_output(str(project_path), 'patterns')
                return patterns
        except Exception:
            pass  # Silently skip if patterns not available

        return None

    def activate_persona(self, name: str, project_path: Optional[Path] = None, load_patterns: bool = True) -> Dict:
        """
        Activate a persona (loads if not cached).

        Optionally enriches persona with project-specific code patterns from .coderef/patterns.json

        Args:
            name: Persona name to activate
            project_path: Optional path to project for pattern loading
            load_patterns: Whether to load .coderef/patterns.json (default: True)

        Returns:
            Dict with persona and optional patterns:
            {
                'persona': PersonaDefinition,
                'patterns': Optional[Dict]  # Only if load_patterns=True and patterns exist
            }

        Raises:
            FileNotFoundError: If persona doesn't exist
            ValueError: If persona is invalid
        """
        persona = self.load_persona(name)
        self.state.active_persona = persona
        self.state.activated_at = datetime.now()

        result = {'persona': persona}

        # Optionally load code patterns for enhanced context
        if load_patterns:
            patterns = self.load_coderef_patterns(project_path)
            if patterns:
                result['patterns'] = patterns
                result['patterns_loaded'] = True
                result['pattern_source'] = str(project_path or Path.cwd())
            else:
                result['patterns_loaded'] = False

        return result

    def get_active_persona(self) -> Optional[PersonaDefinition]:
        """
        Get currently active persona.

        Returns:
            Active PersonaDefinition or None if no persona is active
        """
        return self.state.active_persona

    def clear_persona(self):
        """Reset to no active persona."""
        self.state.clear()

    def is_persona_active(self) -> bool:
        """Check if any persona is currently active."""
        return self.state.is_active()

    def get_active_persona_name(self) -> Optional[str]:
        """Get the name of the active persona."""
        return self.state.get_name()

    def list_available_personas(self) -> list[str]:
        """
        List all available persona names from base/, custom/, and coderef-personas/ directories.

        Returns:
            List of persona names (e.g., ['coderef-expert', 'docs-expert', 'mcp-expert', 'research-scout'])
        """
        personas = []

        # Check base/ directory
        base_dir = self.personas_dir / "base"
        if base_dir.exists():
            for file in base_dir.glob("*.json"):
                # Skip backup files
                if not file.stem.endswith('.old') and not file.stem.endswith('.backup'):
                    personas.append(file.stem)

        # Check custom/ directory
        custom_dir = self.personas_dir / "custom"
        if custom_dir.exists():
            for file in custom_dir.glob("*.json"):
                # Skip backup files
                if not file.stem.endswith('.old') and not file.stem.endswith('.backup'):
                    personas.append(file.stem)

        # Check coderef-personas/ directory
        coderef_dir = self.personas_dir / "coderef-personas"
        if coderef_dir.exists():
            for file in coderef_dir.glob("*.json"):
                # Skip backup files
                if not file.stem.endswith('.old') and not file.stem.endswith('.backup'):
                    personas.append(file.stem)

        return sorted(personas)

    def get_persona_info(self, name: str) -> Dict:
        """
        Get brief info about a persona without fully activating it.

        Args:
            name: Persona name

        Returns:
            Dict with name, description, expertise, use_cases
        """
        persona = self.load_persona(name)
        return {
            "name": persona.name,
            "version": persona.version,
            "description": persona.description,
            "expertise": persona.expertise,
            "use_cases": persona.use_cases
        }
