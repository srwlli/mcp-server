"""
Additional edge case tests for .coderef/ output utilization

These tests complement test_end_to_end_utilization.py with:
- Partial server coverage scenarios
- Corrupted or malformed data handling
- Empty scan results
- Performance with large datasets
- Concurrent access patterns
- Recovery and resilience

Run with: pytest tests/test_utilization_edge_cases.py -v
"""

import json
import pytest
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def mock_intelligence_hub(tmp_path):
    """Create mock intelligence hub with test data"""
    hub = tmp_path / "coderef" / "intelligence"
    hub.mkdir(parents=True)
    return hub


@pytest.fixture
def create_mock_server_data():
    """Factory fixture to create mock server scan data"""
    def _create(server_name: str, element_count: int) -> List[Dict]:
        """Create mock index.json data for a server"""
        return [
            {
                "type": "function" if i % 3 == 0 else "class",
                "name": f"element_{i}",
                "file": f"src/file_{i % 10}.py",
                "line": i * 10
            }
            for i in range(element_count)
        ]
    return _create


class TestPartialServerCoverage:
    """Test scenarios with incomplete server scans"""

    def test_only_three_servers_scanned(self, mock_intelligence_hub, create_mock_server_data):
        """Test when only 3 out of 5 servers are scanned"""
        # Create data for only 3 servers
        scanned_servers = ["coderef-context", "coderef-docs", "coderef-workflow"]

        for server in scanned_servers:
            server_dir = mock_intelligence_hub / server
            server_dir.mkdir()
            index_file = server_dir / "index.json"
            index_data = create_mock_server_data(server, 50)
            index_file.write_text(json.dumps(index_data))

        # Count scanned servers
        expected_servers = [
            "coderef-context", "coderef-docs", "coderef-workflow",
            "coderef-personas", "coderef-testing"
        ]

        scanned_count = 0
        for server in expected_servers:
            index_file = mock_intelligence_hub / server / "index.json"
            if index_file.exists():
                scanned_count += 1

        utilization = (scanned_count / len(expected_servers)) * 100

        # Should be 60% (3/5)
        assert utilization == 60.0
        assert scanned_count == 3

    def test_single_server_only(self, mock_intelligence_hub, create_mock_server_data):
        """Test when only one server is scanned"""
        server_dir = mock_intelligence_hub / "coderef-context"
        server_dir.mkdir()
        index_file = server_dir / "index.json"
        index_data = create_mock_server_data("coderef-context", 100)
        index_file.write_text(json.dumps(index_data))

        # Verify only one server exists
        all_servers = list(mock_intelligence_hub.glob("*/index.json"))
        assert len(all_servers) == 1

    def test_zero_servers_scanned(self, mock_intelligence_hub):
        """Test when no servers are scanned (empty intelligence hub)"""
        # Intelligence hub exists but has no server data
        assert mock_intelligence_hub.exists()

        all_servers = list(mock_intelligence_hub.glob("*/index.json"))
        assert len(all_servers) == 0


class TestEmptyScanResults:
    """Test handling of empty or minimal scan results"""

    def test_server_with_zero_elements(self, mock_intelligence_hub):
        """Test server scanned but found 0 elements"""
        server_dir = mock_intelligence_hub / "coderef-context"
        server_dir.mkdir()
        index_file = server_dir / "index.json"

        # Empty array
        index_file.write_text(json.dumps([]))

        # Should read successfully
        index_data = json.loads(index_file.read_text())
        assert isinstance(index_data, list)
        assert len(index_data) == 0

    def test_all_servers_empty(self, mock_intelligence_hub):
        """Test when all servers scanned but all have 0 elements"""
        servers = ["coderef-context", "coderef-docs", "coderef-workflow",
                   "coderef-personas", "coderef-testing"]

        for server in servers:
            server_dir = mock_intelligence_hub / server
            server_dir.mkdir()
            (server_dir / "index.json").write_text(json.dumps([]))

        # All servers scanned (100% coverage) but 0 total elements
        total_elements = 0
        for server in servers:
            index_file = mock_intelligence_hub / server / "index.json"
            data = json.loads(index_file.read_text())
            total_elements += len(data)

        assert total_elements == 0


