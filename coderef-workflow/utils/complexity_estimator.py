"""
Complexity Estimator for Python-based Planning Workflows.

Simplified complexity estimation when TypeScript ComplexityScorer MCP tool is unavailable.
Provides basic LOC-based and pattern-based complexity scoring.

Part of WO-WORKFLOW-SCANNER-INTEGRATION-001 IMPL-008
"""

from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from coderef.utils import read_coderef_output

from logger_config import logger


class ComplexityEstimator:
    """
    Estimates code complexity using .coderef/index.json data.

    Fallback estimator when ComplexityScorer MCP tool unavailable.
    Uses heuristics based on element type, parameter count, and file patterns.
    """

    def __init__(self, project_path: Path):
        """
        Initialize complexity estimator.

        Args:
            project_path: Path to project root
        """
        self.project_path = project_path
        self.elements_cache = None
        logger.debug(f"ComplexityEstimator initialized for: {project_path}")

    def _load_elements(self) -> List[Dict]:
        """Load elements from .coderef/index.json (lazy loading)."""
        if self.elements_cache is None:
            try:
                self.elements_cache = read_coderef_output(str(self.project_path), 'index')
                if not self.elements_cache:
                    self.elements_cache = []
                logger.info(f"Loaded {len(self.elements_cache)} elements for complexity estimation")
            except Exception as e:
                logger.warning(f"Failed to load .coderef/index.json: {str(e)}")
                self.elements_cache = []

        return self.elements_cache

    def estimate_element_complexity(self, element_name: str) -> Optional[Dict]:
        """
        Estimate complexity for a single element.

        Args:
            element_name: Name of element to analyze

        Returns:
            dict with:
            - complexity_score: int (0-10)
            - risk_level: 'low' | 'medium' | 'high' | 'critical'
            - estimated_loc: int (estimated lines of code)
            - parameter_count: int
            - factors: List[str] (complexity factors identified)
        """
        elements = self._load_elements()

        # Find the element
        elem = None
        for e in elements:
            if e.get('name') == element_name:
                elem = e
                break

        if not elem:
            logger.warning(f"Element not found for complexity estimation: {element_name}")
            return None

        # Extract element data
        elem_type = elem.get('type', 'unknown')
        parameters = elem.get('parameters', [])
        calls = elem.get('calls', [])

        # Complexity scoring (0-10 scale)
        score = 0
        factors = []

        # Base complexity by type
        type_complexity = {
            'class': 3,
            'method': 2,
            'function': 2,
            'component': 4,  # React components often complex
            'hook': 3,
            'interface': 1,
            'type': 1,
            'decorator': 2,
            'constant': 1
        }
        score += type_complexity.get(elem_type, 2)

        # Parameter count increases complexity
        param_count = len(parameters)
        if param_count > 5:
            score += 3
            factors.append(f"High parameter count ({param_count})")
        elif param_count > 3:
            score += 2
            factors.append(f"Moderate parameter count ({param_count})")
        elif param_count > 0:
            score += 1

        # Number of function calls indicates complexity
        calls_count = len(calls)
        if calls_count > 10:
            score += 2
            factors.append(f"Many function calls ({calls_count})")
        elif calls_count > 5:
            score += 1
            factors.append(f"Several function calls ({calls_count})")

        # Cap at 10
        score = min(score, 10)

        # Determine risk level
        if score <= 3:
            risk_level = 'low'
        elif score <= 6:
            risk_level = 'medium'
        elif score <= 8:
            risk_level = 'high'
        else:
            risk_level = 'critical'

        # Estimate LOC (rough heuristic)
        estimated_loc = score * 10  # Rough estimate: score 5 ≈ 50 LOC

        return {
            'element_name': element_name,
            'complexity_score': score,
            'risk_level': risk_level,
            'estimated_loc': estimated_loc,
            'parameter_count': param_count,
            'calls_count': calls_count,
            'factors': factors
        }

    def estimate_task_complexity(self, element_names: List[str]) -> Dict:
        """
        Estimate complexity for a task involving multiple elements.

        Args:
            element_names: List of element names in the task

        Returns:
            dict with:
            - avg_complexity_score: float
            - max_complexity_score: int
            - total_estimated_loc: int
            - high_complexity_elements: List[str] (elements with score > 7)
            - complexity_distribution: dict
        """
        if not element_names:
            return {
                'avg_complexity_score': 0,
                'max_complexity_score': 0,
                'total_estimated_loc': 0,
                'high_complexity_elements': [],
                'complexity_distribution': {}
            }

        scores = []
        total_loc = 0
        high_complexity = []
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}

        for elem_name in element_names:
            result = self.estimate_element_complexity(elem_name)

            if result:
                score = result['complexity_score']
                scores.append(score)
                total_loc += result.get('estimated_loc', 0)

                # Track high-complexity elements
                if score > 7:
                    high_complexity.append({
                        'name': elem_name,
                        'score': score,
                        'risk_level': result['risk_level']
                    })

                # Distribution
                distribution[result['risk_level']] += 1

        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0

        logger.info(f"Task complexity: avg={avg_score:.1f}, max={max_score}, {len(high_complexity)} high-complexity elements")

        return {
            'avg_complexity_score': round(avg_score, 1),
            'max_complexity_score': max_score,
            'total_estimated_loc': total_loc,
            'high_complexity_elements': high_complexity,
            'complexity_distribution': distribution,
            'elements_analyzed': len(element_names)
        }
