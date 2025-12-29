# Papertrail Integration - Safe Development Plan

**Workorder:** WO-ENHANCE-GENERATORS-WITH-PAPERTRAIL-001
**Status:** Planning
**Risk Level:** HIGH (Large integration, affects 2 production servers)
**Strategy:** Parallel development → Isolated testing → Phased integration

---

## Phase 1: Parallel Development Server (Weeks 1-2)

### Create Development Servers

```bash
# Copy production servers to development versions
cd C:\Users\willh\.mcp-servers

# Create dev servers
cp -r coderef-docs coderef-docs-papertrail
cp -r coderef-workflow coderef-workflow-papertrail
```

### Update .mcp.json

```json
{
  "mcpServers": {
    "coderef-docs": {
      "command": "python",
      "args": ["-m", "coderef-docs.server"],
      "env": {
        "PYTHONPATH": "C:\\Users\\willh\\.mcp-servers"
      }
    },
    "coderef-docs-papertrail": {
      "command": "python",
      "args": ["-m", "coderef-docs-papertrail.server"],
      "env": {
        "PYTHONPATH": "C:\\Users\\willh\\.mcp-servers",
        "PAPERTRAIL_ENABLED": "true"
      }
    }
  }
}
```

**Result:** Both servers run side-by-side. Production untouched.

---

## Phase 2: Isolated Papertrail Module Development (Weeks 2-4)

### Build Papertrail as Standalone Module

```
coderef-docs-papertrail/
├── papertrail/
│   ├── __init__.py
│   ├── template_engine_extended.py    # Template inheritance + includes
│   ├── uds_validator.py               # Schema validation
│   ├── document_health.py             # Health scoring (0-100)
│   ├── ai_generator.py                # AI enhancement layer
│   ├── header_footer_generator.py     # Header/footer injection
│   └── schemas/
│       ├── uds.py                     # UDS schema definitions
│       └── validation_rules.json      # Validation rules
├── tests/
│   └── test_papertrail_isolated.py    # Test WITHOUT coderef integration
└── server.py                          # Modified to import papertrail (optional)
```

**Critical Rules:**
- ✅ Papertrail code lives in `papertrail/` subdirectory
- ✅ Production generators NOT modified yet
- ✅ Test Papertrail modules in isolation first
- ❌ DO NOT touch production `tool_handlers.py` yet

---

## Phase 3: Integration Testing (Weeks 4-5)

### Test Papertrail with Development Server Only

```python
# coderef-docs-papertrail/tool_handlers.py

from papertrail.template_engine_extended import TemplateEngineExtended
from papertrail.header_footer_generator import HeaderFooterGenerator

async def handle_generate_foundation_docs(arguments):
    """NEW handler with Papertrail integration"""

    # Use Papertrail modules
    engine = TemplateEngineExtended()
    header_gen = HeaderFooterGenerator(
        workorder_id=arguments.get("workorder_id"),
        feature_id=arguments.get("feature_id"),
        mcp_server="coderef-docs-papertrail"
    )

    # Generate docs with enhanced templates
    docs = await engine.generate_with_papertrail(...)

    return docs
```

**Testing Strategy:**
```bash
# Run ONLY the development server
python -m coderef-docs-papertrail.server

# Test via Claude Code with /generate-docs-papertrail
# Compare output to production /generate-docs
```

---

## Phase 4: Feature Flag Integration (Week 6)

### Add Feature Flags to Production Server

```python
# coderef-docs/tool_handlers.py

import os

PAPERTRAIL_ENABLED = os.getenv("PAPERTRAIL_ENABLED", "false") == "true"

async def handle_generate_foundation_docs(arguments):
    if PAPERTRAIL_ENABLED:
        # Use new Papertrail-enhanced generator
        from papertrail.template_engine_extended import TemplateEngineExtended
        return await _generate_with_papertrail(arguments)
    else:
        # Use existing production generator (safe fallback)
        return await _generate_legacy(arguments)
```

**Benefits:**
- ✅ Single codebase, controlled rollout
- ✅ Easy rollback (set env var to false)
- ✅ Production stable during testing
- ✅ Gradual migration per tool

---

## Phase 5: Gradual Migration (Weeks 7-8)

### Migration Order (Least Risky → Most Risky)

1. **Week 7: User Docs (Low Risk)**
   - Enable Papertrail for `generate_quickref_interactive` only
   - Test with 10 real projects
   - Validate header/footer metadata
   - If stable → proceed