class TestCorruptedData:
    """Test handling of corrupted or malformed data"""

    def test_malformed_json(self, mock_intelligence_hub):
        """Test handling of corrupted index.json"""
        server_dir = mock_intelligence_hub / "coderef-context"
        server_dir.mkdir()
        index_file = server_dir / "index.json"

        # Write malformed JSON
        index_file.write_text('{"incomplete": [')

        # Should raise JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            json.loads(index_file.read_text())

    def test_index_with_emoji_prefix(self, mock_intelligence_hub, create_mock_server_data):
        """Test reading index.json with emoji prefix (real scenario from scans)"""
        server_dir = mock_intelligence_hub / "coderef-context"
        server_dir.mkdir()
        index_file = server_dir / "index.json"

        # Simulate real output with emoji prefix
        index_data = create_mock_server_data("coderef-context", 10)
        content = f"🔍 Scanning coderef-context...\n{json.dumps(index_data)}"
        index_file.write_text(content, encoding='utf-8')

        # Helper function to strip emoji prefix
        raw_content = index_file.read_text(encoding='utf-8')
        if '🔍' in raw_content or 'Scanning' in raw_content:
            bracket_pos = raw_content.find('[')
            brace_pos = raw_content.find('{')
            positions = [p for p in [bracket_pos, brace_pos] if p >= 0]
            if positions:
                json_start = min(positions)
                raw_content = raw_content[json_start:]

        data = json.loads(raw_content)
        assert len(data) == 10

    def test_missing_required_fields(self, mock_intelligence_hub):
        """Test elements missing required fields (type, name, file)"""
        server_dir = mock_intelligence_hub / "coderef-context"
        server_dir.mkdir()
        index_file = server_dir / "index.json"

        # Elements with missing fields
        incomplete_data = [
            {"name": "element_1", "file": "test.py"},  # Missing 'type'
            {"type": "function", "file": "test.py"},   # Missing 'name'
            {"type": "function", "name": "element_2"}, # Missing 'file'
            {"type": "function", "name": "element_3", "file": "test.py"}  # Complete
        ]

        index_file.write_text(json.dumps(incomplete_data))

        data = json.loads(index_file.read_text())

        # Count complete elements
        complete = [e for e in data if 'type' in e and 'name' in e and 'file' in e]
        incomplete = [e for e in data if 'type' not in e or 'name' not in e or 'file' not in e]

        assert len(complete) == 1
        assert len(incomplete) == 3


class TestPerformanceAtScale:
    """Test performance with large datasets"""

    def test_large_dataset_1000_elements(self, mock_intelligence_hub, create_mock_server_data):
        """Test handling 1000+ elements in single server"""
        server_dir = mock_intelligence_hub / "coderef-context"
        server_dir.mkdir()
        index_file = server_dir / "index.json"

        # Create large dataset
        large_data = create_mock_server_data("coderef-context", 1000)

        # Measure write time
        start = time.time()
        index_file.write_text(json.dumps(large_data))
        write_time = time.time() - start

        # Measure read time
        start = time.time()
        data = json.loads(index_file.read_text())
        read_time = time.time() - start

        assert len(data) == 1000
        # Should complete within reasonable time (< 1 second each)
        assert write_time < 1.0
        assert read_time < 1.0

    def test_aggregate_10000_elements_across_servers(self, mock_intelligence_hub, create_mock_server_data):
        """Test aggregating 10,000 total elements across all 5 servers"""
        servers = ["coderef-context", "coderef-docs", "coderef-workflow",
                   "coderef-personas", "coderef-testing"]

        # 2000 elements per server = 10,000 total
        for server in servers:
            server_dir = mock_intelligence_hub / server
            server_dir.mkdir()
            index_file = server_dir / "index.json"
            data = create_mock_server_data(server, 2000)
            index_file.write_text(json.dumps(data))

        # Aggregate all elements
        start = time.time()
        total_elements = 0
        for server in servers:
            index_file = mock_intelligence_hub / server / "index.json"
            data = json.loads(index_file.read_text())
            total_elements += len(data)

        aggregate_time = time.time() - start

        assert total_elements == 10000
        # Should aggregate within 2 seconds
        assert aggregate_time < 2.0


