"""
Planning Analyzer Generator for MCP Planning Workflow System.

Analyzes projects to discover foundation docs, coding standards, reference components,
and patterns. Automates section 0 (Preparation) of implementation plans.
"""

from pathlib import Path
from typing import List, Dict
import json
import re

from type_defs import PreparationSummaryDict
from logger_config import logger
from constants import EXCLUDE_DIRS, ALLOWED_FILE_EXTENSIONS

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

    def analyze(self) -> PreparationSummaryDict:
        """
        Main analysis method - orchestrates all scanning operations.

        Returns:
            PreparationSummaryDict with all analysis results
        """
        import time
        start_time = time.time()

        logger.info("Starting project analysis", extra={'project_path': str(self.project_path)})

        # Run all scanner methods with progress logging
        logger.info("Scanning foundation docs...")
        foundation_docs = self.scan_foundation_docs()

        logger.info("Scanning coding standards...")
        coding_standards = self.scan_coding_standards()

        logger.info("Finding reference components...")
        reference_components = self.find_reference_components()

        logger.info("Analyzing code patterns...")
        key_patterns_identified = self.identify_patterns()

        logger.info("Detecting technology stack...")
        technology_stack = self.detect_technology_stack()

        logger.info("Analyzing project structure...")
        project_structure = self.analyze_project_structure()

        logger.info("Identifying gaps and risks...")
        gaps_and_risks = self.identify_gaps_and_risks()

        # Build result
        result: PreparationSummaryDict = {
            'foundation_docs': foundation_docs,
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

    def find_reference_components(self) -> dict:
        """
        Finds similar components based on file names and patterns.

        Returns:
            Dict with 'primary', 'secondary', and optional 'note' keys
        """
        logger.debug("Finding reference components...")
        return {'primary': None, 'secondary': [], 'note': 'Reference component matching requires feature name - not yet implemented'}

    def identify_patterns(self) -> List[str]:
        """
        Analyzes code files to identify reusable patterns.

        Looks for: error handling patterns, naming conventions,
        file organization patterns, component structure patterns.

        Returns:
            List of pattern descriptions
        """
        logger.debug("Identifying patterns...")

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

    def identify_gaps_and_risks(self) -> List[str]:
        """
        Identifies missing documentation, standards, or potential risks.

        Checks for: missing foundation docs, missing standards,
        no test directory, no CI config.

        Returns:
            List of gap/risk descriptions
        """
        logger.debug("Identifying gaps and risks...")

        gaps = []

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
