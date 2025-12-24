"""
Type definitions for coderef-docs server (QUA-001).

Provides TypedDicts and type aliases for better type safety and IDE support.
"""

from typing import TypedDict, List, Optional, Dict, Any
from pathlib import Path

__all__ = [
    # Generator types
    'PathsDict',
    'TemplateInfoDict',
    'TemplateDict',
    'WorkflowStepDict',
    # Changelog types
    'ChangeDict',
    'VersionEntryDict',
    # Standards types
    'UIPatternDict',
    'BehaviorPatternDict',
    'UXPatternDict',
    'ComponentMetadataDict',
    'StandardsResultDict',
    # Audit types
    'StandardsDataDict',
    'AuditViolationDict',
    'ComplianceScoreDict',
    'ViolationStatsDict',
    'AuditResultDict',
    # Consistency types
    'ConsistencyResultDict',
    'CheckResultDict',
    # Planning workflow types
    'PlanningTemplateDict',
    'PreparationSummaryDict',
    'ValidationIssueDict',
    'ValidationResultDict',
    'PlanReviewDict',
    'PlanResultDict',
    # Inventory types
    'FileMetadataDict',
    'ProjectMetricsDict',
    'InventoryManifestDict',
    'InventoryResultDict',
    # Dependency inventory types
    'DependencyDict',
    'VulnerabilityDict',
    'DependencyMetricsDict',
    'DependencyManifestDict',
    'DependencyResultDict',
    # API inventory types
    'APIEndpointDict',
    'APIMetricsDict',
    'APIManifestDict',
    'APIResultDict',
    # Database inventory types
    'DatabaseColumnDict',
    'DatabaseFieldDict',
    'DatabaseRelationshipDict',
    'DatabaseIndexDict',
    'DatabaseSchemaDict',
    'DatabaseMetricsDict',
    'DatabaseManifestDict',
    'DatabaseResultDict',
    # Configuration inventory types
    'ConfigFileDict',
    'ConfigMetricsDict',
    'ConfigManifestDict',
    'ConfigResultDict',
    # Test inventory types
    'TestFileDict',
    'TestMetricsDict',
    'TestManifestDict',
    'TestResultDict',
    # Documentation inventory types
    'DocumentationFileDict',
    'DocumentationManifestDict',
    'DocumentationResultDict',
    # Risk assessment types
    'RiskDimensionDict',
    'CompositeScoreDict',
    'RecommendationDict',
    'MitigationStrategyDict',
    'OptionComparisonDict',
    'ProjectContextDict',
    'ProposedChangeDict',
    'RiskAssessmentDict',
    'RiskAssessmentResultDict',
]


class PathsDict(TypedDict):
    """Return type for prepare_generation() method."""
    project_path: Path
    output_dir: Path


class TemplateInfoDict(TypedDict, total=False):
    """Template metadata extracted from template files.

    All fields are optional since they're parsed from template content.
    """
    framework: str
    purpose: str
    save_as: str
    store_as: str


class TemplateDict(TypedDict, total=False):
    """Template information returned by get_templates_for_generation().

    All templates have: template_name, template_content, status
    Error templates also have: error
    """
    template_name: str
    template_content: str
    status: str
    error: str  # Present only if status == 'error'


class WorkflowStepDict(TypedDict, total=False):
    """Workflow step information from get_workflow_info().

    Contains template metadata plus template_name.
    May contain 'error' field if template loading failed.
    """
    template_name: str
    framework: str
    purpose: str
    save_as: str
    store_as: str
    error: str  # Present only if there was an error


class ChangeDict(TypedDict, total=False):
    """Changelog change entry.

    Required fields: id, type, severity, title, description, files, reason, impact, breaking
    Optional fields: migration
    """
    id: str
    type: str
    severity: str
    title: str
    description: str
    files: List[str]
    reason: str
    impact: str
    breaking: bool
    migration: str  # Optional


