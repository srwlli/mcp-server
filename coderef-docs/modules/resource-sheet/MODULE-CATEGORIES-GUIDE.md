# Resource Sheet Module Categories - Guide for Dummies

**Created:** 2026-01-02
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001
**Purpose:** Explain module categories in plain English with real examples

---

## What This Guide Is

This guide explains **where different types of code belong** in the resource sheet documentation system.

Think of it like organizing a kitchen:
- 🍴 **Utensils** go in one drawer
- 🍽️ **Plates** go in a cabinet
- 🥘 **Pots** go in another cabinet

Same idea - different code types go in different categories.

---

## The 8 Categories (Kitchen Analogy)

### 1. `state/` - The Pantry (Stores Ingredients)
**What:** Code that stores and manages data
**Examples:** Shopping list, recipe ingredients, leftovers tracking

### 2. `tools/` - The Utensil Drawer (Things You Use)
**What:** Helper tools and utilities
**Examples:** Can opener, measuring cups, knife sharpener

### 3. `generators/` - The Recipe Box (Templates)
**What:** Templates and code that creates other code
**Examples:** Recipe cards, meal templates, cooking instructions

### 4. `ui/` - The Dining Room (What You See)
**What:** Visual components users interact with
**Examples:** Plates, napkins, table settings

### 5. `services/` - The Delivery Service (External Communication)
**What:** Code that talks to outside systems (APIs, databases)
**Examples:** Food delivery, grocery delivery, catering service

### 6. `data/` - The Menu (Data Definitions)
**What:** Defines what data looks like
**Examples:** Menu with prices, nutrition labels, ingredient lists

### 7. `infrastructure/` - The Kitchen Equipment (Behind the Scenes)
**What:** Build, deploy, configuration
**Examples:** Oven, dishwasher, plumbing

### 8. `testing/` - The Taste Testers (Quality Control)
**What:** Code that tests other code
**Examples:** Food critics, quality inspectors

---

## Category Breakdown (With Real Code Examples)

### Category 1: `state/` - Data Storage & Management

**Think:** "Where does my data live?"

#### `state/hooks/` - React Hooks
**What it is:** Functions that start with `use` and manage React state
**Real example:**
```typescript
// useShoppingCart.ts
function useShoppingCart() {
  const [items, setItems] = useState([]);

  const addItem = (item) => {
    setItems([...items, item]);
  };

  return { items, addItem };
}
```
**Ask yourself:** Does it start with `use`? Does it return state? → Yes = `state/hooks/`

---

#### `state/stores/` - Global State (Redux, Zustand)
**What it is:** App-wide data that many components need
**Real example:**
```typescript
// userStore.ts
const useUserStore = create((set) => ({
  currentUser: null,
  login: (user) => set({ currentUser: user }),
  logout: () => set({ currentUser: null })
}));
```
**Ask yourself:** Does the whole app need this data? → Yes = `state/stores/`

---

#### `state/context/` - React Context
**What it is:** Data passed down to child components without props
**Real example:**
```typescript
// ThemeContext.tsx
const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```
**Ask yourself:** Does it use `createContext`? → Yes = `state/context/`

---

### Category 2: `tools/` - Utilities & Helpers

**Think:** "Tools I use to get work done"

#### `tools/cli-commands/` - Command Line Tools
**What it is:** Programs you run in the terminal with flags and options
**Real example:**
```javascript
// coderef-scan.js
#!/usr/bin/env node
program
  .command('scan <path>')
  .option('-d, --depth <number>', 'scan depth')
  .action((path, options) => {
    console.log(`Scanning ${path} at depth ${options.depth}`);
  });
```
**Ask yourself:** Do I run this in the terminal? Does it have flags like `-d` or `--help`? → Yes = `tools/cli-commands/`

---

#### `tools/scripts/` - Automation Scripts
**What it is:** Scripts you run to automate tasks (not interactive)
**Real example:**
```bash
# cleanup.sh
#!/bin/bash
echo "Cleaning up old files..."
find . -name "*.log" -delete
find . -name "*.tmp" -delete
echo "Done!"
```
**Ask yourself:** Is it a `.sh` or `.bash` file? Does it just run without asking questions? → Yes = `tools/scripts/`

---

#### `tools/utilities/` - Helper Functions
**What it is:** Simple functions you reuse everywhere
**Real example:**
```typescript
// formatDate.ts
export function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US');
}

// deepClone.ts
export function deepClone<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj));
}
```
**Ask yourself:** Is it a simple function I use in multiple places? No React, no CLI? → Yes = `tools/utilities/`

---

### Category 3: `generators/` - Code that Creates Code

**Think:** "Templates and tools that create new files"

