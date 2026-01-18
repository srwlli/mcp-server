# Phase 3 Handoff - Dynamic Dashboard & Ecosystem Workflows

**Session:** WO-CSV-ECOSYSTEM-SYNC-001
**Phase:** 3 - Dynamic Dashboard & Automated CSV Maintenance
**Lead Agents:** coderef-dashboard (Task 1), coderef-workflow (Task 2), coderef-dashboard (Task 3)
**Pattern:** Parallel execution (Task 1 and Task 2 independent, Task 3 after Task 1)
**Orchestrator Approval:** 2026-01-17

---

## Phase 2 Completion Summary

✅ **CSV Successfully Updated:**
- Resources: 306 → 346 (+40, +13%)
- Path accuracy: 100% (all global/local corrected)
- Timestamps: 100% complete (all from git log)
- Descriptions: 100% complete (no truncations)
- Validation: PASSING (100% data quality)

✅ **CSV is now single source of truth** - ready for dynamic integration

---

## Phase 3 Overview

**Goal:** Make CSV a living document that updates automatically

**3 Parallel/Sequential Tasks:**

1. **Dynamic Resources Page** (coderef-dashboard) - Reads CSV in real-time
2. **Automated CSV Maintenance** (coderef-workflow) - Workflows update CSV automatically
3. **Page Structure Standard** (coderef-dashboard) - Rollout CLAUDE.md + coderef/ to 6 pages

**Pattern:**
- Tasks 1 & 2: **Parallel** (independent codebases, no conflicts)
- Task 3: **After Task 1** (depends on resources page implementation)

---

## Task 1: Dynamic Resources Page (coderef-dashboard)

### Current State (Hardcoded)

**Problem:** Resources page uses hardcoded TypeScript constants, doesn't read CSV

**File:** `packages/dashboard/src/app/resources/page.tsx`

**Current Architecture:**
```typescript
// Hardcoded resource types
const resourceTypes = ['Tool', 'Command', 'Script', 'Tab', 'Output', 'Workflow'];

// Hardcoded data (NOT reading CSV)
// UI filters/displays based on TypeScript constants
```

**Issues:**
- CSV updates don't reflect in UI automatically
- New resource types (like Persona) not displayed
- Manual code changes needed for every CSV update

### Target State (Dynamic)

**Solution:** Read CSV file, parse, display dynamically

**Implementation Options:**

**Option A: Server-Side (Recommended)**
```typescript
// app/resources/page.tsx (Server Component)
import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export default async function ResourcesPage() {
  const csvPath = path.join(process.cwd(), 'packages/dashboard/src/app/resources/coderef/tools-and-commands.csv');
  const csvContent = fs.readFileSync(csvPath, 'utf-8');
  const resources = parse(csvContent, { columns: true });

  return <ResourcesUI resources={resources} />;
}
```

**Option B: API Route + Client**
```typescript
// app/api/resources/route.ts
export async function GET() {
  const csvPath = path.join(process.cwd(), 'packages/dashboard/src/app/resources/coderef/tools-and-commands.csv');
  const csvContent = fs.readFileSync(csvPath, 'utf-8');
  const resources = parse(csvContent, { columns: true });
  return Response.json(resources);
}

// app/resources/page.tsx (Client Component)
const { data: resources } = useSWR('/api/resources', fetcher);
```

**Option C: File Watching (Real-time)**
```typescript
// Use chokidar to watch CSV file for changes
// Revalidate page when CSV updated
// Enables real-time updates without page refresh
```

### Requirements

**Must Have:**
- ✅ Read CSV file dynamically (no hardcoded data)
- ✅ Display all 10 resource types (including new Persona type)
- ✅ Filter by Type, Server, Category, Status
- ✅ Search by Name, Description
- ✅ Show all 346 resources

**Should Have:**
- ✅ Real-time updates (file watching or polling)
- ✅ Performance optimization (pagination, virtualization)
- ✅ Error handling (CSV parse errors, file not found)

**Nice to Have:**
- Sort by Created, LastUpdated
- Export filtered results
- Resource detail view

### Deliverables