class VersionEntryDict(TypedDict, total=False):
    """Changelog version entry.

    Required fields: version, date, summary, changes
    Optional fields: contributors
    """
    version: str
    date: str
    summary: str
    changes: List[ChangeDict]
    contributors: List[str]  # Optional


# Standards Generator TypedDicts (INFRA-006)

class UIPatternDict(TypedDict, total=False):
    """UI pattern data structure."""
    buttons: dict  # {size: [...], variant: [...], common_props: [...]}
    modals: dict   # {size: [...], position: [...], backdrop: [...]}
    forms: dict    # {input_types: [...], validation: [...], error_states: [...]}
    colors: dict   # {hex_codes: [...], css_vars: [...], theme_colors: [...]}
    typography: dict  # {font_sizes: [...], weights: [...], families: [...]}
    spacing: dict  # {margins: [...], paddings: [...], gaps: [...]}
    icons: dict    # {library: str, sizes: [...], colors: [...]}


class BehaviorPatternDict(TypedDict, total=False):
    """Behavior pattern data structure."""
    error_handling: dict  # {patterns: [...], messages: [...], recovery: [...]}
    loading_states: dict  # {indicators: [...], skeleton: [...], flags: [...]}
    toasts: dict  # {duration: [...], position: [...], types: [...]}
    validation: dict  # {rules: [...], timing: [...], messages: [...]}
    api_communication: dict  # {error_handling: [...], retries: [...]}


class UXPatternDict(TypedDict, total=False):
    """UX pattern data structure."""
    navigation: dict  # {routing: [...], breadcrumbs: [...], back_buttons: [...]}
    permissions: dict  # {auth_guards: [...], role_checks: [...], fallbacks: [...]}
    offline_handling: dict  # {detection: [...], fallbacks: [...], sync: [...]}
    accessibility: dict  # {aria: [...], keyboard: [...], screen_readers: [...]}


class ComponentMetadataDict(TypedDict):
    """Component inventory metadata."""
    name: str
    type: str  # 'ui' | 'layout' | 'utility'
    usage_count: int
    status: str  # 'active' | 'deprecated' | 'experimental'
    props: List[str]
    file_path: str
    notes: str


class StandardsResultDict(TypedDict):
    """Result from save_standards operation."""
    files: List[str]  # List of created file paths
    patterns_count: int  # Total patterns discovered
    success: bool
    ui_patterns_count: int
    behavior_patterns_count: int
    ux_patterns_count: int
    components_count: int


# Audit Generator TypedDicts (INFRA-006 Tool #9)

class StandardsDataDict(TypedDict, total=False):
    """Parsed standards data from markdown documents."""
    ui_patterns: dict  # {buttons: {allowed_sizes: [...], allowed_variants: [...]}, modals: {...}, colors: {...}}
    behavior_patterns: dict  # {error_messages: {expected_patterns: [...]}, loading_states: {required: bool}}
    ux_patterns: dict  # {navigation: {routing_detected: bool}, accessibility: {aria_required: bool}}
    components: dict  # {known_components: [...]}
    source_files: List[str]  # List of standards files that were parsed
    parse_errors: List[str]  # List of warnings/errors during parsing


class AuditViolationDict(TypedDict, total=False):
    """Single violation detected during audit."""
    id: str  # Unique violation ID (e.g., 'V-001')
    type: str  # Violation type (e.g., 'non_standard_button_size')
    severity: str  # 'critical', 'major', or 'minor'
    category: str  # 'ui_patterns', 'behavior_patterns', 'ux_patterns'
    file_path: str  # Relative path to file
    line_number: int  # Line where violation occurs
    column: int  # Column position (optional)
    message: str  # Human-readable violation description
    actual_value: str  # What was found in code
    expected_value: str  # What standards specify
    fix_suggestion: str  # Actionable fix instruction
    code_snippet: str  # 3-5 lines of context around violation


class ComplianceScoreDict(TypedDict):
    """Compliance metrics by category."""
    overall_score: int  # 0-100
    ui_compliance: int  # 0-100
    behavior_compliance: int  # 0-100
    ux_compliance: int  # 0-100
    grade: str  # A/B/C/D/F based on score
    passing: bool  # True if score >= 80


