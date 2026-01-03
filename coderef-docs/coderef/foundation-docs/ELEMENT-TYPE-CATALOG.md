# Element Type Catalog - Resource Sheet System

**Version:** 1.0.0
**Last Updated:** 2026-01-03
**Workorder:** WO-RESOURCE-SHEET-CONSOLIDATION-001

---

## Purpose

Comprehensive catalog of all 20 element types used for resource sheet classification and module selection. Each type includes detection patterns, conditional modules, focus areas, and validation checklists.

---

## Overview

The resource sheet system classifies code elements into **20 distinct types** ranked by refactoring impact. Each type determines which conditional modules are selected and which quality standards apply.

**Classification Hierarchy:**
- **Critical Impact (Rank 1-5):** Entry points, state management, network layers
- **High Impact (Rank 6-10):** Data models, persistence, routing
- **Medium Impact (Rank 11-16):** UI patterns, permissions, logging
- **Low Impact (Rank 17-20):** Theming, build tools, testing utilities

---

## Critical Impact Element Types (Rank 1-5)

### 1. Top-Level Widgets / Pages
**Rank:** 1 (Critical Impact)

**Description:**
Entry components that orchestrate entire workflows, serve as route targets, and coordinate multiple child components. These are the top of the component hierarchy.

**Detection Patterns:**
- **Filename:** `*Page.tsx`, `*Dashboard.tsx`, `*Widget.tsx`, `*View.tsx`
- **Path:** `pages/`, `views/`, `app/`, `routes/`
- **Code Patterns:**
  - Imports 5+ child components
  - Route definitions (`<Route path="..." component={...} />`)
  - Top-level layout wrappers

**Conditional Modules:**
- composition (props, children contracts)
- events (user interaction handling)
- accessibility (page-level a11y requirements)
- state (page-level state coordination)
- lifecycle (mount/unmount, navigation effects)

**Focus Areas:**
- Component orchestration and composition hierarchy
- Route integration and navigation contracts
- State coordination between child components
- Page-level accessibility (landmarks, focus management)
- Performance (bundle size, lazy loading)

**Validation Checklist:**
- [ ] Component hierarchy documented with all major children
- [ ] Route path and navigation contracts specified
- [ ] State ownership clear (which state lives in page vs children)
- [ ] Accessibility landmarks identified
- [ ] Bundle size and lazy loading strategy documented

**Example:**
```typescript
// File: pages/UserDashboard.tsx
export function UserDashboard() {
  return (
    <DashboardLayout>
      <UserProfile />
      <ActivityFeed />
      <RecommendationsWidget />
    </DashboardLayout>
  );
}
```

---

### 2. Stateful Containers
**Rank:** 2 (Critical Impact)

**Description:**
Components that manage and coordinate state, often wrapping multiple presentation components. These components own complex state logic and distribute data/callbacks to children.

**Detection Patterns:**
- **Filename:** `*Container.tsx`, `*Provider.tsx`, `*Controller.tsx`, `*Manager.tsx`
- **Code Patterns:**
  - Multiple `useState` or `useReducer` hooks (3+)
  - Passes callbacks to 3+ child components
  - Wraps presentation components with state logic

**Conditional Modules:**
- composition (wrapper patterns, children contracts)
- events (callback propagation, event coordination)
- state (ownership table, state transitions)
- lifecycle (initialization, cleanup)
- persistence (if state persists across sessions)

**Focus Areas:**
- State ownership rules (which component owns which state)
- Callback contracts (what callbacks do children receive)
- State initialization and hydration logic
- Failure recovery (what happens if child fails)
- Re-render optimization (memoization, selective updates)

**Validation Checklist:**
- [ ] State ownership table complete with all state variables
- [ ] Callback contracts documented with signatures
- [ ] State initialization logic explained
- [ ] Failure recovery paths defined for child failures
- [ ] Re-render optimization strategy documented

**Example:**
```typescript
// File: containers/UserFormContainer.tsx
export function UserFormContainer() {
  const [formData, setFormData] = useState<FormData>({});
  const [errors, setErrors] = useState<Errors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFieldChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <UserForm
      data={formData}
      errors={errors}
      onFieldChange={handleFieldChange}
      onSubmit={handleSubmit}
    />
  );
}
```

---

### 3. Global State Layer
**Rank:** 3 (Critical Impact)

**Description:**
Application-wide state management systems (Redux stores, Zustand stores, React Context providers). These define the source of truth for shared application state.

