# Resource Sheet Standards (UDS)

**Purpose:** Define Universal Documentation Standards for resource/reference sheets
**Scope:** All projects using resource sheets for component documentation
**Enforcement:** Automated via `validate-resource-sheets.ps1`

---

## Overview

Resource sheets are lightweight documentation artifacts that capture essential context about components, services, or features. This standard ensures consistency across projects.

---

## Naming Convention

### Pattern

```
{ComponentName}-RESOURCE-SHEET.md
```

**Historical Note:** The term `REFERENCE-SHEET` was previously used but is now deprecated. All documentation should use `RESOURCE-SHEET` for consistency.

### Format Requirements

**Component Name Format:** PascalCase-with-hyphens

The component name portion must follow **PascalCase-with-hyphens** format:
- Each word starts with a capital letter
- Words are separated by hyphens (not underscores or spaces)
- Subsequent letters in each word are lowercase
- No ALL-CAPS component names (except for the `-RESOURCE-SHEET` suffix)

**Pattern Breakdown:**
```
Auth-Service-RESOURCE-SHEET.md
^    ^       ^
|    |       |
|    |       +-- Suffix (always ALL-CAPS)
|    +---------- Second word (PascalCase)
+--------------- First word (PascalCase)
```

**Valid Format (PascalCase-with-hyphens):**
- `Auth-Service` ✅
- `Widget-System` ✅
- `File-Api-Route` ✅
- `User-Controller` ✅

**Invalid Formats:**
- `AUTH-SERVICE` ❌ (ALL-CAPS - should be `Auth-Service`)
- `auth-service` ❌ (lowercase - should be `Auth-Service`)
- `AuthService` ❌ (no hyphens for multi-word - should be `Auth-Service`)
- `auth_service` ❌ (snake_case - should be `Auth-Service`)
- `authService` ❌ (camelCase - should be `Auth-Service`)

### Rules

1. **Component name MUST match subject**: If documenting `AuthService`, filename is `Auth-Service-RESOURCE-SHEET.md`
2. **Use PascalCase-with-hyphens**: Each word capitalized, separated by hyphens (e.g., `User-Controller`, not `USER-CONTROLLER`)
3. **Suffix required**: Must end with `-RESOURCE-SHEET.md` (suffix is always ALL-CAPS)
4. **No spaces**: Use hyphens for multi-word components (e.g., `Api-Gateway-RESOURCE-SHEET.md`)
5. **Match actual component name**: If code uses `AuthService`, convert to `Auth-Service` for filename

### Examples

✅ **Valid (PascalCase-with-hyphens):**
- `Auth-Service-RESOURCE-SHEET.md` (PascalCase with hyphens)
- `User-Controller-RESOURCE-SHEET.md` (PascalCase with hyphens)
- `Widget-System-RESOURCE-SHEET.md` (PascalCase with hyphens)
- `File-Api-Route-RESOURCE-SHEET.md` (PascalCase with hyphens, multi-word)
- `Database-Migration-RESOURCE-SHEET.md` (PascalCase with hyphens)
- `Api-Gateway-RESOURCE-SHEET.md` (PascalCase with hyphens)

❌ **Invalid:**
- `AUTH-SERVICE-RESOURCE-SHEET.md` (ALL-CAPS component name - should be `Auth-Service-RESOURCE-SHEET.md`)
- `FILE-API-ROUTE-RESOURCE-SHEET.md` (ALL-CAPS component name - should be `File-Api-Route-RESOURCE-SHEET.md`)
- `USER-CONTROLLER-RESOURCE-SHEET.md` (ALL-CAPS component name - should be `User-Controller-RESOURCE-SHEET.md`)
- `auth-service-RESOURCE-SHEET.md` (lowercase component name - should be `Auth-Service-RESOURCE-SHEET.md`)
- `file-api-route-RESOURCE-SHEET.md` (lowercase component name - should be `File-Api-Route-RESOURCE-SHEET.md`)
- `AuthService-RESOURCE-SHEET.md` (no hyphens for multi-word - should be `Auth-Service-RESOURCE-SHEET.md`)
- `authService-RESOURCE-SHEET.md` (camelCase - should be `Auth-Service-RESOURCE-SHEET.md`)
- `auth_service-RESOURCE-SHEET.md` (snake_case - should be `Auth-Service-RESOURCE-SHEET.md`)
- `Auth-Service.md` (missing suffix)
- `auth service RESOURCE SHEET.md` (spaces not allowed)
- `Auth-Service-RESOURCE.md` (incomplete suffix)
- `Auth-Service-REFERENCE-SHEET.md` (deprecated - use RESOURCE-SHEET)

