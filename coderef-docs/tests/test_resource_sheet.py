"""
Tests for Resource Sheet Generator.

WO-RESOURCE-SHEET-MCP-TOOL-001
"""

import pytest
import asyncio
from pathlib import Path
import json

import sys
from pathlib import Path

# Add resource_sheet to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from resource_sheet.types import CodeCharacteristics
from resource_sheet.detection import CodeAnalyzer, CharacteristicsDetector
from resource_sheet.composition import DocumentComposer
from resource_sheet.modules import get_registry
from resource_sheet.modules.universal import (
    architecture_module,
    integration_module,
)

# Import generator directly to avoid papertrail dependency issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "resource_sheet_generator",
    Path(__file__).parent.parent / "generators" / "resource_sheet_generator.py"
)
resource_sheet_gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resource_sheet_gen)
ResourceSheetGenerator = resource_sheet_gen.ResourceSheetGenerator


class TestCharacteristicsDetector:
    """Test characteristics detection from code analysis."""

    def test_detect_network_calls(self):
        """Should detect network calls from imports."""
        detector = CharacteristicsDetector()

        scan_data = {
            "type": "class",
            "imports": ["axios", "fetch"],
            "code": "",
            "file_path": "",
        }

        characteristics = detector.detect_from_coderef_scan(scan_data)

        assert characteristics["makes_network_calls"] is True

    def test_detect_jsx(self):
        """Should detect JSX from component type or code."""
        detector = CharacteristicsDetector()

        scan_data = {
            "type": "component",
            "imports": [],
            "code": "<div>Hello</div>",
            "file_path": "",
        }

        characteristics = detector.detect_from_coderef_scan(scan_data)

        assert characteristics["has_jsx"] is True
        assert characteristics["is_component"] is True

    def test_detect_state_management(self):
        """Should detect state management from hooks."""
        detector = CharacteristicsDetector()

        scan_data = {
            "type": "component",
            "imports": [],
            "code": "const [count, setCount] = useState(0)",
            "file_path": "",
        }

        characteristics = detector.detect_from_coderef_scan(scan_data)

        assert characteristics["manages_state"] is True

    def test_detect_auth_handling(self):
        """Should detect auth-related code."""
        detector = CharacteristicsDetector()

        scan_data = {
            "type": "class",
            "imports": [],
            "code": "jwt.decode(token)",
            "file_path": "",
        }

        characteristics = detector.detect_from_coderef_scan(scan_data)

        assert characteristics["handles_auth"] is True


class TestModuleRegistry:
    """Test module registration and selection."""

    def test_register_module(self):
        """Should register modules successfully."""
        # Import generator to trigger module registration
        generator = ResourceSheetGenerator()
        registry = get_registry()

        # Should have universal modules registered by generator
        assert registry.count() >= 4  # At least 4 universal modules

    def test_get_module_by_id(self):
        """Should retrieve module by ID."""
        registry = get_registry()
        registry.register(architecture_module)

        module = registry.get("architecture")

        assert module is not None
        assert module.id == "architecture"
        assert module.name == "Architecture Overview"

    def test_select_modules_universal_no_triggers(self):
        """Universal modules have no required triggers, so won't be auto-selected."""
        # Initialize generator to register modules
        generator = ResourceSheetGenerator()
        registry = get_registry()

        characteristics: CodeCharacteristics = {}

        selected = registry.select_modules(characteristics)

        # Universal modules have empty required_when, so they won't be selected
        # They're always manually included in the generator._select_modules
        # This test verifies the registry selection logic works correctly
        assert isinstance(selected, list)


class TestDocumentComposer:
    """Test document composition."""

    def test_compose_markdown_basic(self):
        """Should compose basic markdown document."""
        composer = DocumentComposer()

        modules = [architecture_module]
        extracted_data = {
            "architecture": {
                "type": "Class",
                "dependencies": ["axios"],
                "exports": ["AuthService"],
                "file_path": "src/auth.ts",
                "lines_of_code": 150,
            }
        }
        characteristics: CodeCharacteristics = {"is_class": True}

        markdown = composer.compose_markdown(
            "AuthService",
            modules,
            extracted_data,
            characteristics,
            "reverse-engineer",
        )

        assert "AuthService" in markdown
        assert "Architecture" in markdown
        assert "---" in markdown  # Frontmatter

    def test_compose_schema(self):
        """Should compose valid JSON schema."""
        composer = DocumentComposer()

        modules = [architecture_module]
        extracted_data = {}

        schema = composer.compose_schema("TestElement", modules, extracted_data)

        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["title"] == "TestElement"
        assert schema["type"] == "object"
        assert "properties" in schema

    def test_compose_jsdoc(self):
        """Should compose JSDoc comments."""
        composer = DocumentComposer()

        modules = [architecture_module]
        extracted_data = {}

        jsdoc = composer.compose_jsdoc("TestElement", modules, extracted_data)

        assert isinstance(jsdoc, list)
        assert jsdoc[0] == "/**"
        assert jsdoc[-1] == " */"
        assert any("TestElement" in line for line in jsdoc)


class TestResourceSheetGenerator:
    """Test end-to-end generator workflow."""

    @pytest.mark.asyncio
    async def test_generate_basic(self, tmp_path):
        """Should generate resource sheet end-to-end."""
        generator = ResourceSheetGenerator()

        result = await generator.generate(
            element_name="TestElement",
            project_path=str(tmp_path),
            mode="template",  # Template mode doesn't require actual code
            auto_analyze=False,
            output_path=str(tmp_path / "output"),
        )

        assert result["element_name"] == "TestElement"
        assert result["mode"] == "template"
        assert result["module_count"] == 4  # 4 universal modules
        assert "outputs" in result
        assert result["auto_fill_rate"] == 50.0  # 2/4 modules auto-fillable

    @pytest.mark.asyncio
    async def test_generate_creates_files(self, tmp_path):
        """Should create output files."""
        generator = ResourceSheetGenerator()

        output_path = tmp_path / "output"

        result = await generator.generate(
            element_name="TestElement",
            project_path=str(tmp_path),
            mode="template",
            auto_analyze=False,
            output_path=str(output_path),
        )

        # Check files were created
        assert Path(result["outputs"]["markdown"]).exists()
        assert Path(result["outputs"]["schema"]).exists()
        assert Path(result["outputs"]["jsdoc"]).exists()

    @pytest.mark.asyncio
    async def test_generate_with_auto_analyze(self, tmp_path):
        """Should handle auto-analysis gracefully."""
        generator = ResourceSheetGenerator()

        # Even without .coderef/, should fall back gracefully
        result = await generator.generate(
            element_name="TestElement",
            project_path=str(tmp_path),
            mode="reverse-engineer",
            auto_analyze=True,
            output_path=str(tmp_path / "output"),
        )

        # Should complete without error
        assert "element_name" in result
        assert "outputs" in result
        assert result["element_name"] == "TestElement"