**Detection Patterns:**
- **Filename:** `*store.ts`, `*Context.tsx`, `*Provider.tsx`, `*slice.ts`
- **Path:** `store/`, `context/`, `state/`
- **Code Patterns:**
  - `createStore`, `createSlice`, `createContext`
  - Global state initialization
  - Action creators and reducers

**Conditional Modules:**
- state (ownership, source of truth, state shape)
- persistence (localStorage, sessionStorage integration)

**Focus Areas:**
- State shape and type definitions
- Action/mutation contracts
- Selector patterns and memoization
- Persistence strategy (what persists, when, how)
- State hydration and initialization
- Migration strategy for state schema changes

**Validation Checklist:**
- [ ] Complete state shape documented with TypeScript types
- [ ] All actions/mutations cataloged with payloads
- [ ] Persistence strategy specified (keys, timing, fallbacks)
- [ ] State hydration logic explained
- [ ] Migration strategy for breaking state changes

**Example:**
```typescript
// File: store/authStore.ts
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  login: (user, token) => set({ user, token }),
  logout: () => set({ user: null, token: null }),
}));
```

---

### 4. Custom Hooks
**Rank:** 4 (Critical Impact)

**Description:**
Reusable React hooks that encapsulate stateful logic and side effects. These hooks are consumed by multiple components and define reusable behavior contracts.

**Detection Patterns:**
- **Filename:** `use*.ts`, `use*.tsx`
- **Path:** `hooks/`, `composables/`
- **Code Patterns:**
  - Function name starts with `use` (React convention)
  - Contains `useState`, `useEffect`, `useRef`, etc.
  - Returns values/callbacks for consumer components

**Conditional Modules:**
- signature (parameters, return value, usage contract)
- side_effects (useEffect dependencies, cleanup)
- lifecycle (when hook runs, re-run triggers)

**Focus Areas:**
- Hook signature (parameters, return value)
- Side effect contracts (what effects run, when, why)
- Dependency array correctness
- Cleanup logic (prevent memory leaks)
- Common usage patterns and pitfalls

**Validation Checklist:**
- [ ] Hook signature fully typed (parameters + return)
- [ ] All side effects documented with dependencies
- [ ] Cleanup logic explained (if applicable)
- [ ] Usage examples provided (1-2 common cases)
- [ ] Common pitfalls documented (stale closures, infinite loops)

**Example:**
```typescript
// File: hooks/useLocalStorage.ts
export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    const item = window.localStorage.getItem(key);
    return item ? JSON.parse(item) : initialValue;
  });

  const setValue = (value: T) => {
    setStoredValue(value);
    window.localStorage.setItem(key, JSON.stringify(value));
  };

  return [storedValue, setValue];
}
```

---

### 5. API Client Layer
**Rank:** 5 (Critical Impact)

**Description:**
HTTP clients and API interaction modules that define network contracts with backend services. These modules abstract network calls and handle request/response transformations.

**Detection Patterns:**
- **Filename:** `*client.ts`, `*api.ts`, `*sdk.ts`, `*service.ts`
- **Path:** `api/`, `services/`, `client/`
- **Code Patterns:**
  - `fetch`, `axios`, `http` imports
  - Base URL configuration
  - Request interceptors and transformations

**Conditional Modules:**
- endpoints (endpoint catalog, request/response contracts)
- auth (authentication mechanisms, token handling)
- retry (retry strategies, exponential backoff)
- errors (error handling, failure recovery)

**Focus Areas:**
- Endpoint catalog (all API endpoints with contracts)
- Request/response type definitions
- Authentication and authorization
- Retry and timeout strategies
- Error handling and user-facing error messages

**Validation Checklist:**
- [ ] All endpoints cataloged with method, path, payload, response
- [ ] Auth mechanism documented (tokens, headers, refresh logic)
- [ ] Retry strategy specified (attempts, backoff, conditions)
- [ ] Error handling complete (network errors, 4xx, 5xx responses)
- [ ] Timeout configuration documented

**Example:**
```typescript
// File: api/userClient.ts
export class UserClient {
  async getUser(userId: string): Promise<User> {
    const response = await fetch(`/api/users/${userId}`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    if (!response.ok) throw new ApiError(response.status);
    return response.json();
  }
}
```

---

## High Impact Element Types (Rank 6-10)