class ViolationStatsDict(TypedDict):
    """Statistics about violations found."""
    total_violations: int
    critical_count: int
    major_count: int
    minor_count: int
    violations_by_file: dict  # Mapping file paths to counts
    violations_by_type: dict  # Mapping violation types to counts
    most_violated_file: str  # File with most violations
    most_common_violation: str  # Most frequent violation type


class AuditResultDict(TypedDict, total=False):
    """Complete audit results."""
    report_path: str  # Path to generated report
    compliance_score: int  # 0-100
    compliance_details: ComplianceScoreDict
    violation_stats: ViolationStatsDict
    violations: List[AuditViolationDict]
    scan_metadata: dict  # {timestamp: str, duration: float, files_scanned: int}
    success: bool


# Consistency Checker TypedDicts (INFRA-006 Tool #10)

class ConsistencyResultDict(TypedDict, total=False):
    """Result from check_consistency operation."""
    status: str  # 'pass' | 'fail'
    violations_found: int
    violations: List[AuditViolationDict]  # Reuses AuditViolationDict structure
    files_checked: int
    files_list: List[str]  # List of files that were checked
    duration: float  # Seconds
    severity_threshold: str  # 'critical', 'major', or 'minor'
    exit_code: int  # 0 (pass) | 1 (fail)


class CheckResultDict(TypedDict, total=False):
    """Per-file check result."""
    file_path: str
    violations: List[AuditViolationDict]
    clean: bool  # True if no violations found


# Planning Workflow System TypedDicts

class PlanningTemplateDict(TypedDict):
    """Return type for get_planning_template tool."""
    section: str
    content: dict | str


class PreparationSummaryDict(TypedDict):
    """Return type for analyze_project_for_planning tool (section 0)."""
    foundation_docs: dict
    coding_standards: dict
    reference_components: dict
    key_patterns_identified: List[str]
    technology_stack: dict
    project_structure: dict
    gaps_and_risks: List[str]


class ValidationIssueDict(TypedDict):
    """Individual validation issue."""
    severity: str  # 'critical' | 'major' | 'minor'
    section: str
    issue: str
    suggestion: str


class ValidationResultDict(TypedDict):
    """Return type for validate_implementation_plan tool."""
    validation_result: str  # 'PASS' | 'PASS_WITH_WARNINGS' | 'NEEDS_REVISION' | 'FAIL'
    score: int  # 0-100
    issues: List[ValidationIssueDict]
    checklist_results: dict
    approved: bool


class PlanReviewDict(TypedDict):
    """Return type for generate_plan_review_report tool."""
    report_markdown: str
    summary: str
    approval_status: str


class PlanResultDict(TypedDict):
    """Return type for create_plan tool."""
    plan_path: str  # Path to saved plan.json file
    feature_name: str
    sections_completed: List[str]  # List of section names (0-9)
    has_context: bool  # Whether context.json was available
    has_analysis: bool  # Whether analysis data was available
    status: str  # 'complete' | 'partial'
    next_steps: List[str]  # Recommended next actions
    success: bool


# Inventory Generator TypedDicts

class FileMetadataDict(TypedDict, total=False):
    """Individual file metadata in inventory manifest."""
    path: str  # Relative path from project root
    name: str  # File name including extension
    extension: str  # File extension (e.g., .py, .js, .md)
    size: int  # File size in bytes
    lines: int  # Number of lines in file
    category: str  # File category: core, source, template, config, test, docs, unknown
    risk_level: str  # Risk level: low, medium, high, critical
    role: str  # Role or purpose of the file
    description: str  # Brief description of file contents
    dependencies: List[str]  # List of imports/dependencies detected
    last_modified: str  # ISO 8601 timestamp of last modification
    language: str  # Primary programming language
    complexity: str  # Complexity level: simple, moderate, complex
    sensitive: bool  # Whether file contains sensitive data