#### `generators/scaffolding/` - File/Project Generators
**What it is:** Code that creates new files from templates
**Real example:**
```javascript
// create-component.js
function createComponent(name) {
  const componentCode = `
    import React from 'react';

    export function ${name}() {
      return <div>${name}</div>;
    }
  `;

  fs.writeFileSync(`src/components/${name}.tsx`, componentCode);
  console.log(`Created component: ${name}`);
}
```
**Ask yourself:** Does it create new files? Does it use templates? → Yes = `generators/scaffolding/`

---

#### `generators/templates/` - Template Files
**What it is:** Template files with placeholders like `{{name}}`
**Real example:**
```typescript
// component.template.tsx
import React from 'react';

interface {{name}}Props {
  // Add props here
}

export function {{name}}(props: {{name}}Props) {
  return <div>{{name}} Component</div>;
}
```
**Ask yourself:** Is this a template file with `{{placeholders}}`? → Yes = `generators/templates/`

---

### Category 4: `ui/` - Visual Components

**Think:** "Things users see and click on"

#### `ui/components/` - Simple UI Components
**What it is:** Reusable UI building blocks (buttons, inputs, cards)
**Real example:**
```typescript
// Button.tsx
interface ButtonProps {
  label: string;
  onClick: () => void;
}

export function Button({ label, onClick }: ButtonProps) {
  return (
    <button onClick={onClick} className="btn">
      {label}
    </button>
  );
}
```
**Ask yourself:** Is it a simple UI element? Returns JSX? → Yes = `ui/components/`

---

#### `ui/pages/` - Full Page Components
**What it is:** Complete pages in your app (routes)
**Real example:**
```typescript
// Dashboard.tsx
export function Dashboard() {
  return (
    <div className="dashboard">
      <Header />
      <Sidebar />
      <MainContent />
      <Footer />
    </div>
  );
}
```
**Ask yourself:** Is it a full page? Connected to a route? → Yes = `ui/pages/`

---

#### `ui/widgets/` - Complex Multi-Part UI
**What it is:** Complex UI with multiple parts and internal state
**Real example:**
```typescript
// FileExplorer.tsx
export function FileExplorer() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [expandedFolders, setExpandedFolders] = useState([]);

  return (
    <div className="file-explorer">
      <ProjectSelector />
      <FileTree
        expanded={expandedFolders}
        onSelect={setSelectedFile}
      />
      <FileViewer file={selectedFile} />
    </div>
  );
}
```
**Ask yourself:** Is it complex? Has multiple parts? Has internal state? → Yes = `ui/widgets/`

---

### Category 5: `services/` - External Communication

**Think:** "Code that talks to the outside world"

#### `services/api-endpoints/` - HTTP/API Clients
**What it is:** Code that makes network requests to APIs
**Real example:**
```typescript
// UserService.ts
class UserService {
  async getUser(id: string) {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
  }

  async updateUser(id: string, data: any) {
    const response = await fetch(`/api/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
    return response.json();
  }
}
```
**Ask yourself:** Does it use `fetch` or `axios`? Makes HTTP requests? → Yes = `services/api-endpoints/`

---

#### `services/auth/` - Authentication Services
**What it is:** Code that handles login/logout/tokens
**Real example:**
```typescript
// AuthService.ts
class AuthService {
  async login(email: string, password: string) {
    const response = await fetch('/api/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    const { token } = await response.json();
    localStorage.setItem('token', token);
    return token;
  }

  logout() {
    localStorage.removeItem('token');
  }
}
```
**Ask yourself:** Does it handle login/logout? Manage tokens? → Yes = `services/auth/`

---

#### `services/data-access/` - Database/Storage Access
**What it is:** Code that reads/writes to databases or storage
**Real example:**
```typescript
// DatabaseService.ts
class DatabaseService {
  async query(sql: string) {
    const connection = await this.getConnection();
    return connection.execute(sql);
  }

  async save(table: string, data: any) {
    return this.query(`INSERT INTO ${table} VALUES (...)`, data);
  }
}
```
**Ask yourself:** Does it talk to a database? Uses SQL or ORM? → Yes = `services/data-access/`

---

### Category 6: `data/` - Data Definitions

**Think:** "Blueprints for what data looks like"

#### `data/models/` - TypeScript Interfaces/Types
**What it is:** Defines the shape of your data
**Real example:**
```typescript
// User.ts
export interface User {
  id: string;
  email: string;
  name: string;
  age: number;
  createdAt: Date;
}

// Project.ts
export interface Project {
  id: string;
  name: string;
  owner: User;
  tasks: Task[];
}
```
**Ask yourself:** Is it a TypeScript `interface` or `type`? Defines data shape? → Yes = `data/models/`

---

#### `data/schemas/` - Validation Schemas
**What it is:** Runtime validation (Zod, Yup, Joi)
**Real example:**
```typescript
// userSchema.ts
import { z } from 'zod';

export const userSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2),
  age: z.number().min(0).max(120)
});
```
**Ask yourself:** Does it use Zod/Yup/Joi? Validates data at runtime? → Yes = `data/schemas/`

---

### Category 7: `infrastructure/` - Behind the Scenes

**Think:** "Build, deploy, configure"

#### `infrastructure/build-scripts/` - Build Tools
**What it is:** Scripts that bundle/compile/build your app
**Real example:**
```javascript
// build.js
const esbuild = require('esbuild');