### 6. Data Models & Schemas
**Rank:** 6 (High Impact)

**Description:**
Type definitions, validators, and data schemas that define application data contracts. These files establish type safety and validation rules across the codebase.

**Detection Patterns:**
- **Filename:** `*types.ts`, `*schema.ts`, `*models.ts`, `*validator.ts`
- **Path:** `types/`, `models/`, `schemas/`
- **Code Patterns:**
  - TypeScript `type` and `interface` definitions
  - Zod, Yup, Joi schema definitions
  - Validation functions

**Conditional Modules:**
- (minimal - mostly universal modules apply)

**Focus Areas:**
- Complete type catalog with documentation
- Validation rules and constraints
- Default values and optional fields
- Type evolution strategy (breaking changes)
- Shared vs feature-specific types

**Validation Checklist:**
- [ ] All types documented with field descriptions
- [ ] Validation rules specified (min/max, patterns, custom)
- [ ] Default values documented
- [ ] Breaking change migration strategy defined
- [ ] Dependencies between types mapped

---

### 7. Persistence Subsystem
**Rank:** 7 (High Impact)

**Description:**
Modules handling data persistence (localStorage, sessionStorage, indexedDB, cache). These define what data persists, where, and how.

**Detection Patterns:**
- **Filename:** `*storage.ts`, `*cache.ts`, `*persistence.ts`, `*db.ts`
- **Code Patterns:**
  - `localStorage`, `sessionStorage`, `indexedDB` API calls
  - Cache initialization and management
  - Storage key definitions

**Conditional Modules:**
- persistence (storage keys catalog, hydration strategy)
- errors (storage quota errors, corruption recovery)

**Focus Areas:**
- Storage keys catalog (ALL keys used)
- Data shape for each persisted key
- Hydration logic (when data loads from storage)
- Migration strategy for storage schema changes
- Storage quota handling and cleanup

**Validation Checklist:**
- [ ] Complete storage keys catalog with data shapes
- [ ] Hydration logic documented (timing, fallbacks)
- [ ] Migration strategy for schema changes
- [ ] Quota exceeded handling specified
- [ ] Cleanup/expiration logic documented

---

### 8. Eventing / Messaging
**Rank:** 8 (High Impact)

**Description:**
Event bus systems and cross-component messaging layers. These define how unrelated components communicate without direct coupling.

**Detection Patterns:**
- **Filename:** `*eventBus.ts`, `*messageHub.ts`, `*events.ts`, `*pubsub.ts`
- **Code Patterns:**
  - Event emitter patterns
  - Subscribe/publish methods
  - Event type registries

**Conditional Modules:**
- events (event catalog, payload contracts, side effects)
- errors (event delivery failures, subscriber errors)

**Focus Areas:**
- Event catalog (all event types)
- Event payload contracts (TypeScript types)
- Subscriber contracts (what happens on event)
- Event ordering guarantees (or lack thereof)
- Error handling for subscriber failures

**Validation Checklist:**
- [ ] Event catalog complete with all event types
- [ ] Payload contracts typed for each event
- [ ] Subscriber behavior documented
- [ ] Event ordering guarantees specified
- [ ] Subscriber error handling defined

---

### 9. Routing & Navigation
**Rank:** 9 (High Impact)

**Description:**
Router configuration defining application navigation structure. These files map URLs to components and define navigation flow.

**Detection Patterns:**
- **Filename:** `*router.ts`, `*routes.ts`, `*navigation.ts`
- **Path:** `routes/`, `router/`
- **Code Patterns:**
  - React Router, Vue Router, Next.js routing
  - Route definitions with paths and components
  - Navigation guards and redirects

**Conditional Modules:**
- state (navigation state, query params)
- lifecycle (route enter/leave hooks)

**Focus Areas:**
- Route catalog (all paths mapped to components)
- Navigation guards (auth, permissions)
- Query parameter contracts
- Nested routing structure
- Redirect logic and fallbacks

**Validation Checklist:**
- [ ] Route catalog complete with all paths
- [ ] Navigation guards documented (when they run, what they check)
- [ ] Query parameter contracts typed
- [ ] Nested route structure mapped
- [ ] 404 and redirect handling specified

---

### 10. File/Tree Primitives
**Rank:** 10 (High Impact)

**Description:**
Tree data structures and path utilities for file system or hierarchy representations. These define foundational data structures for tree-based features.

