"""Configuration generator for discovering and analyzing configuration files."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
import re

# Add parent directory to path for constants import
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import Paths
from logger_config import logger, log_error, log_security_event


class ConfigGenerator:
    """Helper class for generating configuration file inventories with sensitive value detection."""

    def __init__(self, project_path: Path):
        """
        Initialize configuration generator.

        Args:
            project_path: Path to project directory to analyze
        """
        self.project_path = project_path
        self.inventory_dir = project_path / Paths.INVENTORY_DIR
        self.schema_path = self.inventory_dir / "config-schema.json"
        self.schema = self._load_schema()
        logger.info(f"Initialized ConfigGenerator for {project_path}")

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
            logger.debug("Configuration manifest validation passed")
        except jsonschema.ValidationError as e:
            log_error('config_manifest_validation_error', f"Manifest validation failed: {str(e)}", error=str(e))
            raise

    def detect_config_files(self) -> List[Path]:
        """
        Discover configuration files by pattern matching.

        Looks for:
        - JSON files: *.json, .*.json
        - YAML files: *.yaml, *.yml
        - TOML files: *.toml
        - INI files: *.ini, *.cfg, *.conf
        - ENV files: .env*, *.env

        Returns:
            List of configuration file paths

        Raises:
            PermissionError: If directory cannot be accessed
        """
        logger.info(f"Discovering configuration files in {self.project_path}")

        config_files = []

        # Config file patterns by type
        config_patterns = {
            'json': ['*.json', '.*.json'],
            'yaml': ['*.yaml', '*.yml'],
            'toml': ['*.toml'],
            'ini': ['*.ini', '*.cfg', '*.conf', '*.config'],
            'env': ['.env*', '*.env']
        }

        # Directories to exclude
        exclude_dirs = {'node_modules', '.git', 'dist', 'build', '.next', 'out',
                       'coverage', '__pycache__', '.venv', 'venv', 'vendor'}

        try:
            for root, dirs, filenames in self.project_path.walk():
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                # Check each file against config patterns
                for filename in filenames:
                    file_path = root / filename

                    # Check if file matches any config pattern
                    for format_type, patterns in config_patterns.items():
                        for pattern in patterns:
                            if self._match_pattern(filename, pattern):
                                config_files.append(file_path)
                                logger.debug(f"Found {format_type} config: {file_path}")
                                break

            logger.info(f"Discovered {len(config_files)} configuration files")
            return config_files

        except PermissionError as e:
            log_security_event('permission_denied', f"Cannot access project directory: {self.project_path}",
                             path=str(self.project_path))
            raise PermissionError(f"Cannot access project directory: {self.project_path}")

    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """
        Check if filename matches glob-style pattern.

        Args:
            filename: File name to check
            pattern: Glob pattern (e.g., '*.json', '.env*')

        Returns:
            True if filename matches pattern
        """
        import fnmatch
        return fnmatch.fnmatch(filename.lower(), pattern.lower())

    def detect_format(self, file_path: Path) -> str:
        """
        Detect configuration file format from extension.

        Args:
            file_path: Path to configuration file

        Returns:
            Format string (json, yaml, toml, ini, env)
        """
        filename = file_path.name.lower()
        extension = file_path.suffix.lower()

        # ENV files (special handling)
        if filename.startswith('.env') or filename.endswith('.env'):
            return 'env'

        # Extension-based detection
        if extension == '.json':
            return 'json'
        elif extension in ['.yaml', '.yml']:
            return 'yaml'
        elif extension == '.toml':
            return 'toml'
        elif extension in ['.ini', '.cfg', '.conf', '.config']:
            return 'ini'

        # Default to unknown
        return 'unknown'

    def parse_config_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse configuration file based on its format.

        Args:
            file_path: Path to configuration file

        Returns:
            Parsed configuration dictionary

        Raises:
            ValueError: If format is unsupported or file is malformed
        """
        format_type = self.detect_format(file_path)
        logger.debug(f"Parsing {format_type} config file: {file_path}")

        try:
            if format_type == 'json':
                return self._parse_json(file_path)
            elif format_type == 'yaml':
                return self._parse_yaml(file_path)
            elif format_type == 'toml':
                return self._parse_toml(file_path)
            elif format_type == 'ini':
                return self._parse_ini(file_path)
            elif format_type == 'env':
                return self._parse_env(file_path)
            else:
                logger.warning(f"Unknown config format for {file_path}")
                return {}

        except Exception as e:
            log_error('config_parse_error', f"Failed to parse {file_path}: {str(e)}",
                     path=str(file_path), format=format_type)
            # Return empty dict on parse error (graceful degradation)
            return {}

    def _parse_json(self, file_path: Path) -> Dict[str, Any]:
        """Parse JSON configuration file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _parse_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Parse YAML configuration file."""
        try:
            import yaml
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                # YAML can return None for empty files
                return data if isinstance(data, dict) else {}
        except ImportError:
            log_error('yaml_import_error', "pyyaml not installed. Run: pip install pyyaml")
            return {}

    def _parse_toml(self, file_path: Path) -> Dict[str, Any]:
        """Parse TOML configuration file."""
        try:
            import toml
            with open(file_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except ImportError:
            log_error('toml_import_error', "toml not installed. Run: pip install toml")
            return {}

    def _parse_ini(self, file_path: Path) -> Dict[str, Any]:
        """Parse INI configuration file."""
        import configparser
        config = configparser.ConfigParser()
        config.read(file_path, encoding='utf-8')

        # Convert ConfigParser to nested dict
        result = {}
        for section in config.sections():
            result[section] = dict(config.items(section))

        return result

    def _parse_env(self, file_path: Path) -> Dict[str, Any]:
        """Parse .env configuration file."""
        try:
            from dotenv import dotenv_values
            # dotenv_values returns a dict
            return dotenv_values(file_path)
        except ImportError:
            log_error('dotenv_import_error', "python-dotenv not installed. Run: pip install python-dotenv")
            # Fallback: simple line-by-line parsing
            return self._parse_env_fallback(file_path)

    def _parse_env_fallback(self, file_path: Path) -> Dict[str, Any]:
        """Fallback parser for .env files without python-dotenv."""
        result = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    # Parse KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        result[key.strip()] = value.strip()
        except Exception as e:
            log_error('env_parse_error', f"Failed to parse .env file: {str(e)}")
        return result

    def detect_sensitive_values(self, config_data: Dict[str, Any], file_path: Path) -> List[str]:
        """
        Detect sensitive keys using regex patterns.

        Detects:
        - API keys (api_key, apikey, API_KEY, etc.)
        - Passwords (password, passwd, pwd, etc.)
        - Tokens (token, auth_token, access_token, etc.)
        - Secrets (secret, private_key, etc.)

        Args:
            config_data: Parsed configuration dictionary
            file_path: Path to configuration file (for logging)

        Returns:
            List of sensitive keys found
        """
        sensitive_keys = []

        # Sensitive key patterns (case-insensitive)
        patterns = [
            r'api[_-]?key',
            r'password',
            r'passwd',
            r'pwd',
            r'token',
            r'auth[_-]?token',
            r'access[_-]?token',
            r'secret',
            r'private[_-]?key',
            r'credential',
            r'auth',
            r'bearer',
            r'session[_-]?key',
            r'encryption[_-]?key',
        ]

        def check_keys(data: Any, prefix: str = ''):
            """Recursively check keys in nested dictionaries."""
            if isinstance(data, dict):
                for key, value in data.items():
                    full_key = f"{prefix}.{key}" if prefix else key

                    # Check if key matches sensitive pattern
                    key_lower = key.lower()
                    for pattern in patterns:
                        if re.search(pattern, key_lower):
                            sensitive_keys.append(full_key)
                            logger.debug(f"Detected sensitive key: {full_key}")
                            break

                    # Recursively check nested dicts
                    check_keys(value, full_key)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    check_keys(item, f"{prefix}[{i}]")

        # Check all keys in config
        check_keys(config_data)

        if sensitive_keys:
            log_security_event('sensitive_data_detected',
                             f"Found {len(sensitive_keys)} sensitive keys in {file_path}",
                             path=str(file_path),
                             count=len(sensitive_keys))

        return sensitive_keys

    def mask_sensitive_values(self, config_data: Dict[str, Any], sensitive_keys: List[str]) -> Dict[str, Any]:
        """
        Replace sensitive values with [REDACTED].

        Args:
            config_data: Parsed configuration dictionary
            sensitive_keys: List of sensitive keys to mask

        Returns:
            Configuration dictionary with sensitive values masked
        """
        import copy
        masked_data = copy.deepcopy(config_data)

        def mask_recursive(data: Any, path: str = ''):
            """Recursively mask sensitive values."""
            if isinstance(data, dict):
                for key, value in data.items():
                    full_path = f"{path}.{key}" if path else key

                    # Check if this key should be masked
                    if full_path in sensitive_keys:
                        data[key] = '[REDACTED]'
                        logger.debug(f"Masked sensitive value at: {full_path}")
                    else:
                        # Recursively process nested structures
                        mask_recursive(value, full_path)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    mask_recursive(item, f"{path}[{i}]")

        mask_recursive(masked_data)
        return masked_data

    def analyze_config_file(self, file_path: Path, mask_sensitive: bool = True) -> Dict[str, Any]:
        """
        Analyze a single configuration file.

        Args:
            file_path: Path to configuration file
            mask_sensitive: Whether to mask sensitive values

        Returns:
            Configuration file metadata dictionary
        """
        try:
            # Get file stats
            stats = file_path.stat()
            relative_path = file_path.relative_to(self.project_path)

            # Detect format
            format_type = self.detect_format(file_path)

            # Parse configuration
            config_data = self.parse_config_file(file_path)

            # Detect sensitive values
            sensitive_keys = self.detect_sensitive_values(config_data, file_path)

            # Mask sensitive values if requested
            if mask_sensitive and sensitive_keys:
                config_data = self.mask_sensitive_values(config_data, sensitive_keys)

            # Count keys (flatten nested dict)
            def count_keys(data: Any) -> int:
                if isinstance(data, dict):
                    return len(data) + sum(count_keys(v) for v in data.values())
                elif isinstance(data, list):
                    return sum(count_keys(item) for item in data)
                return 0

            key_count = count_keys(config_data)

            return {
                'file_path': str(relative_path).replace('\\', '/'),
                'format': format_type,
                'key_count': key_count,
                'sensitive_keys': sensitive_keys,
                'has_sensitive': len(sensitive_keys) > 0,
                'last_modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'size_bytes': stats.st_size,
                'config_data': config_data if len(sensitive_keys) == 0 else None  # Only include data if no sensitive values
            }

        except PermissionError as e:
            log_security_event('permission_denied', f"Cannot access config file: {file_path}", path=str(file_path))
            return None
        except Exception as e:
            log_error('config_analysis_error', f"Failed to analyze {file_path}: {str(e)}", path=str(file_path))
            return None

    def generate_manifest(
        self,
        formats: Optional[List[str]] = None,
        mask_sensitive: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive configuration inventory manifest.

        Args:
            formats: List of formats to analyze (None = all formats)
            mask_sensitive: Whether to mask sensitive values (default: True)

        Returns:
            Complete configuration manifest dictionary

        Raises:
            IOError: If manifest cannot be generated
        """
        logger.info(f"Generating configuration manifest (mask_sensitive={mask_sensitive})")

        try:
            # Discover configuration files
            config_files = self.detect_config_files()

            # Filter by requested formats
            if formats and 'all' not in formats:
                filtered_files = []
                for file_path in config_files:
                    if self.detect_format(file_path) in formats:
                        filtered_files.append(file_path)
                config_files = filtered_files

            logger.info(f"Analyzing {len(config_files)} configuration files...")

            # Analyze each config file
            analyzed_files = []
            formats_detected = set()

            for i, file_path in enumerate(config_files):
                logger.debug(f"Analyzing {file_path}...")

                file_data = self.analyze_config_file(file_path, mask_sensitive=mask_sensitive)

                if file_data:
                    analyzed_files.append(file_data)
                    formats_detected.add(file_data['format'])

                # Log progress for large sets
                if (i + 1) % 10 == 0:
                    logger.info(f"Analyzed {i + 1}/{len(config_files)} config files...")

            # Calculate metrics
            metrics = {
                'total_files': len(analyzed_files),
                'sensitive_files': sum(1 for f in analyzed_files if f['has_sensitive']),
                'formats_detected': list(formats_detected),
                'total_keys': sum(f['key_count'] for f in analyzed_files),
                'total_sensitive_keys': sum(len(f['sensitive_keys']) for f in analyzed_files)
            }

            # Build manifest structure
            manifest = {
                'project_name': self.project_path.name,
                'project_path': str(self.project_path),
                'generated_at': datetime.now().isoformat(),
                'formats': list(formats_detected),
                'config_files': analyzed_files,
                'metrics': metrics
            }

            # Validate manifest
            self.validate_manifest(manifest)

            logger.info(f"Configuration manifest generation complete: {len(analyzed_files)} files, {metrics['sensitive_files']} with sensitive data")
            return manifest

        except Exception as e:
            log_error('config_manifest_generation_error', f"Failed to generate manifest: {str(e)}", error=str(e))
            raise IOError(f"Failed to generate configuration manifest: {str(e)}")

    def save_manifest(self, manifest: Dict[str, Any], output_file: Optional[Path] = None) -> Path:
        """
        Save configuration manifest to JSON file.

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
            output_file = self.inventory_dir / "config.json"

        try:
            # Validate before saving
            self.validate_manifest(manifest)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
                f.write('\n')  # Add trailing newline

            logger.info(f"Configuration manifest saved to {output_file}")
            return output_file

        except Exception as e:
            log_error('config_manifest_save_error', f"Failed to save manifest: {str(e)}", path=str(output_file))
            raise IOError(f"Failed to save manifest to {output_file}: {str(e)}")