class ProjectMetricsDict(TypedDict, total=False):
    """Project-level metrics and health indicators."""
    total_files: int  # Total number of files
    total_size: int  # Total size in bytes
    total_lines: int  # Total lines of code
    file_categories: dict  # Count by category {core: int, source: int, ...}
    risk_distribution: dict  # Count by risk {low: int, medium: int, high: int, critical: int}
    language_breakdown: dict  # Count by language {python: int, javascript: int, ...}


class InventoryManifestDict(TypedDict):
    """Complete inventory manifest structure."""
    project_name: str  # Name of the project
    project_path: str  # Absolute path to project directory
    generated_at: str  # ISO 8601 timestamp when manifest was generated
    analysis_depth: str  # Depth of analysis: quick, standard, deep
    metrics: ProjectMetricsDict  # Project-level metrics
    files: List[FileMetadataDict]  # Array of file metadata


class InventoryResultDict(TypedDict):
    """Return type for inventory_manifest tool."""
    manifest_path: str  # Path to saved manifest.json file
    files_analyzed: int  # Number of files analyzed
    project_name: str  # Name of the project
    analysis_depth: str  # Depth of analysis performed
    metrics: ProjectMetricsDict  # Project metrics summary
    success: bool


# Dependency Inventory TypedDicts (Phase 2: Dependency Analysis)

class DependencyDict(TypedDict, total=False):
    """Individual dependency metadata."""
    name: str  # Package name
    version: str  # Current version installed
    type: str  # Dependency type: direct, dev, peer, transitive
    ecosystem: str  # Package manager: npm, pip, cargo, composer
    latest_version: str  # Latest available version (from registry API)
    outdated: bool  # Whether current version is behind latest
    license: str  # Package license (e.g., MIT, Apache-2.0)
    vulnerabilities: List[str]  # List of CVE IDs affecting this package
    vulnerability_count: int  # Number of vulnerabilities found
    severity: str  # Highest vulnerability severity: critical, high, medium, low
    description: str  # Package description
    homepage: str  # Package homepage URL


class VulnerabilityDict(TypedDict, total=False):
    """Security vulnerability metadata."""
    id: str  # CVE ID or vulnerability identifier
    package_name: str  # Affected package name
    ecosystem: str  # Package ecosystem: npm, pip, cargo, composer
    severity: str  # Severity level: critical, high, medium, low
    summary: str  # Brief vulnerability description
    details: str  # Detailed vulnerability explanation
    affected_versions: str  # Version range affected (e.g., "<1.2.3")
    fixed_version: str  # First version with fix
    published: str  # ISO 8601 timestamp when vulnerability was published
    modified: str  # ISO 8601 timestamp when last modified
    references: List[str]  # URLs to advisories, patches, etc.
    cvss_score: float  # CVSS score (0.0-10.0)


class DependencyMetricsDict(TypedDict, total=False):
    """Dependency analysis metrics."""
    total_dependencies: int  # Total dependencies across all types
    direct_count: int  # Direct production dependencies
    dev_count: int  # Development dependencies
    peer_count: int  # Peer dependencies (npm only)
    transitive_count: int  # Transitive (indirect) dependencies
    outdated_count: int  # Number of outdated packages
    vulnerable_count: int  # Number of packages with vulnerabilities
    critical_vulnerabilities: int  # Count of critical severity vulnerabilities
    high_vulnerabilities: int  # Count of high severity vulnerabilities
    medium_vulnerabilities: int  # Count of medium severity vulnerabilities
    low_vulnerabilities: int  # Count of low severity vulnerabilities
    license_breakdown: dict  # Count by license type {MIT: int, Apache-2.0: int, ...}
    ecosystem_breakdown: dict  # Count by ecosystem {npm: int, pip: int, cargo: int, composer: int}