**Detection Patterns:**
- **Filename:** `*Tree.ts`, `*Node.ts`, `*PathUtils.ts`, `*Hierarchy.ts`
- **Code Patterns:**
  - Tree node type definitions
  - Tree traversal algorithms
  - Path manipulation utilities

**Conditional Modules:**
- (minimal - mostly universal modules)

**Focus Areas:**
- Node type definitions (properties, children)
- Tree traversal algorithms (DFS, BFS, iterators)
- Path utilities (join, resolve, normalize)
- Immutability contracts (mutate vs return new tree)
- Performance characteristics (O(n) operations)

**Validation Checklist:**
- [ ] Node type fully documented with all properties
- [ ] Traversal algorithms explained with complexity
- [ ] Path utility functions cataloged
- [ ] Immutability contracts specified
- [ ] Performance characteristics documented

---

## Medium Impact Element Types (Rank 11-16)

### 11. Context Menus / Commands
**Rank:** 11 (Medium Impact)

**Description:**
Context menu systems and command registries. These define user-triggered actions and their behavior.

**Detection Patterns:**
- **Filename:** `*ContextMenu.tsx`, `*CommandRegistry.ts`, `*actions.ts`
- **Code Patterns:**
  - Menu item definitions
  - Command handler registrations
  - Keyboard shortcut mappings

**Conditional Modules:**
- events (menu item clicks, command execution)
- accessibility (keyboard shortcuts, screen reader support)

**Focus Areas:**
- Command catalog (all available commands)
- Keyboard shortcut mappings
- Conditional visibility (when menus/commands show)
- Permission gating (who can execute commands)
- Undo/redo support

**Validation Checklist:**
- [ ] Command catalog complete with all commands
- [ ] Keyboard shortcuts documented
- [ ] Conditional visibility rules specified
- [ ] Permission requirements defined
- [ ] Undo/redo behavior documented (if applicable)

---

### 12. Permission & AuthZ
**Rank:** 12 (Medium Impact)

**Description:**
Authorization and permission management systems. These define who can do what in the application.

**Detection Patterns:**
- **Filename:** `*permissions.ts`, `*authz.ts`, `*rbac.ts`, `*acl.ts`
- **Code Patterns:**
  - Permission check functions
  - Role definitions
  - Access control lists

**Conditional Modules:**
- auth (permission evaluation logic)
- errors (permission denied handling)

**Focus Areas:**
- Permission catalog (all permissions)
- Role definitions and inheritance
- Permission evaluation logic
- Default permissions (logged out, logged in)
- Permission denial behavior

**Validation Checklist:**
- [ ] Permission catalog complete
- [ ] Role definitions documented
- [ ] Permission evaluation logic explained
- [ ] Default permissions specified
- [ ] Denial behavior defined (redirects, error messages)

---

### 13. Error Handling
**Rank:** 13 (Medium Impact)

**Description:**
Error boundaries and centralized error handling. These catch and recover from errors application-wide.

**Detection Patterns:**
- **Filename:** `*ErrorBoundary.tsx`, `*errorHandler.ts`
- **Code Patterns:**
  - `componentDidCatch`, `getDerivedStateFromError`
  - Global error handler registrations
  - Error logging and reporting

**Conditional Modules:**
- errors (error types, recovery strategies)
- lifecycle (error boundary lifecycle)

**Focus Areas:**
- Error types catalog (what errors are caught)
- Recovery strategies (retry, fallback UI, reload)
- Error logging and reporting
- User-facing error messages
- Development vs production behavior

**Validation Checklist:**
- [ ] Error types cataloged
- [ ] Recovery strategies documented per error type
- [ ] Logging/reporting destinations specified
- [ ] User-facing messages defined
- [ ] Dev vs prod differences explained

---

### 14. Logging / Telemetry
**Rank:** 14 (Medium Impact)

**Description:**
Analytics and telemetry systems for tracking user behavior and system events.

**Detection Patterns:**
- **Filename:** `*analytics.ts`, `*telemetry.ts`, `*logger.ts`, `*tracking.ts`
- **Code Patterns:**
  - Analytics SDK initialization
  - Event tracking calls
  - User property setters

**Conditional Modules:**
- events (tracked events catalog)

**Focus Areas:**
- Tracked events catalog (all tracked events)
- Event properties and dimensions
- User identification and properties
- Privacy compliance (PII handling, consent)
- Sampling and rate limiting

