"""
Constants for docs-mcp server.

Centralizes all hardcoded paths, file names, and magic strings for easier configuration
and maintenance (REF-002, REF-003, QUA-003).
"""

from enum import Enum
from pathlib import Path

__all__ = [
    # Path constants
    'Paths',
    'PlanningPaths',
    # File name constants
    'Files',
    # Enums
    'TemplateNames',
    'ChangeType',
    'Severity',
    'ScanDepth',
    'FocusArea',
    'AuditSeverity',
    'AuditScope',
    'SeverityThreshold',
    'ValidationSeverity',
    'PlanStatus',
    'FileCategory',
    'RiskLevel',
    'AnalysisDepth',
    'PackageManager',
    'DependencyType',
    'VulnerabilitySeverity',
    'APIFramework',
    'HTTPMethod',
    'DatabaseSystem',
    'DatabaseType',
    'ORMFramework',
    'ConfigFormat',
    'TestFramework',
    'DocumentationType',
    # Validation constants
    'MAX_PATH_LENGTH',
    'TEMPLATE_NAME_PATTERN',
    'VERSION_PATTERN',
    # Security constants
    'EXCLUDE_DIRS',
    'MAX_FILE_SIZE',
    'ALLOWED_FILE_EXTENSIONS',
    # Context Expert constants
    'ContextExpertPaths',
    'ContextExpertStatus',
    'ContextExpertCapability',
    'ResourceType',
    'ExpertDomain',
    'EXPERT_ID_PATTERN',
]


class Paths:
    """Path constants for documentation and changelog locations."""
    CODEREF = 'coderef'
    FOUNDATION_DOCS = 'coderef/foundation-docs'
    CHANGELOG_DIR = 'coderef/changelog'
    TEMPLATES_DIR = 'templates/power'  # POWER framework templates only
    TOOL_TEMPLATES_DIR = 'templates/tools'  # Tool-specific templates (DELIVERABLES, communication)
    STANDARDS_DIR = 'coderef/standards'
    AUDITS_DIR = 'coderef/audits'
    CONTEXT_DIR = 'coderef'  # Base directory for context/ and working/
    INVENTORY_DIR = 'coderef/inventory'  # Inventory manifests directory
    RISK_ASSESSMENTS_DIR = 'coderef/risk-assessments'  # Risk assessment output directory


class Files:
    """File name constants."""
    README = 'README.md'
    ARCHITECTURE = 'ARCHITECTURE.md'
    API = 'API.md'
    COMPONENTS = 'COMPONENTS.md'
    SCHEMA = 'SCHEMA.md'
    USER_GUIDE = 'USER-GUIDE.md'
    CHANGELOG = 'CHANGELOG.json'
    CHANGELOG_SCHEMA = 'schema.json'
    # Standards documents
    UI_STANDARDS = 'UI-STANDARDS.md'
    BEHAVIOR_STANDARDS = 'BEHAVIOR-STANDARDS.md'
    UX_PATTERNS = 'UX-PATTERNS.md'
    COMPONENT_INDEX = 'COMPONENT-INDEX.md'
    # Audit reports
    AUDIT_REPORT = 'AUDIT-REPORT-{timestamp}.md'
    # Inventory manifests
    INVENTORY_MANIFEST = 'manifest.json'
    INVENTORY_SCHEMA = 'schema.json'
    INVENTORY_API_MANIFEST = 'api.json'
    INVENTORY_DATABASE_MANIFEST = 'database.json'
    INVENTORY_CONFIG_MANIFEST = 'config.json'
    INVENTORY_TESTS_MANIFEST = 'tests.json'
    INVENTORY_DOCUMENTATION_MANIFEST = 'documentation.json'
    # Workorder log
    WORKORDER_LOG = 'workorder-log.txt'


class TemplateNames(str, Enum):
    """Valid template names for documentation generation."""
    README = 'readme'
    ARCHITECTURE = 'architecture'
    API = 'api'
    COMPONENTS = 'components'
    MY_GUIDE = 'my-guide'
    SCHEMA = 'schema'
    USER_GUIDE = 'user-guide'


class ChangeType(str, Enum):
    """Valid changelog entry types."""
    BUGFIX = 'bugfix'
    ENHANCEMENT = 'enhancement'
    FEATURE = 'feature'
    BREAKING_CHANGE = 'breaking_change'
    DEPRECATION = 'deprecation'
    SECURITY = 'security'


class Severity(str, Enum):
    """Valid changelog severity levels."""
    CRITICAL = 'critical'
    MAJOR = 'major'
    MINOR = 'minor'
    PATCH = 'patch'


class ScanDepth(str, Enum):
    """Valid scan depth options for establish_standards tool."""
    QUICK = 'quick'
    STANDARD = 'standard'
    DEEP = 'deep'


