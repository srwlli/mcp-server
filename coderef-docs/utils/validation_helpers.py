"""
Validation helpers for direct validation integration.

WO-CODEREF-DOCS-DIRECT-VALIDATION-001: Helper functions for writing validation
metadata to markdown frontmatter _uds sections.
"""

import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def write_validation_metadata_to_frontmatter(
    file_path: Path,
    validation_result: Any
) -> None:
    """
    Write validation metadata to markdown frontmatter _uds section.

    Reads existing file, extracts frontmatter, adds _uds validation metadata,
    and writes back to file preserving all content.

    Args:
        file_path: Path to markdown file
        validation_result: ValidationResult object with score, errors, warnings attributes

    Raises:
        IOError: If file cannot be read or written
        yaml.YAMLError: If frontmatter YAML is invalid
    """
    if not file_path.exists():
        logger.error(f"File does not exist: {file_path}")
        return

    try:
        # Read file content
        content = file_path.read_text(encoding='utf-8')

        # Extract frontmatter and body
        frontmatter, body = _extract_frontmatter(content)

        # Add validation metadata to frontmatter
        frontmatter = _add_validation_metadata(frontmatter, validation_result)

        # Reconstruct file with updated frontmatter
        new_content = _reconstruct_file(frontmatter, body)

        # Write back to file
        file_path.write_text(new_content, encoding='utf-8')

        logger.info(
            f"Wrote validation metadata to {file_path.name}: "
            f"score={validation_result.score}"
        )

    except Exception as e:
        logger.error(f"Failed to write validation metadata to {file_path}: {e}")
        # Don't raise - validation metadata is supplementary, not critical


def _extract_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """
    Extract YAML frontmatter and body from markdown content.

    Args:
        content: Full markdown file content

    Returns:
        Tuple of (frontmatter_dict, body_content)

    If no frontmatter exists, returns empty dict and full content as body.
    """
    # Match YAML frontmatter: ---\n...\n---
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if match:
        frontmatter_yaml = match.group(1)
        body = match.group(2)

        try:
            frontmatter = yaml.safe_load(frontmatter_yaml) or {}
        except yaml.YAMLError as e:
            logger.warning(f"Invalid YAML frontmatter, creating new: {e}")
            frontmatter = {}
    else:
        # No frontmatter found
        frontmatter = {}
        body = content

    return frontmatter, body


def _add_validation_metadata(
    frontmatter: Dict[str, Any],
    validation_result: Any
) -> Dict[str, Any]:
    """
    Add _uds validation metadata to frontmatter dict.

    Args:
        frontmatter: Existing frontmatter dictionary
        validation_result: ValidationResult object

    Returns:
        Updated frontmatter dictionary with _uds section
    """
    # Serialize validation errors to simple format
    errors = []
    if hasattr(validation_result, 'errors') and validation_result.errors:
        for error in validation_result.errors:
            if hasattr(error, 'to_dict'):
                errors.append(error.to_dict())
            elif hasattr(error, '__dict__'):
                errors.append({
                    'severity': str(getattr(error, 'severity', 'ERROR')),
                    'message': str(getattr(error, 'message', str(error))),
                    'field': getattr(error, 'field', None)
                })
            else:
                errors.append({'message': str(error)})

    # Serialize validation warnings
    warnings = []
    if hasattr(validation_result, 'warnings') and validation_result.warnings:
        warnings = [str(w) for w in validation_result.warnings]

    # Get validator class name
    validator_name = validation_result.__class__.__name__ if hasattr(validation_result, '__class__') else 'Unknown'
    if validator_name == 'ValidationResult':
        # Try to get validator from result metadata
        validator_name = getattr(validation_result, 'validator_name', 'UnknownValidator')

    # Create _uds metadata
    _uds_metadata = {
        'validation_score': int(validation_result.score) if hasattr(validation_result, 'score') else 0,
        'validation_errors': errors,
        'validation_warnings': warnings,
        'validated_at': datetime.utcnow().isoformat() + 'Z',
        'validator': validator_name
    }

    # Add to frontmatter
    frontmatter['_uds'] = _uds_metadata

    return frontmatter


def _reconstruct_file(frontmatter: Dict[str, Any], body: str) -> str:
    """
    Reconstruct markdown file from frontmatter dict and body.

    Args:
        frontmatter: Frontmatter dictionary
        body: Markdown body content

    Returns:
        Complete markdown file content with YAML frontmatter
    """
    if not frontmatter:
        # No frontmatter to add
        return body

    # Convert frontmatter to YAML
    frontmatter_yaml = yaml.dump(
        frontmatter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )

    # Reconstruct file
    return f"---\n{frontmatter_yaml}---\n{body}"


def extract_validation_metadata(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Extract validation metadata from markdown frontmatter _uds section.

    Utility function for reading validation metadata (e.g., for testing).

    Args:
        file_path: Path to markdown file

    Returns:
        _uds metadata dictionary, or None if not present
    """
    if not file_path.exists():
        return None

    try:
        content = file_path.read_text(encoding='utf-8')
        frontmatter, _ = _extract_frontmatter(content)
        return frontmatter.get('_uds')
    except Exception as e:
        logger.error(f"Failed to extract validation metadata from {file_path}: {e}")
        return None
