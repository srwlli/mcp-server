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

### Rules

1. **Component name MUST match subject**: If documenting `AuthService`, filename is `AuthService-RESOURCE-SHEET.md`
2. **Use exact casing**: Match the component's actual name (e.g., `UserController`, not `usercontroller`)
3. **Suffix required**: Must end with `-RESOURCE-SHEET.md`
4. **No spaces**: Use hyphens for multi-word components (e.g., `API-Gateway-RESOURCE-SHEET.md`)

### Examples

✅ **Valid:**
- `AuthService-RESOURCE-SHEET.md`
- `UserController-RESOURCE-SHEET.md`
- `Database-Migration-RESOURCE-SHEET.md`
- `API-Gateway-RESOURCE-SHEET.md`

❌ **Invalid:**
- `auth-service-RESOURCE-SHEET.md` (wrong casing)
- `AuthService.md` (missing suffix)
- `auth service RESOURCE SHEET.md` (spaces not allowed)
- `AuthService-RESOURCE.md` (incomplete suffix)
- `AuthService-REFERENCE-SHEET.md` (deprecated - use RESOURCE-SHEET)

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
  > ⚠️ **Warning:** Changing this setting requires server restart
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
   - Contains required fields: `Agent`, `Date`, `Task`
   - Date format: `YYYY-MM-DD`
   - Task is valid enum value

2. **Naming Convention**
   - Filename matches pattern: `{Component}-RESOURCE-SHEET.md`
   - Component name in filename matches YAML `Component` field (if present)

3. **UDS Headers**
   - Contains `Executive Summary` section
   - Contains `Audience & Intent` section
   - Contains `Quick Reference` section

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
