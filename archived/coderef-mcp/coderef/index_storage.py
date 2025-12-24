"""
Index Storage Module for CodeRef MCP Server

Provides persistent storage for CodeRef index and graph data using the
same format as the CodeRef CLI (.coderef/ directory).

File format:
- .coderef/index.json: Array of elements [{type, name, file, line, exported}]
- .coderef/graph.json: Dependency graph {nodes: [], edges: []}
"""

import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

CODEREF_DIR = ".coderef"
INDEX_FILE = "index.json"
GRAPH_FILE = "graph.json"


def get_coderef_path(project_path: str) -> Path:
    """Get the .coderef directory path for a project."""
    return Path(project_path) / CODEREF_DIR


def ensure_coderef_dir(project_path: str) -> Path:
    """Ensure .coderef directory exists, create if needed."""
    coderef_path = get_coderef_path(project_path)
    coderef_path.mkdir(parents=True, exist_ok=True)
    return coderef_path


def load_index(project_path: str) -> Optional[list[dict[str, Any]]]:
    """
    Load index from .coderef/index.json.

    Args:
        project_path: Root directory of the project

    Returns:
        List of element dictionaries, or None if file doesn't exist
    """
    index_path = get_coderef_path(project_path) / INDEX_FILE

    if not index_path.exists():
        logger.debug(f"No index file found at {index_path}")
        return None

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"Loaded index with {len(data)} elements from {index_path}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse index file {index_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load index from {index_path}: {e}")
        return None


def save_index(project_path: str, elements: list[dict[str, Any]]) -> bool:
    """
    Save index to .coderef/index.json using atomic write.

    Args:
        project_path: Root directory of the project
        elements: List of element dictionaries to save

    Returns:
        True if save succeeded, False otherwise
    """
    coderef_path = ensure_coderef_dir(project_path)
    index_path = coderef_path / INDEX_FILE

    try:
        # Write to temp file first for atomic operation
        fd, temp_path = tempfile.mkstemp(suffix=".json", dir=str(coderef_path))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(elements, f, indent=2)

            # Atomic rename (works on same filesystem)
            shutil.move(temp_path, index_path)
            logger.info(f"Saved index with {len(elements)} elements to {index_path}")
            return True
        except Exception:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    except Exception as e:
        logger.error(f"Failed to save index to {index_path}: {e}")
        return False


def load_graph(project_path: str) -> Optional[dict[str, Any]]:
    """
    Load dependency graph from .coderef/graph.json.

    Args:
        project_path: Root directory of the project

    Returns:
        Graph dictionary with nodes and edges, or None if file doesn't exist
    """
    graph_path = get_coderef_path(project_path) / GRAPH_FILE

    if not graph_path.exists():
        logger.debug(f"No graph file found at {graph_path}")
        return None

    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])
            logger.info(f"Loaded graph with {len(nodes)} nodes, {len(edges)} edges from {graph_path}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse graph file {graph_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load graph from {graph_path}: {e}")
        return None


def save_graph(project_path: str, graph: dict[str, Any]) -> bool:
    """
    Save dependency graph to .coderef/graph.json using atomic write.

    Args:
        project_path: Root directory of the project
        graph: Graph dictionary with nodes and edges

    Returns:
        True if save succeeded, False otherwise
    """
    coderef_path = ensure_coderef_dir(project_path)
    graph_path = coderef_path / GRAPH_FILE

    try:
        # Write to temp file first for atomic operation
        fd, temp_path = tempfile.mkstemp(suffix=".json", dir=str(coderef_path))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(graph, f, indent=2)

            # Atomic rename
            shutil.move(temp_path, graph_path)
            nodes = graph.get("nodes", [])
            edges = graph.get("edges", [])
            logger.info(f"Saved graph with {len(nodes)} nodes, {len(edges)} edges to {graph_path}")
            return True
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    except Exception as e:
        logger.error(f"Failed to save graph to {graph_path}: {e}")
        return False


def get_index_mtime(project_path: str) -> Optional[float]:
    """Get modification time of the index file."""
    index_path = get_coderef_path(project_path) / INDEX_FILE
    if index_path.exists():
        return index_path.stat().st_mtime
    return None


def is_index_stale(project_path: str, source_extensions: list[str] = None) -> bool:
    """
    Check if the index is stale by comparing file modification times.

    An index is considered stale if any source file in the project
    has been modified after the index was last updated.

    Args:
        project_path: Root directory of the project
        source_extensions: File extensions to check (default: common code extensions)

    Returns:
        True if index is stale or doesn't exist, False if index is fresh
    """
    if source_extensions is None:
        source_extensions = [
            ".ts", ".tsx", ".js", ".jsx",  # TypeScript/JavaScript
            ".py",  # Python
            ".go",  # Go
            ".rs",  # Rust
            ".java",  # Java
            ".cs",  # C#
            ".cpp", ".cc", ".c", ".h", ".hpp",  # C/C++
        ]

    index_mtime = get_index_mtime(project_path)

    if index_mtime is None:
        logger.debug(f"No index found for {project_path}, considered stale")
        return True

    project_root = Path(project_path)

    # Common directories to skip
    skip_dirs = {
        "node_modules", ".git", ".coderef", "__pycache__",
        "dist", "build", ".next", "venv", ".venv", "env"
    }

    try:
        for root, dirs, files in os.walk(project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]

            for file in files:
                if any(file.endswith(ext) for ext in source_extensions):
                    file_path = Path(root) / file
                    try:
                        file_mtime = file_path.stat().st_mtime
                        if file_mtime > index_mtime:
                            logger.debug(f"Index stale: {file_path} modified after index")
                            return True
                    except OSError:
                        # Skip files we can't stat
                        continue

        logger.debug(f"Index is fresh for {project_path}")
        return False

    except Exception as e:
        logger.error(f"Error checking index freshness: {e}")
        # If we can't check, assume stale to be safe
        return True


def index_exists(project_path: str) -> bool:
    """Check if an index file exists for the project."""
    index_path = get_coderef_path(project_path) / INDEX_FILE
    return index_path.exists()


def get_index_info(project_path: str) -> Optional[dict[str, Any]]:
    """
    Get metadata about the existing index.

    Returns:
        Dictionary with index info, or None if no index exists
    """
    coderef_path = get_coderef_path(project_path)
    index_path = coderef_path / INDEX_FILE
    graph_path = coderef_path / GRAPH_FILE

    if not index_path.exists():
        return None

    info = {
        "index_path": str(index_path),
        "index_exists": True,
        "graph_exists": graph_path.exists(),
    }

    try:
        stat = index_path.stat()
        info["index_mtime"] = stat.st_mtime
        info["index_size_bytes"] = stat.st_size

        # Load and count elements
        index_data = load_index(project_path)
        if index_data:
            info["element_count"] = len(index_data)

        # Check freshness
        info["is_stale"] = is_index_stale(project_path)

    except Exception as e:
        logger.error(f"Error getting index info: {e}")

    return info
