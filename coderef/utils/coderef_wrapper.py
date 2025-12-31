#!/usr/bin/env python3
"""
coderef_wrapper.py - Wrapper utilities for calling parse_coderef_data.py scripts

Provides simple Python functions for MCP servers to call the production-ready
parse_coderef_data.py scripts without subprocess overhead.

Usage:
    from coderef.utils.coderef_wrapper import preprocess_index, generate_foundation_docs

    # Preprocess large index.json
    data = preprocess_index(project_path)

    # Generate all foundation docs
    docs = generate_foundation_docs(project_path)
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


# Path to coderef-system scripts
CODEREF_SYSTEM = Path("C:/Users/willh/Desktop/projects/coderef-system")
PREPROCESSOR_SCRIPT = CODEREF_SYSTEM / "packages" / "parse_coderef_data.py"
GENERATOR_SCRIPT = CODEREF_SYSTEM / "scripts" / "parse_coderef_data.py"


def preprocess_index(project_path: str) -> Dict:
    """
    Call packages/parse_coderef_data.py to preprocess .coderef/index.json

    This extracts statistics and groups elements by type, file, and package.
    Useful for large index.json files (>100KB) before doc generation.

    Args:
        project_path: Absolute path to project directory

    Returns:
        Dict with keys: statistics, by_type, by_file, by_package, sample_elements

    Raises:
        FileNotFoundError: If .coderef/index.json doesn't exist
        subprocess.CalledProcessError: If script execution fails

    Example:
        >>> data = preprocess_index("C:/Users/willh/.mcp-servers/coderef-context")
        >>> print(data['statistics']['total_elements'])
        160
    """
    project_path = Path(project_path).resolve()
    index_path = project_path / ".coderef" / "index.json"

    if not index_path.exists():
        raise FileNotFoundError(f".coderef/index.json not found in {project_path}")

    # Run preprocessor script
    result = subprocess.run(
        [sys.executable, str(PREPROCESSOR_SCRIPT)],
        cwd=str(project_path),
        capture_output=True,
        text=True,
        check=True
    )

    # Read generated output
    output_path = project_path / ".coderef" / "doc_generation_data.json"
    if output_path.exists():
        return json.loads(output_path.read_text(encoding='utf-8'))
    else:
        raise RuntimeError("Preprocessor did not generate doc_generation_data.json")


def generate_foundation_docs(project_path: str, output_dir: Optional[str] = None) -> Dict[str, str]:
    """
    Call scripts/parse_coderef_data.py to generate all foundation documentation

    Generates 8 markdown files from .coderef/ data:
    - README.md, ARCHITECTURE.md, API.md, SCHEMA.md
    - COMPONENTS.md, DEPENDENCIES.md, TESTING.md, CHANGELOG.md

    Args:
        project_path: Absolute path to project directory
        output_dir: Optional custom output directory (default: coderef/foundation-docs/)

    Returns:
        Dict mapping doc names to file paths

    Raises:
        FileNotFoundError: If .coderef/index.json doesn't exist
        subprocess.CalledProcessError: If script execution fails

    Example:
        >>> docs = generate_foundation_docs("C:/Users/willh/.mcp-servers/coderef-workflow")
        >>> print(docs.keys())
        dict_keys(['README', 'ARCHITECTURE', 'API', 'SCHEMA', ...])
    """
    project_path = Path(project_path).resolve()
    index_path = project_path / ".coderef" / "index.json"

    if not index_path.exists():
        raise FileNotFoundError(f".coderef/index.json not found in {project_path}")

    # Run generator script
    result = subprocess.run(
        [sys.executable, str(GENERATOR_SCRIPT), str(project_path)],
        capture_output=True,
        text=True,
        check=True
    )

    # Determine output directory
    if output_dir:
        docs_dir = Path(output_dir)
    else:
        docs_dir = project_path / "coderef" / "foundation-docs"

    # Map generated files
    doc_files = {
        "README": docs_dir / "README.md",
        "ARCHITECTURE": docs_dir / "ARCHITECTURE.md",
        "API": docs_dir / "API.md",
        "SCHEMA": docs_dir / "SCHEMA.md",
        "COMPONENTS": docs_dir / "COMPONENTS.md",
        "DEPENDENCIES": docs_dir / "DEPENDENCIES.md",
        "TESTING": docs_dir / "TESTING.md",
        "CHANGELOG": docs_dir / "CHANGELOG.md"
    }

    # Return only existing files
    return {name: str(path) for name, path in doc_files.items() if path.exists()}


def read_coderef_output(project_path: str, output_type: str) -> Dict:
    """
    Read a specific .coderef/ output file

    Convenience function for reading common .coderef/ outputs.

    Args:
        project_path: Absolute path to project directory
        output_type: Type of output to read
            - 'index' → .coderef/index.json
            - 'graph' → .coderef/graph.json
            - 'context' → .coderef/context.json
            - 'patterns' → .coderef/reports/patterns.json
            - 'coverage' → .coderef/reports/coverage.json
            - 'drift' → .coderef/reports/drift.json

    Returns:
        Parsed JSON content

    Raises:
        FileNotFoundError: If output file doesn't exist
        ValueError: If output_type is invalid

    Example:
        >>> patterns = read_coderef_output(project_path, 'patterns')
        >>> print(patterns['common_patterns'])
    """
    project_path = Path(project_path).resolve()
    coderef_dir = project_path / ".coderef"

    output_map = {
        'index': coderef_dir / "index.json",
        'graph': coderef_dir / "graph.json",
        'context': coderef_dir / "context.json",
        'patterns': coderef_dir / "reports" / "patterns.json",
        'coverage': coderef_dir / "reports" / "coverage.json",
        'drift': coderef_dir / "reports" / "drift.json",
        'validation': coderef_dir / "reports" / "validation.json"
    }

    if output_type not in output_map:
        valid_types = ', '.join(output_map.keys())
        raise ValueError(f"Invalid output_type '{output_type}'. Valid: {valid_types}")

    output_path = output_map[output_type]

    if not output_path.exists():
        raise FileNotFoundError(f"{output_type} not found at {output_path}")

    return json.loads(output_path.read_text(encoding='utf-8'))


def check_coderef_available(project_path: str) -> bool:
    """
    Check if .coderef/ structure exists and is populated

    Args:
        project_path: Absolute path to project directory

    Returns:
        True if .coderef/index.json exists and is non-empty

    Example:
        >>> if check_coderef_available(project_path):
        ...     data = preprocess_index(project_path)
        ... else:
        ...     print("Run populate-coderef.py first")
    """
    project_path = Path(project_path).resolve()
    index_path = project_path / ".coderef" / "index.json"

    if not index_path.exists():
        return False

    try:
        index = json.loads(index_path.read_text(encoding='utf-8'))
        return len(index) > 0
    except:
        return False