esbuild.build({
  entryPoints: ['src/index.ts'],
  bundle: true,
  minify: true,
  outfile: 'dist/bundle.js'
});
```
**Ask yourself:** Does it build/bundle/compile? Uses esbuild/webpack/rollup? → Yes = `infrastructure/build-scripts/`

---

#### `infrastructure/ci-cd/` - CI/CD Pipelines
**What it is:** GitHub Actions, deployment configs
**Real example:**
```yaml
# .github/workflows/test.yml
name: Run Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm test
```
**Ask yourself:** Is it a GitHub Actions workflow? Deployment config? → Yes = `infrastructure/ci-cd/`

---

### Category 8: `testing/` - Quality Control

**Think:** "Code that tests other code"

#### `testing/test-helpers/` - Test Utilities
**What it is:** Helper functions for tests
**Real example:**
```typescript
// renderWithProviders.tsx
import { render } from '@testing-library/react';

export function renderWithProviders(component: React.ReactElement) {
  return render(
    <Provider store={testStore}>
      <Router>
        {component}
      </Router>
    </Provider>
  );
}
```
**Ask yourself:** Is it a helper function used in tests? → Yes = `testing/test-helpers/`

---

#### `testing/mocks/` - Mock Factories
**What it is:** Functions that create fake data for tests
**Real example:**
```typescript
// mockUser.ts
export function createMockUser(overrides = {}) {
  return {
    id: '123',
    email: 'test@example.com',
    name: 'Test User',
    ...overrides
  };
}
```
**Ask yourself:** Does it create fake/mock data for tests? → Yes = `testing/mocks/`

---

## Quick Decision Tree

### Step 1: What does it DO?

```
Does it store/manage data?
  └─ YES → Go to Category 1 (state/)
  └─ NO → Continue

Does it help you do tasks?
  └─ YES → Go to Category 2 (tools/)
  └─ NO → Continue

Does it create new files/code?
  └─ YES → Go to Category 3 (generators/)
  └─ NO → Continue

Does it show UI to users?
  └─ YES → Go to Category 4 (ui/)
  └─ NO → Continue

Does it talk to external systems?
  └─ YES → Go to Category 5 (services/)
  └─ NO → Continue

Does it define data shapes?
  └─ YES → Go to Category 6 (data/)
  └─ NO → Continue

Does it build/deploy/configure?
  └─ YES → Go to Category 7 (infrastructure/)
  └─ NO → Continue

Does it test other code?
  └─ YES → Go to Category 8 (testing/)
```

---

## Step 2: Subcategory Details

### If Category 1 (state/):
```
Does it start with "use"?
  └─ YES → state/hooks/
  └─ NO → Continue

Does it use Redux/Zustand/MobX?
  └─ YES → state/stores/
  └─ NO → Continue

Does it use createContext?
  └─ YES → state/context/
```

### If Category 2 (tools/):
```
Does it have CLI flags (--help, -v)?
  └─ YES → tools/cli-commands/
  └─ NO → Continue

Is it a .sh or .bash file?
  └─ YES → tools/scripts/
  └─ NO → Continue

Is it a simple helper function?
  └─ YES → tools/utilities/
```

### If Category 3 (generators/):
```
Does it CREATE files?
  └─ YES → generators/scaffolding/
  └─ NO → Continue

Is it a TEMPLATE file?
  └─ YES → generators/templates/
```

### If Category 4 (ui/):
```
Is it a simple button/input/card?
  └─ YES → ui/components/
  └─ NO → Continue

Is it a full page?
  └─ YES → ui/pages/
  └─ NO → Continue

Is it complex with multiple parts?
  └─ YES → ui/widgets/
```

### If Category 5 (services/):
```
Does it handle login/logout?
  └─ YES → services/auth/
  └─ NO → Continue

Does it query a database?
  └─ YES → services/data-access/
  └─ NO → Continue

Does it make HTTP requests?
  └─ YES → services/api-endpoints/
```

### If Category 6 (data/):
```
Is it a TypeScript interface/type?
  └─ YES → data/models/
  └─ NO → Continue