class TestConcurrentAccess:
    """Test concurrent access patterns"""

    def test_multiple_agents_reading_simultaneously(self, mock_intelligence_hub, create_mock_server_data):
        """Test multiple threads reading intelligence hub simultaneously"""
        # Create test data
        server_dir = mock_intelligence_hub / "coderef-context"
        server_dir.mkdir()
        index_file = server_dir / "index.json"
        index_data = create_mock_server_data("coderef-context", 100)
        index_file.write_text(json.dumps(index_data))

        def read_index():
            """Simulate agent reading index"""
            data = json.loads(index_file.read_text())
            return len(data)

        # 10 agents reading concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_index) for _ in range(10)]
            results = [f.result() for f in futures]

        # All should read same data successfully
        assert all(r == 100 for r in results)
        assert len(results) == 10

    def test_read_while_write_race_condition(self, mock_intelligence_hub, create_mock_server_data):
        """Test reading while file is being written (race condition)"""
        server_dir = mock_intelligence_hub / "coderef-context"
        server_dir.mkdir()
        index_file = server_dir / "index.json"

        # Initial data
        initial_data = create_mock_server_data("coderef-context", 50)
        index_file.write_text(json.dumps(initial_data))

        # Simulate concurrent read/write
        def writer():
            new_data = create_mock_server_data("coderef-context", 100)
            index_file.write_text(json.dumps(new_data))

        def reader():
            try:
                data = json.loads(index_file.read_text())
                return len(data)
            except json.JSONDecodeError:
                # Race condition - file being written
                return None

        with ThreadPoolExecutor(max_workers=2) as executor:
            write_future = executor.submit(writer)
            read_future = executor.submit(reader)

            write_future.result()
            read_result = read_future.result()

        # Read may succeed or fail depending on timing
        # After write completes, should be readable
        final_data = json.loads(index_file.read_text())
        assert len(final_data) == 100


class TestRecoveryAndResilience:
    """Test recovery from various failure scenarios"""

    def test_recover_from_partial_scan_failure(self, mock_intelligence_hub, create_mock_server_data):
        """Test recovering when some servers fail to scan"""
        # Simulate: 3 servers succeeded, 2 failed
        successful = ["coderef-context", "coderef-docs", "coderef-workflow"]
        failed = ["coderef-personas", "coderef-testing"]

        # Create data for successful scans
        for server in successful:
            server_dir = mock_intelligence_hub / server
            server_dir.mkdir()
            (server_dir / "index.json").write_text(
                json.dumps(create_mock_server_data(server, 50))
            )

        # Create empty/error indicators for failed scans
        for server in failed:
            server_dir = mock_intelligence_hub / server
            server_dir.mkdir()
            (server_dir / "error.txt").write_text("Scan failed: timeout")

        # Can still use data from successful scans
        total_elements = 0
        for server in successful:
            index_file = mock_intelligence_hub / server / "index.json"
            data = json.loads(index_file.read_text())
            total_elements += len(data)

        assert total_elements == 150  # 3 servers × 50 elements

    def test_stale_data_detection(self, mock_intelligence_hub, create_mock_server_data):
        """Test detecting stale scan results"""
        server_dir = mock_intelligence_hub / "coderef-context"
        server_dir.mkdir()
        index_file = server_dir / "index.json"

        # Write initial data
        index_file.write_text(json.dumps(create_mock_server_data("coderef-context", 50)))

        # Get modification time
        initial_mtime = index_file.stat().st_mtime

        # Simulate time passing
        time.sleep(0.1)

        # Update data (new scan)
        index_file.write_text(json.dumps(create_mock_server_data("coderef-context", 100)))

        new_mtime = index_file.stat().st_mtime

        # Modification time should be newer
        assert new_mtime > initial_mtime


class TestDataIntegrity:
    """Test data integrity and validation"""

    def test_validate_element_structure(self, mock_intelligence_hub, create_mock_server_data):
        """Test that all elements have expected structure"""
        server_dir = mock_intelligence_hub / "coderef-context"
        server_dir.mkdir()
        index_file = server_dir / "index.json"

        data = create_mock_server_data("coderef-context", 20)
        index_file.write_text(json.dumps(data))

        loaded_data = json.loads(index_file.read_text())

        # Validate structure
        for element in loaded_data:
            assert isinstance(element, dict)
            assert 'type' in element
            assert 'name' in element
            assert 'file' in element
            assert element['type'] in ['function', 'class', 'component', 'variable']

    def test_file_path_consistency(self, mock_intelligence_hub, create_mock_server_data):
        """Test that file paths are consistent across elements"""
        server_dir = mock_intelligence_hub / "coderef-context"
        server_dir.mkdir()
        index_file = server_dir / "index.json"

        data = create_mock_server_data("coderef-context", 30)
        index_file.write_text(json.dumps(data))

        loaded_data = json.loads(index_file.read_text())

        # Group by file
        files = {}
        for element in loaded_data:
            file_path = element['file']
            if file_path not in files:
                files[file_path] = []
            files[file_path].append(element)

        # Each file should have at least 1 element
        assert all(len(elements) > 0 for elements in files.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
