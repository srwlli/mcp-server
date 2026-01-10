"""
Framework detection module for identifying test frameworks in a project.

Auto-detects pytest, jest, vitest, cargo, mocha by scanning project structure,
configuration files, and dependencies. Results are cached for efficiency.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta

from src.models import TestFramework, FrameworkInfo


logger = logging.getLogger(__name__)


class FrameworkDetector:
    """Detects test frameworks in a project with caching support."""

    def __init__(self, cache_ttl_minutes: int = 60):
        """
        Initialize framework detector.

        Args:
            cache_ttl_minutes: Cache time-to-live in minutes (default 60)
        """
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self._cache: Dict[str, Tuple[List[FrameworkInfo], datetime]] = {}

    def detect_frameworks(self, project_path: str) -> List[FrameworkInfo]:
        """
        Detect all test frameworks in a project.

        Scans project structure for framework indicators and returns list of
        detected frameworks. Results are cached.

        Args:
            project_path: Path to project root directory

        Returns:
            List of FrameworkInfo objects for detected frameworks
        """
        project_path_obj = Path(project_path).resolve()
        path_str = str(project_path_obj)

        # Check cache
        if path_str in self._cache:
            frameworks, cached_at = self._cache[path_str]
            if datetime.utcnow() - cached_at < self.cache_ttl:
                logger.info(f"Using cached frameworks for {path_str}")
                return frameworks

        # Detect frameworks
        frameworks = []

        if self._detect_pytest(project_path_obj):
            frameworks.append(
                FrameworkInfo(
                    framework=TestFramework.PYTEST,
                    version=self._get_pytest_version(project_path_obj),
                    config_file=self._find_pytest_config(project_path_obj),
                )
            )

        if self._detect_jest(project_path_obj):
            frameworks.append(
                FrameworkInfo(
                    framework=TestFramework.JEST,
                    version=self._get_jest_version(project_path_obj),
                    config_file=self._find_jest_config(project_path_obj),
                )
            )

        if self._detect_vitest(project_path_obj):
            frameworks.append(
                FrameworkInfo(
                    framework=TestFramework.VITEST,
                    version=self._get_vitest_version(project_path_obj),
                    config_file=self._find_vitest_config(project_path_obj),
                )
            )

        if self._detect_cargo(project_path_obj):
            frameworks.append(
                FrameworkInfo(
                    framework=TestFramework.CARGO,
                    version=self._get_cargo_version(project_path_obj),
                    config_file=self._find_cargo_toml(project_path_obj),
                )
            )

        if self._detect_mocha(project_path_obj):
            frameworks.append(
                FrameworkInfo(
                    framework=TestFramework.MOCHA,
                    version=self._get_mocha_version(project_path_obj),
                    config_file=self._find_mocha_config(project_path_obj),
                )
            )

        # Cache results
        self._cache[path_str] = (frameworks, datetime.utcnow())

        logger.info(f"Detected {len(frameworks)} frameworks in {path_str}")
        return frameworks

    def clear_cache(self, project_path: Optional[str] = None) -> None:
        """
        Clear cached detection results.

        Args:
            project_path: If provided, clear cache only for this path.
                         If None, clear all cached results.
        """
        if project_path is None:
            self._cache.clear()
            logger.info("Cleared all framework detection cache")
        else:
            path_str = str(Path(project_path).resolve())
            if path_str in self._cache:
                del self._cache[path_str]
                logger.info(f"Cleared framework detection cache for {path_str}")

    # ========================================================================
    # Pytest Detection
    # ========================================================================

    def _detect_pytest(self, project_path: Path) -> bool:
        """Detect pytest framework."""
        # Check for pytest config files
        if (project_path / "pytest.ini").exists():
            return True
        if (project_path / "setup.cfg").exists():
            setup_cfg = project_path / "setup.cfg"
            if setup_cfg.read_text().find("[tool:pytest]") >= 0:
                return True
        if (project_path / "pyproject.toml").exists():
            pyproject = project_path / "pyproject.toml"
            if pyproject.read_text().find("[tool.pytest") >= 0:
                return True
        if (project_path / "tox.ini").exists():
            return True

        # Check for conftest.py
        if (project_path / "conftest.py").exists():
            return True

        # Check for tests directory with test files
        tests_dir = project_path / "tests"
        if tests_dir.exists() and tests_dir.is_dir():
            test_files = list(tests_dir.glob("test_*.py")) + list(
                tests_dir.glob("*_test.py")
            )
            if test_files:
                return True

        return False

    def _get_pytest_version(self, project_path: Path) -> Optional[str]:
        """Get pytest version from pyproject.toml or setup.py."""
        try:
            # Check pyproject.toml
            pyproject = project_path / "pyproject.toml"
            if pyproject.exists():
                content = pyproject.read_text()
                for line in content.split("\n"):
                    if "pytest>=" in line or "pytest==" in line:
                        # Extract version
                        parts = line.split("pytest")[1].strip().split('"')[0]
                        return parts.replace(">=", "").replace("==", "").strip()
        except Exception as e:
            logger.debug(f"Error getting pytest version: {e}")
        return None

    def _find_pytest_config(self, project_path: Path) -> Optional[str]:
        """Find pytest configuration file path."""
        for config_file in [
            "pytest.ini",
            "setup.cfg",
            "pyproject.toml",
            "tox.ini",
            "conftest.py",
        ]:
            config_path = project_path / config_file
            if config_path.exists():
                return str(config_path.relative_to(project_path))
        return None

    # ========================================================================
    # Jest Detection
    # ========================================================================

    def _detect_jest(self, project_path: Path) -> bool:
        """Detect jest framework."""
        # Check for jest config files
        for config_file in ["jest.config.js", "jest.config.ts", "jest.config.mjs"]:
            if (project_path / config_file).exists():
                return True

        # Check package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                content = json.loads(package_json.read_text())
                if "jest" in content:
                    return True
                deps = content.get("devDependencies", {})
                if "jest" in deps:
                    return True
            except Exception as e:
                logger.debug(f"Error reading package.json: {e}")
                return False

        return False

    def _get_jest_version(self, project_path: Path) -> Optional[str]:
        """Get jest version from package.json."""
        try:
            package_json = project_path / "package.json"
            if package_json.exists():
                content = json.loads(package_json.read_text())
                deps = content.get("devDependencies", {})
                if "jest" in deps:
                    return deps["jest"].lstrip("^~")
        except Exception as e:
            logger.debug(f"Error getting jest version: {e}")
        return None

    def _find_jest_config(self, project_path: Path) -> Optional[str]:
        """Find jest configuration file path."""
        for config_file in ["jest.config.js", "jest.config.ts", "jest.config.mjs"]:
            if (project_path / config_file).exists():
                return str(config_file)
        return None

    # ========================================================================
    # Vitest Detection
    # ========================================================================

    def _detect_vitest(self, project_path: Path) -> bool:
        """Detect vitest framework."""
        # Check for vitest config files
        for config_file in ["vitest.config.ts", "vitest.config.js", "vite.config.ts"]:
            if (project_path / config_file).exists():
                config_path = project_path / config_file
                if "vitest" in config_path.read_text():
                    return True

        # Check package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                content = json.loads(package_json.read_text())
                deps = content.get("devDependencies", {})
                if "vitest" in deps:
                    return True
            except Exception as e:
                logger.debug(f"Error reading package.json: {e}")

        return False

    def _get_vitest_version(self, project_path: Path) -> Optional[str]:
        """Get vitest version from package.json."""
        try:
            package_json = project_path / "package.json"
            if package_json.exists():
                content = json.loads(package_json.read_text())
                deps = content.get("devDependencies", {})
                if "vitest" in deps:
                    return deps["vitest"].lstrip("^~")
        except Exception as e:
            logger.debug(f"Error getting vitest version: {e}")
        return None

    def _find_vitest_config(self, project_path: Path) -> Optional[str]:
        """Find vitest configuration file path."""
        for config_file in ["vitest.config.ts", "vitest.config.js", "vite.config.ts"]:
            if (project_path / config_file).exists():
                return str(config_file)
        return None

    # ========================================================================
    # Cargo (Rust) Detection
    # ========================================================================

    def _detect_cargo(self, project_path: Path) -> bool:
        """Detect cargo (Rust) test framework."""
        cargo_toml = project_path / "Cargo.toml"
        if not cargo_toml.exists():
            return False

        try:
            content = cargo_toml.read_text()
            # Check for [dev-dependencies] section
            if "[dev-dependencies]" in content:
                return True
            # Check for test sources
            if (project_path / "tests").exists():
                return True
            # Check for inline tests (marked with #[test])
            src_dir = project_path / "src"
            if src_dir.exists():
                for rs_file in src_dir.glob("**/*.rs"):
                    if "#[test]" in rs_file.read_text():
                        return True
        except Exception as e:
            logger.debug(f"Error detecting cargo: {e}")

        return False

    def _get_cargo_version(self, project_path: Path) -> Optional[str]:
        """Get cargo version (returns Rust version or None)."""
        # Cargo is built-in with Rust, version is Rust version
        return None

    def _find_cargo_toml(self, project_path: Path) -> Optional[str]:
        """Find cargo configuration file path."""
        if (project_path / "Cargo.toml").exists():
            return "Cargo.toml"
        return None

    # ========================================================================
    # Mocha Detection
    # ========================================================================

    def _detect_mocha(self, project_path: Path) -> bool:
        """Detect mocha test framework."""
        # Check for .mocharc files
        for config_file in [".mocharc.json", ".mocharc.js", ".mocharc.cjs"]:
            if (project_path / config_file).exists():
                return True

        # Check package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                content = json.loads(package_json.read_text())
                if "mocha" in content:
                    return True
                deps = content.get("devDependencies", {})
                if "mocha" in deps:
                    return True
            except Exception as e:
                logger.debug(f"Error reading package.json: {e}")

        # Check for test directory with mocha patterns
        test_dir = project_path / "test"
        if test_dir.exists():
            test_files = list(test_dir.glob("**/*.js")) + list(
                test_dir.glob("**/*.ts")
            )
            if test_files:
                return True

        return False

    def _get_mocha_version(self, project_path: Path) -> Optional[str]:
        """Get mocha version from package.json."""
        try:
            package_json = project_path / "package.json"
            if package_json.exists():
                content = json.loads(package_json.read_text())
                deps = content.get("devDependencies", {})
                if "mocha" in deps:
                    return deps["mocha"].lstrip("^~")
        except Exception as e:
            logger.debug(f"Error getting mocha version: {e}")
        return None

    def _find_mocha_config(self, project_path: Path) -> Optional[str]:
        """Find mocha configuration file path."""
        for config_file in [".mocharc.json", ".mocharc.js", ".mocharc.cjs"]:
            if (project_path / config_file).exists():
                return str(config_file)
        return None


# Singleton instance
_detector = FrameworkDetector()


def detect_frameworks(project_path: str) -> List[FrameworkInfo]:
    """Detect test frameworks in a project (singleton wrapper)."""
    return _detector.detect_frameworks(project_path)


def clear_cache(project_path: Optional[str] = None) -> None:
    """Clear framework detection cache."""
    _detector.clear_cache(project_path)