class FocusArea(str, Enum):
    """Valid focus areas for establish_standards tool."""
    UI_COMPONENTS = 'ui_components'
    BEHAVIOR_PATTERNS = 'behavior_patterns'
    UX_FLOWS = 'ux_flows'
    ALL = 'all'


class AuditSeverity(str, Enum):
    """Valid severity levels for audit violations."""
    CRITICAL = 'critical'  # Must fix immediately - breaks functionality/accessibility
    MAJOR = 'major'  # Should fix soon - causes inconsistency or poor UX
    MINOR = 'minor'  # Style improvement - cosmetic inconsistency
    ALL = 'all'  # Filter for all severity levels


class AuditScope(str, Enum):
    """Valid scope options for audit_codebase tool."""
    UI_PATTERNS = 'ui_patterns'  # Audit UI component patterns only
    BEHAVIOR_PATTERNS = 'behavior_patterns'  # Audit behavior patterns only
    UX_PATTERNS = 'ux_patterns'  # Audit UX patterns only
    ALL = 'all'  # Audit all pattern categories


class SeverityThreshold(str, Enum):
    """Valid severity threshold options for check_consistency tool."""
    CRITICAL = 'critical'  # Fail only on critical violations
    MAJOR = 'major'  # Fail on critical and major violations (default)
    MINOR = 'minor'  # Fail on any violation (all severities)

    @classmethod
    def values(cls) -> list[str]:
        """Return list of all valid severity threshold values."""
        return [e.value for e in cls]


# Validation constants
MAX_PATH_LENGTH = 1000
TEMPLATE_NAME_PATTERN = r'^[a-zA-Z0-9_-]+$'
VERSION_PATTERN = r'^\d+\.\d+\.\d+$'

# Standards scanner security constants (SEC-004, SEC-007, SEC-008)
EXCLUDE_DIRS = ['node_modules', '.git', 'dist', 'build', '.next', 'out', 'coverage', '__pycache__', '.venv', 'venv', 'vendor']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB - skip files larger than this
ALLOWED_FILE_EXTENSIONS = ['.tsx', '.jsx', '.ts', '.js', '.css', '.scss', '.less']


# Planning Workflow System Constants
class PlanningPaths:
    """Paths for planning workflow system."""
    TEMPLATE_PATH = Path('mcp-specific-context') / 'feature-implementation-planning-standard.json'
    TEMPLATE_AI_PATH = Path('coderef') / 'context' / 'planning-template-for-ai.json'  # AI-optimized template
    PLANS_DIR = Path('plans')
    REVIEWS_DIR = Path('coderef') / 'planning-reviews'
    WORKING_DIR = Path('coderef') / 'working'  # Working directory for active features


class ValidationSeverity(Enum):
    """Validation issue severity levels (used in plan validation)."""
    CRITICAL = 'critical'  # -10 points from score
    MAJOR = 'major'        # -5 points from score
    MINOR = 'minor'        # -1 point from score


class PlanStatus(Enum):
    """Implementation plan status."""
    DRAFT = 'draft'
    REVIEWING = 'reviewing'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    IMPLEMENTED = 'implemented'


class FileCategory(str, Enum):
    """Valid file categories for inventory classification."""
    CORE = 'core'  # Core infrastructure (server, main entry points)
    SOURCE = 'source'  # Source code (business logic, modules)
    TEMPLATE = 'template'  # Templates and static resources
    CONFIG = 'config'  # Configuration files
    TEST = 'test'  # Test files
    DOCS = 'docs'  # Documentation files
    UNKNOWN = 'unknown'  # Uncategorized files


class RiskLevel(str, Enum):
    """Valid risk levels for file inventory."""
    LOW = 'low'  # Small, simple files with minimal impact
    MEDIUM = 'medium'  # Moderate complexity or moderate impact
    HIGH = 'high'  # Complex or high-impact files
    CRITICAL = 'critical'  # Critical infrastructure or security-sensitive


class AnalysisDepth(str, Enum):
    """Valid analysis depth options for inventory generation."""
    QUICK = 'quick'  # Fast scan with basic metadata only
    STANDARD = 'standard'  # Standard analysis with categorization and basic dependencies
    DEEP = 'deep'  # Deep analysis with full dependency parsing and complexity metrics


class PackageManager(str, Enum):
    """Valid package manager types for dependency analysis."""
    NPM = 'npm'  # Node.js package manager
    PIP = 'pip'  # Python package installer
    CARGO = 'cargo'  # Rust package manager
    COMPOSER = 'composer'  # PHP dependency manager


class DependencyType(str, Enum):
    """Valid dependency types for package analysis."""
    DIRECT = 'direct'  # Direct production dependencies
    DEV = 'dev'  # Development dependencies
    PEER = 'peer'  # Peer dependencies (npm)
    TRANSITIVE = 'transitive'  # Transitive (indirect) dependencies


