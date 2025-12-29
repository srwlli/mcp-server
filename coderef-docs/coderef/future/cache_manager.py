"""
Cache manager with automatic invalidation via file system watching.

Monitors project directories for code changes and invalidates extractor caches
when relevant files are modified. Provides both time-based and file-based
invalidation strategies.

Part of WO-CACHE-INVALIDATION-001.
"""

import os
import time
import threading
from pathlib import Path
from typing import Dict, Set, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from logger_config import logger


class CodeChangeHandler(FileSystemEventHandler):
    """
    File system event handler for code changes.

    Monitors specified file patterns and triggers cache invalidation
    when relevant files are modified.
    """

    def __init__(self, on_change_callback: Callable[[str], None], file_patterns: Set[str]):
        """
        Initialize handler.

        Args:
            on_change_callback: Function to call when relevant file changes
            file_patterns: Set of file extensions to monitor (e.g., {'.ts', '.js', '.py'})
        """
        self.on_change_callback = on_change_callback
        self.file_patterns = file_patterns
        self.debounce_time = 2.0  # Wait 2 seconds after last change
        self.last_change_time = 0
        self.debounce_timer: Optional[threading.Timer] = None

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = event.src_path
        file_ext = Path(file_path).suffix.lower()

        # Only process relevant file types
        if file_ext not in self.file_patterns:
            return

        # Debounce: Wait for burst of changes to settle
        self._schedule_invalidation(file_path)

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        self.on_modified(event)  # Same logic as modification

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events."""
        self.on_modified(event)  # Same logic as modification

    def _schedule_invalidation(self, file_path: str) -> None:
        """
        Debounced invalidation scheduling.

        Waits for changes to settle before triggering invalidation.
        Prevents excessive cache clearing during rapid file saves.
        """
        # Cancel previous timer if exists
        if self.debounce_timer:
            self.debounce_timer.cancel()

        # Schedule new invalidation
        def trigger():
            logger.info(f"Code change detected: {file_path}")
            self.on_change_callback(file_path)

        self.debounce_timer = threading.Timer(self.debounce_time, trigger)
        self.debounce_timer.start()


class CacheManager:
    """
    Manages cache invalidation for extractor functions.

    Provides two invalidation strategies:
    1. File-based: Watch file system for code changes
    2. Time-based: Expire cache after TTL

    Usage:
        manager = CacheManager()
        manager.register_invalidator("apis", extract_apis.cache_clear)
        manager.watch_directory("/path/to/project", file_patterns={'.ts', '.js'})
        manager.start()
    """

    def __init__(self):
        self.observers: Dict[str, Observer] = {}
        self.invalidators: Dict[str, Callable[[], None]] = {}
        self.last_invalidation: Dict[str, float] = {}
        self.ttl: float = 300.0  # 5 minutes default TTL
        self.is_running = False

    def register_invalidator(self, name: str, cache_clear_fn: Callable[[], None]) -> None:
        """
        Register a cache invalidator function.

        Args:
            name: Unique name for this cache (e.g., "apis", "schemas")
            cache_clear_fn: Function to call to clear cache (e.g., extract_apis.cache_clear)

        Example:
            >>> manager.register_invalidator("apis", extract_apis.cache_clear)
        """
        self.invalidators[name] = cache_clear_fn
        self.last_invalidation[name] = time.time()
        logger.info(f"Registered cache invalidator: {name}")

    def watch_directory(self, project_path: str, file_patterns: Set[str] = None) -> None:
        """
        Watch directory for code changes.

        Args:
            project_path: Path to project directory to watch
            file_patterns: File extensions to monitor (default: {'.ts', '.tsx', '.js', '.jsx', '.py'})

        Example:
            >>> manager.watch_directory("/path/to/project", file_patterns={'.ts', '.js'})
        """
        if file_patterns is None:
            file_patterns = {'.ts', '.tsx', '.js', '.jsx', '.py', '.vue', '.svelte'}

        # Create observer for this directory
        observer = Observer()
        handler = CodeChangeHandler(
            on_change_callback=self._on_code_change,
            file_patterns=file_patterns
        )

        observer.schedule(handler, project_path, recursive=True)
        self.observers[project_path] = observer

        logger.info(f"Watching directory: {project_path} (patterns: {file_patterns})")

    def start(self) -> None:
        """Start all file system observers."""
        if self.is_running:
            logger.warning("Cache manager already running")
            return

        for path, observer in self.observers.items():
            observer.start()
            logger.info(f"Started watching: {path}")

        self.is_running = True

    def stop(self) -> None:
        """Stop all file system observers."""
        if not self.is_running:
            return

        for path, observer in self.observers.items():
            observer.stop()
            observer.join(timeout=5)
            logger.info(f"Stopped watching: {path}")

        self.is_running = False

    def _on_code_change(self, file_path: str) -> None:
        """
        Handle code change event.

        Invalidates all registered caches when code changes are detected.
        """
        logger.info(f"Invalidating caches due to change in: {file_path}")

        for name, cache_clear_fn in self.invalidators.items():
            cache_clear_fn()
            self.last_invalidation[name] = time.time()
            logger.debug(f"Cleared cache: {name}")

    def check_ttl_expiration(self) -> None:
        """
        Check if any caches have exceeded TTL.

        Call this periodically (e.g., every 60 seconds) to enforce time-based expiration.
        """
        current_time = time.time()

        for name, last_invalidation_time in self.last_invalidation.items():
            age = current_time - last_invalidation_time

            if age > self.ttl:
                logger.info(f"Cache '{name}' expired (age: {age:.1f}s > TTL: {self.ttl}s)")
                self.invalidators[name]()
                self.last_invalidation[name] = current_time

    def manual_invalidate(self, name: Optional[str] = None) -> None:
        """
        Manually invalidate cache(s).

        Args:
            name: Specific cache to invalidate, or None to invalidate all

        Example:
            >>> manager.manual_invalidate("apis")  # Invalidate only APIs cache
            >>> manager.manual_invalidate()        # Invalidate all caches
        """
        if name:
            if name in self.invalidators:
                self.invalidators[name]()
                self.last_invalidation[name] = time.time()
                logger.info(f"Manually invalidated cache: {name}")
            else:
                logger.warning(f"Unknown cache name: {name}")
        else:
            # Invalidate all
            for cache_name in self.invalidators:
                self.invalidators[cache_name]()
                self.last_invalidation[cache_name] = time.time()
            logger.info("Manually invalidated all caches")


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Get global cache manager instance (singleton pattern).

    Returns:
        CacheManager: Global instance

    Example:
        >>> manager = get_cache_manager()
        >>> manager.register_invalidator("apis", extract_apis.cache_clear)
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def initialize_cache_watching(project_path: str) -> None:
    """
    Initialize cache watching for a project.

    Convenience function to set up file watching with defaults.

    Args:
        project_path: Path to project directory

    Example:
        >>> initialize_cache_watching("/path/to/project")
    """
    manager = get_cache_manager()

    # Register extractors (imported lazily to avoid circular imports)
    try:
        from extractors import extract_apis, extract_schemas, extract_components

        manager.register_invalidator("apis", extract_apis.cache_clear)
        manager.register_invalidator("schemas", extract_schemas.cache_clear)
        manager.register_invalidator("components", extract_components.cache_clear)
    except ImportError as e:
        logger.warning(f"Could not import extractors: {e}")

    # Watch project directory
    manager.watch_directory(project_path)

    # Start watching
    manager.start()

    logger.info(f"Cache watching initialized for: {project_path}")


# Cleanup on module unload
def cleanup():
    """Stop cache manager on shutdown."""
    global _cache_manager
    if _cache_manager:
        _cache_manager.stop()
        logger.info("Cache manager stopped")


import atexit
atexit.register(cleanup)
