# Phase 3: APIs & Databases - Implementation Plan

**Feature**: api_inventory + database_inventory (Tools #16, #17)
**Version**: v1.7.0
**Status**: Planning
**Created**: 2025-10-15
**Complexity**: High (2 distinct tools)

---

## Executive Summary

Phase 3 delivers two complementary inventory tools:
1. **`api_inventory`** (Tool #16): Discovers API endpoints, frameworks, and documentation
2. **`database_inventory`** (Tool #17): Analyzes database schemas, migrations, and relationships

**Challenge**: This is the first phase with 2 tools. Requires careful scoping to avoid scope creep.

---

## Scope Decision

**Option A** (SELECTED): Build both tools sequentially
- **api_inventory** first (Phases 3A-3F)
- **database_inventory** second (Phases 3G-3L)
- **Estimated effort**: 16-20 hours total

**Why**: Both tools are valuable and complement the inventory system. Sequential implementation reduces risk.

---

## Tool #16: api_inventory

### What it analyzes:
1. **Framework Detection**
   - Python: FastAPI, Flask, Django REST Framework
   - Node.js: Express, Koa, NestJS
   - Detect by framework imports/signatures

2. **Endpoint Discovery**
   - REST endpoints (path, method, params)
   - GraphQL schemas (queries, mutations)
   - WebSocket endpoints

3. **Documentation Coverage**
   - OpenAPI/Swagger specs
   - Inline route documentation
   - Coverage percentage

### Input Parameters:
- `project_path` (required)
- `frameworks` (optional): ["all"] or specific frameworks
- `include_graphql` (optional): default false
- `scan_documentation` (optional): default true

### Output: `coderef/inventory/api.json`
```json
{
  "project_name": "my-project",
  "frameworks": ["fastapi"],
  "endpoints": [
    {
      "path": "/api/users",
      "method": "GET",
      "framework": "fastapi",
      "file": "routes/users.py",
      "line": 45,
      "params": ["user_id", "limit"],
      "documented": true,
      "doc_coverage": 85
    }
  ],
  "metrics": {
    "total_endpoints": 127,
    "documented_endpoints": 108,
    "documentation_coverage": 85,
    "frameworks_detected": ["fastapi"],
    "rest_endpoints": 120,
    "graphql_endpoints": 7
  }
}
```

### Complexity: Medium-High
- Framework detection: regex patterns + AST parsing
- Endpoint extraction: framework-specific parsers
- Documentation parsing: OpenAPI YAML/JSON parsing

---

## Tool #17: database_inventory

### What it analyzes:
1. **Database Detection**
   - SQL databases: PostgreSQL, MySQL, SQLite
   - NoSQL: MongoDB, Redis
   - ORM detection: SQLAlchemy, Django ORM, Prisma, TypeORM

2. **Schema Analysis**
   - Tables/Collections
   - Columns/Fields (type, nullable, default)
   - Relationships (foreign keys, references)
   - Indexes

3. **Migration Tracking**
   - Migration files (Alembic, Django, Flyway)
   - Applied vs pending migrations
   - Migration history

### Input Parameters:
- `project_path` (required)
- `database_types` (optional): ["all"] or specific types
- `include_migrations` (optional): default true
- `scan_relationships` (optional): default true

### Output: `coderef/inventory/database.json`
```json
{
  "project_name": "my-project",
  "databases": ["postgresql"],
  "orm": "sqlalchemy",
  "tables": [
    {
      "name": "users",
      "database": "postgresql",
      "file": "models/user.py",
      "columns": [
        {"name": "id", "type": "Integer", "primary_key": true},
        {"name": "email", "type": "String", "nullable": false}
      ],
      "relationships": [
        {"target": "posts", "type": "one_to_many"}
      ],
      "indexes": ["idx_email"]
    }
  ],
  "migrations": {
    "framework": "alembic",
    "total": 45,
    "applied": 45,
    "pending": 0,
    "files": ["migrations/001_init.py", ...]
  },
  "metrics": {
    "total_tables": 23,
    "total_columns": 187,
    "total_indexes": 45,
    "total_relationships": 38
  }
}
```

### Complexity: High
- Database/ORM detection: import analysis
- Schema parsing: ORM model parsing (AST)
- Migration tracking: file scanning + version detection
- Relationship mapping: complex graph analysis

---

## Implementation Phases

### Phase 3A: API Tool Foundation (3 hours)
- Create `generators/api_generator.py`
- Add framework detection logic (regex + imports)
- Basic endpoint data structure
- Schema definition: `coderef/inventory/api-schema.json`

### Phase 3B: API Parsers (4 hours)
- FastAPI parser (decorator-based routes)
- Flask parser (route decorator)
- Express parser (app.get/post/etc)
- GraphQL schema parser (optional)

### Phase 3C: API Documentation Scanner (2 hours)
- OpenAPI/Swagger YAML/JSON parser
- Inline docstring extraction
- Coverage calculation

### Phase 3D: API MCP Integration (1 hour)
- Add Tool #16 to server.py
- Handler: `handle_api_inventory`
- Constants: `APIFramework`, `HTTPMethod` enums
- TypeDicts: `APIEndpointDict`, `APIManifestDict`

### Phase 3E: API Documentation (1 hour)
- README.md update
- API.md: Tool #16 documentation
- my-guide.md update
- Slash command: `/api-inventory`

### Phase 3F: API Testing + Commit (1 hour)
- Test on docs-mcp project (FastAPI)
- Test on sample Express project
- Changelog entry (v1.7.0)
- Git commit + push

**API Tool Subtotal**: 12 hours

---

### Phase 3G: Database Tool Foundation (2 hours)
- Create `generators/database_generator.py`
- Database/ORM detection
- Basic schema data structure
- Schema definition: `coderef/inventory/database-schema.json`

### Phase 3H: Database Schema Parsers (3 hours)
- SQLAlchemy model parser (Python AST)
- Django ORM parser
- Prisma schema parser
- Raw SQL file parser (basic)

### Phase 3I: Migration Scanner (2 hours)
- Alembic migration detection
- Django migrations detection
- Migration version tracking
- Applied vs pending detection

### Phase 3J: Database MCP Integration (1 hour)
- Add Tool #17 to server.py
- Handler: `handle_database_inventory`
- Constants: `DatabaseType`, `ORMFramework` enums
- TypeDicts: `TableDict`, `DatabaseManifestDict`

### Phase 3K: Database Documentation (1 hour)
- README.md update
- API.md: Tool #17 documentation
- my-guide.md update
- Slash command: `/database-inventory`

### Phase 3L: Database Testing + Commit (1 hour)
- Test on docs-mcp (SQLite via SQLAlchemy)
- Changelog entry (v1.7.0 update)
- Git commit + push

**Database Tool Subtotal**: 10 hours

---

## Total Estimated Effort: 22 hours

**Breakdown**:
- API Tool (3A-3F): 12 hours
- Database Tool (3G-3L): 10 hours

**Risk**: High complexity, especially database schema parsing and migration tracking

---

## Success Criteria

### API Tool:
✅ Detects 3+ frameworks (FastAPI, Flask, Express minimum)
✅ Extracts REST endpoints with method + path
✅ Parses OpenAPI/Swagger specs
✅ Calculates documentation coverage
✅ JSON schema validation
✅ Performance: <3 seconds for 100 endpoints

### Database Tool:
✅ Detects 2+ ORMs (SQLAlchemy, Django minimum)
✅ Parses table schemas with columns + types
✅ Identifies relationships (foreign keys)
✅ Tracks migrations (Alembic, Django)
✅ JSON schema validation
✅ Performance: <5 seconds for 50 tables

---

## Risks & Mitigation

### Risk 1: Scope Too Large (High)
**Mitigation**:
- Start with minimum viable parsers
- Support 2-3 frameworks initially, expand later
- GraphQL is optional (can skip if time-constrained)

### Risk 2: Framework Diversity (Medium)
**Mitigation**:
- Focus on Python/Node.js frameworks (most common)
- Defer Ruby, PHP, Java frameworks to future versions

### Risk 3: AST Parsing Complexity (Medium)
**Mitigation**:
- Use Python `ast` module for Python frameworks
- Use regex fallbacks for complex cases
- Accept 80% accuracy vs 100% perfection

### Risk 4: Migration File Formats (Medium)
**Mitigation**:
- Support major migration frameworks only
- Focus on file detection + counts
- Defer deep migration analysis to Phase 3.5

---

## Simplification Options (If Needed)

If implementation exceeds estimates:

**Option 1**: Reduce frameworks
- API: Support only FastAPI + Flask (drop Express)
- Database: Support only SQLAlchemy (drop Django ORM)

**Option 2**: Reduce features
- Skip GraphQL support
- Skip migration applied/pending detection (just count files)
- Skip deep relationship mapping

**Option 3**: Split Phase
- Ship api_inventory as v1.7.0
- Ship database_inventory as v1.7.1 (separate release)

---

## Dependencies

**New Python Packages**:
- `pyyaml>=6.0` - For OpenAPI/Swagger parsing
- `sqlparse>=0.4.0` - For SQL file parsing (optional)

**External APIs**: None (all local analysis)

---

## Output Files

- `coderef/inventory/api.json` (per project)
- `coderef/inventory/database.json` (per project)
- `coderef/inventory/api-schema.json` (validation)
- `coderef/inventory/database-schema.json` (validation)

---

## Next Steps

1. ✅ Complete this plan
2. Review plan with user
3. Start Phase 3A (API Tool Foundation)
4. Execute phases sequentially
5. Checkpoint commits after each major phase

---

**Plan Version**: 1.0
**Last Updated**: 2025-10-15 00:30 UTC
**Status**: Draft - Ready for Review
