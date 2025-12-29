# Cache Manager (Future Feature)

**Status:** 🔮 Not Integrated
**Created:** 2025-12-28
**File:** `cache_manager.py`

## What It Does

Automatic cache invalidation via file system watching. When code files change, the cache manager auto-clears LRU caches for `extract_apis`, `extract_schemas`, and `extract_components`.

## Why It's Not Integrated

- **Current system works fine:** Cache resets on server restart
- **Rare use case:** Most users generate docs once, not during active coding
- **Adds complexity:** Requires `watchdog` dependency and integration hooks

## To Integrate (If Needed)

1. Install dependency: `uv add watchdog`
2. Import in `server.py`: `from cache_manager import initialize_cache_watching`
3. Call at startup or on first tool use
4. Add cleanup hooks for shutdown

## Current Value

**Zero** - File exists but isn't imported or called anywhere.

## Recommendation

Leave archived unless long-running server sessions with active coding become a common use case.