class DependencyManifestDict(TypedDict):
    """Complete dependency inventory manifest."""
    project_name: str  # Name of the project
    project_path: str  # Absolute path to project directory
    generated_at: str  # ISO 8601 timestamp when manifest was generated
    package_managers: List[str]  # Detected package managers (npm, pip, cargo, composer)
    dependencies: dict  # Dependencies by ecosystem {npm: {direct: [...], dev: [...]}, pip: {...}}
    vulnerabilities: List[VulnerabilityDict]  # All vulnerabilities found
    metrics: DependencyMetricsDict  # Aggregated metrics


class DependencyResultDict(TypedDict):
    """Return type for dependency_inventory tool."""
    manifest_path: str  # Path to saved dependencies.json file
    package_managers: List[str]  # Detected package managers
    total_dependencies: int  # Total dependencies analyzed
    vulnerable_count: int  # Number of packages with vulnerabilities
    outdated_count: int  # Number of outdated packages
    metrics: DependencyMetricsDict  # Dependency metrics summary
    success: bool


# API Inventory TypedDicts (Phase 3: API Analysis)

class APIEndpointDict(TypedDict, total=False):
    """Individual API endpoint metadata."""
    path: str  # Endpoint path (e.g., /api/users/{id})
    method: str  # HTTP method: GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD
    framework: str  # Framework: fastapi, flask, express, graphql
    file: str  # Relative path to source file from project root
    line: int  # Line number where endpoint is defined
    function: str  # Name of handler function
    parameters: List[str]  # List of function parameters
    documented: bool  # Whether endpoint has documentation
    doc_coverage: int  # Documentation coverage score (0-100)
    description: str  # Endpoint description from documentation
    summary: str  # Short summary from OpenAPI spec
    tags: List[str]  # OpenAPI tags for grouping endpoints
    deprecated: bool  # Whether endpoint is deprecated


class APIMetricsDict(TypedDict, total=False):
    """API-level metrics and coverage statistics."""
    total_endpoints: int  # Total number of API endpoints discovered
    documented_endpoints: int  # Number of endpoints with documentation
    documentation_coverage: int  # Percentage of endpoints with documentation (0-100)
    frameworks_detected: List[str]  # List of frameworks found in project
    framework_breakdown: dict  # Count of endpoints by framework
    method_breakdown: dict  # Count of endpoints by HTTP method
    rest_endpoints: int  # Number of REST endpoints
    graphql_endpoints: int  # Number of GraphQL endpoints
    deprecated_endpoints: int  # Number of deprecated endpoints


class APIManifestDict(TypedDict):
    """Complete API inventory manifest structure."""
    project_name: str  # Name of the project
    project_path: str  # Absolute path to project directory
    generated_at: str  # ISO 8601 timestamp when manifest was generated
    frameworks: List[str]  # List of detected API frameworks
    endpoints: List[APIEndpointDict]  # Array of endpoint metadata
    metrics: APIMetricsDict  # API-level metrics
    openapi_files: List[str]  # List of OpenAPI/Swagger files found (optional)


class APIResultDict(TypedDict):
    """Return type for api_inventory tool."""
    manifest_path: str  # Path to saved api.json file
    frameworks: List[str]  # Detected frameworks
    total_endpoints: int  # Number of endpoints discovered
    documented_endpoints: int  # Number of endpoints with documentation
    documentation_coverage: int  # Documentation coverage percentage (0-100)
    metrics: APIMetricsDict  # API metrics summary
    success: bool


# Database Inventory TypedDicts (Phase 3: Database Schema Analysis)

class DatabaseColumnDict(TypedDict, total=False):
    """SQL table column metadata."""
    name: str  # Column name
    type: str  # Column data type (e.g., VARCHAR, INTEGER, TIMESTAMP)
    nullable: bool  # Whether column allows NULL values
    primary_key: bool  # Whether column is a primary key
    unique: bool  # Whether column has unique constraint
    foreign_key: str  # Referenced table.column if foreign key
    default: str  # Default value for column


class DatabaseFieldDict(TypedDict, total=False):
    """NoSQL document field metadata."""
    name: str  # Field name
    type: str  # Field data type (e.g., String, Number, Date)
    required: bool  # Whether field is required
    default: str  # Default value for field


