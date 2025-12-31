"""
Planning Analyzer Generator for MCP Planning Workflow System.

Analyzes projects to discover foundation docs, coding standards, reference components,
and patterns. Automates section 0 (Preparation) of implementation plans.
"""

from pathlib import Path
from typing import List, Dict
import json
import re
import asyncio
import sys

# Add coderef/ utilities to path for wrapper functions
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from coderef.utils import check_coderef_available, read_coderef_output

from type_defs import PreparationSummaryDict
from logger_config import logger
from constants import EXCLUDE_DIRS, ALLOWED_FILE_EXTENSIONS
from mcp_client import call_coderef_tool

__all__ = ['PlanningAnalyzer']


class PlanningAnalyzer:
    """
    Analyzes projects for implementation planning preparation.

    Scans project directory to discover:
    - Foundation documentation (API.md, ARCHITECTURE.md, etc.)
    - Coding standards (BEHAVIOR-STANDARDS.md, etc.)
    - Reference components (similar files/patterns)
    - Key patterns (error handling, naming conventions)
    - Technology stack (language, framework, database, testing)
    - Project structure (organization pattern)
    - Gaps and risks (missing docs, standards, tests, CI)

    Returns PreparationSummaryDict for populating section 0 of implementation plans.
    """

    def __init__(self, project_path: Path):
        """
        Initialize PlanningAnalyzer with project path.

        Args:
            project_path: Path to project directory to analyze
        """
        self.project_path = project_path
        logger.debug(f"Initialized PlanningAnalyzer for project: {project_path}")

    async def analyze(self) -> PreparationSummaryDict:
        """
        Main analysis method - orchestrates all scanning operations.

        Async version supports MCP tool calls for enhanced analysis.

        Returns:
            PreparationSummaryDict with all analysis results
        """
        import time
        start_time = time.time()

        logger.info("Starting project analysis", extra={'project_path': str(self.project_path)})

        # Run all scanner methods with progress logging
        logger.info("Scanning foundation docs...")
        foundation_docs = self.scan_foundation_docs()

        logger.info("Reading foundation doc content...")
        foundation_doc_content = self.read_foundation_doc_content()

        logger.info("Reading inventory data...")
        inventory_data = await self.read_inventory_data()

        logger.info("Scanning coding standards...")
        coding_standards = self.scan_coding_standards()

        logger.info("Finding reference components...")
        reference_components = await self.find_reference_components()

        logger.info("Analyzing code patterns...")
        key_patterns_identified = await self.identify_patterns()

        logger.info("Detecting technology stack...")
        technology_stack = self.detect_technology_stack()

        logger.info("Analyzing project structure...")
        project_structure = self.analyze_project_structure()

        logger.info("Identifying gaps and risks...")
        gaps_and_risks = await self.identify_gaps_and_risks()

        # Build result
        result: PreparationSummaryDict = {
            'foundation_docs': foundation_docs,
            'foundation_doc_content': foundation_doc_content,
            'inventory_data': inventory_data,
            'coding_standards': coding_standards,
            'reference_components': reference_components,
            'key_patterns_identified': key_patterns_identified,
            'technology_stack': technology_stack,
            'project_structure': project_structure,
            'gaps_and_risks': gaps_and_risks
        }

        duration = time.time() - start_time
        logger.info(f"Analysis completed in {duration:.2f}s", extra={'duration_seconds': duration})

        return result

    def scan_foundation_docs(self) -> dict:
        """
        Scans for foundation documentation files.

        Checks for: README.md, API.md, ARCHITECTURE.md, COMPONENTS.md,
        SCHEMA.md, USER-GUIDE.md in project root and coderef/foundation-docs/.

        Returns:
            Dict with 'available' and 'missing' lists
        """
        logger.debug("Scanning foundation docs...")

        # Foundation docs to check (check both root and coderef/foundation-docs/)
        foundation_docs = [
            'README.md',
            'API.md',
            'ARCHITECTURE.md',
            'COMPONENTS.md',
            'SCHEMA.md',
            'USER-GUIDE.md'
        ]

        foundation_docs_dir = self.project_path / 'coderef' / 'foundation-docs'
        available = []
        missing = []

        for doc in foundation_docs:
            # Check root first, then coderef/foundation-docs/
            root_path = self.project_path / doc
            docs_path = foundation_docs_dir / doc

            if root_path.exists():
                available.append(f"{doc} (root)")
            elif docs_path.exists():
                available.append(f"{doc} (coderef/foundation-docs)")
            else:
                missing.append(doc)

        logger.debug(f"Found {len(available)} foundation docs, {len(missing)} missing")
        return {'available': available, 'missing': missing}

    def read_foundation_doc_content(self) -> dict:
        """
        Read and extract key content from foundation docs.

        Reads ARCHITECTURE.md, API.md, COMPONENTS.md, SCHEMA.md and extracts:
        - Location (root or coderef/foundation-docs)
        - Preview (first 500 characters)
        - Headers (first 10 markdown headers)
        - Size (character count)

        Returns:
            Dict mapping doc name to content info
        """
        logger.debug("Reading foundation doc content...")
        doc_content = {}
        docs_to_read = ['ARCHITECTURE.md', 'API.md', 'COMPONENTS.md', 'SCHEMA.md', 'README.md']

        for doc_name in docs_to_read:
            # Check root first, then coderef/foundation-docs/
            for location in [self.project_path, self.project_path / 'coderef' / 'foundation-docs']:
                doc_path = location / doc_name
                if doc_path.exists():
                    try:
                        content = doc_path.read_text(encoding='utf-8', errors='ignore')
                        rel_location = str(location.relative_to(self.project_path)) if location != self.project_path else 'root'
                        doc_content[doc_name] = {
                            'location': rel_location,
                            'preview': content[:500],  # First 500 chars
                            'headers': self._extract_headers(content),
                            'size': len(content)
                        }
                        logger.debug(f"Read {doc_name} from {rel_location} ({len(content)} chars)")
                    except Exception as e:
                        logger.warning(f"Error reading {doc_name}: {e}")
                    break  # Found the doc, don't check other locations

        logger.debug(f"Read content from {len(doc_content)} foundation docs")
        return doc_content

    def _extract_headers(self, content: str) -> List[str]:
        """
        Extract markdown headers from content.

        Args:
            content: Markdown content to parse

        Returns:
            List of first 10 header titles (without # prefix)
        """
        headers = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
        return headers[:10]  # Limit to first 10 headers

    async def read_inventory_data(self) -> dict:
        """
        Read existing inventory data from coderef/inventory/ or generate live inventory.

        Priority order:
        1. Read .coderef/index.json (fastest - pre-scanned data)
        2. Call coderef_scan MCP tool (AST-based live scan)
        3. Read coderef/inventory/ manifest files (legacy fallback)

        Returns:
            Dict with inventory type as key, summary data as value
        """
        logger.debug("Reading inventory data...")

        # Priority 1: Try to read .coderef/index.json (FASTEST)
        if check_coderef_available(str(self.project_path)):
            try:
                index_data = read_coderef_output(str(self.project_path), 'index')
                logger.info(f"Read .coderef/index.json: {len(index_data)} elements")

                # Group by type for summary
                by_type = {}
                for element in index_data:
                    element_type = element.get('type', 'unknown')
                    by_type[element_type] = by_type.get(element_type, 0) + 1

                # Extract unique files
                files = set(e.get('file') for e in index_data if 'file' in e)

                return {
                    'index_data': index_data,
                    'source': 'coderef_index',
                    'total_elements': len(index_data),
                    'by_type': by_type,
                    'files': len(files),
                    'utilization': '.coderef/index.json (preprocessed)'
                }
            except Exception as e:
                logger.debug(f".coderef/index.json read failed: {str(e)}, trying coderef_scan")

        # Priority 2: Try to use coderef_scan for live inventory
        try:
            result = await call_coderef_tool(
                "coderef_scan",
                {
                    "project_path": str(self.project_path),
                    "languages": ["ts", "tsx", "js", "jsx", "py"]
                }
            )
            if result.get("success"):
                scan_data = result.get("data", {})
                logger.info(f"Generated live inventory via coderef_scan: {scan_data.get('summary', {})}")
                return {
                    'scan_results': scan_data,
                    'source': 'coderef_scan',
                    'total_elements': scan_data.get('summary', {}).get('total_elements', 0)
                }
        except Exception as e:
            logger.debug(f"coderef_scan unavailable: {str(e)}, reading manifest files")

        # Fallback to reading manifest files
        inventory_data = {}
        inventory_dir = self.project_path / 'coderef' / 'inventory'

        if not inventory_dir.exists():
            logger.debug("No coderef/inventory/ directory found")
            return {'available': [], 'missing': ['Run /quick-inventory to generate inventory data']}

        inventory_files = {
            'manifest.json': 'file_inventory',
            'dependencies.json': 'dependencies',
            'api.json': 'api_endpoints',
            'database.json': 'database_schemas',
            'config.json': 'configuration',
            'tests.json': 'test_infrastructure',
            'documentation.json': 'documentation'
        }

        available = []
        for filename, key in inventory_files.items():
            inventory_path = inventory_dir / filename
            if inventory_path.exists():
                try:
                    data = json.loads(inventory_path.read_text(encoding='utf-8'))
                    # Extract summary info from each inventory type
                    summary = self._extract_inventory_summary(key, data)
                    inventory_data[key] = summary
                    available.append(filename)
                    logger.debug(f"Read {filename} inventory data")
                except Exception as e:
                    logger.warning(f"Error reading {filename}: {e}")

        inventory_data['available'] = available
        inventory_data['missing'] = [f for f in inventory_files.keys() if f not in available]

        logger.debug(f"Read {len(available)} inventory files")
        return inventory_data

    def _extract_inventory_summary(self, inventory_type: str, data: dict) -> dict:
        """
        Extract relevant summary from inventory data.

        Args:
            inventory_type: Type of inventory (file_inventory, dependencies, etc.)
            data: Raw inventory JSON data

        Returns:
            Dict with summary information relevant for planning
        """
        summary = {}

        # Safely get nested values with defaults
        def safe_get(d, *keys, default=None):
            """Safely get nested dict values."""
            result = d
            for key in keys:
                if result is None or not isinstance(result, dict):
                    return default
                result = result.get(key, default)
            return result if result is not None else default

        if inventory_type == 'file_inventory':
            # Extract file counts and categories
            summary['total_files'] = safe_get(data, 'metrics', 'total_files', default=0)
            by_category = safe_get(data, 'by_category', default={})
            summary['categories'] = list(by_category.keys())[:5] if by_category else []
            files = safe_get(data, 'files', default=[])
            summary['high_risk_files'] = len([f for f in files if isinstance(f, dict) and f.get('risk_level') == 'high'])

        elif inventory_type == 'dependencies':
            # Extract dependency info
            summary['total_dependencies'] = safe_get(data, 'metrics', 'total_dependencies', default=0)
            summary['ecosystems'] = safe_get(data, 'ecosystems_detected', default=[])
            summary['security_vulnerabilities'] = safe_get(data, 'security_summary', 'total_vulnerabilities', default=0)
            summary['outdated_count'] = safe_get(data, 'metrics', 'outdated_count', default=0)

        elif inventory_type == 'api_endpoints':
            # Extract API info
            summary['total_endpoints'] = safe_get(data, 'metrics', 'total_endpoints', default=0)
            summary['frameworks'] = safe_get(data, 'frameworks_detected', default=[])
            summary['undocumented_endpoints'] = safe_get(data, 'metrics', 'undocumented_count', default=0)

        elif inventory_type == 'database_schemas':
            # Extract database info
            summary['total_tables'] = safe_get(data, 'metrics', 'total_tables', default=0)
            summary['database_systems'] = safe_get(data, 'systems_detected', default=[])
            summary['migration_files'] = safe_get(data, 'metrics', 'migration_count', default=0)

        elif inventory_type == 'test_infrastructure':
            # Extract test info
            summary['total_test_files'] = safe_get(data, 'test_summary', 'total_test_files', default=0)
            summary['frameworks'] = safe_get(data, 'frameworks_detected', default=[])
            summary['coverage'] = safe_get(data, 'coverage_data', 'overall', default='unknown')
            summary['test_readiness_score'] = safe_get(data, 'test_summary', 'test_readiness_score', default=0)

        elif inventory_type == 'documentation':
            # Extract docs info
            summary['total_files'] = safe_get(data, 'metrics', 'total_files', default=0)
            summary['formats'] = safe_get(data, 'formats', default=[])
            summary['quality_score'] = safe_get(data, 'metrics', 'quality_score', default=0)
            summary['coverage_percentage'] = safe_get(data, 'metrics', 'coverage_percentage', default=0)

        elif inventory_type == 'configuration':
            # Extract config info
            files = safe_get(data, 'files', default=[])
            summary['total_files'] = len(files) if isinstance(files, list) else 0
            summary['formats_detected'] = safe_get(data, 'formats_detected', default=[])
            summary['sensitive_values_found'] = safe_get(data, 'security_summary', 'total_secrets_found', default=0)

        return summary

    def scan_coding_standards(self) -> dict:
        """
        Scans for coding standards documents.

        Checks for standards in coderef/standards/: BEHAVIOR-STANDARDS.md,
        COMPONENT-PATTERN.md, UI-STANDARDS.md, UX-PATTERNS.md, COMPONENT-INDEX.md.

        Returns:
            Dict with 'available' and 'missing' lists
        """
        logger.debug("Scanning coding standards...")

        # Standards docs to check in coderef/standards/
        standards_docs = [
            'BEHAVIOR-STANDARDS.md',
            'COMPONENT-PATTERN.md',
            'UI-STANDARDS.md',
            'UX-PATTERNS.md',
            'COMPONENT-INDEX.md'
        ]

        standards_dir = self.project_path / 'coderef' / 'standards'
        available = []
        missing = []

        # Check if standards directory exists
        if not standards_dir.exists():
            logger.debug("No coderef/standards/ directory found")
            return {'available': [], 'missing': standards_docs}

        for standard in standards_docs:
            standard_path = standards_dir / standard
            if standard_path.exists():
                available.append(standard)
            else:
                missing.append(standard)

        logger.debug(f"Found {len(available)} coding standards, {len(missing)} missing")
        return {'available': available, 'missing': missing}

    async def find_reference_components(self) -> dict:
        """
        Finds similar components based on file names and patterns.

        Uses coderef_query tool for dependency graph analysis.

        Returns:
            Dict with 'primary', 'secondary', and 'total_found' keys
        """
        logger.debug("Finding reference components...")

        try:
            # Try to use coderef_query tool for actual component discovery
            result = await call_coderef_tool(
                "coderef_query",
                {
                    "project_path": str(self.project_path),
                    "query_type": "depends-on-me",
                    "target": "*",
                    "max_depth": 2
                }
            )

            if result.get("success"):
                # Extract primary and secondary components from dependency graph
                query_results = result.get("data", {})
                return {
                    'primary': None,
                    'secondary': list(query_results.keys())[:10],  # Top 10 dependencies
                    'total_found': len(query_results),
                    'source': 'coderef_query'
                }
            else:
                logger.warning("coderef_query failed, using fallback")
                return self._find_reference_components_fallback()

        except Exception as e:
            logger.warning(f"Error calling coderef_query: {str(e)}, using fallback")
            return self._find_reference_components_fallback()

    def _find_reference_components_fallback(self) -> dict:
        """Fallback method when coderef tool unavailable."""
        return {'primary': None, 'secondary': [], 'total_found': 0, 'note': 'Using fallback - coderef tools unavailable'}

    async def identify_patterns(self) -> List[str]:
        """
        Analyzes code files to identify reusable patterns.

        Uses coderef_patterns tool for AST-based pattern detection (99% accuracy).
        Falls back to regex-based analysis if coderef unavailable.

        Looks for: error handling patterns, naming conventions,
        file organization patterns, component structure patterns.

        Returns:
            List of pattern descriptions
        """
        logger.debug("Identifying patterns...")

        try:
            # Try to use coderef_patterns tool for AST-based detection
            result = await call_coderef_tool(
                "coderef_patterns",
                {
                    "project_path": str(self.project_path),
                    "pattern_type": "all",
                    "limit": 20
                }
            )

            if result.get("success"):
                patterns_data = result.get("data", {})
                patterns = patterns_data.get("patterns", [])
                if patterns:
                    logger.info(f"Found {len(patterns)} patterns via coderef_patterns")
                    return [str(p) for p in patterns[:15]]

        except Exception as e:
            logger.debug(f"coderef_patterns unavailable: {str(e)}, using fallback regex analysis")

        # Fallback to regex-based analysis
        source_files = self._scan_source_files()
        if not source_files:
            logger.debug("No source files found for pattern analysis")
            return []

        # Pattern counters
        try_catch_count = 0
        error_throw_count = 0
        export_from_count = 0
        function_names = []
        const_names = []

        # Analyze files (limit to first 200 files for performance)
        files_to_analyze = source_files[:200] if len(source_files) > 200 else source_files

        for file_path in files_to_analyze:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')

                # Error handling patterns
                if re.search(r'try\s*\{', content):
                    try_catch_count += 1
                if re.search(r'throw\s+new\s+\w+Error', content):
                    error_throw_count += 1

                # File organization patterns
                if re.search(r'export\s+.*\s+from', content):
                    export_from_count += 1

                # Naming conventions (extract function and const names)
                func_matches = re.findall(r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                function_names.extend(func_matches)

                const_matches = re.findall(r'const\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                const_names.extend(const_matches)

            except Exception as e:
                logger.debug(f"Error reading file {file_path}: {e}")
                continue

        # Build pattern descriptions (filter by frequency)
        patterns = []

        if try_catch_count >= 3:
            patterns.append(f"Error handling: try-catch blocks found in {try_catch_count} files")

        if error_throw_count >= 3:
            patterns.append(f"Error handling: throw new Error pattern found in {error_throw_count} files")

        if export_from_count >= 3:
            patterns.append(f"File organization: barrel exports (export from) found in {export_from_count} files")

        # Analyze naming conventions
        if function_names:
            camel_case_count = sum(1 for name in function_names if name[0].islower() and not '_' in name)
            if camel_case_count > len(function_names) * 0.7:  # 70%+ use camelCase
                patterns.append(f"Naming: camelCase for functions ({camel_case_count}/{len(function_names)} functions)")

        if const_names:
            upper_snake_count = sum(1 for name in const_names if name.isupper() and '_' in name)
            if upper_snake_count > len(const_names) * 0.3:  # 30%+ use UPPER_SNAKE
                patterns.append(f"Naming: UPPER_SNAKE_CASE for constants ({upper_snake_count}/{len(const_names)} constants)")

        logger.debug(f"Identified {len(patterns)} patterns")
        return patterns

    def detect_technology_stack(self) -> dict:
        """
        Identifies technology stack from indicator files.

        Checks for: package.json (Node.js), requirements.txt (Python),
        go.mod (Go), Cargo.toml (Rust). Extracts language, framework,
        database, testing tools, build system.

        Returns:
            Dict with detected technology information
        """
        logger.debug("Detecting technology stack...")

        tech_stack = {
            'language': 'unknown',
            'framework': 'unknown',
            'database': 'unknown',
            'testing': 'unknown',
            'build': 'unknown'
        }

        # Check for Node.js/TypeScript (package.json)
        package_json_path = self.project_path / 'package.json'
        if package_json_path.exists():
            try:
                package_data = json.loads(package_json_path.read_text(encoding='utf-8'))
                tech_stack['language'] = 'JavaScript/TypeScript'

                # Extract dependencies
                dependencies = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}

                # Detect framework
                if 'react' in dependencies:
                    tech_stack['framework'] = 'React'
                elif 'next' in dependencies:
                    tech_stack['framework'] = 'Next.js'
                elif 'vue' in dependencies:
                    tech_stack['framework'] = 'Vue.js'
                elif 'express' in dependencies:
                    tech_stack['framework'] = 'Express'

                # Detect database
                if 'pg' in dependencies or 'postgres' in dependencies:
                    tech_stack['database'] = 'PostgreSQL'
                elif 'mongodb' in dependencies or 'mongoose' in dependencies:
                    tech_stack['database'] = 'MongoDB'
                elif 'mysql' in dependencies:
                    tech_stack['database'] = 'MySQL'

                # Detect testing
                if 'jest' in dependencies:
                    tech_stack['testing'] = 'Jest'
                elif 'vitest' in dependencies:
                    tech_stack['testing'] = 'Vitest'
                elif 'mocha' in dependencies:
                    tech_stack['testing'] = 'Mocha'

                # Detect build system
                scripts = package_data.get('scripts', {})
                if 'vite' in str(scripts):
                    tech_stack['build'] = 'Vite'
                elif 'webpack' in str(scripts) or 'webpack' in dependencies:
                    tech_stack['build'] = 'Webpack'
                elif 'build' in scripts:
                    tech_stack['build'] = 'npm scripts'

            except Exception as e:
                logger.debug(f"Error parsing package.json: {e}")

        # Check for Python (requirements.txt, setup.py, pyproject.toml)
        requirements_path = self.project_path / 'requirements.txt'
        setup_py_path = self.project_path / 'setup.py'
        pyproject_path = self.project_path / 'pyproject.toml'

        if requirements_path.exists() or setup_py_path.exists() or pyproject_path.exists():
            tech_stack['language'] = 'Python'

            # Try to detect framework from requirements.txt
            if requirements_path.exists():
                try:
                    requirements = requirements_path.read_text(encoding='utf-8').lower()
                    if 'fastapi' in requirements:
                        tech_stack['framework'] = 'FastAPI'
                    elif 'flask' in requirements:
                        tech_stack['framework'] = 'Flask'
                    elif 'django' in requirements:
                        tech_stack['framework'] = 'Django'

                    if 'pytest' in requirements:
                        tech_stack['testing'] = 'pytest'
                    elif 'unittest' in requirements:
                        tech_stack['testing'] = 'unittest'

                except Exception as e:
                    logger.debug(f"Error reading requirements.txt: {e}")

        # Check for Go (go.mod)
        go_mod_path = self.project_path / 'go.mod'
        if go_mod_path.exists():
            tech_stack['language'] = 'Go'
            tech_stack['build'] = 'go build'

        # Check for Rust (Cargo.toml)
        cargo_path = self.project_path / 'Cargo.toml'
        if cargo_path.exists():
            tech_stack['language'] = 'Rust'
            tech_stack['build'] = 'Cargo'

        logger.debug(f"Detected technology stack: {tech_stack['language']}, {tech_stack['framework']}")
        return tech_stack

    def analyze_project_structure(self) -> dict:
        """
        Analyzes directory structure to understand organization.

        Identifies: main directories, file counts, organization pattern
        (feature-based, layered, flat, component-based).

        Returns:
            Dict describing project structure
        """
        logger.debug("Analyzing project structure...")

        dir_file_counts = {}

        # Walk directory tree and count files per directory
        try:
            for item in self.project_path.rglob('*'):
                # Skip excluded directories
                if any(excluded in item.parts for excluded in EXCLUDE_DIRS):
                    continue

                if item.is_dir():
                    # Count files in this directory (non-recursive)
                    file_count = sum(1 for f in item.iterdir() if f.is_file())
                    if file_count > 0:
                        # Store relative path
                        rel_path = item.relative_to(self.project_path)
                        dir_file_counts[str(rel_path)] = file_count

        except PermissionError as e:
            logger.warning(f"Permission denied analyzing structure: {e}")

        # Identify main directories (10+ files)
        main_directories = [dir_path for dir_path, count in dir_file_counts.items() if count >= 10]

        # Detect organization pattern
        organization_pattern = 'unknown'
        dir_names = [Path(d).parts[0] if Path(d).parts else d for d in dir_file_counts.keys()]

        if 'src' in dir_names or 'lib' in dir_names:
            if 'components' in dir_names or any('components' in d for d in dir_file_counts.keys()):
                organization_pattern = 'component-based'
            elif 'features' in dir_names or 'modules' in dir_names:
                organization_pattern = 'feature-based'
            elif any(pattern in dir_names for pattern in ['controllers', 'models', 'views', 'services']):
                organization_pattern = 'layered (MVC/service-based)'
            else:
                organization_pattern = 'modular (src-based)'
        elif len([f for f in self.project_path.iterdir() if f.is_file() and f.suffix in ALLOWED_FILE_EXTENSIONS]) > 10:
            organization_pattern = 'flat (files in root)'

        logger.debug(f"Project structure: {organization_pattern}, {len(main_directories)} main directories")
        return {
            'main_directories': main_directories[:10],  # Limit to top 10
            'file_counts': {k: v for k, v in sorted(dir_file_counts.items(), key=lambda item: item[1], reverse=True)[:10]},
            'organization_pattern': organization_pattern
        }

    async def identify_gaps_and_risks(self) -> List[str]:
        """
        Identifies missing documentation, standards, or potential risks.

        Attempts to call coderef_coverage for test coverage analysis.
        Falls back to filesystem checks for missing foundation docs, standards,
        test directory, CI config.

        Returns:
            List of gap/risk descriptions
        """
        logger.debug("Identifying gaps and risks...")

        gaps = []

        # Try to use coderef_coverage for test coverage gaps
        try:
            result = await call_coderef_tool(
                "coderef_coverage",
                {
                    "project_path": str(self.project_path),
                    "format": "summary"
                }
            )
            if result.get("success"):
                coverage_data = result.get("data", {})
                coverage_percent = coverage_data.get("coverage_percent", 0)
                if coverage_percent < 50:
                    gaps.append(f"Low test coverage: {coverage_percent}% (target: ≥80%)")
                    logger.info(f"Coverage analysis from coderef_coverage: {coverage_percent}%")
        except Exception as e:
            logger.debug(f"coderef_coverage unavailable: {str(e)}, using fallback checks")

        # Check for missing foundation docs
        foundation_docs = self.scan_foundation_docs()
        if foundation_docs['missing']:
            gaps.append(f"Missing foundation docs: {', '.join(foundation_docs['missing'][:3])}")

        # Check for missing coding standards
        coding_standards = self.scan_coding_standards()
        if coding_standards['missing'] and len(coding_standards['missing']) == 5:
            # All standards missing
            gaps.append("No coding standards directory found (coderef/standards/)")
        elif coding_standards['missing']:
            gaps.append(f"Missing coding standards: {', '.join(coding_standards['missing'][:3])}")

        # Check for test directory
        test_dirs = ['tests', 'test', '__tests__', 'spec']
        has_test_dir = any((self.project_path / test_dir).exists() for test_dir in test_dirs)
        if not has_test_dir:
            gaps.append("No test directory found (tests/, test/, or __tests__/)")

        # Check for CI configuration
        ci_configs = [
            '.github/workflows',
            '.gitlab-ci.yml',
            '.circleci/config.yml',
            'azure-pipelines.yml',
            'jenkins file'
        ]
        has_ci = any((self.project_path / ci_config).exists() for ci_config in ci_configs)
        if not has_ci:
            gaps.append("No CI configuration found (.github/workflows/, .gitlab-ci.yml, etc.)")

        # Check for README.md
        if not (self.project_path / 'README.md').exists():
            gaps.append("No README.md found in project root")

        logger.debug(f"Identified {len(gaps)} gaps/risks")
        return gaps

    def _scan_source_files(self) -> List[Path]:
        """
        Helper method to recursively scan source files.

        Excludes EXCLUDE_DIRS and filters by ALLOWED_FILE_EXTENSIONS.

        Returns:
            List of Path objects for source files
        """
        logger.debug("Scanning source files...")
        source_files = []

        try:
            for file_path in self.project_path.rglob('*'):
                # Skip if file is in excluded directory
                if any(excluded in file_path.parts for excluded in EXCLUDE_DIRS):
                    continue

                # Skip if not a file
                if not file_path.is_file():
                    continue

                # Check if file extension is allowed
                if file_path.suffix in ALLOWED_FILE_EXTENSIONS:
                    source_files.append(file_path)

        except PermissionError as e:
            logger.warning(f"Permission denied scanning files: {e}")

        logger.debug(f"Found {len(source_files)} source files")
        return source_files
