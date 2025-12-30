"""
UDS Health Scoring - Document health and quality metrics

Calculates health scores (0-100) for documents based on:
- Traceability (40%): workorder_id, feature_id, MCP attribution
- Completeness (30%): required sections present
- Freshness (20%): age of document (<7 days = full points)
- Validation (10%): passes schema validation
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import json
import re

from .validator import validate_uds, ValidationSeverity


@dataclass
class HealthScore:
    """
    Document health score breakdown

    Attributes:
        score: Overall health score (0-100)
        traceability: Traceability score (0-40)
        completeness: Completeness score (0-30)
        freshness: Freshness score (0-20)
        validation: Validation score (0-10)
        has_workorder_id: Has workorder ID
        has_feature_id: Has feature ID
        has_mcp_attribution: Has MPC attribution
        age_days: Age of document in days
        passes_validation: Passes schema validation
    """
    score: int
    traceability: int
    completeness: int
    freshness: int
    validation: int
    has_workorder_id: bool
    has_feature_id: bool
    has_mcp_attribution: bool
    age_days: int
    passes_validation: bool


class HealthScorer:
    """
    Health Scorer - Calculates document health scores

    Health scoring formula:
    - Traceability (40 points):
      * Has workorder_id: 20 points
      * Has feature_id: 10 points
      * Has MCP attribution (generated_by): 10 points

    - Completeness (30 points):
      * Has all required sections: 20 points
      * Has examples: 10 points

    - Freshness (20 points):
      * <7 days old: 20 points
      * 7-30 days old: 10 points
      * 30-90 days old: 5 points
      * >90 days old: 0 points

    - Validation (10 points):
      * Passes schema validation: 10 points
    """

    def calculate_health(self, document: str, doc_type: str) -> HealthScore:
        """
        Calculate health score for document

        Args:
            document: Document content
            doc_type: Document type (plan, deliverables, etc.)

        Returns:
            HealthScore: Detailed health score breakdown
        """
        # Initialize scores
        traceability = 0
        completeness = 0
        freshness = 0
        validation_score = 0

        # Extract metadata
        header = self._extract_header(document)

        # 1. Traceability (40 points)
        has_workorder_id = False
        has_feature_id = False
        has_mcp_attribution = False

        if header:
            if "workorder_id" in header:
                has_workorder_id = True
                traceability += 20

            if "feature_id" in header:
                has_feature_id = True
                traceability += 10

            if "generated_by" in header and "coderef" in header["generated_by"]:
                has_mcp_attribution = True
                traceability += 10

        # 2. Completeness (30 points)
        # Check required sections (20 points)
        validation_result = validate_uds(document, doc_type)
        section_errors = [e for e in validation_result.errors if e.section is not None]

        if len(section_errors) == 0:
            completeness += 20  # All required sections present

        # Check for examples (10 points)
        if self._has_examples(document):
            completeness += 10

        # 3. Freshness (20 points)
        age_days = self._get_age_days(header)
        if age_days < 7:
            freshness = 20
        elif age_days < 30:
            freshness = 10
        elif age_days < 90:
            freshness = 5
        else:
            freshness = 0

        # 4. Validation (10 points)
        passes_validation = validation_result.valid
        if passes_validation:
            validation_score = 10

        # Calculate total score
        total_score = traceability + completeness + freshness + validation_score

        return HealthScore(
            score=total_score,
            traceability=traceability,
            completeness=completeness,
            freshness=freshness,
            validation=validation_score,
            has_workorder_id=has_workorder_id,
            has_feature_id=has_feature_id,
            has_mcp_attribution=has_mcp_attribution,
            age_days=age_days,
            passes_validation=passes_validation
        )

    def _extract_header(self, document: str) -> Optional[dict]:
        """Extract YAML frontmatter from document"""
        import yaml

        match = re.match(r'^---\n(.*?)\n---', document, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError:
                return None
        return None

    def _has_examples(self, document: str) -> bool:
        """Check if document has examples section or code blocks"""
        # Check for "Examples" heading
        if re.search(r'^#+\s+Examples', document, re.MULTILINE | re.IGNORECASE):
            return True

        # Check for code blocks (``` or ~~~)
        if re.search(r'^```', document, re.MULTILINE):
            return True

        return False

    def _get_age_days(self, header: Optional[dict]) -> int:
        """Get age of document in days from timestamp"""
        if not header or "timestamp" not in header:
            # No timestamp, assume very old
            return 999

        try:
            timestamp_str = header["timestamp"]
            # Parse ISO 8601 timestamp
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'

            timestamp = datetime.fromisoformat(timestamp_str)
            age = datetime.utcnow() - timestamp.replace(tzinfo=None)
            return age.days
        except (ValueError, AttributeError):
            return 999


def calculate_health(document: str, doc_type: str) -> HealthScore:
    """
    Convenience function to calculate health score

    Args:
        document: Document content
        doc_type: Document type

    Returns:
        HealthScore: Health score breakdown
    """
    scorer = HealthScorer()
    return scorer.calculate_health(document, doc_type)


def store_health_score(
    feature_name: str,
    doc_type: str,
    health_score: HealthScore,
    context_dir: Path
):
    """
    Store health score to coderef/context/ directory

    Args:
        feature_name: Feature name
        doc_type: Document type
        health_score: Health score to store
        context_dir: Path to coderef/context/ directory
    """
    context_dir = Path(context_dir)
    context_dir.mkdir(parents=True, exist_ok=True)

    health_file = context_dir / f"{feature_name}-{doc_type}-health.json"

    health_data = {
        "feature_name": feature_name,
        "doc_type": doc_type,
        "score": health_score.score,
        "breakdown": {
            "traceability": health_score.traceability,
            "completeness": health_score.completeness,
            "freshness": health_score.freshness,
            "validation": health_score.validation
        },
        "details": {
            "has_workorder_id": health_score.has_workorder_id,
            "has_feature_id": health_score.has_feature_id,
            "has_mcp_attribution": health_score.has_mcp_attribution,
            "age_days": health_score.age_days,
            "passes_validation": health_score.passes_validation
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    with open(health_file, 'w') as f:
        json.dump(health_data, f, indent=2)


def load_health_score(feature_name: str, doc_type: str, context_dir: Path) -> Optional[HealthScore]:
    """
    Load health score from coderef/context/ directory

    Args:
        feature_name: Feature name
        doc_type: Document type
        context_dir: Path to coderef/context/ directory

    Returns:
        HealthScore or None if not found
    """
    health_file = Path(context_dir) / f"{feature_name}-{doc_type}-health.json"

    if not health_file.exists():
        return None

    with open(health_file, 'r') as f:
        data = json.load(f)

    return HealthScore(
        score=data["score"],
        traceability=data["breakdown"]["traceability"],
        completeness=data["breakdown"]["completeness"],
        freshness=data["breakdown"]["freshness"],
        validation=data["breakdown"]["validation"],
        has_workorder_id=data["details"]["has_workorder_id"],
        has_feature_id=data["details"]["has_feature_id"],
        has_mcp_attribution=data["details"]["has_mcp_attribution"],
        age_days=data["details"]["age_days"],
        passes_validation=data["details"]["passes_validation"]
    )