class DatabaseRelationshipDict(TypedDict, total=False):
    """ORM relationship metadata."""
    name: str  # Relationship name
    related_table: str  # Name of related table/collection
    type: str  # Type of relationship: one-to-one, one-to-many, many-to-many, relationship


class DatabaseIndexDict(TypedDict, total=False):
    """Database index metadata."""
    name: str  # Index name
    columns: List[str]  # Indexed columns/fields
    unique: bool  # Whether index enforces uniqueness


class DatabaseSchemaDict(TypedDict, total=False):
    """Individual table/collection schema metadata."""
    name: str  # Table or collection name
    type: str  # Schema object type: table, collection
    database_type: str  # Database paradigm: sql, nosql
    orm: str  # ORM/ODM framework: sqlalchemy, sequelize, mongoose
    source: str  # Source of schema: alembic_migration, knex_migration
    file: str  # Relative path to source file from project root
    line: int  # Line number where schema is defined
    class_name: str  # Name of model class
    columns: List[DatabaseColumnDict]  # SQL table columns
    fields: List[DatabaseFieldDict]  # NoSQL document fields
    relationships: List[DatabaseRelationshipDict]  # ORM relationships
    indexes: List[DatabaseIndexDict]  # Database indexes
    constraints: List[dict]  # Table constraints (SQL only)
    validators: List[str]  # Schema validators (NoSQL)


class DatabaseMetricsDict(TypedDict, total=False):
    """Database inventory metrics."""
    total_schemas: int  # Total number of tables/collections discovered
    sql_tables: int  # Number of SQL tables
    nosql_collections: int  # Number of NoSQL collections
    database_systems_detected: List[str]  # List of database systems found in project
    system_breakdown: dict  # Count of schemas by database type
    orm_breakdown: dict  # Count of schemas by ORM/source
    total_columns: int  # Total number of columns across all tables
    total_relationships: int  # Total number of relationships


class DatabaseManifestDict(TypedDict):
    """Complete database inventory manifest structure."""
    project_name: str  # Name of the project
    project_path: str  # Absolute path to project directory
    generated_at: str  # ISO 8601 timestamp when manifest was generated
    database_systems: List[str]  # List of detected database systems
    schemas: List[DatabaseSchemaDict]  # Array of table/collection schemas
    metrics: DatabaseMetricsDict  # Database-level metrics


class DatabaseResultDict(TypedDict):
    """Return type for database_inventory tool."""
    manifest_path: str  # Path to saved database.json file
    database_systems: List[str]  # Detected database systems
    total_schemas: int  # Number of schemas discovered
    sql_tables: int  # Number of SQL tables
    nosql_collections: int  # Number of NoSQL collections
    metrics: DatabaseMetricsDict  # Database metrics summary
    success: bool


# Configuration Inventory TypedDicts (Phase 4: Configuration & Testing Analysis)

class ConfigFileDict(TypedDict, total=False):
    """Individual configuration file metadata."""
    file_path: str  # Relative path from project root
    format: str  # Configuration format: json, yaml, toml, ini, env
    key_count: int  # Total number of configuration keys (including nested)
    sensitive_keys: List[str]  # List of detected sensitive keys
    has_sensitive: bool  # Whether file contains sensitive values
    last_modified: str  # ISO 8601 timestamp of last modification
    size_bytes: int  # File size in bytes
    config_data: dict  # Parsed configuration data (null if contains sensitive values)


class ConfigMetricsDict(TypedDict, total=False):
    """Configuration inventory metrics."""
    total_files: int  # Total number of configuration files
    sensitive_files: int  # Number of files containing sensitive values
    formats_detected: List[str]  # List of formats found in project
    total_keys: int  # Total configuration keys across all files
    total_sensitive_keys: int  # Total sensitive keys detected