---

## Directory Location

### Standard Location

All resource sheets MUST be stored in the standardized directory:

```
coderef/resources-sheets/
```

**Rules:**

1. **Consistent naming**: Directory must be named `resources-sheets` (plural, with hyphen)
2. **Not `reference-sheets`**: Historical directory name is deprecated
3. **Project-level directory**: Located at project root under `coderef/` folder
4. **No subdirectories**: All resource sheets in single directory for easy discovery

### Examples

✅ **Valid Paths:**
- `coderef/resources-sheets/Auth-Service-RESOURCE-SHEET.md`
- `coderef/resources-sheets/Widget-System-RESOURCE-SHEET.md`
- `coderef/resources-sheets/File-Api-Route-RESOURCE-SHEET.md`

❌ **Invalid Paths:**
- `docs/Auth-Service-RESOURCE-SHEET.md` (wrong directory)
- `coderef/reference-sheets/Auth-Service-RESOURCE-SHEET.md` (deprecated directory name)
- `coderef/Auth-Service-RESOURCE-SHEET.md` (missing `resources-sheets/` subdirectory)
- `coderef/resources-sheets/auth/Auth-Service-RESOURCE-SHEET.md` (no subdirectories allowed)

### Rationale

**Centralized Discovery:**
- Single location makes all resource sheets easy to find
- Prevents duplication across different directories
- Simplifies validation and tooling

**Consistent Naming:**
- `resources-sheets` matches terminology (resource sheets, not reference sheets)
- Plural form indicates collection of multiple sheets
- Hyphenated for consistency with filename convention

---

## YAML Front Matter

### Field Naming Convention

**Standard:** All YAML field names MUST use `snake_case`

**Rationale:**
- Follows YAML industry best practices
- Consistent with modern configuration standards
- Improves readability and maintainability

**Rules:**
1. **All field names lowercase** - `agent`, not `Agent`
2. **Underscores for multi-word fields** - `parent_project`, not `parentProject` or `ParentProject`
3. **No exceptions** - All required and optional fields follow this convention

**Examples:**
```yaml
# ✅ Correct (snake_case)
agent: coderef-assistant
date: 2026-01-04
task: UPDATE
subject: AuthService
parent_project: backend-api
category: service
related_files:
  - src/auth.ts
related_docs:
  - API-Guide.md

# ❌ Incorrect (PascalCase or camelCase)
Agent: coderef-assistant          # Wrong - should be 'agent'
Date: 2026-01-04                  # Wrong - should be 'date'
Task: UPDATE                      # Wrong - should be 'task'
parentProject: backend-api        # Wrong - should be 'parent_project'
relatedFiles:                     # Wrong - should be 'related_files'
  - src/auth.ts
```

### Required Structure

Every resource sheet MUST start with YAML front matter:

```yaml
---
agent: {agent-name}
date: YYYY-MM-DD
task: REVIEW|CONSOLIDATE|DOCUMENT|UPDATE|CREATE
subject: {component-name}
parent_project: {project-name}
category: service|controller|model|utility|integration|component|middleware|validator|schema|config|other
---
```

### Required Fields

