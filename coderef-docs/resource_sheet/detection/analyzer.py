"""
Code Analyzer - Orchestrates Code Analysis.

WO-RESOURCE-SHEET-MCP-TOOL-001

High-level analyzer that coordinates between coderef_scan,
AST parsing, and characteristics detection.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import subprocess

from ..types import CodeCharacteristics
from .characteristics import CharacteristicsDetector


class CodeAnalyzer:
    """
    Orchestrates code analysis for resource sheet generation.

    Handles calling coderef_scan, parsing results, and detecting
    characteristics for module selection.
    """

    def __init__(self):
        self.detector = CharacteristicsDetector()

    async def analyze_element(
        self,
        element_name: str,
        project_path: str,
        use_coderef_scan: bool = True,
    ) -> Dict[str, Any]:
        """
        Analyze a code element to extract structure and characteristics.

        Args:
            element_name: Name of element to analyze (e.g., "AuthService")
            project_path: Path to project root
            use_coderef_scan: Whether to use coderef_scan tool (default: True)

        Returns:
            Analysis result with scan_data, characteristics, and metadata
        """
        scan_data = {}
        characteristics: CodeCharacteristics = {}

        if use_coderef_scan:
            scan_data = await self._run_coderef_scan(element_name, project_path)
            if scan_data:
                characteristics = self.detector.detect_from_coderef_scan(scan_data)

        # Fallback to file-based detection if coderef_scan unavailable
        if not characteristics:
            file_path = self._find_element_file(element_name, project_path)
            if file_path:
                code = Path(file_path).read_text(encoding="utf-8")
                language = file_path.suffix.lstrip(".")
                characteristics = self.detector.detect_from_file_content(code, language)

        return {
            "element_name": element_name,
            "scan_data": scan_data,
            "characteristics": characteristics,
            "analysis_method": "coderef_scan" if scan_data else "file_content",
        }

    async def _run_coderef_scan(
        self, element_name: str, project_path: str
    ) -> Dict[str, Any]:
        """
        Run coderef_scan to analyze code element.

        Args:
            element_name: Element to scan
            project_path: Project root path

        Returns:
            Scan result data or empty dict if scan fails
        """
        try:
            # Check if .coderef/index.json exists
            index_path = Path(project_path) / ".coderef" / "index.json"
            if index_path.exists():
                # Read from cached scan
                with open(index_path, "r", encoding="utf-8") as f:
                    index_data = json.load(f)

                # Find element in index
                for element in index_data:
                    if element.get("name") == element_name:
                        return element

            # If not in cache, would call coderef_scan MCP tool here
            # For Phase 1, return empty to fall back to file-based detection
            return {}

        except Exception as e:
            print(f"Warning: coderef_scan failed: {e}")
            return {}

    def _find_element_file(self, element_name: str, project_path: str) -> Optional[str]:
        """
        Find file containing the element.

        Args:
            element_name: Element name to find
            project_path: Project root

        Returns:
            File path if found, None otherwise
        """
        project = Path(project_path)

        # Common patterns for file names
        patterns = [
            f"**/{element_name}.ts",
            f"**/{element_name}.tsx",
            f"**/{element_name}.js",
            f"**/{element_name}.jsx",
            f"**/{element_name}.py",
            f"**/{element_name.lower()}.ts",
            f"**/{element_name.lower()}.tsx",
        ]

        for pattern in patterns:
            matches = list(project.glob(pattern))
            if matches:
                return str(matches[0])

        return None

    def get_characteristics_summary(self, characteristics: CodeCharacteristics) -> str:
        """
        Generate human-readable summary of detected characteristics.

        Args:
            characteristics: Detected characteristics

        Returns:
            Formatted summary string
        """
        true_characteristics = [k for k, v in characteristics.items() if v]

        if not true_characteristics:
            return "No characteristics detected"

        summary = "Detected Characteristics:\n"
        for char in true_characteristics:
            summary += f"  ✓ {char.replace('_', ' ').title()}\n"

        return summary
