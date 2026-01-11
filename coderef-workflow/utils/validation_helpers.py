"""
Centralized validation error handling for Papertrail validators.

Provides consistent validation result processing with 3-tier thresholds:
- Score >= 90: Pass (log success)
- Score 50-89: Warn (log issues, continue)
- Score < 50: Fail (log errors, raise ValueError)

Part of WO-VALIDATOR-INTEGRATION-001 (GAP-005).
"""

from typing import Dict, Any
from logger_config import logger


def handle_validation_result(result: Dict[str, Any], file_type: str = "document") -> None:
    """
    Consistent validation error handling across workflows.

    Args:
        result: Validation result dictionary with 'score', 'valid', 'errors', 'warnings' keys
        file_type: Human-readable file type for logging (e.g., "analysis.json", "plan.json")

    Returns:
        None

    Raises:
        ValueError: If validation score < 50 (critical failure threshold)

    Examples:
        >>> # Success case (score >= 90)
        >>> result = {'valid': True, 'score': 95, 'errors': [], 'warnings': []}
        >>> handle_validation_result(result, "analysis.json")
        # Logs: "analysis.json validation passed (score: 95)"

        >>> # Warning case (50 <= score < 90)
        >>> result = {'valid': False, 'score': 75, 'errors': [{'severity': 'MINOR', 'message': 'Missing field'}], 'warnings': ['Typo']}
        >>> handle_validation_result(result, "plan.json")
        # Logs warnings, continues execution

        >>> # Failure case (score < 50)
        >>> result = {'valid': False, 'score': 30, 'errors': [{'severity': 'CRITICAL', 'message': 'Invalid structure'}]}
        >>> handle_validation_result(result, "context.json")
        # Raises ValueError with error details
    """
    score = result.get('score', 0)

    # Tier 1: Success (score >= 90)
    if score >= 90:
        logger.info(f"{file_type} validation passed (score: {score})")
        return

    # Tier 2: Warning (50 <= score < 90)
    if 50 <= score < 90:
        logger.warning(f"{file_type} validation score: {score}")

        # Log errors with severity
        for error in result.get('errors', []):
            severity = error.get('severity', 'ERROR') if isinstance(error, dict) else 'ERROR'
            message = error.get('message', str(error)) if isinstance(error, dict) else str(error)
            logger.warning(f"  {severity}: {message}")

        # Log warnings
        for warning in result.get('warnings', []):
            warning_msg = warning if isinstance(warning, str) else str(warning)
            logger.warning(f"  WARNING: {warning_msg}")

        return

    # Tier 3: Critical failure (score < 50)
    logger.error(f"{file_type} validation failed critically (score: {score})")

    # Log all errors
    errors = result.get('errors', [])
    for error in errors:
        severity = error.get('severity', 'ERROR') if isinstance(error, dict) else 'ERROR'
        message = error.get('message', str(error)) if isinstance(error, dict) else str(error)
        logger.error(f"  {severity}: {message}")

    # Raise exception with details
    error_count = len(errors)
    raise ValueError(
        f"Validation failed: {file_type} score {score} (minimum: 50). "
        f"Fix {error_count} error{'s' if error_count != 1 else ''} before proceeding."
    )