**Files to Update:**
1. `packages/dashboard/src/app/resources/page.tsx` - Dynamic CSV reading
2. `packages/dashboard/src/app/resources/coderef/CLAUDE.md` - Update architecture notes
3. `packages/dashboard/src/lib/csv-parser.ts` (new) - CSV parsing utilities
4. API route (if Option B chosen)

**Files to Create:**
5. `packages/dashboard/src/app/resources/coderef/Resources-Page-Implementation-RESOURCE-SHEET.md` - Document new architecture

**Testing:**
- Verify all 346 resources display correctly
- Test filtering by all fields
- Test search functionality
- Verify new resources added to CSV appear automatically

---

## Task 2: Automated CSV Maintenance (coderef-workflow)

### Current State (Manual)

**Problem:** Workflows don't update CSV when creating/modifying resources

**Workflows Affected:**
- `/create-workorder` - Should add workorder to CSV when created
- `/archive-feature` - Should update CSV status when archiving
- `/create-plan` - Could check CSV for existing resources
- `generate_foundation_docs` - Should add new docs to CSV
- `generate_resource_sheet` - Should add resource sheets to CSV

### Target State (Automated)

**Solution:** Integrate CSV update logic into all resource-creating workflows

**Implementation Pattern:**

```python
# In coderef-workflow tools

def create_workorder(workorder_id, feature_name, ...):
    # Existing workorder creation logic
    create_workorder_files(...)

    # NEW: Add to CSV
    csv_path = "~/Desktop/coderef-dashboard/packages/dashboard/src/app/resources/coderef/tools-and-commands.csv"
    add_csv_entry(
        type="Workflow",
        server="project-specific",
        category="Planning",
        name=workorder_id,
        description=f"Workorder: {feature_name}",
        status="active",
        path=workorder_path,
        created=datetime.now().isoformat()
    )

    return result
```

### Workflows to Update

**Priority 1: High-impact workflows**

1. **generate_foundation_docs**
   - When: Generates README, ARCHITECTURE, API docs
   - CSV Entry: Type=Output, Category=Documentation, Status=active
   - Add: After each doc generated

2. **generate_resource_sheet**
   - When: Creates new resource sheet
   - CSV Entry: Type=ResourceSheet, Server=documentation, Category=Component/Workflow/etc
   - Add: After resource sheet saved

3. **archive_feature**
   - When: Archives completed feature
   - CSV Update: Change Status from active → archived for all feature resources
   - Update: After moving files to coderef/archived/

**Priority 2: Medium-impact workflows**

4. **/create-workorder** (command)
   - When: User creates new workorder
   - CSV Entry: Type=Workorder, Status=active
   - Add: After workorder files created

5. **/create-plan** (command)
   - When: Agent creates implementation plan
   - CSV Entry: Type=Output, Name=plan.json, Status=active
   - Add: After plan.json saved

**Priority 3: Nice-to-have**

6. **validate_document** (if creates validation reports)
7. **audit_codebase** (if creates audit outputs)

### Helper Utilities Needed

**Create CSV management module:**

```python
# coderef-workflow/csv_manager.py

def add_csv_entry(type, server, category, name, description, status, path, created=None, last_updated=None):
    """Add new entry to CSV"""
    csv_path = get_csv_path()
    entry = {
        'Type': type,
        'Server': server,
        'Category': category,
        'Name': name,
        'Description': description,
        'Status': status,
        'Path': path,
        'Created': created or datetime.now().isoformat(),
        'LastUpdated': last_updated or datetime.now().isoformat()
    }
    append_to_csv(csv_path, entry)

def update_csv_status(resource_name, new_status):
    """Update status for existing resource"""
    # Read CSV, find matching entry, update Status, write back

def check_csv_exists(resource_name):
    """Check if resource already in CSV"""
    # Prevents duplicate entries
```

### Deliverables

**Files to Update:**
1. `coderef-workflow/tools.py` - Add CSV update calls to workflows
2. `coderef-workflow/csv_manager.py` (new) - CSV management utilities
3. `coderef-workflow/CLAUDE.md` - Document CSV maintenance patterns

**Files to Create:**
4. `coderef-workflow/coderef/CSV-Maintenance-Workflow-RESOURCE-SHEET.md` - Document automated patterns