class ConfigManifestDict(TypedDict):
    """Complete configuration inventory manifest structure."""
    project_name: str  # Name of the project
    project_path: str  # Absolute path to project directory
    generated_at: str  # ISO 8601 timestamp when manifest was generated
    formats: List[str]  # Configuration formats detected in project
    config_files: List[ConfigFileDict]  # Array of configuration file metadata
    metrics: ConfigMetricsDict  # Configuration-level metrics


class ConfigResultDict(TypedDict):
    """Return type for config_inventory tool."""
    manifest_path: str  # Path to saved config.json file
    formats_detected: List[str]  # Detected configuration formats
    total_files: int  # Number of configuration files discovered
    sensitive_files: int  # Number of files with sensitive values
    success: bool


# Test Inventory TypedDicts (Phase 4: Configuration & Testing Analysis)

class TestFileDict(TypedDict, total=False):
    """Individual test file metadata."""
    file_path: str  # Relative path from project root
    framework: str  # Test framework: pytest, unittest, jest, mocha, vitest
    last_modified: str  # ISO 8601 timestamp of last modification
    size_bytes: int  # File size in bytes
    line_count: int  # Number of lines in test file


class TestMetricsDict(TypedDict, total=False):
    """Test inventory metrics."""
    total_test_files: int  # Total number of test files discovered
    frameworks_detected: List[str]  # List of test frameworks found in project
    untested_files_count: int  # Number of source files without tests
    coverage_available: bool  # Whether coverage data is available
    overall_coverage: Optional[float]  # Overall test coverage percentage (null if unavailable)


class TestManifestDict(TypedDict):
    """Complete test inventory manifest structure."""
    project_name: str  # Name of the project
    project_path: str  # Absolute path to project directory
    generated_at: str  # ISO 8601 timestamp when manifest was generated
    frameworks: List[str]  # Test frameworks detected in project
    test_files: List[TestFileDict]  # Array of test file metadata
    coverage_data: Optional[Dict[str, Any]]  # Coverage data (null if not available)
    untested_files: List[str]  # List of source files without tests
    metrics: TestMetricsDict  # Test-level metrics


class TestResultDict(TypedDict):
    """Return type for test_inventory tool."""
    manifest_path: str  # Path to saved tests.json file
    frameworks_detected: List[str]  # Detected test frameworks
    total_test_files: int  # Number of test files discovered
    untested_files_count: int  # Number of untested source files
    coverage_available: bool  # Whether coverage data is available
    success: bool


# Documentation Inventory TypedDicts (Phase 5: Documentation & Assets Analysis)

class DocumentationFileDict(TypedDict, total=False):
    """Individual documentation file metadata."""
    file_path: str  # Relative path from project root
    format: str  # Documentation format: markdown, restructured_text, asciidoc, html, orgmode, plaintext
    size_bytes: int  # File size in bytes
    sections_count: int  # Number of sections/headings
    code_examples_count: int  # Number of code examples/blocks
    external_links_count: int  # Number of external hyperlinks
    internal_links_count: int  # Number of internal hyperlinks
    last_modified: str  # ISO 8601 timestamp of last modification
    freshness_score: float  # Freshness score based on last modified date (0-100)
    completeness_score: float  # Completeness score based on sections and examples (0-100)
    error: str  # Error message if file could not be analyzed (optional)


class DocumentationManifestDict(TypedDict):
    """Complete documentation inventory manifest structure."""
    project_name: str  # Name of the project
    project_path: str  # Absolute path to project directory
    generated_at: str  # ISO 8601 timestamp when manifest was generated
    documentation_files: List[DocumentationFileDict]  # Array of documentation file metadata
    source_components_count: int  # Total number of source code components
    metrics: Dict[str, Any]  # Documentation-level metrics dict


class DocumentationResultDict(TypedDict):
    """Return type for documentation_inventory tool."""
    manifest_path: str  # Path to saved documentation.json file
    total_documentation_files: int  # Number of documentation files discovered
    coverage_score: float  # Documentation coverage percentage (0-100)
    freshness_score: float  # Average freshness score (0-100)
    completeness_score: float  # Average completeness score (0-100)
    quality_score: float  # Overall quality score (0-100)
    success: bool