**Validation Checklist:**
- [ ] Tracked events catalog complete
- [ ] Event properties documented
- [ ] User identification logic explained
- [ ] PII handling documented
- [ ] Sampling strategy specified

---

### 15. Performance-Critical UI
**Rank:** 15 (Medium Impact)

**Description:**
High-performance UI components requiring optimization (virtualization, memoization, lazy loading).

**Detection Patterns:**
- **Filename:** `*VirtualList.tsx`, `*LazyGrid.tsx`, `*OptimizedTable.tsx`
- **Code Patterns:**
  - `React.memo`, `useMemo`, `useCallback`
  - Virtualization libraries (react-window, react-virtualized)
  - Lazy loading and code splitting

**Conditional Modules:**
- composition (render optimization patterns)
- lifecycle (mount/update performance)

**Focus Areas:**
- Performance targets (FPS, render time)
- Optimization techniques used
- Profiling results and bottlenecks
- Trade-offs (memory vs speed)
- Edge cases that break optimization

**Validation Checklist:**
- [ ] Performance targets specified
- [ ] Optimization techniques documented
- [ ] Profiling results included
- [ ] Trade-offs explained
- [ ] Edge cases identified

---

### 16. Design System Components
**Rank:** 16 (Medium Impact)

**Description:**
Reusable UI components following design system guidelines. These define the visual language of the application.

**Detection Patterns:**
- **Filename:** `Button.tsx`, `Input.tsx`, `Modal.tsx`, `Card.tsx` (in design system path)
- **Path:** `components/`, `ui/`, `design-system/`
- **Code Patterns:**
  - Variant props (size, color, variant)
  - Style composition patterns
  - Theme integration

**Conditional Modules:**
- composition (props, variants, children)
- accessibility (ARIA attributes, keyboard support)
- events (user interaction handling)

**Focus Areas:**
- Variant catalog (all available variants)
- Accessibility compliance (WCAG level)
- Theme integration (how component uses theme)
- Composition patterns (how to combine components)
- Usage guidelines (do's and don'ts)

**Validation Checklist:**
- [ ] Variant catalog complete
- [ ] WCAG compliance level documented
- [ ] Theme integration explained
- [ ] Composition examples provided
- [ ] Usage guidelines included

---

## Low Impact Element Types (Rank 17-20)

### 17. Theming & Styling
**Rank:** 17 (Low Impact)

**Description:**
Theme configuration and global styling systems. These define the visual appearance across the application.

**Detection Patterns:**
- **Filename:** `*theme.ts`, `*styles.ts`, `*colors.ts`, `*tokens.ts`
- **Path:** `theme/`, `styles/`
- **Code Patterns:**
  - Theme object definitions
  - CSS-in-JS theme providers
  - Design token definitions

**Conditional Modules:**
- (minimal - mostly documentation)

**Focus Areas:**
- Theme structure (colors, typography, spacing)
- Design token catalog
- Dark mode support
- Theme switching mechanism
- Backward compatibility with theme changes

**Validation Checklist:**
- [ ] Theme structure documented
- [ ] Design tokens cataloged
- [ ] Dark mode strategy specified
- [ ] Theme switching logic explained
- [ ] Migration strategy for theme changes

---

### 18. Build Tooling
**Rank:** 18 (Low Impact)

**Description:**
Build scripts, bundler configurations, and developer tooling.

**Detection Patterns:**
- **Filename:** `webpack.config.js`, `vite.config.ts`, `tsconfig.json`, `build.ts`
- **Path:** `scripts/`, `config/`

**Conditional Modules:**
- (minimal - infrastructure documentation)

**Focus Areas:**
- Build pipeline stages
- Environment-specific configurations
- Plugin and loader catalog
- Performance optimizations (code splitting, tree shaking)
- Local development workflow

**Validation Checklist:**
- [ ] Build pipeline stages documented
- [ ] Environment configurations explained
- [ ] Plugins/loaders cataloged
- [ ] Performance optimizations specified
- [ ] Dev workflow documented

---

### 19. CI/CD Pipelines
**Rank:** 19 (Low Impact)

**Description:**
CI/CD configuration defining automated testing and deployment workflows.

**Detection Patterns:**
- **Filename:** `.github/workflows/*.yml`, `Jenkinsfile`, `gitlab-ci.yml`
- **Path:** `.github/`, `.gitlab/`, `ci/`

**Conditional Modules:**
- (minimal - infrastructure documentation)

