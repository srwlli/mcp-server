"""Unit tests for framework_detector module."""

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from src.framework_detector import FrameworkDetector, detect_frameworks
from src.models import TestFramework


@pytest.fixture
def temp_project() -> Generator[Path, None, None]:
    """Create a temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def detector() -> FrameworkDetector:
    """Create a fresh detector instance for each test."""
    return FrameworkDetector(cache_ttl_minutes=60)


class TestPytestDetection:
    """Test pytest framework detection."""

    def test_detect_pytest_with_pytest_ini(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with pytest.ini file."""
        (temp_project / "pytest.ini").write_text("[pytest]\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert len(frameworks) > 0
        assert any(f.framework == TestFramework.PYTEST for f in frameworks)

    def test_detect_pytest_with_setup_cfg(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with setup.cfg [tool:pytest] section."""
        (temp_project / "setup.cfg").write_text("[tool:pytest]\ntestpaths = tests\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.PYTEST for f in frameworks)

    def test_detect_pytest_with_pyproject_toml(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with pyproject.toml [tool.pytest] section."""
        (temp_project / "pyproject.toml").write_text("[tool.pytest.ini_options]\ntestpaths = [\"tests\"]\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.PYTEST for f in frameworks)

    def test_detect_pytest_with_conftest(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with conftest.py file."""
        (temp_project / "conftest.py").write_text("# pytest config\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.PYTEST for f in frameworks)

    def test_detect_pytest_with_tests_directory(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with tests directory containing test files."""
        tests_dir = temp_project / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_example.py").write_text("def test_example(): pass\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.PYTEST for f in frameworks)

    def test_detect_pytest_with_tox_ini(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with tox.ini file."""
        (temp_project / "tox.ini").write_text("[testenv]\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.PYTEST for f in frameworks)

    def test_pytest_config_file_finding(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test that pytest config file is correctly identified."""
        (temp_project / "pytest.ini").write_text("[pytest]\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        pytest_fw = next((f for f in frameworks if f.framework == TestFramework.PYTEST), None)
        assert pytest_fw is not None
        assert pytest_fw.config_file == "pytest.ini"


class TestJestDetection:
    """Test jest framework detection."""

    def test_detect_jest_with_jest_config_js(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with jest.config.js."""
        (temp_project / "jest.config.js").write_text("module.exports = {};\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.JEST for f in frameworks)

    def test_detect_jest_with_jest_config_ts(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with jest.config.ts."""
        (temp_project / "jest.config.ts").write_text("export default {};\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.JEST for f in frameworks)

    def test_detect_jest_in_package_json(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with jest in package.json."""
        package_json = {"devDependencies": {"jest": "^29.0.0"}}
        (temp_project / "package.json").write_text(json.dumps(package_json))
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.JEST for f in frameworks)

    def test_jest_version_detection(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test that jest version is correctly extracted."""
        package_json = {"devDependencies": {"jest": "^29.5.0"}}
        (temp_project / "package.json").write_text(json.dumps(package_json))
        frameworks = detector.detect_frameworks(str(temp_project))
        jest_fw = next((f for f in frameworks if f.framework == TestFramework.JEST), None)
        assert jest_fw is not None
        assert jest_fw.version == "29.5.0"

    def test_jest_config_file_finding(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test that jest config file is correctly identified."""
        (temp_project / "jest.config.js").write_text("module.exports = {};\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        jest_fw = next((f for f in frameworks if f.framework == TestFramework.JEST), None)
        assert jest_fw is not None
        assert jest_fw.config_file == "jest.config.js"


class TestVitestDetection:
    """Test vitest framework detection."""

    def test_detect_vitest_with_vitest_config_ts(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with vitest.config.ts."""
        (temp_project / "vitest.config.ts").write_text("import { defineConfig } from 'vitest/config';\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.VITEST for f in frameworks)

    def test_detect_vitest_in_package_json(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with vitest in package.json."""
        package_json = {"devDependencies": {"vitest": "^0.34.0"}}
        (temp_project / "package.json").write_text(json.dumps(package_json))
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.VITEST for f in frameworks)

    def test_vitest_version_detection(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test that vitest version is correctly extracted."""
        package_json = {"devDependencies": {"vitest": "^0.34.6"}}
        (temp_project / "package.json").write_text(json.dumps(package_json))
        frameworks = detector.detect_frameworks(str(temp_project))
        vitest_fw = next((f for f in frameworks if f.framework == TestFramework.VITEST), None)
        assert vitest_fw is not None
        assert vitest_fw.version == "0.34.6"


class TestCargoDetection:
    """Test cargo (Rust) framework detection."""

    def test_detect_cargo_with_cargo_toml(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with Cargo.toml having dev-dependencies."""
        cargo_toml = "[package]\nname = \"test\"\n[dev-dependencies]\n"
        (temp_project / "Cargo.toml").write_text(cargo_toml)
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.CARGO for f in frameworks)

    def test_detect_cargo_with_tests_directory(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with tests directory."""
        (temp_project / "Cargo.toml").write_text("[package]\nname = \"test\"\n")
        (temp_project / "tests").mkdir()
        (temp_project / "tests" / "integration_test.rs").write_text("# test\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.CARGO for f in frameworks)

    def test_detect_cargo_with_inline_tests(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with inline #[test] annotations."""
        (temp_project / "Cargo.toml").write_text("[package]\nname = \"test\"\n")
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "lib.rs").write_text("#[test]\nfn test_example() {}\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.CARGO for f in frameworks)

    def test_cargo_config_file_finding(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test that Cargo.toml is correctly identified."""
        (temp_project / "Cargo.toml").write_text("[package]\nname = \"test\"\n[dev-dependencies]\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        cargo_fw = next((f for f in frameworks if f.framework == TestFramework.CARGO), None)
        assert cargo_fw is not None
        assert cargo_fw.config_file == "Cargo.toml"


class TestMochaDetection:
    """Test mocha framework detection."""

    def test_detect_mocha_with_mocharc_json(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with .mocharc.json."""
        (temp_project / ".mocharc.json").write_text('{"require": "ts-node/register"}')
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.MOCHA for f in frameworks)

    def test_detect_mocha_in_package_json(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with mocha in package.json."""
        package_json = {"devDependencies": {"mocha": "^10.0.0"}}
        (temp_project / "package.json").write_text(json.dumps(package_json))
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.MOCHA for f in frameworks)

    def test_detect_mocha_with_test_directory(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test detection with test directory containing test files."""
        test_dir = temp_project / "test"
        test_dir.mkdir()
        (test_dir / "test_example.js").write_text("describe('test', () => {});\n")
        frameworks = detector.detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.MOCHA for f in frameworks)

    def test_mocha_version_detection(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test that mocha version is correctly extracted."""
        package_json = {"devDependencies": {"mocha": "^10.2.0"}}
        (temp_project / "package.json").write_text(json.dumps(package_json))
        frameworks = detector.detect_frameworks(str(temp_project))
        mocha_fw = next((f for f in frameworks if f.framework == TestFramework.MOCHA), None)
        assert mocha_fw is not None
        assert mocha_fw.version == "10.2.0"


class TestMultipleFrameworks:
    """Test detection of multiple frameworks in one project."""

    def test_detect_multiple_frameworks(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test that multiple frameworks can be detected in one project."""
        # Add pytest
        (temp_project / "pytest.ini").write_text("[pytest]\n")
        # Add jest
        package_json = {"devDependencies": {"jest": "^29.0.0"}}
        (temp_project / "package.json").write_text(json.dumps(package_json))

        frameworks = detector.detect_frameworks(str(temp_project))
        assert len(frameworks) >= 2
        assert any(f.framework == TestFramework.PYTEST for f in frameworks)
        assert any(f.framework == TestFramework.JEST for f in frameworks)


class TestCaching:
    """Test framework detection caching."""

    def test_caching_works(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test that detection results are cached."""
        (temp_project / "pytest.ini").write_text("[pytest]\n")

        # First call - detects frameworks
        frameworks1 = detector.detect_frameworks(str(temp_project))

        # Delete the file
        (temp_project / "pytest.ini").unlink()

        # Second call should return cached results
        frameworks2 = detector.detect_frameworks(str(temp_project))
        assert frameworks1 == frameworks2

    def test_cache_clear(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test that cache can be cleared."""
        (temp_project / "pytest.ini").write_text("[pytest]\n")
        frameworks1 = detector.detect_frameworks(str(temp_project))
        assert len(frameworks1) > 0

        # Clear cache
        detector.clear_cache(str(temp_project))

        # Delete the file
        (temp_project / "pytest.ini").unlink()

        # Now should detect no frameworks
        frameworks2 = detector.detect_frameworks(str(temp_project))
        assert len(frameworks2) == 0

    def test_no_frameworks_detected(self, temp_project: Path, detector: FrameworkDetector) -> None:
        """Test behavior when no frameworks are detected."""
        frameworks = detector.detect_frameworks(str(temp_project))
        assert len(frameworks) == 0


class TestSingletonWrapper:
    """Test the singleton wrapper functions."""

    def test_detect_frameworks_function(self, temp_project: Path) -> None:
        """Test the module-level detect_frameworks function."""
        (temp_project / "pytest.ini").write_text("[pytest]\n")
        frameworks = detect_frameworks(str(temp_project))
        assert any(f.framework == TestFramework.PYTEST for f in frameworks)
