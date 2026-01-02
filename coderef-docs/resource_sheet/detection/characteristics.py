"""
Characteristics Detector - Maps Code Patterns to Boolean Flags.

WO-RESOURCE-SHEET-MCP-TOOL-001

Analyzes coderef_scan output or AST to detect boolean characteristics
that drive module selection.
"""

from typing import Dict, Any
from ..types import CodeCharacteristics


class CharacteristicsDetector:
    """
    Detects code characteristics from analysis data.

    Transforms raw code analysis into boolean flags that modules
    can use for conditional inclusion.
    """

    def detect_from_coderef_scan(self, scan_data: Dict[str, Any]) -> CodeCharacteristics:
        """
        Detect characteristics from coderef_scan output.

        Args:
            scan_data: Output from coderef_scan MCP tool

        Returns:
            Detected boolean characteristics
        """
        characteristics: CodeCharacteristics = {}

        # Structure detection
        element_type = scan_data.get("type", "").lower()
        characteristics["is_class"] = "class" in element_type
        characteristics["is_function"] = "function" in element_type
        characteristics["is_component"] = "component" in element_type
        characteristics["is_hook"] = "hook" in element_type or scan_data.get("name", "").startswith("use")

        # Behavior detection from imports
        imports = scan_data.get("imports", [])
        characteristics["makes_network_calls"] = any(
            lib in str(imports) for lib in ["fetch", "axios", "http", "request"]
        )
        characteristics["has_error_handling"] = "error" in scan_data.get("code", "").lower()

        # UI detection
        code = scan_data.get("code", "")
        characteristics["has_jsx"] = "jsx" in element_type or "<" in code and ">" in code
        characteristics["has_props"] = "props" in code.lower()
        characteristics["has_events"] = any(
            event in code for event in ["onClick", "onChange", "onSubmit", "addEventListener"]
        )
        characteristics["has_event_handlers"] = any(
            handler in code for handler in ["onClick", "onChange", "onSubmit", "onFocus", "onBlur"]
        )
        characteristics["has_aria_attributes"] = "aria-" in code

        # State detection
        characteristics["manages_state"] = any(
            state_hook in code for state_hook in ["useState", "useReducer", "this.state"]
        )
        characteristics["uses_global_state"] = any(
            lib in str(imports) for lib in ["redux", "zustand", "recoil", "jotai"]
        )
        characteristics["has_lifecycle_methods"] = any(
            hook in code for hook in ["useEffect", "useLayoutEffect", "componentDidMount", "componentWillUnmount"]
        )

        # Storage detection
        characteristics["uses_local_storage"] = "localStorage" in code
        characteristics["uses_indexed_db"] = "indexedDB" in code or "idb" in str(imports)

        # Data detection
        characteristics["has_types"] = scan_data.get("language") in ["typescript", "ts", "tsx"]
        characteristics["has_schema"] = any(
            validator in str(imports) for validator in ["zod", "yup", "joi", "ajv"]
        )
        characteristics["has_validation"] = "validate" in code.lower()

        # Testing detection
        test_keywords = ["test", "spec", "mock", "jest", "vitest"]
        file_path = scan_data.get("file_path", "").lower()
        characteristics["has_tests"] = any(keyword in file_path for keyword in test_keywords)
        characteristics["has_mocks"] = "mock" in code.lower()

        # Auth detection
        auth_keywords = ["jwt", "token", "auth", "login", "session"]
        characteristics["handles_auth"] = any(keyword in code.lower() for keyword in auth_keywords)

        # Retry detection
        characteristics["has_retry_logic"] = any(
            retry in code.lower() for retry in ["retry", "backoff", "attempt"]
        )

        return characteristics

    def detect_from_ast(self, ast_data: Any) -> CodeCharacteristics:
        """
        Detect characteristics from AST analysis.

        Args:
            ast_data: Parsed AST structure

        Returns:
            Detected boolean characteristics

        Note: Not implemented in Phase 1 - placeholder for future enhancement
        """
        return {}

    def detect_from_file_content(self, code: str, language: str) -> CodeCharacteristics:
        """
        Detect characteristics from raw file content.

        Args:
            code: File content as string
            language: Programming language

        Returns:
            Detected boolean characteristics
        """
        # Simplified detection for Phase 1
        return self.detect_from_coderef_scan({
            "code": code,
            "language": language,
            "type": "unknown",
            "imports": [],
            "file_path": "",
        })

    def calculate_confidence(self, characteristics: CodeCharacteristics) -> Dict[str, float]:
        """
        Calculate confidence scores for each detected characteristic.

        Args:
            characteristics: Detected characteristics

        Returns:
            Confidence scores (0.0-1.0) for each characteristic
        """
        # Placeholder for Phase 2 - returns 1.0 for all detected characteristics
        return {key: 1.0 if value else 0.0 for key, value in characteristics.items()}