2. **Week 8: Foundation Docs (Medium Risk)**
   - Enable Papertrail for `generate_foundation_docs`
   - Test with 5 projects
   - Validate UDS schema compliance
   - If stable → proceed

3. **Week 9: Planning Docs (High Risk)**
   - Enable Papertrail for coderef-workflow planning docs
   - Test with 3 features
   - Validate document health tracking
   - If stable → full rollout

---

## Phase 6: Production Cutover (Week 10)

### Final Migration

```bash
# 1. Verify all Papertrail tests pass
pytest coderef-docs-papertrail/tests/ -v

# 2. Merge Papertrail modules into production
cp -r coderef-docs-papertrail/papertrail coderef-docs/

# 3. Update production tool_handlers.py
# (Already has feature flag code from Phase 4)

# 4. Enable Papertrail in production
# Set PAPERTRAIL_ENABLED=true in .mcp.json

# 5. Monitor for 24 hours

# 6. If stable, deprecate dev servers
# Remove coderef-docs-papertrail from .mcp.json
```

---

## Rollback Plan

### If Issues Detected

```bash
# Immediate rollback (< 1 minute)
# Set PAPERTRAIL_ENABLED=false in .mcp.json
# Restart Claude Code

# System reverts to production generators
# Zero data loss, zero downtime
```

### If Catastrophic Failure

```bash
# Restore from backup
cp -r coderef-docs-backup coderef-docs

# Clear MCP cache
rm ~/.cursor/projects/*/mcp-cache.json

# Restart Claude Code
```

---

## Key Safety Principles

1. **Parallel Development**
   - ✅ Build in separate server (coderef-docs-papertrail)
   - ✅ Production never touched during development

2. **Isolated Testing**
   - ✅ Test Papertrail modules standalone first
   - ✅ Test dev server in isolation
   - ✅ Compare output to production

3. **Feature Flags**
   - ✅ Gradual rollout per tool
   - ✅ Easy rollback with env var

4. **Phased Migration**
   - ✅ Low-risk tools first (quickref)
   - ✅ High-risk tools last (planning docs)
   - ✅ Validate at each phase

5. **Always Have Escape Hatch**
   - ✅ Feature flag = instant rollback
   - ✅ Backup servers ready to restore
   - ✅ MCP cache clearing process documented

---

## Success Criteria

**Before Phase 1:**
- [ ] Development servers created (coderef-docs-papertrail, coderef-workflow-papertrail)
- [ ] .mcp.json configured with both production + dev servers
- [ ] Backup of production servers created

**Before Phase 4:**
- [ ] Papertrail modules 100% tested in isolation
- [ ] Dev server generates valid docs with headers/footers
- [ ] UDS schema validation passes 100% of test cases

**Before Phase 6:**
- [ ] All Papertrail-enabled tools tested with 10+ real projects
- [ ] Document health scoring validated
- [ ] Performance benchmarks show < 10% overhead vs production

**Production Cutover:**
- [ ] Feature flags deployed and tested
- [ ] Rollback plan validated (dry run successful)
- [ ] Team trained on rollback procedure
- [ ] Monitoring in place for 24 hours

---

## Timeline Summary

| Phase | Duration | Risk | Deliverable |
|-------|----------|------|-------------|
| 1. Parallel Dev | 1-2 weeks | Low | Dev servers created |
| 2. Module Dev | 2-3 weeks | Low | Papertrail modules complete |
| 3. Integration Test | 1 week | Medium | Dev server validated |
| 4. Feature Flags | 1 week | Medium | Flags deployed |
| 5. Gradual Migration | 2-3 weeks | Medium-High | Tools migrated |
| 6. Cutover | 1 week | High | Production fully migrated |

**Total: 8-11 weeks**

---

## Next Steps

1. **Create workorder:** `/create-workorder` for WO-ENHANCE-GENERATORS-WITH-PAPERTRAIL-001
2. **Set up parallel servers:** Copy coderef-docs → coderef-docs-papertrail
3. **Build Papertrail modules:** Start with template_engine_extended.py
4. **Test in isolation:** Validate each module before integration
5. **Deploy with feature flags:** Gradual rollout, easy rollback

---

**Author:** Claude (AI Agent)
**Created:** 2025-12-28
**Status:** DRAFT
**Review Required:** User approval before Phase 1 execution