| Field | Type | Description | Format | Example |
|-------|------|-------------|--------|---------|
| agent | string | Creator/updater name | Any string (1-100 chars) | `coderef-assistant` |
| date | string | Creation/update date | `YYYY-MM-DD` | `2026-01-04` |
| task | enum | Type of work performed | One of: `REVIEW`, `CONSOLIDATE`, `DOCUMENT`, `UPDATE`, `CREATE` | `CONSOLIDATE` |
| subject | string | Component/topic being documented | Any string (1-200 chars) | `AuthService` |
| parent_project | string | Parent project/codebase | Any string (1-100 chars) | `backend-api` |
| category | enum | Classification type | One of: `service`, `controller`, `model`, `utility`, `integration`, `component`, `middleware`, `validator`, `schema`, `config`, `other` | `service` |

### Optional Fields

| Field | Type | Description | Format | Example |
|-------|------|-------------|--------|---------|
| version | string | Resource sheet version | Semver (`X.Y.Z`) | `1.0.0` |
| related_files | array | Related source files | Array of file paths | `["src/auth/auth.service.ts"]` |
| related_docs | array | Related documentation | Array of .md files | `["API-Auth-Guide.md"]` |
| workorder | string | Associated workorder ID | `WO-{CATEGORY}-{ID}` | `WO-AUTH-001` |
| tags | array | Categorization tags | Array of strings | `["authentication", "security"]` |
| status | enum | Documentation status | One of: `DRAFT`, `REVIEW`, `APPROVED`, `ARCHIVED` | `APPROVED` |

### Complete Example

```yaml
---
agent: coderef-assistant
date: 2026-01-04
task: CONSOLIDATE
subject: AuthService
parent_project: backend-api
category: service
version: 1.0.0
related_files:
  - src/auth/auth.service.ts
  - src/auth/token.service.ts
related_docs:
  - API-Authentication-Guide.md
workorder: WO-AUTH-SYSTEM-001
tags: [authentication, security, api]
status: APPROVED
---
```

---

## UDS-Compliant Section Headers

### Required Sections

Every resource sheet MUST include these sections:

1. **Executive Summary**
   - **Purpose:** 2-3 sentence overview
   - **Content:** What this component is, why it exists, primary responsibility
   - **Example:**
     ```markdown
     ## Executive Summary

     AuthService is the centralized authentication handler for the application. It manages user login, token generation, and session validation. This service is critical for all protected API endpoints.
     ```

2. **Audience & Intent**
   - **Purpose:** Who should read this and why
   - **Content:** Target audience, use cases, when to reference
   - **Example:**
     ```markdown
     ## Audience & Intent

     **Audience:** Backend developers, API consumers, security reviewers
     **Intent:** Quick reference for authentication flows, token handling, and error scenarios
     **When to use:** Before modifying auth logic, debugging login issues, adding new protected routes
     ```

3. **Quick Reference**
   - **Purpose:** Fast lookups (most-used patterns, common operations)
   - **Content:** Code snippets, CLI commands, common patterns
   - **Example:**
     ```markdown
     ## Quick Reference

     ### Login Flow
     ```javascript
     const token = await authService.login(username, password);
     ```

     ### Validate Token
     ```javascript
     const isValid = await authService.validateToken(token);
     ```

     ### Common Errors
     - `AUTH_INVALID_CREDENTIALS` - Username/password mismatch
     - `AUTH_TOKEN_EXPIRED` - Token exceeded TTL (24 hours)
     ```

### Optional Sections

- **Architecture** - Component design, dependencies
- **API Reference** - Endpoint documentation
- **Configuration** - Environment variables, settings
- **Testing Guide** - How to test this component
- **Known Issues** - Current bugs, limitations
- **Related Resources** - Links to other docs

---

## Content Guidelines

### Tone

- **Concise**: Resource sheets are quick references, not comprehensive guides
- **Actionable**: Focus on "how to use" over "why it exists"
- **Current**: Update dates when content changes
- **Professional**: No emojis - use text markers like [WARN], [INFO], [DEPRECATED]

