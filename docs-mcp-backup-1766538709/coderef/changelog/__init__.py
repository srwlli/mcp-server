"""Changelog management for docs-mcp."""

from pathlib import Path

CHANGELOG_DIR = Path(__file__).parent
CHANGELOG_FILE = CHANGELOG_DIR / "CHANGELOG.json"
SCHEMA_FILE = CHANGELOG_DIR / "schema.json"

__all__ = ['CHANGELOG_DIR', 'CHANGELOG_FILE', 'SCHEMA_FILE']