class VulnerabilitySeverity(str, Enum):
    """Valid vulnerability severity levels."""
    CRITICAL = 'critical'  # Critical severity - immediate action required
    HIGH = 'high'  # High severity - fix as soon as possible
    MEDIUM = 'medium'  # Medium severity - fix in next release
    LOW = 'low'  # Low severity - fix when convenient


class APIFramework(str, Enum):
    """Valid API framework types for endpoint discovery."""
    FASTAPI = 'fastapi'  # FastAPI (Python)
    FLASK = 'flask'  # Flask (Python)
    EXPRESS = 'express'  # Express.js (Node.js)
    GRAPHQL = 'graphql'  # GraphQL


class HTTPMethod(str, Enum):
    """Valid HTTP methods for REST endpoints."""
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'


class DatabaseSystem(str, Enum):
    """Valid database systems for schema discovery."""
    POSTGRESQL = 'postgresql'  # PostgreSQL
    MYSQL = 'mysql'  # MySQL/MariaDB
    MONGODB = 'mongodb'  # MongoDB
    SQLITE = 'sqlite'  # SQLite


class DatabaseType(str, Enum):
    """Valid database paradigms."""
    SQL = 'sql'  # Relational SQL databases
    NOSQL = 'nosql'  # NoSQL document/key-value stores


class ORMFramework(str, Enum):
    """Valid ORM/ODM frameworks for schema extraction."""
    SQLALCHEMY = 'sqlalchemy'  # SQLAlchemy (Python)
    SEQUELIZE = 'sequelize'  # Sequelize (Node.js)
    MONGOOSE = 'mongoose'  # Mongoose (MongoDB Node.js)


class ConfigFormat(str, Enum):
    """Valid configuration file formats."""
    JSON = 'json'  # JSON configuration files
    YAML = 'yaml'  # YAML configuration files
    TOML = 'toml'  # TOML configuration files
    INI = 'ini'  # INI/CFG configuration files
    ENV = 'env'  # Environment variable files (.env)


class TestFramework(str, Enum):
    """Valid test framework types for test discovery."""
    PYTEST = 'pytest'  # pytest (Python)
    UNITTEST = 'unittest'  # unittest (Python)
    JEST = 'jest'  # Jest (JavaScript/TypeScript)
    MOCHA = 'mocha'  # Mocha (JavaScript)
    VITEST = 'vitest'  # Vitest (JavaScript/TypeScript)


class DocumentationType(str, Enum):
    """Valid documentation format types for documentation discovery."""
    MARKDOWN = 'markdown'  # Markdown (.md) files
    RESTRUCTURED_TEXT = 'restructured_text'  # reStructuredText (.rst) files
    ASCIIDOC = 'asciidoc'  # AsciiDoc (.adoc) files
    HTML = 'html'  # HTML (.html) files
    ORGMODE = 'orgmode'  # Org-mode (.org) files
    PLAINTEXT = 'plaintext'  # Plain text (.txt) files

# Context Expert System Constants (NEW in v3.0.0)
class ContextExpertPaths:
    """Paths for context expert system."""
    ROOT = 'coderef/experts'
    EXPERTS = 'coderef/experts'
    CACHE = 'coderef/experts/cache'
    INDEX = 'coderef/experts/index.json'
    REGISTRY = 'coderef/experts/experts.json'  # Comprehensive registry file


class ContextExpertStatus(str, Enum):
    """Status of a context expert."""
    ACTIVE = 'active'      # Expert is up-to-date and ready
    STALE = 'stale'        # Expert context needs refresh
    ARCHIVED = 'archived'  # Expert is no longer active


class ContextExpertCapability(str, Enum):
    """Capabilities a context expert can have."""
    ANSWER_QUESTIONS = 'answer_questions'  # Can answer questions about the resource
    REVIEW_CHANGES = 'review_changes'      # Can review changes to the resource
    GENERATE_DOCS = 'generate_docs'        # Can generate documentation


class ResourceType(str, Enum):
    """Type of resource a context expert is assigned to."""
    FILE = 'file'           # Single file expert
    DIRECTORY = 'directory' # Directory/module expert


class ExpertDomain(str, Enum):
    """Domain specialization for context experts."""
    UI = 'ui'           # Components, styling, accessibility
    DB = 'db'           # Schemas, migrations, queries
    SCRIPT = 'script'   # Build scripts, automation
    DOCS = 'docs'       # Documentation structure, templates
    API = 'api'         # API endpoints, handlers
    CORE = 'core'       # Core business logic
    TEST = 'test'       # Testing infrastructure
    INFRA = 'infra'     # Infrastructure, deployment


# Context Expert validation pattern
EXPERT_ID_PATTERN = r'^CE-[a-zA-Z0-9_-]+-\d{3}$'
