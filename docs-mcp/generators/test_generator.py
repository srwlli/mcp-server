"""Test generator for discovering test files and analyzing coverage."""

import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys

# Add parent directory to path for constants import
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import Paths
from logger_config import logger, log_error


class TestGenerator:
    """Helper class for generating test file inventories with coverage analysis."""

    def __init__(self, project_path: Path):
        """
        Initialize test generator.

        Args:
            project_path: Path to project directory to analyze
        """
        self.project_path = project_path
        self.inventory_dir = project_path / Paths.INVENTORY_DIR
        self.schema_path = self.inventory_dir / "tests-schema.json"
        self.schema = self._load_schema()
        logger.info(f"Initialized TestGenerator for {project_path}")

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """
        Load JSON schema for manifest validation (SEC-002).

        Returns:
            Schema dictionary or None if schema file doesn't exist

        Raises:
            json.JSONDecodeError: If schema JSON is malformed
        """
        if not self.schema_path.exists():
            logger.warning(f"No schema found at {self.schema_path}")
            return None

        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            logger.debug(f"Loaded schema from {self.schema_path}")
            return schema
        except json.JSONDecodeError as e:
            log_error('schema_load_error', f"Malformed schema file: {self.schema_path}", error=str(e))
            raise json.JSONDecodeError(
                f"Malformed schema file: {self.schema_path}",
                e.doc,
                e.pos
            )

    def validate_manifest(self, data: Dict[str, Any]) -> None:
        """
        Validate manifest data against JSON schema (SEC-002).

        Args:
            data: Manifest dictionary to validate

        Raises:
            jsonschema.ValidationError: If data doesn't match schema
            jsonschema.SchemaError: If schema itself is invalid
        """
        if self.schema is None:
            logger.warning("No schema available, skipping validation")
            return

        try:
            import jsonschema
            jsonschema.validate(data, self.schema)
            logger.debug("Test manifest validation passed")
        except jsonschema.ValidationError as e:
            log_error('test_manifest_validation_error', f"Manifest validation failed: {str(e)}", error=str(e))
            raise

    def detect_test_files(self) -> List[Path]:
        """
        Discover test files by pattern matching.

        Looks for:
        - Python: test_*.py, *_test.py in tests/ directories
        - JavaScript/TypeScript: *.test.js, *.test.ts, *.spec.js, *.spec.ts

        Returns:
            List of test file paths

        Raises:
            PermissionError: If directory cannot be accessed
        """
        logger.info(f"Discovering test files in {self.project_path}")

        test_files = []

        # Test file patterns by language
        test_patterns = {
            'python': ['test_*.py', '*_test.py'],
            'javascript': ['*.test.js', '*.test.ts', '*.spec.js', '*.spec.ts', '*.test.jsx', '*.test.tsx']
        }

        # Directories to exclude
        exclude_dirs = {'node_modules', '.git', 'dist', 'build', '.next', 'out',
                       'coverage', '__pycache__', '.venv', 'venv', 'vendor'}

        try:
            for root, dirs, filenames in self.project_path.walk():
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                for filename in filenames:
                    file_path = root / filename

                    # Check if file matches any test pattern
                    for lang, patterns in test_patterns.items():
                        for pattern in patterns:
                            if self._match_pattern(filename, pattern):
                                test_files.append(file_path)
                                logger.debug(f"Found {lang} test: {file_path}")
                                break

            logger.info(f"Discovered {len(test_files)} test files")
            return test_files

        except PermissionError as e:
            from logger_config import log_security_event
            log_security_event('permission_denied', f"Cannot access project directory: {self.project_path}",
                             path=str(self.project_path))
            raise PermissionError(f"Cannot access project directory: {self.project_path}")

    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """
        Check if filename matches glob-style pattern.

        Args:
            filename: File name to check
            pattern: Glob pattern (e.g., 'test_*.py')

        Returns:
            True if filename matches pattern
        """
        import fnmatch
        return fnmatch.fnmatch(filename.lower(), pattern.lower())

    def detect_frameworks(self, test_files: List[Path]) -> List[str]:
        """
        Detect test frameworks used in project.

        Args:
            test_files: List of test file paths

        Returns:
            List of detected framework names
        """
        frameworks = set()

        for test_file in test_files[:10]:  # Sample first 10 files for performance
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)  # Read first 5000 chars

                # Python frameworks
                if test_file.suffix == '.py':
                    if 'import pytest' in content or 'from pytest' in content:
                        frameworks.add('pytest')
                    if 'import unittest' in content or 'from unittest' in content:
                        frameworks.add('unittest')

                # JavaScript/TypeScript frameworks
                elif test_file.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                    if re.search(r'\bdescribe\s*\(', content) or re.search(r'\btest\s*\(', content):
                        # Could be jest, mocha, or vitest
                        if 'jest' in content.lower() or '@jest' in content:
                            frameworks.add('jest')
                        elif 'mocha' in content.lower():
                            frameworks.add('mocha')
                        elif 'vitest' in content.lower() or 'from \'vitest\'' in content:
                            frameworks.add('vitest')
                        else:
                            # Default to jest if unclear (most common)
                            frameworks.add('jest')

            except Exception as e:
                logger.debug(f"Could not analyze {test_file}: {str(e)}")
                continue

        frameworks_list = sorted(list(frameworks))
        logger.info(f"Detected test frameworks: {frameworks_list}")
        return frameworks_list

    def analyze_coverage(self) -> Optional[Dict[str, Any]]:
        """
        Analyze test coverage if coverage data available.

        Looks for:
        - Python: .coverage file
        - JavaScript: coverage.json, coverage/coverage-final.json, lcov.info

        Returns:
            Coverage data dictionary or None if not available
        """
        coverage_data = None

        # Check for Python coverage (.coverage file)
        python_coverage = self.project_path / '.coverage'
        if python_coverage.exists():
            logger.info("Found Python coverage data (.coverage)")
            coverage_data = self._parse_python_coverage(python_coverage)

        # Check for JavaScript coverage (coverage.json)
        js_coverage_paths = [
            self.project_path / 'coverage.json',
            self.project_path / 'coverage' / 'coverage-final.json'
        ]

        for coverage_path in js_coverage_paths:
            if coverage_path.exists():
                logger.info(f"Found JavaScript coverage data: {coverage_path}")
                coverage_data = self._parse_js_coverage(coverage_path)
                break

        # Check for lcov.info
        lcov_path = self.project_path / 'lcov.info'
        if lcov_path.exists() and not coverage_data:
            logger.info("Found lcov.info coverage data")
            coverage_data = self._parse_lcov_coverage(lcov_path)

        if not coverage_data:
            logger.info("No coverage data found")

        return coverage_data

    def _parse_python_coverage(self, coverage_file: Path) -> Dict[str, Any]:
        """Parse Python .coverage file."""
        try:
            # Attempt to use coverage library if available
            import coverage
            cov = coverage.Coverage(data_file=str(coverage_file))
            cov.load()

            total_statements = 0
            covered_statements = 0
            file_coverage = {}

            for filename in cov.get_data().measured_files():
                analysis = cov.analysis2(filename)
                statements = len(analysis[1])
                missing = len(analysis[3])
                covered = statements - missing

                total_statements += statements
                covered_statements += covered

                if statements > 0:
                    file_coverage[filename] = {
                        'coverage': round((covered / statements) * 100, 2),
                        'statements': statements,
                        'covered': covered
                    }

            overall_coverage = round((covered_statements / total_statements) * 100, 2) if total_statements > 0 else 0

            return {
                'type': 'python',
                'overall_coverage': overall_coverage,
                'files': file_coverage,
                'total_statements': total_statements,
                'covered_statements': covered_statements
            }

        except ImportError:
            logger.warning("coverage library not installed, cannot parse .coverage file")
            return {'type': 'python', 'available': False, 'reason': 'coverage library not installed'}
        except Exception as e:
            log_error('coverage_parse_error', f"Failed to parse .coverage: {str(e)}")
            return {'type': 'python', 'available': False, 'reason': str(e)}

    def _parse_js_coverage(self, coverage_file: Path) -> Dict[str, Any]:
        """Parse JavaScript coverage.json file."""
        try:
            with open(coverage_file, 'r', encoding='utf-8') as f:
                coverage_json = json.load(f)

            file_coverage = {}
            total_statements = 0
            covered_statements = 0

            for filepath, data in coverage_json.items():
                if 's' in data:  # Statement coverage
                    statements = data['s']
                    total = len(statements)
                    covered = sum(1 for v in statements.values() if v > 0)

                    total_statements += total
                    covered_statements += covered

                    if total > 0:
                        file_coverage[filepath] = {
                            'coverage': round((covered / total) * 100, 2),
                            'statements': total,
                            'covered': covered
                        }

            overall_coverage = round((covered_statements / total_statements) * 100, 2) if total_statements > 0 else 0

            return {
                'type': 'javascript',
                'overall_coverage': overall_coverage,
                'files': file_coverage,
                'total_statements': total_statements,
                'covered_statements': covered_statements
            }

        except Exception as e:
            log_error('js_coverage_parse_error', f"Failed to parse coverage.json: {str(e)}")
            return {'type': 'javascript', 'available': False, 'reason': str(e)}

    def _parse_lcov_coverage(self, lcov_file: Path) -> Dict[str, Any]:
        """Parse lcov.info coverage file."""
        try:
            with open(lcov_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple LCOV parsing
            files = content.split('end_of_record')
            file_coverage = {}
            total_lines = 0
            covered_lines = 0

            for file_block in files:
                if not file_block.strip():
                    continue

                # Extract filename
                sf_match = re.search(r'SF:(.+)', file_block)
                if not sf_match:
                    continue
                filename = sf_match.group(1).strip()

                # Extract line coverage
                lf_match = re.search(r'LF:(\d+)', file_block)
                lh_match = re.search(r'LH:(\d+)', file_block)

                if lf_match and lh_match:
                    lines = int(lf_match.group(1))
                    hit = int(lh_match.group(1))

                    total_lines += lines
                    covered_lines += hit

                    if lines > 0:
                        file_coverage[filename] = {
                            'coverage': round((hit / lines) * 100, 2),
                            'lines': lines,
                            'covered': hit
                        }

            overall_coverage = round((covered_lines / total_lines) * 100, 2) if total_lines > 0 else 0

            return {
                'type': 'lcov',
                'overall_coverage': overall_coverage,
                'files': file_coverage,
                'total_lines': total_lines,
                'covered_lines': covered_lines
            }

        except Exception as e:
            log_error('lcov_parse_error', f"Failed to parse lcov.info: {str(e)}")
            return {'type': 'lcov', 'available': False, 'reason': str(e)}

    def identify_untested_files(self, test_files: List[Path]) -> List[str]:
        """
        Identify source files without corresponding tests.

        Args:
            test_files: List of test file paths

        Returns:
            List of untested source file paths
        """
        # Get all source files
        source_files = set()
        exclude_dirs = {'node_modules', '.git', 'dist', 'build', '.next', 'out',
                       'coverage', '__pycache__', '.venv', 'venv', 'vendor', 'tests', 'test', '__tests__'}

        for root, dirs, filenames in self.project_path.walk():
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for filename in filenames:
                if filename.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                    # Exclude test files themselves
                    if not any(pattern in filename for pattern in ['test_', '_test.', '.test.', '.spec.']):
                        file_path = root / filename
                        source_files.add(str(file_path.relative_to(self.project_path)))

        # Map test files to source files
        tested_files = set()
        for test_file in test_files:
            test_name = test_file.name
            # Extract source file name from test file name
            source_name = test_name.replace('test_', '').replace('_test', '').replace('.test', '').replace('.spec', '')

            # Look for matching source files
            for source_file in source_files:
                if source_name in source_file:
                    tested_files.add(source_file)

        untested = sorted(list(source_files - tested_files))
        logger.info(f"Found {len(untested)} untested files out of {len(source_files)} source files")
        return untested

    def generate_manifest(self) -> Dict[str, Any]:
        """
        Generate comprehensive test inventory manifest.

        Returns:
            Complete test manifest dictionary

        Raises:
            IOError: If manifest cannot be generated
        """
        logger.info("Generating test inventory manifest")

        try:
            # Discover test files
            test_files = self.detect_test_files()

            # Detect frameworks
            frameworks = self.detect_frameworks(test_files)

            # Analyze coverage (optional)
            coverage_data = self.analyze_coverage()

            # Identify untested files
            untested_files = self.identify_untested_files(test_files)

            # Build test file metadata
            test_file_data = []
            for test_file in test_files:
                try:
                    stats = test_file.stat()
                    relative_path = test_file.relative_to(self.project_path)

                    test_file_data.append({
                        'file_path': str(relative_path).replace('\\', '/'),
                        'framework': self._guess_framework(test_file),
                        'last_modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                        'size_bytes': stats.st_size
                    })
                except Exception as e:
                    logger.debug(f"Could not get metadata for {test_file}: {str(e)}")

            # Calculate metrics
            metrics = {
                'total_test_files': len(test_files),
                'frameworks_detected': frameworks,
                'untested_files_count': len(untested_files),
                'coverage_available': coverage_data is not None and coverage_data.get('available', True),
                'overall_coverage': coverage_data.get('overall_coverage', 0) if coverage_data and coverage_data.get('available', True) else None
            }

            # Build manifest
            # Resolve path to get actual project name (handles '.' case)
            resolved_path = self.project_path.resolve()
            manifest = {
                'project_name': resolved_path.name,
                'project_path': str(resolved_path),
                'generated_at': datetime.now().isoformat(),
                'frameworks': frameworks,
                'test_files': test_file_data,
                'coverage_data': coverage_data,
                'untested_files': untested_files,
                'metrics': metrics
            }

            # Validate manifest
            self.validate_manifest(manifest)

            logger.info(f"Test manifest generation complete: {len(test_files)} test files, {len(untested_files)} untested files")
            return manifest

        except Exception as e:
            log_error('test_manifest_generation_error', f"Failed to generate manifest: {str(e)}", error=str(e))
            raise IOError(f"Failed to generate test manifest: {str(e)}")

    def _guess_framework(self, test_file: Path) -> str:
        """Guess test framework from file extension and content."""
        if test_file.suffix == '.py':
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(2000)
                if 'import pytest' in content or 'from pytest' in content:
                    return 'pytest'
                elif 'import unittest' in content or 'from unittest' in content:
                    return 'unittest'
            except:
                pass
            return 'python'
        elif test_file.suffix in ['.js', '.ts', '.jsx', '.tsx']:
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(2000)
                if 'vitest' in content:
                    return 'vitest'
                elif 'mocha' in content:
                    return 'mocha'
            except:
                pass
            return 'jest'
        return 'unknown'

    def save_manifest(self, manifest: Dict[str, Any], output_file: Optional[Path] = None) -> Path:
        """
        Save test manifest to JSON file.

        Args:
            manifest: Manifest dictionary to save
            output_file: Optional custom output file path

        Returns:
            Path to saved manifest file

        Raises:
            IOError: If file cannot be written
        """
        if output_file is None:
            self.inventory_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.inventory_dir / "tests.json"

        try:
            # Validate before saving
            self.validate_manifest(manifest)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
                f.write('\n')  # Add trailing newline

            logger.info(f"Test manifest saved to {output_file}")
            return output_file

        except Exception as e:
            log_error('test_manifest_save_error', f"Failed to save manifest: {str(e)}", path=str(output_file))
            raise IOError(f"Failed to save manifest to {output_file}: {str(e)}")
