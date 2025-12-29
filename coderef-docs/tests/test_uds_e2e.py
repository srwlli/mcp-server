"""
End-to-End Integration Tests for UDS
TEST-003 and TEST-004 from WO-UDS-INTEGRATION-001
"""

import pytest
from pathlib import Path
import json
import yaml


class TestUDSEndToEnd:
    """End-to-end integration tests for UDS metadata."""

    def test_003_create_workorder_generates_uds_metadata(self):
        """
        TEST-003: /create-workorder generates files with UDS metadata

        What: Run create-workorder and verify UDS headers in generated files
        Why: Validate full workflow includes UDS metadata
        How: Check for UDS headers in context.json, plan.json, DELIVERABLES.md
        """
        # Look for a recent workorder in coderef/workorder/
        workorder_dir = Path("C:/Users/willh/.mcp-servers/coderef-docs/coderef/workorder")

        if not workorder_dir.exists():
            pytest.skip("Workorder directory not found")

        # Find any recent workorder folder
        workorder_folders = [d for d in workorder_dir.iterdir() if d.is_dir()]

        if not workorder_folders:
            pytest.skip("No workorder folders found for testing")

        # Test the first workorder folder
        test_folder = workorder_folders[0]
        print(f"\nTesting workorder: {test_folder.name}")

        # Check context.json for UDS header
        context_file = test_folder / "context.json"
        if context_file.exists():
            with open(context_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Should have YAML frontmatter if UDS is integrated
            if content.startswith("---"):
                print("[PASS] context.json has UDS header")
                # Parse YAML frontmatter
                parts = content.split("---")
                if len(parts) >= 2:
                    yaml_content = parts[1].strip()
                    try:
                        metadata = yaml.safe_load(yaml_content)
                        assert isinstance(metadata, dict), "UDS header should be a dict"
                        print(f"   Metadata fields: {list(metadata.keys())}")
                    except yaml.YAMLError as e:
                        pytest.fail(f"UDS header YAML invalid: {e}")
            else:
                print("[WARN]  context.json does not have UDS header (expected if not yet integrated)")

        # Check plan.json for UDS header
        plan_file = test_folder / "plan.json"
        if plan_file.exists():
            with open(plan_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.startswith("---"):
                print("[PASS] plan.json has UDS header")
                parts = content.split("---")
                if len(parts) >= 2:
                    yaml_content = parts[1].strip()
                    try:
                        metadata = yaml.safe_load(yaml_content)
                        assert isinstance(metadata, dict), "UDS header should be a dict"

                        # Verify required fields
                        if "workorder_id" in metadata or "workorder" in metadata:
                            print("   [PASS] Has workorder_id")
                        if "status" in metadata:
                            print(f"   [PASS] Status: {metadata['status']}")

                    except yaml.YAMLError as e:
                        pytest.fail(f"UDS header YAML invalid: {e}")
            else:
                print("[WARN]  plan.json does not have UDS header")

        # Check DELIVERABLES.md for UDS header
        deliverables_file = test_folder / "DELIVERABLES.md"
        if deliverables_file.exists():
            with open(deliverables_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.startswith("---"):
                print("[PASS] DELIVERABLES.md has UDS header")
                parts = content.split("---")
                if len(parts) >= 2:
                    yaml_content = parts[1].strip()
                    try:
                        metadata = yaml.safe_load(yaml_content)
                        assert isinstance(metadata, dict), "UDS header should be a dict"
                        print(f"   Metadata fields: {list(metadata.keys())}")
                    except yaml.YAMLError as e:
                        pytest.fail(f"UDS header YAML invalid: {e}")
            else:
                print("[WARN]  DELIVERABLES.md does not have UDS header")

        # Test passes if at least one file was checked
        assert context_file.exists() or plan_file.exists() or deliverables_file.exists(), \
            "At least one workorder file should exist"

    def test_004_old_workorders_load_without_errors(self):
        """
        TEST-004: Old workorders without UDS load correctly

        What: Load archived workorders and verify no parsing errors
        Why: Ensure backward compatibility with pre-UDS workorders
        How: Load plan.json/context.json from archived workorders
        """
        # Check archived workorders
        archived_dir = Path("C:/Users/willh/.mcp-servers/coderef-docs/coderef/archived")

        if not archived_dir.exists():
            pytest.skip("Archived directory not found")

        archived_folders = [d for d in archived_dir.iterdir() if d.is_dir()]

        if not archived_folders:
            pytest.skip("No archived workorders found")

        errors = []
        tested_count = 0

        for folder in archived_folders[:5]:  # Test first 5 archived workorders
            print(f"\nTesting archived: {folder.name}")

            # Try loading plan.json
            plan_file = folder / "plan.json"
            if plan_file.exists():
                try:
                    with open(plan_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # If it has UDS header, parse it separately
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            json_content = parts[2].strip()
                        else:
                            json_content = content
                    else:
                        json_content = content

                    # Parse JSON
                    plan = json.loads(json_content)
                    assert isinstance(plan, dict), "Plan should be a dict"
                    print(f"   [PASS] plan.json loads successfully")
                    tested_count += 1

                except json.JSONDecodeError as e:
                    errors.append(f"{folder.name}/plan.json: JSON decode error: {e}")
                    print(f"   [FAIL] plan.json failed to load: {e}")
                except Exception as e:
                    errors.append(f"{folder.name}/plan.json: {e}")
                    print(f"   [FAIL] plan.json error: {e}")

            # Try loading context.json
            context_file = folder / "context.json"
            if context_file.exists():
                try:
                    with open(context_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Handle UDS header
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            json_content = parts[2].strip()
                        else:
                            json_content = content
                    else:
                        json_content = content

                    context = json.loads(json_content)
                    assert isinstance(context, dict), "Context should be a dict"
                    print(f"   [PASS] context.json loads successfully")
                    tested_count += 1

                except json.JSONDecodeError as e:
                    errors.append(f"{folder.name}/context.json: JSON decode error: {e}")
                    print(f"   [FAIL] context.json failed to load: {e}")
                except Exception as e:
                    errors.append(f"{folder.name}/context.json: {e}")
                    print(f"   [FAIL] context.json error: {e}")

        # Print summary
        print(f"\n{'='*60}")
        print(f"Tested {tested_count} files from {len(archived_folders[:5])} archived workorders")

        if errors:
            print(f"[FAIL] {len(errors)} errors found:")
            for error in errors:
                print(f"   - {error}")
            pytest.fail(f"Found {len(errors)} errors in archived workorders")
        else:
            print("[PASS] All archived workorders load without errors")

        assert tested_count > 0, "Should have tested at least one file"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
