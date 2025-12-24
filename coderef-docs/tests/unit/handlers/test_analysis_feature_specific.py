#!/usr/bin/env python3
"""
Unit tests for feature-specific analysis saving.
Tests feature folder persistence (no timestamps) instead of timestamped cache.
"""

import asyncio
import sys
from pathlib import Path
import json
import tempfile
import shutil
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import tool_handlers


async def test_feature_specific_save():
    """Test that analysis is saved to feature folder without timestamp."""
    print("\n[TEST 1] Testing feature-specific analysis save...")

    # Create temporary project directory
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Create minimal project structure
        (project_path / 'src').mkdir()
        (project_path / 'README.md').write_text('# Test Project')

        # Run analysis with feature_name
        result = await tool_handlers.handle_analyze_project_for_planning({
            'project_path': str(project_path),
            'feature_name': 'auth-system'
        })

        # Parse result
        result_text = result[0].text
        result_data = json.loads(result_text)

        # Verify metadata exists
        assert '_metadata' in result_data, "Missing _metadata in response"
        assert 'saved_to' in result_data['_metadata'], "Missing saved_to in metadata"
        assert 'feature_name' in result_data['_metadata'], "Missing feature_name in metadata"
        assert 'generated_at' in result_data['_metadata'], "Missing generated_at in metadata"

        # Verify feature_name matches
        assert result_data['_metadata']['feature_name'] == 'auth-system', "feature_name mismatch"

        # Verify file was created in correct location
        saved_path = project_path / result_data['_metadata']['saved_to']
        assert saved_path.exists(), f"Analysis file not created at {saved_path}"

        # Verify path structure (coderef/working/{feature_name}/analysis.json)
        normalized_path = result_data['_metadata']['saved_to'].replace('\\', '/')
        assert 'coderef/working/auth-system/analysis.json' in normalized_path, \
            f"Expected coderef/working/auth-system/analysis.json, got {normalized_path}"

        # Verify filename is analysis.json (NO timestamp)
        assert saved_path.name == 'analysis.json', f"Expected analysis.json, got {saved_path.name}"

        # Verify file contains valid JSON
        with open(saved_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)

        # Verify file data matches result (except metadata)
        assert 'foundation_docs' in file_data, "File missing foundation_docs"
        assert 'technology_stack' in file_data, "File missing technology_stack"

        print(f"  [OK] Analysis file created: {saved_path.relative_to(project_path)}")
        print(f"  [OK] Feature name: {result_data['_metadata']['feature_name']}")
        print(f"  [OK] No timestamp in filename")
        print("[PASS] Test 1 passed!\n")
        return True


async def test_analysis_without_feature_name():
    """Test that analysis returns without saving when feature_name is omitted."""
    print("[TEST 2] Testing analysis without feature_name (no save)...")

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        (project_path / 'src').mkdir()
        (project_path / 'README.md').write_text('# Test')

        # Run analysis WITHOUT feature_name
        result = await tool_handlers.handle_analyze_project_for_planning({
            'project_path': str(project_path)
        })

        result_data = json.loads(result[0].text)

        # Verify analysis data is present
        assert 'foundation_docs' in result_data, "Should have foundation_docs"
        assert 'technology_stack' in result_data, "Should have technology_stack"

        # Verify NO metadata (no save occurred)
        assert '_metadata' not in result_data, "Should not have _metadata when feature_name omitted"

        # Verify no working directory was created
        working_dir = project_path / 'coderef' / 'working'
        if working_dir.exists():
            # If it exists, it should be empty
            assert len(list(working_dir.iterdir())) == 0, "Working directory should be empty"

        print(f"  [OK] Analysis returned without saving")
        print(f"  [OK] No metadata in response")
        print(f"  [OK] No files created")
        print("[PASS] Test 2 passed!\n")
        return True


async def test_metadata_structure():
    """Test that _metadata is correctly structured for feature-specific saves."""
    print("[TEST 3] Testing metadata structure...")

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        (project_path / 'src').mkdir()
        (project_path / 'README.md').write_text('# Test')

        result = await tool_handlers.handle_analyze_project_for_planning({
            'project_path': str(project_path),
            'feature_name': 'test-feature'
        })

        result_data = json.loads(result[0].text)

        # Verify metadata structure
        metadata = result_data['_metadata']
        assert isinstance(metadata, dict), "Metadata should be a dict"
        assert isinstance(metadata['saved_to'], str), "saved_to should be a string"
        assert isinstance(metadata['feature_name'], str), "feature_name should be a string"
        assert isinstance(metadata['generated_at'], str), "generated_at should be a string"

        # Verify saved_to is relative path
        assert not metadata['saved_to'].startswith('C:'), "saved_to should be relative, not absolute"
        normalized_path = metadata['saved_to'].replace('\\', '/')
        assert 'coderef/working/test-feature/analysis.json' in normalized_path, \
            f"saved_to should be coderef/working/test-feature/analysis.json, got {metadata['saved_to']}"

        # Verify generated_at is ISO format
        from datetime import datetime
        datetime.fromisoformat(metadata['generated_at'])  # Should not raise

        # Verify feature_name matches
        assert metadata['feature_name'] == 'test-feature', "feature_name should match input"

        print(f"  [OK] Metadata structure valid")
        print(f"  [OK] saved_to is relative: {metadata['saved_to']}")
        print(f"  [OK] feature_name is correct: {metadata['feature_name']}")
        print(f"  [OK] generated_at is ISO format: {metadata['generated_at']}")
        print("[PASS] Test 3 passed!\n")
        return True


