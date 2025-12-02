"""Dependency generator for analyzing package dependencies with security scanning."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys

# Add parent directory to path for constants import
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import Paths
from logger_config import logger, log_error, log_security_event


class DependencyGenerator:
    """Helper class for analyzing package dependencies across multiple ecosystems."""

    def __init__(self, project_path: Path):
        """
        Initialize dependency generator.

        Args:
            project_path: Path to project directory to analyze
        """
        self.project_path = project_path
        self.inventory_dir = project_path / Paths.INVENTORY_DIR
        self.schema_path = self.inventory_dir / "dependencies-schema.json"
        self.schema = self._load_schema()
        logger.info(f"Initialized DependencyGenerator for {project_path}")

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
            logger.debug("Dependency manifest validation passed")
        except jsonschema.ValidationError as e:
            log_error('dependency_manifest_validation_error', f"Manifest validation failed: {str(e)}", error=str(e))
            raise

    def detect_package_managers(self) -> List[str]:
        """
        Detect package managers used in project.

        Returns:
            List of detected package manager names (npm, pip, cargo, composer)
        """
        from constants import PackageManager

        detected = []

        # npm (Node.js)
        if (self.project_path / "package.json").exists():
            detected.append(PackageManager.NPM.value)
            logger.debug("Detected npm (package.json found)")

        # pip (Python)
        python_files = [
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "Pipfile"
        ]
        if any((self.project_path / f).exists() for f in python_files):
            detected.append(PackageManager.PIP.value)
            logger.debug(f"Detected pip (Python dependency files found)")

        # cargo (Rust)
        if (self.project_path / "Cargo.toml").exists():
            detected.append(PackageManager.CARGO.value)
            logger.debug("Detected cargo (Cargo.toml found)")

        # composer (PHP)
        if (self.project_path / "composer.json").exists():
            detected.append(PackageManager.COMPOSER.value)
            logger.debug("Detected composer (composer.json found)")

        logger.info(f"Detected package managers: {detected}")
        return detected

    def parse_npm_dependencies(self) -> Dict[str, Any]:
        """
        Parse npm dependencies from package.json and package-lock.json.

        Returns:
            Dictionary with npm dependencies categorized by type
        """
        from constants import DependencyType

        result = {
            DependencyType.DIRECT.value: [],
            DependencyType.DEV.value: [],
            DependencyType.PEER.value: [],
            DependencyType.TRANSITIVE.value: []
        }

        package_json_path = self.project_path / "package.json"
        if not package_json_path.exists():
            logger.warning("package.json not found")
            return result

        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)

            # Parse direct dependencies
            dependencies = package_data.get('dependencies', {})
            for name, version in dependencies.items():
                result[DependencyType.DIRECT.value].append({
                    'name': name,
                    'version': version.lstrip('^~>=<'),  # Remove semver prefix
                    'type': DependencyType.DIRECT.value,
                    'ecosystem': 'npm'
                })

            # Parse dev dependencies
            dev_dependencies = package_data.get('devDependencies', {})
            for name, version in dev_dependencies.items():
                result[DependencyType.DEV.value].append({
                    'name': name,
                    'version': version.lstrip('^~>=<'),
                    'type': DependencyType.DEV.value,
                    'ecosystem': 'npm'
                })

            # Parse peer dependencies
            peer_dependencies = package_data.get('peerDependencies', {})
            for name, version in peer_dependencies.items():
                result[DependencyType.PEER.value].append({
                    'name': name,
                    'version': version.lstrip('^~>=<'),
                    'type': DependencyType.PEER.value,
                    'ecosystem': 'npm'
                })

            # TODO: Parse package-lock.json for transitive dependencies

            logger.info(f"Parsed npm dependencies: {len(dependencies)} direct, {len(dev_dependencies)} dev, {len(peer_dependencies)} peer")

        except json.JSONDecodeError as e:
            log_error('npm_parse_error', f"Malformed package.json: {str(e)}", error=str(e))
            return result
        except Exception as e:
            log_error('npm_parse_error', f"Failed to parse npm dependencies: {str(e)}", error=str(e))
            return result

        return result

    def parse_python_dependencies(self) -> Dict[str, Any]:
        """
        Parse Python dependencies from requirements.txt, setup.py, pyproject.toml.

        Returns:
            Dictionary with Python dependencies
        """
        from constants import DependencyType

        result = {
            DependencyType.DIRECT.value: [],
            DependencyType.DEV.value: []
        }

        # Parse requirements.txt
        requirements_path = self.project_path / "requirements.txt"
        if requirements_path.exists():
            try:
                with open(requirements_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if not line or line.startswith('#'):
                            continue

                        # Parse package name and version
                        # Format: package==1.0.0, package>=1.0.0, package~=1.0.0
                        import re
                        match = re.match(r'^([a-zA-Z0-9_-]+)([>=<~!]+)(.+)$', line)
                        if match:
                            name, operator, version = match.groups()
                            result[DependencyType.DIRECT.value].append({
                                'name': name,
                                'version': version,
                                'type': DependencyType.DIRECT.value,
                                'ecosystem': 'pip'
                            })
                        else:
                            # No version specified
                            result[DependencyType.DIRECT.value].append({
                                'name': line,
                                'version': 'latest',
                                'type': DependencyType.DIRECT.value,
                                'ecosystem': 'pip'
                            })

                logger.info(f"Parsed requirements.txt: {len(result[DependencyType.DIRECT.value])} dependencies")

            except Exception as e:
                log_error('python_parse_error', f"Failed to parse requirements.txt: {str(e)}", error=str(e))

        # TODO: Parse setup.py and pyproject.toml

        return result

    def parse_cargo_dependencies(self) -> Dict[str, Any]:
        """
        Parse Rust dependencies from Cargo.toml.

        Returns:
            Dictionary with Rust dependencies
        """
        from constants import DependencyType

        result = {
            DependencyType.DIRECT.value: [],
            DependencyType.DEV.value: []
        }

        cargo_toml_path = self.project_path / "Cargo.toml"
        if not cargo_toml_path.exists():
            logger.warning("Cargo.toml not found")
            return result

        try:
            import toml
            with open(cargo_toml_path, 'r', encoding='utf-8') as f:
                cargo_data = toml.load(f)

            # Parse dependencies
            dependencies = cargo_data.get('dependencies', {})
            for name, version_spec in dependencies.items():
                # version_spec can be string or dict
                version = version_spec if isinstance(version_spec, str) else version_spec.get('version', 'latest')

                result[DependencyType.DIRECT.value].append({
                    'name': name,
                    'version': version,
                    'type': DependencyType.DIRECT.value,
                    'ecosystem': 'cargo'
                })

            # Parse dev dependencies
            dev_dependencies = cargo_data.get('dev-dependencies', {})
            for name, version_spec in dev_dependencies.items():
                version = version_spec if isinstance(version_spec, str) else version_spec.get('version', 'latest')

                result[DependencyType.DEV.value].append({
                    'name': name,
                    'version': version,
                    'type': DependencyType.DEV.value,
                    'ecosystem': 'cargo'
                })

            logger.info(f"Parsed Cargo dependencies: {len(dependencies)} direct, {len(dev_dependencies)} dev")

        except ImportError:
            log_error('cargo_parse_error', "toml package not installed. Run: pip install toml")
            return result
        except Exception as e:
            log_error('cargo_parse_error', f"Failed to parse Cargo.toml: {str(e)}", error=str(e))
            return result

        return result

    def scan_vulnerabilities(self, dependencies: List[Dict[str, Any]], ecosystem: str) -> List[Dict[str, Any]]:
        """
        Scan dependencies for security vulnerabilities using OSV API.

        Args:
            dependencies: List of dependency dictionaries
            ecosystem: Package ecosystem (npm, pip, cargo, composer)

        Returns:
            List of vulnerability dictionaries
        """
        vulnerabilities = []

        # OSV API endpoint
        osv_api_url = "https://api.osv.dev/v1/query"

        for dep in dependencies:
            try:
                # Map ecosystem names to OSV ecosystem identifiers
                osv_ecosystem = {
                    'npm': 'npm',
                    'pip': 'PyPI',
                    'cargo': 'crates.io',
                    'composer': 'Packagist'
                }.get(ecosystem, ecosystem)

                # Query OSV API
                import requests
                response = requests.post(
                    osv_api_url,
                    json={
                        "package": {
                            "name": dep['name'],
                            "ecosystem": osv_ecosystem
                        },
                        "version": dep['version']
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    vulns = data.get('vulns', [])

                    for vuln in vulns:
                        from constants import VulnerabilitySeverity

                        vulnerabilities.append({
                            'id': vuln.get('id', 'UNKNOWN'),
                            'package_name': dep['name'],
                            'ecosystem': ecosystem,
                            'severity': self._extract_severity(vuln),
                            'summary': vuln.get('summary', ''),
                            'details': vuln.get('details', ''),
                            'affected_versions': self._extract_affected_versions(vuln),
                            'fixed_version': self._extract_fixed_version(vuln),
                            'published': vuln.get('published', ''),
                            'modified': vuln.get('modified', ''),
                            'references': [ref.get('url', '') for ref in vuln.get('references', [])],
                            'cvss_score': self._extract_cvss_score(vuln)
                        })

            except requests.RequestException as e:
                log_error('osv_api_error', f"Failed to query OSV API for {dep['name']}: {str(e)}")
                continue
            except Exception as e:
                log_error('vulnerability_scan_error', f"Error scanning {dep['name']}: {str(e)}")
                continue

        logger.info(f"Scanned {len(dependencies)} dependencies, found {len(vulnerabilities)} vulnerabilities")
        return vulnerabilities

    def _extract_severity(self, vuln: Dict[str, Any]) -> str:
        """Extract severity from OSV vulnerability data."""
        from constants import VulnerabilitySeverity

        # Try to get severity from severity field
        severity_obj = vuln.get('severity', [])
        if severity_obj:
            severity = severity_obj[0].get('score', '').upper()
            if 'CRITICAL' in severity:
                return VulnerabilitySeverity.CRITICAL.value
            elif 'HIGH' in severity:
                return VulnerabilitySeverity.HIGH.value
            elif 'MEDIUM' in severity or 'MODERATE' in severity:
                return VulnerabilitySeverity.MEDIUM.value
            elif 'LOW' in severity:
                return VulnerabilitySeverity.LOW.value

        # Default to medium if unknown
        return VulnerabilitySeverity.MEDIUM.value

    def _extract_affected_versions(self, vuln: Dict[str, Any]) -> str:
        """Extract affected version range from OSV data."""
        affected = vuln.get('affected', [])
        if affected:
            ranges = affected[0].get('ranges', [])
            if ranges:
                events = ranges[0].get('events', [])
                # Format as version range
                if events:
                    return str(events)
        return 'unknown'

    def _extract_fixed_version(self, vuln: Dict[str, Any]) -> str:
        """Extract fixed version from OSV data."""
        affected = vuln.get('affected', [])
        if affected:
            ranges = affected[0].get('ranges', [])
            if ranges:
                events = ranges[0].get('events', [])
                for event in events:
                    if 'fixed' in event:
                        return event['fixed']
        return 'unknown'

    def _extract_cvss_score(self, vuln: Dict[str, Any]) -> float:
        """Extract CVSS score from OSV data."""
        severity_obj = vuln.get('severity', [])
        if severity_obj:
            score = severity_obj[0].get('score', '')
            # Extract numeric score from CVSS string
            try:
                import re
                match = re.search(r'(\d+\.?\d*)', score)
                if match:
                    return float(match.group(1))
            except (ValueError, AttributeError):
                pass
        return 0.0

    def check_latest_versions(self, dependencies: List[Dict[str, Any]], ecosystem: str) -> List[Dict[str, Any]]:
        """
        Check for latest versions of dependencies.

        Args:
            dependencies: List of dependency dictionaries
            ecosystem: Package ecosystem (npm, pip, cargo, composer)

        Returns:
            Updated list of dependency dictionaries with latest_version and outdated fields
        """
        for dep in dependencies:
            try:
                if ecosystem == 'npm':
                    latest = self._get_npm_latest_version(dep['name'])
                elif ecosystem == 'pip':
                    latest = self._get_pypi_latest_version(dep['name'])
                else:
                    # Cargo and Composer not implemented yet
                    latest = None

                if latest:
                    dep['latest_version'] = latest
                    # Simple version comparison (TODO: use packaging library for accurate comparison)
                    dep['outdated'] = dep['version'] != latest
                else:
                    dep['latest_version'] = 'unknown'
                    dep['outdated'] = False

            except Exception as e:
                log_error('version_check_error', f"Failed to check latest version for {dep['name']}: {str(e)}")
                dep['latest_version'] = 'unknown'
                dep['outdated'] = False

        return dependencies

    def _get_npm_latest_version(self, package_name: str) -> Optional[str]:
        """Get latest version from npm registry."""
        try:
            import requests
            response = requests.get(
                f"https://registry.npmjs.org/{package_name}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('dist-tags', {}).get('latest', None)
        except Exception as e:
            log_error('npm_registry_error', f"Failed to query npm registry for {package_name}: {str(e)}")
        return None

    def _get_pypi_latest_version(self, package_name: str) -> Optional[str]:
        """Get latest version from PyPI."""
        try:
            import requests
            response = requests.get(
                f"https://pypi.org/pypi/{package_name}/json",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('info', {}).get('version', None)
        except Exception as e:
            log_error('pypi_api_error', f"Failed to query PyPI for {package_name}: {str(e)}")
        return None

    def calculate_metrics(self, all_dependencies: Dict[str, Any], vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate dependency metrics.

        Args:
            all_dependencies: Dependencies by ecosystem
            vulnerabilities: List of vulnerabilities

        Returns:
            Metrics dictionary
        """
        from constants import DependencyType, VulnerabilitySeverity

        metrics = {
            'total_dependencies': 0,
            'direct_count': 0,
            'dev_count': 0,
            'peer_count': 0,
            'transitive_count': 0,
            'outdated_count': 0,
            'vulnerable_count': 0,
            'critical_vulnerabilities': 0,
            'high_vulnerabilities': 0,
            'medium_vulnerabilities': 0,
            'low_vulnerabilities': 0,
            'license_breakdown': {},
            'ecosystem_breakdown': {}
        }

        # Count dependencies by type and ecosystem
        for ecosystem, dep_types in all_dependencies.items():
            ecosystem_total = 0
            for dep_type, deps in dep_types.items():
                count = len(deps)
                ecosystem_total += count

                if dep_type == DependencyType.DIRECT.value:
                    metrics['direct_count'] += count
                elif dep_type == DependencyType.DEV.value:
                    metrics['dev_count'] += count
                elif dep_type == DependencyType.PEER.value:
                    metrics['peer_count'] += count
                elif dep_type == DependencyType.TRANSITIVE.value:
                    metrics['transitive_count'] += count

                # Count outdated
                for dep in deps:
                    if dep.get('outdated', False):
                        metrics['outdated_count'] += 1

            metrics['ecosystem_breakdown'][ecosystem] = ecosystem_total
            metrics['total_dependencies'] += ecosystem_total

        # Count vulnerabilities by severity
        vulnerable_packages = set()
        for vuln in vulnerabilities:
            vulnerable_packages.add(vuln['package_name'])

            severity = vuln.get('severity', '').lower()
            if severity == VulnerabilitySeverity.CRITICAL.value:
                metrics['critical_vulnerabilities'] += 1
            elif severity == VulnerabilitySeverity.HIGH.value:
                metrics['high_vulnerabilities'] += 1
            elif severity == VulnerabilitySeverity.MEDIUM.value:
                metrics['medium_vulnerabilities'] += 1
            elif severity == VulnerabilitySeverity.LOW.value:
                metrics['low_vulnerabilities'] += 1

        metrics['vulnerable_count'] = len(vulnerable_packages)

        logger.info(f"Calculated metrics: {metrics['total_dependencies']} total deps, {metrics['vulnerable_count']} vulnerable")
        return metrics

    def parse_composer_dependencies(self) -> Dict[str, Any]:
        """
        Parse PHP dependencies from composer.json.

        Returns:
            Dictionary with PHP dependencies
        """
        from constants import DependencyType

        result = {
            DependencyType.DIRECT.value: [],
            DependencyType.DEV.value: []
        }

        composer_json_path = self.project_path / "composer.json"
        if not composer_json_path.exists():
            logger.warning("composer.json not found")
            return result

        try:
            with open(composer_json_path, 'r', encoding='utf-8') as f:
                composer_data = json.load(f)

            # Parse dependencies
            dependencies = composer_data.get('require', {})
            for name, version in dependencies.items():
                # Skip PHP version requirement
                if name == 'php':
                    continue

                result[DependencyType.DIRECT.value].append({
                    'name': name,
                    'version': version.lstrip('^~>=<'),
                    'type': DependencyType.DIRECT.value,
                    'ecosystem': 'composer'
                })

            # Parse dev dependencies
            dev_dependencies = composer_data.get('require-dev', {})
            for name, version in dev_dependencies.items():
                result[DependencyType.DEV.value].append({
                    'name': name,
                    'version': version.lstrip('^~>=<'),
                    'type': DependencyType.DEV.value,
                    'ecosystem': 'composer'
                })

            logger.info(f"Parsed composer dependencies: {len(dependencies)} direct, {len(dev_dependencies)} dev")

        except json.JSONDecodeError as e:
            log_error('composer_parse_error', f"Malformed composer.json: {str(e)}", error=str(e))
            return result
        except Exception as e:
            log_error('composer_parse_error', f"Failed to parse composer.json: {str(e)}", error=str(e))
            return result

        return result

    def generate_manifest(
        self,
        scan_security: bool = True,
        ecosystems: Optional[List[str]] = None,
        include_transitive: bool = False
    ) -> Dict[str, Any]:
        """
        Generate comprehensive dependency manifest.

        Args:
            scan_security: Whether to scan for security vulnerabilities
            ecosystems: List of ecosystems to analyze (None = all detected)
            include_transitive: Whether to include transitive dependencies

        Returns:
            Complete dependency manifest dictionary

        Raises:
            IOError: If manifest cannot be generated
        """
        logger.info(f"Generating dependency manifest (security={scan_security})")

        try:
            # Detect package managers
            detected_managers = self.detect_package_managers()

            # Filter by requested ecosystems
            if ecosystems and 'all' not in ecosystems:
                detected_managers = [m for m in detected_managers if m in ecosystems]

            if not detected_managers:
                logger.warning("No package managers detected in project")
                return {
                    "project_name": self.project_path.name,
                    "project_path": str(self.project_path),
                    "generated_at": datetime.now().isoformat(),
                    "package_managers": [],
                    "dependencies": {},
                    "vulnerabilities": [],
                    "metrics": {
                        "total_dependencies": 0,
                        "direct_count": 0,
                        "dev_count": 0,
                        "outdated_count": 0,
                        "vulnerable_count": 0
                    }
                }

            # Parse dependencies for each ecosystem
            all_dependencies = {}
            all_vulnerabilities = []

            for manager in detected_managers:
                logger.info(f"Processing {manager} dependencies...")

                # Parse dependencies
                if manager == 'npm':
                    deps_by_type = self.parse_npm_dependencies()
                elif manager == 'pip':
                    deps_by_type = self.parse_python_dependencies()
                elif manager == 'cargo':
                    deps_by_type = self.parse_cargo_dependencies()
                elif manager == 'composer':
                    deps_by_type = self.parse_composer_dependencies()
                else:
                    continue

                # Flatten dependencies for analysis
                all_deps_for_ecosystem = []
                for dep_type, deps in deps_by_type.items():
                    all_deps_for_ecosystem.extend(deps)

                # Check for latest versions (if requested)
                if scan_security and all_deps_for_ecosystem:
                    logger.info(f"Checking latest versions for {len(all_deps_for_ecosystem)} {manager} packages...")
                    all_deps_for_ecosystem = self.check_latest_versions(all_deps_for_ecosystem, manager)

                    # Scan for vulnerabilities
                    logger.info(f"Scanning {len(all_deps_for_ecosystem)} {manager} packages for vulnerabilities...")
                    vulnerabilities = self.scan_vulnerabilities(all_deps_for_ecosystem, manager)
                    all_vulnerabilities.extend(vulnerabilities)

                # Update dependencies with enriched data
                enriched_deps_by_type = {}
                for dep_type, deps in deps_by_type.items():
                    # Match enriched deps back to original structure
                    enriched_deps = []
                    for dep in deps:
                        # Find matching enriched dep
                        enriched_dep = next(
                            (d for d in all_deps_for_ecosystem if d['name'] == dep['name']),
                            dep
                        )
                        enriched_deps.append(enriched_dep)
                    enriched_deps_by_type[dep_type] = enriched_deps

                all_dependencies[manager] = enriched_deps_by_type

            # Calculate metrics
            logger.info("Calculating dependency metrics...")
            metrics = self.calculate_metrics(all_dependencies, all_vulnerabilities)

            # Build manifest structure
            manifest = {
                "project_name": self.project_path.name,
                "project_path": str(self.project_path),
                "generated_at": datetime.now().isoformat(),
                "package_managers": detected_managers,
                "dependencies": all_dependencies,
                "vulnerabilities": all_vulnerabilities,
                "metrics": metrics
            }

            # Validate manifest
            self.validate_manifest(manifest)

            logger.info(f"Dependency manifest generation complete")
            return manifest

        except Exception as e:
            log_error('dependency_manifest_generation_error', f"Failed to generate manifest: {str(e)}", error=str(e))
            raise IOError(f"Failed to generate dependency manifest: {str(e)}")

    def save_manifest(self, manifest: Dict[str, Any], output_file: Optional[Path] = None) -> Path:
        """
        Save manifest to JSON file.

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
            output_file = self.inventory_dir / "dependencies.json"

        try:
            # Validate before saving
            self.validate_manifest(manifest)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
                f.write('\n')  # Add trailing newline

            logger.info(f"Dependency manifest saved to {output_file}")
            return output_file

        except Exception as e:
            log_error('dependency_manifest_save_error', f"Failed to save manifest: {str(e)}", path=str(output_file))
            raise IOError(f"Failed to save manifest to {output_file}: {str(e)}")
