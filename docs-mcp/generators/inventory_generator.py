"""Inventory generator for creating comprehensive project file manifests."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import jsonschema
import sys

# Add parent directory to path for constants import
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import Paths
from logger_config import logger, log_error, log_security_event


class InventoryGenerator:
    """Helper class for generating comprehensive project file inventories."""

    def __init__(self, project_path: Path):
        """
        Initialize inventory generator.

        Args:
            project_path: Path to project directory to inventory
        """
        self.project_path = project_path
        self.inventory_dir = project_path / Paths.INVENTORY_DIR
        self.schema_path = self.inventory_dir / "schema.json"
        self.schema = self._load_schema()
        logger.info(f"Initialized InventoryGenerator for {project_path}")

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
            jsonschema.validate(data, self.schema)
            logger.debug("Manifest validation passed")
        except jsonschema.ValidationError as e:
            log_error('manifest_validation_error', f"Manifest validation failed: {str(e)}", error=str(e))
            raise

    def discover_files(self, exclude_dirs: Optional[List[str]] = None, max_file_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Discover all files in project directory with metadata.

        Args:
            exclude_dirs: List of directory names to exclude (e.g., node_modules, .git)
            max_file_size: Maximum file size to process (bytes)

        Returns:
            List of file metadata dictionaries

        Raises:
            PermissionError: If directory cannot be accessed
        """
        from constants import EXCLUDE_DIRS, MAX_FILE_SIZE

        # Use defaults if not provided
        if exclude_dirs is None:
            exclude_dirs = EXCLUDE_DIRS
        if max_file_size is None:
            max_file_size = MAX_FILE_SIZE

        logger.info(f"Discovering files in {self.project_path} (excluding: {exclude_dirs})")

        files = []
        skipped_files = 0
        permission_errors = 0

        try:
            for root, dirs, filenames in self.project_path.walk():
                # Filter out excluded directories (modifies dirs in-place to prevent descent)
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                for filename in filenames:
                    file_path = root / filename

                    try:
                        # Get file stats
                        stats = file_path.stat()

                        # Skip files that are too large
                        if stats.st_size > max_file_size:
                            logger.debug(f"Skipping large file: {file_path} ({stats.st_size} bytes)")
                            skipped_files += 1
                            continue

                        # Get relative path from project root
                        try:
                            relative_path = file_path.relative_to(self.project_path)
                        except ValueError:
                            # File is outside project path (shouldn't happen, but handle it)
                            logger.warning(f"File outside project path: {file_path}")
                            continue

                        # Count lines for text files
                        lines = self._count_lines(file_path)

                        # Build file metadata
                        file_metadata = {
                            "path": str(relative_path).replace('\\', '/'),  # Use forward slashes
                            "name": filename,
                            "extension": file_path.suffix,
                            "size": stats.st_size,
                            "lines": lines,
                            "last_modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                            "category": "unknown",  # Will be set by categorize_file
                            "risk_level": "low",    # Will be set by calculate_risk_level
                        }

                        files.append(file_metadata)

                    except PermissionError as e:
                        logger.warning(f"Permission denied: {file_path}")
                        permission_errors += 1
                        continue
                    except Exception as e:
                        log_error('file_discovery_error', f"Error processing file {file_path}: {str(e)}", path=str(file_path))
                        continue

            logger.info(f"Discovered {len(files)} files (skipped {skipped_files} large files, {permission_errors} permission errors)")
            return files

        except PermissionError as e:
            log_security_event('permission_denied', f"Cannot access project directory: {self.project_path}", path=str(self.project_path))
            raise PermissionError(f"Cannot access project directory: {self.project_path}")

    def _count_lines(self, file_path: Path) -> int:
        """
        Count lines in a file.

        Args:
            file_path: Path to file

        Returns:
            Number of lines, or 0 if file is binary or cannot be read
        """
        try:
            # Try to read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            # Binary file or cannot be read
            return 0

    def categorize_file(self, file_path: Path) -> str:
        """
        Categorize file using universal taxonomy.

        Categories: core, source, template, config, test, docs

        Args:
            file_path: Path to file

        Returns:
            Category string
        """
        from constants import FileCategory

        filename = file_path.name.lower()
        extension = file_path.suffix.lower()
        path_parts = [p.lower() for p in file_path.parts]

        # Test files
        if 'test' in path_parts or 'tests' in path_parts or '__tests__' in path_parts:
            return FileCategory.TEST.value
        if filename.startswith('test_') or filename.endswith('_test.py'):
            return FileCategory.TEST.value
        if filename.endswith('.test.js') or filename.endswith('.test.ts'):
            return FileCategory.TEST.value
        if filename.endswith('.spec.js') or filename.endswith('.spec.ts'):
            return FileCategory.TEST.value

        # Documentation files
        doc_extensions = ['.md', '.rst', '.txt', '.adoc']
        if extension in doc_extensions:
            return FileCategory.DOCS.value
        if 'docs' in path_parts or 'documentation' in path_parts:
            return FileCategory.DOCS.value
        if filename in ['readme.md', 'changelog.md', 'contributing.md', 'license', 'license.md']:
            return FileCategory.DOCS.value

        # Configuration files
        config_extensions = ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.cfg', '.config']
        config_names = ['package.json', 'tsconfig.json', 'jest.config.js', 'webpack.config.js',
                       'babel.config.js', 'eslintrc', 'prettierrc', 'pyproject.toml', 'setup.py',
                       'requirements.txt', 'pipfile', 'dockerfile', 'docker-compose.yml',
                       '.gitignore', '.env', '.env.example', 'makefile']

        if filename in config_names or filename.startswith('.'):
            return FileCategory.CONFIG.value
        if 'config' in path_parts or 'configuration' in path_parts:
            return FileCategory.CONFIG.value
        # Only treat as config if in root or config directory
        if extension in config_extensions and (len(path_parts) <= 2 or 'config' in path_parts):
            return FileCategory.CONFIG.value

        # Template files
        template_extensions = ['.html', '.htm', '.hbs', '.ejs', '.pug', '.jade', '.mustache', '.jinja', '.j2']
        if extension in template_extensions:
            return FileCategory.TEMPLATE.value
        if 'template' in path_parts or 'templates' in path_parts:
            return FileCategory.TEMPLATE.value

        # Core infrastructure files (main entry points, servers)
        core_names = ['server.py', 'main.py', 'app.py', 'index.py', '__init__.py',
                     'server.js', 'main.js', 'app.js', 'index.js', 'index.ts',
                     '__main__.py', 'manage.py', 'wsgi.py', 'asgi.py']

        if filename in core_names and len(path_parts) <= 2:  # Must be in root or one level deep
            return FileCategory.CORE.value

        # Source code files (everything else that's code)
        source_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h',
                           '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
                           '.css', '.scss', '.sass', '.less']

        if extension in source_extensions:
            return FileCategory.SOURCE.value

        # Default to unknown
        return FileCategory.UNKNOWN.value

    def calculate_risk_level(self, file_metadata: Dict[str, Any]) -> str:
        """
        Calculate risk level based on file characteristics.

        Risk levels: low, medium, high, critical

        Args:
            file_metadata: File metadata dictionary

        Returns:
            Risk level string
        """
        from constants import RiskLevel, FileCategory

        risk_score = 0

        # Category-based risk
        category = file_metadata.get('category', 'unknown')
        if category == FileCategory.CORE.value:
            risk_score += 30  # Core infrastructure is critical
        elif category == FileCategory.CONFIG.value:
            risk_score += 20  # Config files can be sensitive
        elif category == FileCategory.SOURCE.value:
            risk_score += 10  # Source code has moderate risk
        elif category == FileCategory.TEST.value:
            risk_score += 5   # Test files are lower risk
        elif category == FileCategory.DOCS.value:
            risk_score += 0   # Documentation has minimal risk

        # Size-based risk (larger files are riskier)
        size = file_metadata.get('size', 0)
        if size > 1_000_000:  # > 1 MB
            risk_score += 20
        elif size > 100_000:  # > 100 KB
            risk_score += 10
        elif size > 10_000:   # > 10 KB
            risk_score += 5

        # Complexity-based risk (more lines = more complex)
        lines = file_metadata.get('lines', 0)
        if lines > 1000:
            risk_score += 20
        elif lines > 500:
            risk_score += 10
        elif lines > 100:
            risk_score += 5

        # Sensitive file detection
        filename = file_metadata.get('name', '').lower()
        path = file_metadata.get('path', '').lower()

        sensitive_patterns = [
            '.env', 'secret', 'credential', 'password', 'key', 'token',
            'cert', 'private', 'auth', 'api_key', 'database.yml'
        ]

        if any(pattern in filename or pattern in path for pattern in sensitive_patterns):
            risk_score += 40  # Sensitive files are critical

        # Map score to risk level
        if risk_score >= 60:
            return RiskLevel.CRITICAL.value
        elif risk_score >= 40:
            return RiskLevel.HIGH.value
        elif risk_score >= 20:
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value

    def analyze_dependencies(self, file_path: Path) -> List[str]:
        """
        Extract dependencies through import analysis.

        Args:
            file_path: Path to file

        Returns:
            List of imported modules/files
        """
        import re

        extension = file_path.suffix.lower()
        dependencies = set()

        try:
            # Only analyze text files
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Python imports
            if extension == '.py':
                # Match: import module, from module import ...
                patterns = [
                    r'^\s*import\s+([a-zA-Z0-9_\.]+)',
                    r'^\s*from\s+([a-zA-Z0-9_\.]+)\s+import',
                ]
                for pattern in patterns:
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        module = match.group(1).split('.')[0]  # Get root module
                        dependencies.add(module)

            # JavaScript/TypeScript imports
            elif extension in ['.js', '.ts', '.jsx', '.tsx']:
                # Match: import ... from 'module', require('module')
                patterns = [
                    r'import\s+.+\s+from\s+["\']([^"\']+)["\']',
                    r'require\(["\']([^"\']+)["\']\)',
                    r'import\(["\']([^"\']+)["\']\)',  # Dynamic imports
                ]
                for pattern in patterns:
                    for match in re.finditer(pattern, content):
                        module = match.group(1)
                        # Skip relative imports (starting with . or ..)
                        if not module.startswith('.'):
                            # Extract package name (before first /)
                            pkg = module.split('/')[0]
                            # Handle @scoped packages
                            if pkg.startswith('@') and '/' in module:
                                pkg = '/'.join(module.split('/')[:2])
                            dependencies.add(pkg)

            # TODO: Add more languages (Java, Go, etc.) in future iterations

            return sorted(list(dependencies))

        except Exception as e:
            # Failed to parse dependencies - return empty list
            logger.debug(f"Could not analyze dependencies for {file_path}: {str(e)}")
            return []

    def calculate_project_metrics(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate project-level metrics and health indicators.

        Args:
            files: List of file metadata dictionaries

        Returns:
            Dictionary with project metrics
        """
        from constants import FileCategory, RiskLevel

        metrics = {
            "total_files": len(files),
            "total_size": 0,
            "total_lines": 0,
            "file_categories": {
                FileCategory.CORE.value: 0,
                FileCategory.SOURCE.value: 0,
                FileCategory.TEMPLATE.value: 0,
                FileCategory.CONFIG.value: 0,
                FileCategory.TEST.value: 0,
                FileCategory.DOCS.value: 0,
                FileCategory.UNKNOWN.value: 0,
            },
            "risk_distribution": {
                RiskLevel.LOW.value: 0,
                RiskLevel.MEDIUM.value: 0,
                RiskLevel.HIGH.value: 0,
                RiskLevel.CRITICAL.value: 0,
            },
            "language_breakdown": {}
        }

        # Aggregate file data
        for file_meta in files:
            # Total size and lines
            metrics["total_size"] += file_meta.get("size", 0)
            metrics["total_lines"] += file_meta.get("lines", 0)

            # Category breakdown
            category = file_meta.get("category", FileCategory.UNKNOWN.value)
            if category in metrics["file_categories"]:
                metrics["file_categories"][category] += 1

            # Risk distribution
            risk = file_meta.get("risk_level", RiskLevel.LOW.value)
            if risk in metrics["risk_distribution"]:
                metrics["risk_distribution"][risk] += 1

            # Language breakdown (inferred from extension)
            extension = file_meta.get("extension", "").lower()
            language = self._infer_language(extension)
            if language:
                metrics["language_breakdown"][language] = metrics["language_breakdown"].get(language, 0) + 1

        return metrics

    def _infer_language(self, extension: str) -> str:
        """
        Infer programming language from file extension.

        Args:
            extension: File extension (e.g., '.py', '.js')

        Returns:
            Language name or empty string
        """
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.c': 'C',
            '.cpp': 'C++',
            '.h': 'C/C++',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.less': 'Less',
            '.html': 'HTML',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            '.xml': 'XML',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.sql': 'SQL',
        }
        return language_map.get(extension, '')

    def generate_manifest(
        self,
        analysis_depth: str = "standard",
        exclude_dirs: Optional[List[str]] = None,
        max_file_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive project inventory manifest.

        Args:
            analysis_depth: Depth of analysis (quick, standard, deep)
            exclude_dirs: List of directory names to exclude
            max_file_size: Maximum file size to process (bytes)

        Returns:
            Complete manifest dictionary

        Raises:
            ValueError: If analysis_depth is invalid
            IOError: If manifest cannot be generated
        """
        valid_depths = ['quick', 'standard', 'deep']
        if analysis_depth not in valid_depths:
            raise ValueError(f"Invalid analysis_depth. Must be one of: {valid_depths}")

        logger.info(f"Generating inventory manifest with depth={analysis_depth}")

        try:
            # Discover files
            files = self.discover_files(exclude_dirs=exclude_dirs, max_file_size=max_file_size)

            # Process each file: categorize, calculate risk, analyze dependencies
            logger.info(f"Processing {len(files)} files...")
            for i, file_meta in enumerate(files):
                # Reconstruct file path
                file_path = self.project_path / file_meta["path"]

                # Categorize file
                file_meta["category"] = self.categorize_file(Path(file_meta["path"]))

                # Calculate risk level (depends on category being set)
                file_meta["risk_level"] = self.calculate_risk_level(file_meta)

                # Analyze dependencies based on depth
                if analysis_depth in ['standard', 'deep']:
                    file_meta["dependencies"] = self.analyze_dependencies(file_path)
                else:
                    file_meta["dependencies"] = []

                # Log progress for large projects
                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1}/{len(files)} files...")

            # Calculate project metrics
            metrics = self.calculate_project_metrics(files)

            # Build manifest structure
            manifest = {
                "project_name": self.project_path.name,
                "project_path": str(self.project_path),
                "generated_at": datetime.now().isoformat(),
                "analysis_depth": analysis_depth,
                "metrics": metrics,
                "files": files
            }

            # Validate manifest
            self.validate_manifest(manifest)

            logger.info(f"Manifest generation complete: {len(files)} files")
            return manifest

        except Exception as e:
            log_error('manifest_generation_error', f"Failed to generate manifest: {str(e)}", error=str(e))
            raise IOError(f"Failed to generate inventory manifest: {str(e)}")

    def save_manifest(self, manifest: Dict[str, Any], output_file: Optional[Path] = None) -> Path:
        """
        Save manifest to JSON file.

        Args:
            manifest: Manifest dictionary to save
            output_file: Optional custom output file path (defaults to coderef/inventory/manifest.json)

        Returns:
            Path to saved manifest file

        Raises:
            IOError: If file cannot be written
        """
        if output_file is None:
            self.inventory_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.inventory_dir / "manifest.json"

        try:
            # Validate before saving
            self.validate_manifest(manifest)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
                f.write('\n')  # Add trailing newline

            logger.info(f"Manifest saved to {output_file}")
            return output_file

        except Exception as e:
            log_error('manifest_save_error', f"Failed to save manifest: {str(e)}", path=str(output_file))
            raise IOError(f"Failed to save manifest to {output_file}: {str(e)}")