Does it use Zod/Yup/Joi?
  └─ YES → data/schemas/
```

### If Category 7 (infrastructure/):
```
Does it build/bundle code?
  └─ YES → infrastructure/build-scripts/
  └─ NO → Continue

Is it GitHub Actions/.yml?
  └─ YES → infrastructure/ci-cd/
```

### If Category 8 (testing/):
```
Is it a test helper function?
  └─ YES → testing/test-helpers/
  └─ NO → Continue

Does it create mock data?
  └─ YES → testing/mocks/
```

---

## Real-World Examples (You Can Copy)

### Example 1: useAuth Hook
```typescript
// File: useAuth.ts
function useAuth() {
  const [user, setUser] = useState(null);
  return { user, setUser };
}
```
**Decision:**
- Starts with `use`? ✅ YES
- Uses React hooks? ✅ YES
**Category:** `state/hooks/`

---

### Example 2: coderef-scan CLI
```javascript
// File: coderef-scan.js
program
  .command('scan <path>')
  .option('-d, --depth <number>')
  .action((path) => { /* ... */ });
```
**Decision:**
- Has CLI flags? ✅ YES
**Category:** `tools/cli-commands/`

---

### Example 3: Button Component
```typescript
// File: Button.tsx
export function Button({ label }: ButtonProps) {
  return <button>{label}</button>;
}
```
**Decision:**
- Returns JSX? ✅ YES
- Simple UI element? ✅ YES
**Category:** `ui/components/`

---

### Example 4: AuthService
```typescript
// File: AuthService.ts
class AuthService {
  async login(email, password) {
    return fetch('/api/login', { /* ... */ });
  }
}
```
**Decision:**
- Handles login? ✅ YES
**Category:** `services/auth/`

---

### Example 5: User Interface
```typescript
// File: User.ts
export interface User {
  id: string;
  name: string;
}
```
**Decision:**
- TypeScript interface? ✅ YES
**Category:** `data/models/`

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Confusing hooks and utilities
```typescript
// This is NOT a hook (no React, no state)
function formatDate(date) {
  return date.toLocaleDateString();
}
```
**Correct category:** `tools/utilities/` (NOT `state/hooks/`)

---

### ❌ Mistake 2: Confusing pages and components
```typescript
// This IS a page (full screen, routes to /dashboard)
export function Dashboard() {
  return <div>Full page layout</div>;
}
```
**Correct category:** `ui/pages/` (NOT `ui/components/`)

---

### ❌ Mistake 3: Confusing services and utilities
```typescript
// This IS a service (makes HTTP requests)
async function fetchUser(id) {
  return fetch(`/api/users/${id}`);
}
```
**Correct category:** `services/api-endpoints/` (NOT `tools/utilities/`)

---

## Summary Cheat Sheet

| Category | One-Sentence Description | Example File |
|----------|-------------------------|--------------|
| `state/hooks/` | React hooks that manage state | `useAuth.ts` |
| `state/stores/` | Global app state (Redux/Zustand) | `userStore.ts` |
| `state/context/` | React Context providers | `ThemeContext.tsx` |
| `tools/cli-commands/` | Command-line tools with flags | `coderef-scan.js` |
| `tools/scripts/` | Automation bash/shell scripts | `cleanup.sh` |
| `tools/utilities/` | Helper functions (no React/CLI) | `formatDate.ts` |
| `generators/scaffolding/` | Code that creates files | `create-component.js` |
| `generators/templates/` | Template files | `component.template.tsx` |
| `ui/components/` | Simple UI elements | `Button.tsx` |
| `ui/pages/` | Full page components | `Dashboard.tsx` |
| `ui/widgets/` | Complex multi-part UI | `FileExplorer.tsx` |
| `services/api-endpoints/` | HTTP/API clients | `UserService.ts` |
| `services/auth/` | Authentication logic | `AuthService.ts` |
| `services/data-access/` | Database queries | `DatabaseService.ts` |
| `data/models/` | TypeScript interfaces | `User.ts` |
| `data/schemas/` | Runtime validation (Zod) | `userSchema.ts` |
| `infrastructure/build-scripts/` | Build/bundle tools | `build.js` |
| `infrastructure/ci-cd/` | CI/CD configs | `test.yml` |
| `testing/test-helpers/` | Test utilities | `renderWithProviders.tsx` |
| `testing/mocks/` | Mock data factories | `mockUser.ts` |

---

## Next Steps

Now that you understand the categories, you can:

1. ✅ Review the plan with these categories in mind
2. ✅ Understand how modules will be organized
3. ✅ Proceed with implementation

**Remember:** When in doubt, use the decision tree! Start with "What does it DO?" and work your way down.

---

**Questions?** Review the real-world examples section - they show the most common cases you'll encounter.