**Focus Areas:**
- Pipeline stages (build, test, deploy)
- Environment promotion (dev → staging → prod)
- Secret management
- Deployment triggers and gates
- Rollback procedures

**Validation Checklist:**
- [ ] Pipeline stages documented
- [ ] Environment promotion explained
- [ ] Secret management specified
- [ ] Deployment triggers defined
- [ ] Rollback procedure documented

---

### 20. Testing Harness
**Rank:** 20 (Low Impact)

**Description:**
Test utilities, mocks, fixtures, and testing infrastructure.

**Detection Patterns:**
- **Filename:** `*testUtils.ts`, `*mocks.ts`, `*fixtures.ts`, `setupTests.ts`
- **Path:** `test/`, `__mocks__/`, `__fixtures__/`

**Conditional Modules:**
- (minimal - testing documentation)

**Focus Areas:**
- Test utility catalog (helpers, matchers)
- Mock catalog (API mocks, component mocks)
- Fixture data structure
- Setup and teardown logic
- Custom test matchers

**Validation Checklist:**
- [ ] Test utilities cataloged
- [ ] Mocks documented with contracts
- [ ] Fixture data structure explained
- [ ] Setup/teardown logic documented
- [ ] Custom matchers defined

---

## Detection Algorithm

### 3-Stage Detection Process

```
Stage 1: Filename & Path Heuristics (85-90% confidence)
├─ Check filename patterns (useXxx → custom-hook)
├─ Check path patterns (pages/ → top-level-widget)
└─ Quick match against 20 element types

Stage 2: Code Analysis (95%+ confidence)
├─ Parse imports and exports
├─ Detect React hooks, state management patterns
├─ Analyze JSX structure and prop usage
└─ Refine classification from Stage 1

Stage 3: Manual Override (100% confidence)
├─ User explicitly specifies element type
└─ Override auto-detection
```

### Detection Confidence Levels

| Confidence | Stage | Action |
|------------|-------|--------|
| 90-100% | Stage 1 match + code analysis confirms | Proceed with detected type |
| 70-89% | Stage 1 match but code analysis ambiguous | Suggest type, allow override |
| 50-69% | Weak Stage 1 match, no code confirmation | Prompt user for manual classification |
| <50% | No clear match | Require manual specification |

---

## Usage Examples

### Example 1: Detecting Top-Level Widget
```typescript
// File: pages/UserDashboard.tsx
// Detection: Filename match (*Dashboard.tsx) + path (pages/)
// Confidence: 95%
// Type: top-level-widget
// Modules: composition, events, accessibility, state, lifecycle
```

### Example 2: Detecting Custom Hook
```typescript
// File: hooks/useLocalStorage.ts
// Detection: Filename match (use*.ts) + code analysis (useState detected)
// Confidence: 98%
// Type: custom-hook
// Modules: signature, side_effects, lifecycle
```

### Example 3: Detecting API Client
```typescript
// File: services/userClient.ts
// Detection: Filename match (*client.ts) + code analysis (fetch calls detected)
// Confidence: 92%
// Type: api-client
// Modules: endpoints, auth, retry, errors
```

---

## Extending the Catalog

### Adding New Element Types

```python
# In resource_sheet/mapping/element-type-mapping.json

{
  "element_types": {
    "new-element-type": {
      "rank": 21,
      "impact": "medium",
      "detection_patterns": {
        "filename": ["*NewPattern.tsx"],
        "path": ["new-pattern/"],
        "code_patterns": ["specific code signature"]
      },
      "conditional_modules": ["module1", "module2"],
      "focus_areas": ["Area 1", "Area 2"],
      "validation_checklist": [
        "Checklist item 1",
        "Checklist item 2"
      ]
    }
  }
}
```

### Customizing Detection Patterns

- **Filename patterns:** Use glob patterns (`*Page.tsx`, `use*.ts`)
- **Path patterns:** Match directory structure (`pages/`, `hooks/`)
- **Code patterns:** Use AST analysis (detect `useState`, `fetch`, etc.)

---

## Next Steps

- **User Guide:** [RESOURCE-SHEET-USER-GUIDE.md](../user/RESOURCE-SHEET-USER-GUIDE.md)
- **Module Reference:** [MODULE-REFERENCE.md](MODULE-REFERENCE.md)
- **Quick Reference:** [QUICK-REFERENCE-CARD.md](../user/QUICK-REFERENCE-CARD.md)
