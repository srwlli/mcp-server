---
element: AuthService
type: Auto-detected
modules: [architecture, integration, testing, performance]
auto_fill_rate: 50.0%
generated: 2026-01-02
mode: template
version: 1.0.0
---

# AuthService - Authoritative Documentation

## Detected Characteristics

- ✓ Is Class
- ✓ Makes Network Calls
- ✓ Handles Auth
- ✓ Has Error Handling

## 1. Architecture

**Type:** Class

**Dependencies:**
- `axios`
- `jwt-decode`

**Exports:**
- `AuthService`

**File Location:** `src/services/AuthService.ts`

**Lines of Code:** 250

**Manual Review Required:**
- Are there additional architectural patterns to document?
- Any key design decisions to note?

## 2. Integration Points

**Used By:** (Consumers of this element)
- `LoginForm`
- `App.tsx`
- `ProtectedRoute`

**Uses:** (Dependencies)
- `axios`
- `localStorage`
- `EventEmitter`

**Events:**

*Emits:*
- `auth:login`
- `auth:logout`
- `auth:refresh`

*Listens:*
- `app:init`

**Manual Review Required:**
- Any indirect integration points not detected?
- Are there runtime dependencies?

## 3. Testing Strategy

⚠️ Testing documentation module - to be implemented

## 4. Performance

⚠️ Performance documentation module - to be implemented
