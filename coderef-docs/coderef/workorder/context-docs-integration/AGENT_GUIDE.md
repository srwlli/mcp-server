# Agent Implementation Guide - context-docs-integration

**Workorder:** WO-CONTEXT-DOCS-INTEGRATION-001
**Project:** coderef-docs
**Feature:** Integrate coderef-context for intelligent documentation generation
**Status:** Ready for Implementation
**Duration:** 6-8 hours (3 phases)

---

## 🎯 Your Mission

Integrate coderef-context MCP server into coderef-docs to enable intelligent code analysis for automatic documentation generation. Transform coderef-docs from placeholder-based documentation to code-aware documentation that extracts real API endpoints, database schemas, and component definitions.

---

## 📋 What You're Building

**Current State:**
```
User calls: generate_individual_doc("API")
    ↓
coderef-docs returns: Empty template with placeholders
    ↓
User must: Manually write API endpoints by hand
```

**Target State:**
```
User calls: generate_individual_doc("API")
    ↓
coderef-docs calls: coderef-context.coderef_query("api")
    ↓
coderef-context returns: Real API endpoints [extracted from code]
    ↓
coderef-docs transforms & inserts: Into API.md template
    ↓
User receives: Full API.md with real endpoints (done in 10 seconds!)
```

---

## 🚀 Implementation Path (3 Phases)

### Phase 1: Setup & Integration Point (1 hour)

**Goal:** Prepare infrastructure for coderef-context integration

**Tasks:**

#### SETUP-001: Import coderef-context client (15 min)
- Add import in `coderef-docs/server.py`:
  ```python
  from mcp.client import ClientSession
  from src.context_extractor import (
      extract_apis,
      extract_schemas,
      extract_components
  )
  ```

#### SETUP-002: Add coderef-context health check (15 min)
- At server startup, verify coderef-context is available
- Set `CONTEXT_AVAILABLE = True/False` flag
- Log warning if unavailable, continue with graceful degradation

#### SETUP-003: Create extract_* function stubs (30 min)
- Create `src/integration/context_extractor.py`:
  ```python
  async def extract_apis(project_path: str) -> List[Dict]:
      """Extract API endpoints from coderef-context"""
      try:
          # Call coderef-context via MCP
          # Return structured data
          pass
      except Exception as e:
          logger.warning(f"API extraction failed: {e}")
          return []

  async def extract_schemas(project_path: str) -> List[Dict]:
      """Extract database schemas from coderef-context"""
      try:
          # Call coderef-context via MCP
          # Return structured data
          pass
      except Exception as e:
          logger.warning(f"Schema extraction failed: {e}")
          return []

  async def extract_components(project_path: str) -> List[Dict]:
      """Extract component definitions from coderef-context"""
      try:
          # Call coderef-context via MCP
          # Return structured data
          pass
      except Exception as e:
          logger.warning(f"Component extraction failed: {e}")
          return []
  ```

**Success Criteria:**
- [ ] coderef-context client importable
- [ ] Health check runs at startup without errors
- [ ] Three extract functions exist with proper error handling

---

### Phase 2: Integration (3-4 hours)

**Goal:** Implement code intelligence extraction and integrate with generate_individual_doc

**Tasks:**

#### INTEGRATE-001: API endpoint extraction (1 hour)
- In `extract_apis()`:
  1. Call: `coderef_context.coderef_query("api", project_path)`
  2. Parse response to extract endpoint signatures
  3. Transform to markdown table format:
     ```
     | Method | Path | Description |
     |--------|------|-------------|
     | GET | /users | Get all users |
     | POST | /users | Create user |
     ```
  4. Return as dict with `type: "api"`, `content: markdown_table`

#### INTEGRATE-002: Database schema extraction (1 hour)
- In `extract_schemas()`:
  1. Call: `coderef_context.coderef_scan(project_path, pattern="models/**")`
  2. Parse response to extract entity definitions
  3. Transform to entity relationship format:
     ```
     User
       - id (UUID)
       - name (String)
       - email (String)

     Post
       - id (UUID)
       - user_id (UUID) → User.id
       - title (String)
     ```
  4. Return as dict with `type: "schema"`, `content: entity_text`

#### INTEGRATE-003: Component extraction (1 hour)
- In `extract_components()`:
  1. Call: `coderef_context.coderef_scan(project_path, pattern="**/*.tsx,**/*.jsx")`
  2. Parse response to extract component tree
  3. Transform to hierarchy format:
     ```
     App
       ├── Layout
       │   ├── Header
       │   └── Sidebar
       └── Pages
           ├── Dashboard
           └── Settings
     ```
  4. Return as dict with `type: "components"`, `content: hierarchy_text`

#### INTEGRATE-004: Error handling + caching (30 min)
- Wrap all extract_* calls with try/except in `generate_individual_doc()`
- Add memoization: Cache results keyed by (project_path, template_type)
- For each template type in `generate_individual_doc()`:
  ```python
  if template_name == "api":
      extracted = await extract_apis(project_path)
      if extracted:
          # Populate template with real data
          return template.render(endpoints=extracted)
      else:
          # Fall back to placeholder
          return template.render(endpoints=[])
  ```

**Success Criteria:**
- [ ] API.md populated with ≥2 real endpoints when coderef-context available
- [ ] SCHEMA.md populated with ≥2 real entities
- [ ] COMPONENTS.md populated with real component tree
- [ ] Graceful fallback to placeholders if coderef-context unavailable
- [ ] No breaking changes to existing doc generation