**Testing:**
- Test generate_foundation_docs → verify docs added to CSV
- Test generate_resource_sheet → verify sheets added to CSV
- Test archive_feature → verify status updated in CSV
- Verify no duplicate entries created
- Verify CSV remains valid after automated updates

---

## Task 3: New Page Structure Standard (coderef-dashboard)

### Current State (Inconsistent)

**Problem:** Dashboard pages have inconsistent structure

**Example Current Structure:**
```
packages/dashboard/src/app/resources/
├── page.tsx
├── CLAUDE.md (some pages have it, others don't)
└── coderef/ (only resources page has this)
```

### Target State (Standardized)

**Solution:** Every page follows same structure

**New Standard:**
```
packages/dashboard/src/app/{page-name}/
├── page.tsx                                    (UI component)
├── CLAUDE.md                                   (AI context for this page)
└── coderef/
    ├── resource-sheet-index.md                 (catalog of all resource sheets for this page)
    ├── {page-name}-RESOURCE-SHEET.md          (main resource sheet)
    └── {component}-RESOURCE-SHEET.md          (component-specific sheets)
```

### Pages to Update (6 total)

**1. resources/** (already done, use as template)
```
✅ resources/
   ✅ page.tsx
   ✅ CLAUDE.md
   ✅ coderef/
      ✅ resource-sheet-index.md
      ✅ Resources-Page-RESOURCE-SHEET.md
      ✅ build-source-of-truth.py
      ✅ tools-and-commands.csv
```

**2. explorer/**
```
explorer/
├── page.tsx (exists)
├── CLAUDE.md (CREATE - AI context for Explorer page)
└── coderef/ (CREATE)
    ├── resource-sheet-index.md
    ├── Explorer-Page-RESOURCE-SHEET.md
    ├── FileTree-RESOURCE-SHEET.md
    ├── FileViewer-RESOURCE-SHEET.md
    └── ResizableSidebar-RESOURCE-SHEET.md (already exists, move here)
```

**3. workflows/**
```
workflows/
├── page.tsx (exists)
├── CLAUDE.md (CREATE)
└── coderef/ (CREATE)
    ├── resource-sheet-index.md
    └── Workflows-Page-RESOURCE-SHEET.md
```

**4. personas/**
```
personas/
├── page.tsx (exists)
├── CLAUDE.md (CREATE)
└── coderef/ (CREATE)
    ├── resource-sheet-index.md
    └── Personas-Page-RESOURCE-SHEET.md
```

**5. documentation/**
```
documentation/
├── page.tsx (exists)
├── CLAUDE.md (CREATE)
└── coderef/ (CREATE)
    ├── resource-sheet-index.md
    └── Documentation-Page-RESOURCE-SHEET.md
```

**6. testing/**
```
testing/
├── page.tsx (exists)
├── CLAUDE.md (CREATE)
└── coderef/ (CREATE)
    ├── resource-sheet-index.md
    └── Testing-Page-RESOURCE-SHEET.md
```

### CLAUDE.md Template

```markdown
# {Page Name} - AI Context

**Page:** {page-name}
**Purpose:** {1-2 sentence description}
**Status:** {Active/Under Development}

---

## Quick Summary

{3-5 sentences describing page purpose and key features}

---

## Key Components

- **{Component1}:** {description}
- **{Component2}:** {description}

---

## Resources

**Key Files:**
- **coderef/resource-sheet-index.md** = Catalog of all resource sheets
- **coderef/{page-name}-RESOURCE-SHEET.md** = Main resource sheet

**Related Resources:**
- {Link to related pages/components}

---

## Workflows

{Document key user workflows on this page}

---

## Technical Notes

{Important implementation details, gotchas, dependencies}
```

### Deliverables

**Files to Create (6 pages × 2-4 files = ~18 files):**
- 6 CLAUDE.md files
- 6 resource-sheet-index.md files
- 6+ page-specific resource sheets
- Move existing resource sheets to appropriate coderef/ folders

**Files to Update:**
- Update CSV with all new resource sheets created
- Update dashboard CLAUDE.md with new page structure standard

**Documentation:**
- Create PAGE-STRUCTURE-STANDARD.md (documents the new pattern)
- Add to CSV maintenance documentation

---

## Phase 3 Execution Strategy

### Parallel Execution (Optimal)

**Start Simultaneously:**
- **Task 1** (coderef-dashboard): Dynamic Resources page → coderef-dashboard agent working in `~/Desktop/coderef-dashboard`
- **Task 2** (coderef-workflow): CSV automation → coderef-workflow agent working in `~/.mcp-servers/coderef-workflow`

**No conflicts:** Different codebases, different files

**Sequential After Task 1:**
- **Task 3** (coderef-dashboard): Page structure standard → Same agent, after Task 1 done

### Alternative: Sequential Execution

If not running parallel agents:
1. Task 1 (Dynamic Resources page) - Most critical
2. Task 2 (CSV automation) - Enables living document
3. Task 3 (Page structure standard) - Quality/consistency

---

## Phase 3 Validation Checklist

**Task 1 Complete:**
- [ ] Resources page reads CSV file (not hardcoded)
- [ ] All 346 resources display correctly
- [ ] All 10 resource types visible
- [ ] Filter and search working
- [ ] Real-time updates working (file watching or polling)
- [ ] CSV path changes auto-reflected in UI

**Task 2 Complete:**
- [ ] `generate_foundation_docs` adds docs to CSV
- [ ] `generate_resource_sheet` adds sheets to CSV
- [ ] `archive_feature` updates CSV status
- [ ] CSV remains valid after automated updates
- [ ] No duplicate entries created
- [ ] Documentation created for CSV patterns

**Task 3 Complete:**
- [ ] All 6 pages have CLAUDE.md
- [ ] All 6 pages have coderef/ folder
- [ ] All 6 pages have resource-sheet-index.md
- [ ] All new resource sheets added to CSV
- [ ] PAGE-STRUCTURE-STANDARD.md created

---

## Expected Outcome

**After Phase 3:**

1. **CSV is living document**
   - Updates automatically when agents create resources
   - Displayed dynamically in Resources page
   - Single source of truth (no manual maintenance)

2. **Resources page is dynamic**
   - No hardcoded data
   - Real-time updates when CSV changes
   - All 346+ resources visible and searchable

3. **Dashboard pages standardized**
   - Consistent structure across all pages
   - AI context available (CLAUDE.md)
   - Resource sheets organized (coderef/)

**Benefits:**
- Zero manual CSV maintenance
- Instant visibility of new resources
- Consistent development experience
- Better AI agent context across pages

---

## Handoff Instructions

### For coderef-dashboard Agent (Tasks 1 & 3)

**Working Directory:** `C:\Users\willh\Desktop\coderef-dashboard`

**Task 1: Dynamic Resources Page**
1. Read current page.tsx implementation
2. Choose architecture (Server Component vs API Route)
3. Implement CSV reading and parsing
4. Update UI to use dynamic data
5. Test with all 346 resources
6. Add real-time updates (file watching)
7. Update CLAUDE.md with new architecture

**Task 3: Page Structure Standard** (after Task 1)
1. Use resources/ as template
2. Create CLAUDE.md for 5 pages (explorer, workflows, personas, documentation, testing)
3. Create coderef/ folders with resource-sheet-index.md
4. Create page-specific resource sheets
5. Move existing resource sheets to coderef/ folders
6. Add all new sheets to CSV
7. Create PAGE-STRUCTURE-STANDARD.md

### For coderef-workflow Agent (Task 2)

**Working Directory:** `C:\Users\willh\.mcp-servers\coderef-workflow`

**Task 2: CSV Automation**
1. Create csv_manager.py utility module
2. Update generate_foundation_docs to add CSV entries
3. Update generate_resource_sheet to add CSV entries
4. Update archive_feature to update CSV status
5. Test each workflow → verify CSV updated correctly
6. Document CSV maintenance patterns
7. Create CSV-Maintenance-Workflow-RESOURCE-SHEET.md

---

**Phase 3 Status:** READY TO START
**Recommended Approach:** Parallel execution (Tasks 1 & 2 simultaneously)
**Estimated Duration:** 4-6 hours total (2-3 hours per task if parallel)
