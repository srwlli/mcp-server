"""
Comprehensive tests for cache_manager.py module.

Tests cover:
- CodeChangeHandler (file system events, debouncing, pattern filtering)
- CacheManager (registration, watching, TTL, invalidation)
- Module-level functions (singleton, initialization, cleanup)
- Edge cases and error handling
"""

import time
import threading
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import pytest

from cache_manager import (
    CodeChangeHandler,
    CacheManager,
    get_cache_manager,
    initialize_cache_watching,
    cleanup
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_callback():
    """Mock callback function for change events."""
    return Mock()


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory with test files."""
    project = tmp_path / "test_project"
    project.mkdir()

    # Create test files
    (project / "test.ts").write_text("export const foo = 'bar';")
    (project / "test.js").write_text("module.exports = {};")
    (project / "test.py").write_text("def hello(): pass")
    (project / "README.md").write_text("# Test")

    return project


@pytest.fixture
def cache_manager():
    """Create fresh CacheManager instance."""
    manager = CacheManager()
    yield manager
    # Cleanup
    if manager.is_running:
        manager.stop()


@pytest.fixture
def mock_observer():
    """Mock watchdog Observer."""
    with patch('cache_manager.Observer') as mock:
        observer_instance = MagicMock()
        mock.return_value = observer_instance
        yield mock, observer_instance


# ============================================================================
# CodeChangeHandler Tests
# ============================================================================

class TestCodeChangeHandler:
    """Tests for CodeChangeHandler class."""

    def test_init(self, mock_callback):
        """Test handler initialization."""
        patterns = {'.ts', '.js'}
        handler = CodeChangeHandler(mock_callback, patterns)

        assert handler.on_change_callback == mock_callback
        assert handler.file_patterns == patterns
        assert handler.debounce_time == 2.0
        assert handler.last_change_time == 0
        assert handler.debounce_timer is None

    def test_on_modified_relevant_file(self, mock_callback):
        """Test modification event for relevant file type."""
        handler = CodeChangeHandler(mock_callback, {'.ts', '.js'})

        # Create mock event
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/file.ts"

        # Trigger event
        handler.on_modified(event)

        # Should schedule invalidation (callback called after debounce)
        assert handler.debounce_timer is not None

        # Wait for debounce
        time.sleep(2.1)
        mock_callback.assert_called_once_with("/path/to/file.ts")

    def test_on_modified_ignores_directory(self, mock_callback):
        """Test that directory events are ignored."""
        handler = CodeChangeHandler(mock_callback, {'.ts'})

        event = Mock()
        event.is_directory = True
        event.src_path = "/path/to/directory"

        handler.on_modified(event)

        # Should not schedule anything
        assert handler.debounce_timer is None
        mock_callback.assert_not_called()

    def test_on_modified_ignores_irrelevant_file(self, mock_callback):
        """Test that non-matching file patterns are ignored."""
        handler = CodeChangeHandler(mock_callback, {'.ts', '.js'})

        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/file.txt"  # Not in patterns

        handler.on_modified(event)

        assert handler.debounce_timer is None
        mock_callback.assert_not_called()

    def test_on_created_calls_on_modified(self, mock_callback):
        """Test that on_created delegates to on_modified."""
        handler = CodeChangeHandler(mock_callback, {'.ts'})

        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/new.ts"

        handler.on_created(event)

        # Should schedule invalidation
        assert handler.debounce_timer is not None

    def test_on_deleted_calls_on_modified(self, mock_callback):
        """Test that on_deleted delegates to on_modified."""
        handler = CodeChangeHandler(mock_callback, {'.ts'})

        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/deleted.ts"

        handler.on_deleted(event)

        # Should schedule invalidation
        assert handler.debounce_timer is not None

    def test_debouncing_cancels_previous_timer(self, mock_callback):
        """Test that rapid changes are debounced."""
        handler = CodeChangeHandler(mock_callback, {'.ts'})

        event1 = Mock(is_directory=False, src_path="/file1.ts")
        event2 = Mock(is_directory=False, src_path="/file2.ts")
        event3 = Mock(is_directory=False, src_path="/file3.ts")

        # Trigger 3 rapid changes
        handler.on_modified(event1)
        time.sleep(0.5)
        handler.on_modified(event2)
        time.sleep(0.5)
        handler.on_modified(event3)

        # Wait for debounce
        time.sleep(2.5)

        # Only last change should trigger callback
        assert mock_callback.call_count == 1
        mock_callback.assert_called_with("/file3.ts")

    def test_case_insensitive_extension_matching(self, mock_callback):
        """Test that file extensions are matched case-insensitively."""
        handler = CodeChangeHandler(mock_callback, {'.ts'})

        # Test uppercase extension
        event = Mock(is_directory=False, src_path="/path/to/file.TS")
        handler.on_modified(event)

        # Wait for debounce
        time.sleep(2.1)

        # Should match (extensions are lowercased)
        mock_callback.assert_called_once()


# ============================================================================
# CacheManager Tests
# ============================================================================

class TestCacheManager:
    """Tests for CacheManager class."""

    def test_init(self):
        """Test CacheManager initialization."""
        manager = CacheManager()

        assert manager.observers == {}
        assert manager.invalidators == {}
        assert manager.last_invalidation == {}
        assert manager.ttl == 300.0
        assert manager.is_running is False

    def test_register_invalidator(self, cache_manager):
        """Test registering cache invalidator."""
        mock_clear = Mock()

        cache_manager.register_invalidator("test_cache", mock_clear)

        assert "test_cache" in cache_manager.invalidators
        assert cache_manager.invalidators["test_cache"] == mock_clear
        assert "test_cache" in cache_manager.last_invalidation
        assert isinstance(cache_manager.last_invalidation["test_cache"], float)

    def test_register_multiple_invalidators(self, cache_manager):
        """Test registering multiple invalidators."""
        mock_clear1 = Mock()
        mock_clear2 = Mock()
        mock_clear3 = Mock()

        cache_manager.register_invalidator("apis", mock_clear1)
        cache_manager.register_invalidator("schemas", mock_clear2)
        cache_manager.register_invalidator("components", mock_clear3)

        assert len(cache_manager.invalidators) == 3
        assert all(name in cache_manager.invalidators for name in ["apis", "schemas", "components"])

    def test_watch_directory_default_patterns(self, cache_manager, temp_project_dir, mock_observer):
        """Test watching directory with default file patterns."""
        mock_obs_class, mock_obs_instance = mock_observer

        cache_manager.watch_directory(str(temp_project_dir))

        # Should create observer
        assert str(temp_project_dir) in cache_manager.observers
        mock_obs_class.assert_called_once()
        mock_obs_instance.schedule.assert_called_once()

    def test_watch_directory_custom_patterns(self, cache_manager, temp_project_dir, mock_observer):
        """Test watching directory with custom file patterns."""
        mock_obs_class, mock_obs_instance = mock_observer
        custom_patterns = {'.ts', '.tsx'}

        cache_manager.watch_directory(str(temp_project_dir), file_patterns=custom_patterns)

        # Verify handler was created with custom patterns
        call_args = mock_obs_instance.schedule.call_args
        handler = call_args[0][0]
        assert handler.file_patterns == custom_patterns

    def test_watch_multiple_directories(self, cache_manager, tmp_path, mock_observer):
        """Test watching multiple directories."""
        dir1 = tmp_path / "project1"
        dir2 = tmp_path / "project2"
        dir1.mkdir()
        dir2.mkdir()

        cache_manager.watch_directory(str(dir1))
        cache_manager.watch_directory(str(dir2))

        assert len(cache_manager.observers) == 2
        assert str(dir1) in cache_manager.observers
        assert str(dir2) in cache_manager.observers

    def test_start_observers(self, cache_manager, temp_project_dir, mock_observer):
        """Test starting all observers."""
        mock_obs_class, mock_obs_instance = mock_observer

        cache_manager.watch_directory(str(temp_project_dir))
        cache_manager.start()

        assert cache_manager.is_running is True
        mock_obs_instance.start.assert_called_once()

    def test_start_when_already_running(self, cache_manager, temp_project_dir, mock_observer):
        """Test that starting when already running logs warning."""
        mock_obs_class, mock_obs_instance = mock_observer

        cache_manager.watch_directory(str(temp_project_dir))
        cache_manager.start()

        # Start again
        with patch('cache_manager.logger') as mock_logger:
            cache_manager.start()
            mock_logger.warning.assert_called_once()

    def test_stop_observers(self, cache_manager, temp_project_dir, mock_observer):
        """Test stopping all observers."""
        mock_obs_class, mock_obs_instance = mock_observer

        cache_manager.watch_directory(str(temp_project_dir))
        cache_manager.start()
        cache_manager.stop()

        assert cache_manager.is_running is False
        mock_obs_instance.stop.assert_called_once()
        mock_obs_instance.join.assert_called_once_with(timeout=5)

    def test_stop_when_not_running(self, cache_manager):
        """Test that stopping when not running is safe."""
        cache_manager.stop()  # Should not raise

    def test_on_code_change_invalidates_all_caches(self, cache_manager):
        """Test that code change invalidates all registered caches."""
        mock_clear1 = Mock()
        mock_clear2 = Mock()
        mock_clear3 = Mock()

        cache_manager.register_invalidator("apis", mock_clear1)
        cache_manager.register_invalidator("schemas", mock_clear2)
        cache_manager.register_invalidator("components", mock_clear3)

        # Trigger code change
        cache_manager._on_code_change("/path/to/file.ts")

        # All caches should be cleared
        mock_clear1.assert_called_once()
        mock_clear2.assert_called_once()
        mock_clear3.assert_called_once()

    def test_check_ttl_expiration_not_expired(self, cache_manager):
        """Test TTL check when cache is not expired."""
        mock_clear = Mock()
        cache_manager.register_invalidator("test", mock_clear)

        # Check immediately (not expired)
        cache_manager.check_ttl_expiration()

        mock_clear.assert_not_called()

    def test_check_ttl_expiration_expired(self, cache_manager):
        """Test TTL check when cache is expired."""
        mock_clear = Mock()
        cache_manager.ttl = 1.0  # 1 second TTL

        cache_manager.register_invalidator("test", mock_clear)

        # Wait for expiration
        time.sleep(1.5)

        cache_manager.check_ttl_expiration()

        # Should have cleared cache
        mock_clear.assert_called_once()

    def test_check_ttl_expiration_multiple_caches(self, cache_manager):
        """Test TTL expiration with multiple caches."""
        mock_clear1 = Mock()
        mock_clear2 = Mock()

        cache_manager.ttl = 1.0
        cache_manager.register_invalidator("cache1", mock_clear1)

        # Wait a bit before registering second cache
        time.sleep(0.5)
        cache_manager.register_invalidator("cache2", mock_clear2)

        # Wait for first cache to expire
        time.sleep(0.7)

        cache_manager.check_ttl_expiration()

        # Only cache1 should be cleared (cache2 is too new)
        assert mock_clear1.call_count == 1
        mock_clear2.assert_not_called()

    def test_manual_invalidate_specific_cache(self, cache_manager):
        """Test manual invalidation of specific cache."""
        mock_clear1 = Mock()
        mock_clear2 = Mock()

        cache_manager.register_invalidator("cache1", mock_clear1)
        cache_manager.register_invalidator("cache2", mock_clear2)

        cache_manager.manual_invalidate("cache1")

        # Only cache1 should be cleared
        mock_clear1.assert_called_once()
        mock_clear2.assert_not_called()

    def test_manual_invalidate_all_caches(self, cache_manager):
        """Test manual invalidation of all caches."""
        mock_clear1 = Mock()
        mock_clear2 = Mock()
        mock_clear3 = Mock()

        cache_manager.register_invalidator("cache1", mock_clear1)
        cache_manager.register_invalidator("cache2", mock_clear2)
        cache_manager.register_invalidator("cache3", mock_clear3)

        cache_manager.manual_invalidate()  # No name = all

        # All caches should be cleared
        mock_clear1.assert_called_once()
        mock_clear2.assert_called_once()
        mock_clear3.assert_called_once()

    def test_manual_invalidate_unknown_cache(self, cache_manager):
        """Test manual invalidation with unknown cache name."""
        with patch('cache_manager.logger') as mock_logger:
            cache_manager.manual_invalidate("nonexistent")
            mock_logger.warning.assert_called_once()


# ============================================================================
# Module-Level Function Tests
# ============================================================================

class TestModuleLevelFunctions:
    """Tests for module-level functions."""

    def test_get_cache_manager_singleton(self):
        """Test that get_cache_manager returns singleton instance."""
        # Reset global instance
        import cache_manager
        cache_manager._cache_manager = None

        manager1 = get_cache_manager()
        manager2 = get_cache_manager()

        assert manager1 is manager2  # Same instance

    def test_get_cache_manager_creates_instance(self):
        """Test that get_cache_manager creates instance if needed."""
        import cache_manager
        cache_manager._cache_manager = None

        manager = get_cache_manager()

        assert isinstance(manager, CacheManager)

    @patch('cache_manager.get_cache_manager')
    @patch('cache_manager.extract_apis')
    @patch('cache_manager.extract_schemas')
    @patch('cache_manager.extract_components')
    def test_initialize_cache_watching_success(
        self, mock_components, mock_schemas, mock_apis, mock_get_manager, temp_project_dir
    ):
        """Test successful cache watching initialization."""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        # Mock cache_clear methods
        mock_apis.cache_clear = Mock()
        mock_schemas.cache_clear = Mock()
        mock_components.cache_clear = Mock()

        initialize_cache_watching(str(temp_project_dir))

        # Should register all extractors
        assert mock_manager.register_invalidator.call_count == 3

        # Should watch directory
        mock_manager.watch_directory.assert_called_once_with(str(temp_project_dir))

        # Should start
        mock_manager.start.assert_called_once()

    @patch('cache_manager.get_cache_manager')
    def test_initialize_cache_watching_import_error(self, mock_get_manager, temp_project_dir):
        """Test initialization handles import errors gracefully."""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        # Mock import to fail
        with patch('cache_manager.extract_apis', side_effect=ImportError("Not found")):
            with patch('cache_manager.logger') as mock_logger:
                initialize_cache_watching(str(temp_project_dir))

                # Should log warning but continue
                mock_logger.warning.assert_called()
                mock_manager.watch_directory.assert_called_once()
                mock_manager.start.assert_called_once()

    def test_cleanup_stops_manager(self):
        """Test cleanup stops the cache manager."""
        import cache_manager

        # Create mock manager
        mock_manager = Mock()
        cache_manager._cache_manager = mock_manager

        cleanup()

        mock_manager.stop.assert_called_once()

    def test_cleanup_with_no_manager(self):
        """Test cleanup when no manager exists."""
        import cache_manager
        cache_manager._cache_manager = None

        cleanup()  # Should not raise


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for cache manager."""

    @pytest.mark.slow
    def test_full_workflow(self, temp_project_dir, mock_observer):
        """Test complete workflow: register, watch, invalidate."""
        mock_obs_class, mock_obs_instance = mock_observer

        # Create manager
        manager = CacheManager()

        # Register invalidators
        mock_clear1 = Mock()
        mock_clear2 = Mock()
        manager.register_invalidator("apis", mock_clear1)
        manager.register_invalidator("schemas", mock_clear2)

        # Watch directory
        manager.watch_directory(str(temp_project_dir), file_patterns={'.ts'})

        # Start watching
        manager.start()
        assert manager.is_running

        # Simulate code change
        manager._on_code_change("/path/to/file.ts")

        # Both caches should be cleared
        mock_clear1.assert_called_once()
        mock_clear2.assert_called_once()

        # Stop
        manager.stop()
        assert not manager.is_running

    @pytest.mark.slow
    def test_ttl_and_manual_invalidation_combined(self, cache_manager):
        """Test TTL and manual invalidation work together."""
        mock_clear = Mock()

        cache_manager.ttl = 1.0
        cache_manager.register_invalidator("test", mock_clear)

        # Manual invalidate
        cache_manager.manual_invalidate("test")
        assert mock_clear.call_count == 1

        # Wait for TTL
        time.sleep(1.5)
        cache_manager.check_ttl_expiration()
        assert mock_clear.call_count == 2

    def test_concurrent_invalidations(self, cache_manager):
        """Test concurrent invalidations are handled safely."""
        mock_clear = Mock()
        cache_manager.register_invalidator("test", mock_clear)

        # Trigger multiple invalidations concurrently
        threads = []
        for i in range(10):
            t = threading.Thread(target=cache_manager.manual_invalidate, args=("test",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have been called 10 times (one per thread)
        assert mock_clear.call_count == 10


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_watch_nonexistent_directory(self, cache_manager, mock_observer):
        """Test watching non-existent directory."""
        # Should not raise - observer will handle the error
        cache_manager.watch_directory("/nonexistent/path")

    def test_empty_file_patterns(self, cache_manager, temp_project_dir, mock_observer):
        """Test with empty file patterns set."""
        cache_manager.watch_directory(str(temp_project_dir), file_patterns=set())

        # Handler should have empty patterns
        mock_obs_class, mock_obs_instance = mock_observer
        call_args = mock_obs_instance.schedule.call_args
        handler = call_args[0][0]
        assert handler.file_patterns == set()

    def test_invalidator_raises_exception(self, cache_manager):
        """Test that exception in invalidator is handled."""
        def failing_clear():
            raise RuntimeError("Cache clear failed")

        cache_manager.register_invalidator("test", failing_clear)

        # Should raise (caller should handle)
        with pytest.raises(RuntimeError):
            cache_manager.manual_invalidate("test")

    def test_very_short_ttl(self, cache_manager):
        """Test with very short TTL (edge case timing)."""
        mock_clear = Mock()
        cache_manager.ttl = 0.1  # 100ms

        cache_manager.register_invalidator("test", mock_clear)
        time.sleep(0.15)

        cache_manager.check_ttl_expiration()
        mock_clear.assert_called_once()

    def test_zero_ttl(self, cache_manager):
        """Test with zero TTL (always expires)."""
        mock_clear = Mock()
        cache_manager.ttl = 0.0

        cache_manager.register_invalidator("test", mock_clear)

        cache_manager.check_ttl_expiration()
        mock_clear.assert_called_once()

    def test_negative_ttl(self, cache_manager):
        """Test with negative TTL (always expired)."""
        mock_clear = Mock()
        cache_manager.ttl = -1.0

        cache_manager.register_invalidator("test", mock_clear)

        cache_manager.check_ttl_expiration()
        mock_clear.assert_called_once()

    def test_register_same_name_twice(self, cache_manager):
        """Test registering invalidator with same name twice."""
        mock_clear1 = Mock()
        mock_clear2 = Mock()

        cache_manager.register_invalidator("test", mock_clear1)
        cache_manager.register_invalidator("test", mock_clear2)  # Overwrites

        cache_manager.manual_invalidate("test")

        # Should call second one (overwrote first)
        mock_clear1.assert_not_called()
        mock_clear2.assert_called_once()


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance-related tests."""

    @pytest.mark.slow
    def test_debounce_performance(self, mock_callback):
        """Test that debouncing reduces callback calls."""
        handler = CodeChangeHandler(mock_callback, {'.ts'})
        handler.debounce_time = 0.5  # Shorter for test

        # Simulate 100 rapid changes
        for i in range(100):
            event = Mock(is_directory=False, src_path=f"/file{i}.ts")
            handler.on_modified(event)
            time.sleep(0.01)  # 10ms between changes

        # Wait for debounce
        time.sleep(0.6)

        # Should only call callback once (last change)
        assert mock_callback.call_count == 1

    def test_large_number_of_invalidators(self, cache_manager):
        """Test with large number of invalidators."""
        # Register 1000 invalidators
        for i in range(1000):
            mock_clear = Mock()
            cache_manager.register_invalidator(f"cache_{i}", mock_clear)

        assert len(cache_manager.invalidators) == 1000

        # Manual invalidate all
        cache_manager.manual_invalidate()

        # All should be called
        for name, clear_fn in cache_manager.invalidators.items():
            clear_fn.assert_called_once()