---

### Phase 3: Testing & Validation (2-3 hours)

**Goal:** Test integration thoroughly, verify quality, ensure backward compatibility

**Tasks:**

#### TEST-001: Unit tests for extract_* functions (1 hour)
- File: `tests/test_integration_context_docs.py`
- Mock coderef-context calls
- Test each extract function independently:
  ```python
  @pytest.mark.asyncio
  async def test_extract_apis_returns_list():
      # Mock coderef_context to return API data
      # Call extract_apis()
      # Assert returns list of dicts with proper structure
      pass

  @pytest.mark.asyncio
  async def test_extract_apis_graceful_failure():
      # Mock coderef_context to raise exception
      # Call extract_apis()
      # Assert returns empty list, logs warning
      pass
  ```

#### TEST-002: Integration tests with real coderef-context (45 min)
- File: `tests/integration/test_context_docs_integration.py`
- Test actual coderef-context calls with sample projects
- Verify doc output format and content:
  ```python
  @pytest.mark.integration
  async def test_api_md_generation():
      # Create sample project with API endpoints
      # Call generate_individual_doc("api", project_path)
      # Assert API.md contains real endpoint data
      pass
  ```

#### TEST-003: Regression tests (30 min)
- Run all existing coderef-docs tests
- Ensure backward compatibility:
  ```bash
  pytest tests/ -v
  # Expected: All existing tests pass, no new failures
  ```

**Success Criteria:**
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All existing tests still passing (no regressions)
- [ ] ≥90% code coverage for new code

---

## 📂 File Structure

**Create:**
- `src/integration/context_extractor.py` (extract_apis, extract_schemas, extract_components)
- `tests/test_integration_context_docs.py` (unit tests)
- `tests/integration/test_context_docs_integration.py` (integration tests)

**Modify:**
- `server.py` - Add health check, import extractors, call in generate_individual_doc()
- `CLAUDE.md` - Document new integration points

---

## 🔧 How to Call coderef-context

**Pattern 1: Query API endpoints**
```python
async def call_coderef_context():
    # Use existing MCP client session
    result = await session.call_tool(
        "query",
        arguments={
            "project_path": project_path,
            "query_type": "calls",
            "target": "api_endpoint"
        }
    )
    return result
```

**Pattern 2: Scan for patterns**
```python
async def scan_project():
    result = await session.call_tool(
        "scan",
        arguments={
            "project_path": project_path,
            "pattern": "**/*.py",
            "languages": ["python"]
        }
    )
    return result
```

**Note:** Check coderef-context/CLAUDE.md for exact tool names and signatures

---

## ✅ Success Criteria

**Functional:**
- ✅ API.md contains real endpoint signatures from coderef-context
- ✅ SCHEMA.md contains real entity definitions from coderef-context
- ✅ COMPONENTS.md contains real component definitions from coderef-context
- ✅ Graceful fallback to placeholders if coderef-context unavailable

**Quality:**
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ All existing tests still passing (no regressions)
- ✅ ≥90% code coverage for new code
- ✅ mypy passes, black formatted, ruff clean

**Performance:**
- ✅ Doc generation <10s per document
- ✅ Results memoized to avoid redundant calls
- ✅ Graceful timeout handling (120s max)

**Integration:**
- ✅ Health check runs at startup
- ✅ Proper error logging
- ✅ No new external dependencies

---

## 🚨 Common Issues & Solutions

**Issue: coderef-context not available**
- Solution: Check health check at startup, return placeholder docs, log warning

**Issue: coderef-context returns verbose/malformed data**
- Solution: Parse carefully, extract only needed fields, handle errors

**Issue: Doc generation timeout**
- Solution: Add timeout wrapper (120s max), fall back to placeholders on timeout

**Issue: Backward compatibility broken**
- Solution: Always have placeholder fallback, never require coderef-context

---

## 📝 Implementation Order

1. **SETUP-001**: Import client library (15 min)
2. **SETUP-002**: Add health check (15 min)
3. **SETUP-003**: Create extract function stubs (30 min)
4. **INTEGRATE-001**: Implement API extraction (1h)
5. **INTEGRATE-002**: Implement schema extraction (1h)
6. **INTEGRATE-003**: Implement component extraction (1h)
7. **INTEGRATE-004**: Add error handling + caching (30 min)
8. **TEST-001**: Write unit tests (1h)
9. **TEST-002**: Write integration tests (45 min)
10. **TEST-003**: Run regression tests (30 min)

**Total Time: 6-8 hours**

---

## 🎯 Right Now: Next Step

1. Read: `plan.json` (sections 1-4 for context)
2. Read: This file (you're reading it!)
3. Read: `CLAUDE.md` in coderef-context for tool signatures
4. Start: SETUP-001 (import coderef-context client)

---

## 📞 Questions?

- **"What are the coderef-context tools?"** → Read coderef-context/CLAUDE.md "Tools Catalog"
- **"How do I call MCP tools?"** → Check coderef-context/server.py for call pattern
- **"What's the exact transform format?"** → Check existing coderef-docs templates
- **"How do I test?"** → See TEST-001 section above for examples

---

**Status:** Ready for Implementation
**Next Task:** SETUP-001 (Import coderef-context client)
**Expected Duration:** 6-8 hours to complete all 3 phases
**Good Luck!** 🚀