async def test_graceful_degradation():
    """Test that analysis still returns data when file save fails."""
    print("[TEST 4] Testing graceful degradation...")

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        (project_path / 'src').mkdir()
        (project_path / 'README.md').write_text('# Test')

        # Create coderef/working/test-feature as a read-only file (not directory)
        # This will cause mkdir to fail
        working_dir = project_path / 'coderef' / 'working'
        working_dir.mkdir(parents=True)
        fake_file = working_dir / 'test-feature'
        fake_file.write_text('fake')

        # Make it read-only (Windows and Unix compatible)
        os.chmod(fake_file, 0o444)

        try:
            # Run analysis - should succeed despite file save failure
            result = await tool_handlers.handle_analyze_project_for_planning({
                'project_path': str(project_path),
                'feature_name': 'test-feature'
            })

            result_data = json.loads(result[0].text)

            # Verify analysis data is still present
            assert 'foundation_docs' in result_data, "Should still have foundation_docs"
            assert 'technology_stack' in result_data, "Should still have technology_stack"

            # Verify metadata indicates failure
            assert '_metadata' in result_data, "Should have metadata"
            metadata = result_data['_metadata']

            # On failure, saved_to should be None and save_error should be present
            assert metadata['saved_to'] is None, "saved_to should be None on failure"
            assert 'save_error' in metadata, "Should have save_error field"
            assert 'generated_at' in metadata, "Should still have generated_at"
            assert metadata['feature_name'] == 'test-feature', "Should have feature_name"

            print(f"  [OK] Analysis data returned despite save failure")
            print(f"  [OK] Metadata indicates failure: saved_to=None")
            print(f"  [OK] save_error present: {metadata['save_error'][:50]}...")
            print("[PASS] Test 4 passed!\n")
            return True
        finally:
            # Cleanup: restore permissions
            os.chmod(fake_file, 0o644)


async def test_feature_name_validation():
    """Test that feature_name is properly validated."""
    print("[TEST 5] Testing feature_name validation...")

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        (project_path / 'src').mkdir()
        (project_path / 'README.md').write_text('# Test')

        # Test valid feature names
        valid_names = ['auth-system', 'user_profile', 'api-v2', 'feature123']
        for name in valid_names:
            result = await tool_handlers.handle_analyze_project_for_planning({
                'project_path': str(project_path),
                'feature_name': name
            })
            result_data = json.loads(result[0].text)
            assert '_metadata' in result_data, f"Should save for valid name: {name}"
            assert result_data['_metadata']['feature_name'] == name

        print(f"  [OK] All valid feature names accepted: {', '.join(valid_names)}")
        print("[PASS] Test 5 passed!\n")
        return True


async def test_overwrite_existing_analysis():
    """Test that saving to the same feature name overwrites previous analysis."""
    print("[TEST 6] Testing overwrite of existing analysis...")

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        (project_path / 'src').mkdir()
        (project_path / 'README.md').write_text('# Test')

        # Run analysis first time
        result1 = await tool_handlers.handle_analyze_project_for_planning({
            'project_path': str(project_path),
            'feature_name': 'auth-system'
        })
        data1 = json.loads(result1[0].text)
        file1_path = project_path / data1['_metadata']['saved_to']

        # Verify file was created
        assert file1_path.exists(), "First analysis file should exist"

        # Small delay
        import time
        time.sleep(0.1)

        # Run analysis second time (same feature_name)
        result2 = await tool_handlers.handle_analyze_project_for_planning({
            'project_path': str(project_path),
            'feature_name': 'auth-system'
        })
        data2 = json.loads(result2[0].text)
        file2_path = project_path / data2['_metadata']['saved_to']

        # Verify same file path (no timestamp, so it overwrites)
        assert file1_path == file2_path, "Should save to same location"

        # Verify timestamps are different
        assert data1['_metadata']['generated_at'] != data2['_metadata']['generated_at'], \
            "Timestamps should differ"

        # Verify only one analysis.json file exists in the feature directory
        feature_dir = project_path / 'coderef' / 'working' / 'auth-system'
        analysis_files = list(feature_dir.glob('analysis*.json'))
        assert len(analysis_files) == 1, f"Should have exactly 1 analysis file, found {len(analysis_files)}"
        assert analysis_files[0].name == 'analysis.json', "File should be named analysis.json"

        print(f"  [OK] Second analysis overwrites first")
        print(f"  [OK] Same file path: {file1_path.relative_to(project_path)}")
        print(f"  [OK] Only one analysis.json in feature directory")
        print("[PASS] Test 6 passed!\n")
        return True


async def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("FEATURE-SPECIFIC ANALYSIS TESTS")
    print("=" * 60)

    tests = [
        test_feature_specific_save,
        test_analysis_without_feature_name,
        test_metadata_structure,
        test_graceful_degradation,
        test_feature_name_validation,
        test_overwrite_existing_analysis
    ]

    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"\n[FAIL] {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("=" * 60)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)

    return all(results)


if __name__ == '__main__':
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