### Length

- **Minimum**: 100 lines (meaningful content)
- **Maximum**: 500 lines (if longer, split into multiple sheets)
- **Optimal**: 150-250 lines

### Code Examples

- Use fenced code blocks with language tags:
  ```javascript
  // Good
  ```

- Include comments for complex logic
- Show both success and error cases

### Visual Aids

- Use tables for parameter lists, config options
- Use bullet lists for step-by-step instructions
- Use blockquotes for important warnings:
  ```markdown
  > [WARN] Changing this setting requires server restart
  ```

---

## Validation

### Automated Checks

Run the validator script:

```powershell
# Validate all resource sheets in current directory
.\validate-resource-sheets.ps1

# Validate specific directory
.\validate-resource-sheets.ps1 -Path C:\path\to\project

# Verbose output
.\validate-resource-sheets.ps1 -Verbose
```

### Validation Rules

The validator checks:

1. **YAML Front Matter**
   - Starts with `---`
   - Contains required fields: `agent`, `date`, `task`, `subject`, `parent_project`, `category`
   - All fields use `snake_case` naming (e.g., `parent_project`, not `parentProject`)
   - Date format: `YYYY-MM-DD`
   - Task is valid enum value

2. **Directory Location**
   - File must be located in `coderef/resources-sheets/` directory
   - Not in deprecated `coderef/reference-sheets/` directory
   - Not in project root or other directories (e.g., `docs/`)
   - No subdirectories allowed under `resources-sheets/`

3. **Naming Convention**
   - Filename matches pattern: `{Component}-RESOURCE-SHEET.md`
   - Component name uses **PascalCase-with-hyphens** format
   - Component name in filename matches YAML `subject` field
   - **Format Validation:**
     - ✅ Valid: `Auth-Service-RESOURCE-SHEET.md` (PascalCase-with-hyphens)
     - ❌ Invalid: `AUTH-SERVICE-RESOURCE-SHEET.md` (ALL-CAPS)
     - ❌ Invalid: `auth-service-RESOURCE-SHEET.md` (lowercase)
     - ❌ Invalid: `AuthService-RESOURCE-SHEET.md` (missing hyphens for multi-word)

4. **UDS Headers**
   - Contains `Executive Summary` section
   - Contains `Audience & Intent` section
   - Contains `Quick Reference` section

5. **No Emojis**
   - Document must not contain any emoji characters
   - Use text markers instead: [WARN], [INFO], [DEPRECATED], [PASS], [FAIL]

### Validation Severity Levels

The validator assigns severity levels to violations:

- **ERROR**: Critical violations that must be fixed
  - Missing required YAML fields
  - Wrong directory location
  - ALL-CAPS filename format
  - Missing required sections

- **WARNING**: Recommended fixes (non-blocking)
  - Missing optional fields
  - Minor formatting issues
  - Deprecated patterns still functional

### Exit Codes

- `0` - All sheets valid
- `1` - Validation failures detected

---

## Migration Checklist

When converting existing documentation to resource sheets:

- [ ] Add YAML front matter at top of file
- [ ] Rename file to match pattern: `{Component}-RESOURCE-SHEET.md`
- [ ] Add required sections: Executive Summary, Audience & Intent, Quick Reference
- [ ] Update `Date` field to today's date
- [ ] Set `Task` to `UPDATE` (for migrations)
- [ ] Add `Component` field matching filename
- [ ] Run validation script
- [ ] Fix any errors reported by validator
- [ ] Commit to version control

---

## Examples

### Minimal Valid Resource Sheet

```markdown
---
Agent: Taylor
Date: 2026-01-04
Task: CREATE
Component: AuthService
---

# AuthService Resource Sheet

## Executive Summary

AuthService handles user authentication for the application. It manages login, logout, and token validation.

## Audience & Intent

**Audience:** Backend developers
**Intent:** Quick reference for authentication operations
**When to use:** When implementing protected routes

## Quick Reference

### Login
```javascript
const token = await authService.login(username, password);
```

### Logout
```javascript
await authService.logout(token);
```
```