# Risk Assessment TypedDicts (WO-RISK-ASSESSMENT-001)

class RiskDimensionDict(TypedDict, total=False):
    """Risk evaluation for a single dimension."""
    severity: str  # low, medium, high, critical
    likelihood: float  # 0-100 percentage likelihood risk will occur
    score: float  # Dimension risk score (severity × likelihood → 0-100)
    findings: List[str]  # Specific risks or concerns identified
    evidence: List[str]  # Evidence or patterns supporting assessment
    mitigation_available: bool  # Whether mitigation strategies exist


class CompositeScoreDict(TypedDict):
    """Overall risk assessment composite score."""
    score: float  # 0-100 composite risk score
    level: str  # low, medium, high, critical
    explanation: str  # How score was calculated
    confidence: float  # 0.0-1.0 confidence based on context completeness


class RecommendationDict(TypedDict, total=False):
    """Overall recommendation and decision guidance."""
    decision: str  # go, no-go, proceed-with-caution, needs-review
    rationale: str  # Explanation of recommendation
    conditions: List[str]  # Conditions for proceeding safely


class MitigationStrategyDict(TypedDict, total=False):
    """Actionable mitigation strategy for identified risk."""
    risk_dimension: str  # Which dimension this addresses
    strategy: str  # Specific mitigation action
    priority: str  # critical, high, medium, low
    estimated_effort: str  # low, medium, high


class OptionComparisonDict(TypedDict, total=False):
    """Single option in multi-option comparison."""
    option_id: str  # Unique identifier (e.g., 'option_1')
    description: str  # Description of alternative approach
    composite_score: float  # Risk score for this option
    rank: int  # Ranking (1=best/lowest risk)
    pros: List[str]  # Advantages
    cons: List[str]  # Disadvantages


class ProjectContextDict(TypedDict, total=False):
    """Analyzed project context for risk evaluation."""
    files_analyzed: int  # Number of files analyzed
    dependencies_found: int  # Dependencies discovered
    test_coverage: float  # Test coverage percentage (if available)
    architecture_patterns: List[str]  # Identified patterns
    gaps: List[str]  # Missing context or gaps


class ProposedChangeDict(TypedDict):
    """Details of proposed code change."""
    description: str  # Human-readable description
    change_type: str  # create, modify, delete, refactor, migrate
    files_affected: List[str]  # File paths to be modified
    context: Dict[str, Any]  # Additional context (optional)


class RiskAssessmentDict(TypedDict, total=False):
    """Complete risk assessment structure."""
    assessment_id: str  # Unique ID (format: RA-{timestamp})
    generated_at: str  # ISO 8601 timestamp
    project_path: str  # Absolute project path
    proposed_change: ProposedChangeDict  # Change being assessed
    risk_dimensions: Dict[str, RiskDimensionDict]  # 5 dimensions
    composite_score: CompositeScoreDict  # Overall score
    recommendation: RecommendationDict  # Go/no-go recommendation
    mitigation_strategies: List[MitigationStrategyDict]  # Mitigation actions
    options_analyzed: int  # Number of options (1=single, 2+=comparison)
    comparison: Dict[str, Any]  # Multi-option comparison (if applicable)
    project_context: ProjectContextDict  # Analyzed context
    metadata: Dict[str, Any]  # Assessment metadata


class RiskAssessmentResultDict(TypedDict):
    """Return type for assess_risk tool."""
    assessment_path: str  # Path to saved assessment JSON
    assessment_id: str  # Unique assessment ID
    composite_score: float  # Overall risk score (0-100)
    risk_level: str  # low, medium, high, critical
    decision: str  # go, no-go, proceed-with-caution, needs-review
    options_analyzed: int  # Number of options evaluated
    recommended_option: str  # Best option ID (if multi-option)
    duration_ms: float  # Assessment duration in milliseconds
    success: bool
