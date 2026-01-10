"""
Element Type Detection Module - 3-Stage Detection Algorithm

This module implements a 3-stage detection algorithm to automatically classify
code elements into one of 20 element types for resource sheet generation.

Workorder: WO-RESOURCE-SHEET-CONSOLIDATION-001
Task: DETECT-001
Author: Papertrail Agent
Date: 2026-01-03
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DetectionResult:
    """Result of element type detection."""
    element_type: str
    confidence: float
    detection_method: str
    matched_patterns: List[str]
    manual_review_needed: bool


class ElementTypeDetector:
    """3-stage element type detection algorithm.

    Stage 1: Filename Pattern Matching (80-95% confidence)
    Stage 2: Code Analysis Refinement (+10-20% confidence boost)
    Stage 3: Fallback with Manual Review (<80% confidence)
    """

    def __init__(self, mapping_file: Optional[Path] = None):
        """Initialize detector with element type mapping.

        Args:
            mapping_file: Path to element-type-mapping.json
                         Defaults to ../resource_sheet/mapping/element-type-mapping.json
        """
        if mapping_file is None:
            # Default location
            current_dir = Path(__file__).parent
            mapping_file = current_dir.parent / "resource_sheet" / "mapping" / "element-type-mapping.json"

        self.mapping = self._load_mapping(mapping_file)
        self.element_types = self.mapping.get("element_types", [])

    def _load_mapping(self, mapping_file: Path) -> Dict:
        """Load element type mapping from JSON file."""
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def detect(self, file_path: str, code_content: Optional[str] = None) -> DetectionResult:
        """Detect element type using 3-stage algorithm.

        Args:
            file_path: Path to the file (e.g., "components/UserDashboard/UserDashboardPage.tsx")
            code_content: Optional file content for code analysis (Stage 2)

        Returns:
            DetectionResult with element_type, confidence, and metadata
        """
        # Stage 1: Filename pattern matching
        stage1_results = self._stage_1_filename_matching(file_path)

        if not stage1_results:
            # No matches found, fallback to manual review
            return self._stage_3_fallback(file_path, stage1_results)

        # Get best match from Stage 1
        best_match = max(stage1_results, key=lambda x: x[1])  # (element_type, confidence, patterns)
        element_type, confidence, matched_patterns = best_match
        detection_method = "stage_1_filename"

        # Stage 2: Code analysis refinement (if code provided and confidence < 100%)
        if code_content and confidence < 100:
            boost, code_patterns = self._stage_2_code_analysis(element_type, code_content)
            confidence = min(100, confidence + boost)
            matched_patterns.extend(code_patterns)
            detection_method = "stage_1_filename + stage_2_code_analysis"

        # Stage 3: Check if manual review needed
        manual_review = confidence < 80
        if manual_review:
            return self._stage_3_fallback(file_path, stage1_results)

        return DetectionResult(
            element_type=element_type,
            confidence=confidence,
            detection_method=detection_method,
            matched_patterns=matched_patterns,
            manual_review_needed=False
        )

    def _stage_1_filename_matching(self, file_path: str) -> List[Tuple[str, float, List[str]]]:
        """Stage 1: Match file path against filename/path patterns.

        Returns:
            List of (element_type, confidence, matched_patterns) tuples
        """
        file_path_obj = Path(file_path)
        filename = file_path_obj.name
        filename_no_ext = file_path_obj.stem  # Filename without extension
        path_parts = str(file_path_obj).replace('\\', '/')

        results = []

        for element_def in self.element_types:
            element_type = element_def["element_type"]
            detection_patterns = element_def.get("detection_patterns", {})

            matched_patterns = []
            base_confidence = 0

            # Check filename patterns
            filename_patterns = detection_patterns.get("filename_patterns", [])
            for pattern in filename_patterns:
                # Convert pattern to regex
                regex_pattern = self._pattern_to_regex(pattern)

                # Try matching against full filename first
                if re.search(regex_pattern, filename):
                    matched_patterns.append(f"filename: {pattern}")
                    base_confidence = 90  # High confidence for filename match
                    break
                # Also try matching against filename without extension (for patterns ending with $)
                elif pattern.endswith('$') and re.search(regex_pattern.replace('$', '') + '$', filename_no_ext):
                    matched_patterns.append(f"filename: {pattern}")
                    base_confidence = 90  # High confidence for filename match
                    break

            # Check path patterns (boosts confidence if filename already matched)
            path_patterns = detection_patterns.get("path_patterns", [])
            for pattern in path_patterns:
                if pattern in path_parts:
                    matched_patterns.append(f"path: {pattern}")
                    if base_confidence > 0:
                        base_confidence = min(95, base_confidence + 5)  # Boost if already matched
                    else:
                        base_confidence = 85  # Medium confidence for path-only match
                    break

            if matched_patterns:
                results.append((element_type, base_confidence, matched_patterns))

        return results

    def _stage_2_code_analysis(self, element_type: str, code_content: str) -> Tuple[float, List[str]]:
        """Stage 2: Analyze code content for patterns.

        Args:
            element_type: Element type from Stage 1
            code_content: File content to analyze

        Returns:
            (confidence_boost, matched_code_patterns)
        """
        # Find element definition
        element_def = next((e for e in self.element_types if e["element_type"] == element_type), None)
        if not element_def:
            return (0, [])

        detection_patterns = element_def.get("detection_patterns", {})
        code_patterns = detection_patterns.get("code_patterns", [])

        matched_patterns = []
        boost = 0

        for pattern in code_patterns:
            # Check if pattern exists in code (case-insensitive substring match)
            if pattern.lower() in code_content.lower():
                matched_patterns.append(f"code: {pattern}")
                boost += 5  # Each pattern adds 5% confidence

        # Cap boost at 20%
        boost = min(20, boost)

        return (boost, matched_patterns)

    def _stage_3_fallback(self, file_path: str, stage1_results: List[Tuple[str, float, List[str]]]) -> DetectionResult:
        """Stage 3: Fallback when confidence is low or no matches.

        Args:
            file_path: Original file path
            stage1_results: Results from Stage 1 (may be empty)

        Returns:
            DetectionResult with manual_review_needed=True
        """
        # Default to top_level_widgets if nothing matched
        if not stage1_results:
            return DetectionResult(
                element_type="top_level_widgets",
                confidence=0,
                detection_method="stage_3_fallback_default",
                matched_patterns=[],
                manual_review_needed=True
            )

        # Use best match but flag for manual review
        best_match = max(stage1_results, key=lambda x: x[1])
        element_type, confidence, matched_patterns = best_match

        return DetectionResult(
            element_type=element_type,
            confidence=confidence,
            detection_method="stage_3_fallback_low_confidence",
            matched_patterns=matched_patterns,
            manual_review_needed=True
        )

    def _pattern_to_regex(self, pattern: str) -> str:
        """Convert detection pattern to regex.

        Examples:
            "Page$" → r"Page$"
            "^use[A-Z]" → r"^use[A-Z]"
            "store\\.ts$" → r"store\\.ts$"
        """
        # Pattern is already regex-like in most cases
        # Just ensure it's properly escaped if needed
        return pattern

    def get_all_element_types(self) -> List[str]:
        """Get list of all available element types.

        Returns:
            List of element type names (e.g., ["top_level_widgets", "custom_hooks", ...])
        """
        return [e["element_type"] for e in self.element_types]

    def get_element_info(self, element_type: str) -> Optional[Dict]:
        """Get full element definition by type.

        Args:
            element_type: Element type name

        Returns:
            Element definition dict or None if not found
        """
        return next((e for e in self.element_types if e["element_type"] == element_type), None)


# Example usage and testing
def main():
    """Example usage of ElementTypeDetector."""
    detector = ElementTypeDetector()

    # Test cases
    test_cases = [
        ("components/UserDashboard/UserDashboardPage.tsx", None),
        ("hooks/useLocalStorage.ts", "export function useLocalStorage() { useEffect(() => { return () => {} }); }"),
        ("store/index.ts", "const store = configureStore({ reducer: {} });"),
        ("utils/helpers.ts", None),  # Ambiguous case
    ]

    print("Element Type Detection - Test Results")
    print("=" * 70)

    for file_path, code_content in test_cases:
        result = detector.detect(file_path, code_content)
        print(f"\nFile: {file_path}")
        print(f"  Type: {result.element_type}")
        print(f"  Confidence: {result.confidence}%")
        print(f"  Method: {result.detection_method}")
        print(f"  Matched: {', '.join(result.matched_patterns)}")
        print(f"  Manual Review: {'YES' if result.manual_review_needed else 'NO'}")

    print("\n" + "=" * 70)
    print(f"Total Element Types: {len(detector.get_all_element_types())}")


if __name__ == "__main__":
    main()