### Comprehensive Resource Sheet

```markdown
---
Agent: coderef-assistant
Date: 2026-01-04
Task: CONSOLIDATE
Component: AuthService
Workorder: WO-AUTH-SYSTEM-001
Tags: [authentication, security, jwt, api]
Status: APPROVED
Version: 1.0.0
---

# AuthService Resource Sheet

## Executive Summary

AuthService is the centralized authentication and authorization service for the application. It provides JWT-based authentication, role-based access control (RBAC), and session management. This service is critical infrastructure used by all protected API endpoints.

## Audience & Intent

**Audience:** Backend developers, API consumers, security engineers, DevOps
**Intent:** Comprehensive reference for authentication flows, token handling, error scenarios, and security best practices
**When to use:**
- Before modifying authentication logic
- Debugging login/logout issues
- Adding new protected routes
- Implementing role-based features
- Security audits

## Quick Reference

### Login Flow
```javascript
const result = await authService.login({
  username: 'user@example.com',
  password: 'secure-password'
});
// Returns: { token: 'jwt-token', expiresAt: '2026-01-05T12:00:00Z' }
```

### Validate Token
```javascript
const isValid = await authService.validateToken(token);
if (!isValid) {
  throw new UnauthorizedError('Invalid or expired token');
}
```

### Get User from Token
```javascript
const user = await authService.getUserFromToken(token);
// Returns: { id: 123, username: 'user@example.com', roles: ['admin'] }
```

### Check Permissions
```javascript
const hasAccess = await authService.checkPermission(user, 'admin.users.delete');
```

## Architecture

**Dependencies:**
- Database: PostgreSQL (users, sessions tables)
- Cache: Redis (token blacklist, rate limiting)
- External: No third-party auth providers (self-hosted)

**Key Components:**
- `TokenService` - JWT generation and validation
- `SessionService` - Session lifecycle management
- `PermissionService` - RBAC enforcement

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | (required) | Secret key for JWT signing |
| `JWT_EXPIRY` | `24h` | Token expiration time |
| `SESSION_TIMEOUT` | `30m` | Idle session timeout |
| `MAX_LOGIN_ATTEMPTS` | `5` | Rate limit before lockout |

## Common Errors

| Error Code | Meaning | Solution |
|------------|---------|----------|
| `AUTH_INVALID_CREDENTIALS` | Username/password mismatch | Check credentials, handle gracefully |
| `AUTH_TOKEN_EXPIRED` | Token exceeded TTL | Refresh token or re-authenticate |
| `AUTH_INSUFFICIENT_PERMISSIONS` | User lacks required role | Check permission requirements |
| `AUTH_ACCOUNT_LOCKED` | Too many failed attempts | Wait 15 minutes or contact admin |

## Testing

```javascript
// Unit test example
describe('AuthService', () => {
  it('should generate valid JWT token', async () => {
    const token = await authService.generateToken({ userId: 123 });
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    expect(payload.userId).toBe(123);
  });
});
```

## Known Issues

- Issue #42: Token refresh during high load causes race condition
- TODO: Implement OAuth2 support for third-party providers

## Related Resources

- [API Authentication Guide](../guides/API-AUTH.md)
- [Security Best Practices](../standards/SECURITY.md)
- [UserController-RESOURCE-SHEET.md](./UserController-RESOURCE-SHEET.md)

---

**Last Updated:** 2026-01-04
**Maintained by:** Backend Team
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-04 | Initial UDS standard for resource sheets |

---

**Maintained by:** Papertrail Standards Team
**Schema:** `papertrail/schemas/documentation/resource-sheet-metadata-schema.json`
**Validator:** `papertrail/validators/documentation/validate-resource-sheets.ps1`
