# Agent 1 Research Summary - Session Creation System

**Date:** 2026-01-11
**Workorder:** WO-SESSIONS-HUB-002-CREATOR
**Agent:** Agent 1 (Sessions Hub Creator)

---

## Executive Summary

Completed comprehensive Phase 0 research on Sessions Hub Phase 1 design, CodeRef Dashboard architecture, and PromptingWorkflow patterns. Ready to proceed to Phase 1 (Planning) and implementation of Session Creation system (Sprints 1-4).

**Key Finding:** PromptingWorkflow provides excellent reusable patterns for attachment management, which I can leverage directly to save 6-8 hours of development time.

---

## Phase 1 Design Analysis

### System 1: Session Creation (My Domain)

**Purpose:** Interactive wizard to create multi-agent sessions from stubs with freeform instructions and context attachments.

**Core Workflow:**
```
STUB Selection
    ↓
Freeform Instructions (multi-block)
    ↓
Context Attachment (reuse PromptingWorkflow)
    ↓
Agent Assignment (split instructions/context)
    ↓
Session Generation (context-backbone.md + files)
```

**Key Innovation: Context Backbone**
- 15,000-20,000 line comprehensive context package
- Combines: original stub + all instructions + all attachments
- Ensures "perfect context on first try" for agents

**My Deliverables:**
1. `context-backbone.md` (15K+ lines)
2. `context-index.json` (metadata)
3. `communication.json` (DRAFT for orchestrator)
4. `instructions.json` (DRAFT for orchestrator)
5. `agent-prompts/*.md` (one-liner prompts)

---

## Architecture Insights

### Next.js 16 App Router Patterns

**Component Types:**
- `'use client'` directive for components with hooks/events
- Server components by default for static content
- API routes in `src/app/api/` with `GET`/`POST` exports

**File Structure Pattern:**
```
packages/dashboard/src/components/
├── SessionsHub/
│   ├── SessionCreation/          # My territory
│   │   ├── index.tsx             # Container component
│   │   ├── StubSelector.tsx      # Sprint 1
│   │   ├── InstructionEditor.tsx # Sprint 1
│   │   ├── InstructionBlock.tsx  # Sprint 1
│   │   ├── AttachmentManager.tsx # Sprint 2 (REUSE from PromptingWorkflow)
│   │   ├── AgentAssigner.tsx     # Sprint 3
│   │   └── SessionGenerator.tsx  # Sprint 4
│   └── SessionMonitoring/        # FORBIDDEN (Agent 2's territory)
```

**API Routes Pattern:**
```typescript
// src/app/api/sessions/create/route.ts
export async function POST(request: Request): Promise<NextResponse> {
  const body = await request.json();
  // 1. Validate input
  // 2. Generate context-backbone.md
  // 3. Generate communication.json/instructions.json
  // 4. Save to .coderef/sessions/{feature-name}/
  // 5. Return success with file paths
}
```

### Design System

**Tailwind with Custom Tokens:**
```css
/* Use ind-* prefixed tokens throughout */
bg-ind-bg           /* Background color */
bg-ind-panel        /* Panel/card background */
border-ind-border   /* Border color */
text-ind-text       /* Primary text */
text-ind-text-muted /* Muted text */
text-ind-accent     /* Accent color (blue) */
text-ind-success    /* Success (green) */
text-ind-warning    /* Warning (orange) */
text-ind-error      /* Error (red) */
```

**Responsive Design (Mobile-First):**
```tsx
// Always use mobile-first breakpoints
className="p-2 sm:p-4 md:p-6"           // Padding
className="text-xs sm:text-sm md:text-base" // Typography
className="hidden sm:block"              // Visibility
```

---

## Reusable Patterns from PromptingWorkflow

### AttachmentManager Component (REUSE CANDIDATE)

**Source:** `packages/dashboard/src/components/PromptingWorkflow/components/AttachmentManager.tsx`

**Key Features I Can Reuse:**
1. **AttachmentDropZone** - Drag-and-drop file upload
2. **Quick Paste** - Clipboard text paste with auto-filename generation
3. **Attachment Display** - File cards with preview, size, language, remove button
4. **Token Estimation** - Character count / 4 = estimated tokens
5. **Total Stats** - Files count, total size (KB), token count

**Attachment Data Structure:**
```typescript
interface Attachment {
  id: string;                    // UUID
  filename: string;              // UserAuth.tsx or clipboard_001.txt
  type: 'FILE' | 'PASTED_TEXT' | 'IMAGE';
  extension: string;             // .tsx, .txt, .md
  mimeType: string;              // text/typescript, text/plain
  size: number;                  // bytes
  content?: string;              // Actual content (critical for export)
  preview?: string;              // First 200 chars
  language?: string;             // typescript, python (for syntax)
  isText: boolean;
  isBinary: boolean;
  createdAt: Date;
}
```

**How I'll Adapt It:**
- Import directly from PromptingWorkflow
- Add "Context Discovery" feature (suggest files based on stub keywords)
- Add "Per-Agent Assignment" checkboxes (filter which agents see which context)

---

## Component Structure Plan

### Sprint 1: StubSelector + InstructionEditor

**StubSelector.tsx:**
```typescript
interface StubSelectorProps {
  onSelectStub: (stub: Stub) => void;
  selectedStub?: Stub;
}

// Features:
// - List hardcoded stubs (STUB-082, 054, 055, 056, 057)
// - Display: ID, feature name, description, target project
// - Search/filter functionality
// - Card-based UI (similar to StubCard)
```

**InstructionEditor.tsx:**
```typescript
interface InstructionEditorProps {
  blocks: InstructionBlock[];
  onAddBlock: () => void;
  onUpdateBlock: (id: string, content: string, type: BlockType) => void;
  onRemoveBlock: (id: string) => void;
  onReorderBlocks: (blocks: InstructionBlock[]) => void;
}

interface InstructionBlock {
  id: string;              // UUID
  content: string;         // Freeform markdown text
  type: 'task' | 'guideline' | 'example' | 'constraint';
  assignedTo: string[];    // Agent IDs
}

// Features:
// - Freeform textarea with markdown support
// - Block type selector (color-coded borders)
// - Add/remove/reorder blocks
// - Character count display
// - Markdown preview toggle
```

**SessionCreation.tsx (Container):**
```typescript
'use client';

export default function SessionCreation() {
  const [selectedStub, setSelectedStub] = useState<Stub | null>(null);
  const [instructionBlocks, setInstructionBlocks] = useState<InstructionBlock[]>([]);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [agents, setAgents] = useState<AgentAssignment[]>([]);

  // Form validation
  const isValid = selectedStub && instructionBlocks.length > 0 &&
                  instructionBlocks.every(b => b.content.trim());

  return (
    <div className="space-y-6">
      <StubSelector onSelectStub={setSelectedStub} selectedStub={selectedStub} />
      <InstructionEditor blocks={instructionBlocks} onUpdateBlocks={setInstructionBlocks} />
      {/* Sprint 2: Add AttachmentManager */}
      {/* Sprint 3: Add AgentAssigner */}
      {/* Sprint 4: Add SessionGenerator */}
    </div>
  );
}
```

---

## Data Flow

### Sprint 4: Session Generation Flow

```
User clicks "Generate Session"
    ↓
SessionGenerator calls /api/sessions/create
    ↓
API Route Handler:
  1. Load selected stub data
  2. Aggregate instruction blocks by agent
  3. Generate context-backbone.md:
     - Section 1: Session Overview
     - Section 2: Original Stub
     - Section 3: Agent Instructions (organized by agent)
     - Section 4: Context Attachments (full content)
     - Section 5: Agent Assignment Map
  4. Generate context-index.json (metadata)
  5. Generate communication.json (DRAFT with stub reference)
  6. Generate instructions.json (DRAFT per-agent instructions)
  7. Generate agent-prompts/*.md (one-liner prompts)
  8. Save to .coderef/sessions/{feature-name}/
    ↓
Return { session_path, files_created: [...] }
    ↓
UI shows success message + copy-to-clipboard buttons
```

---

## Questions/Clarifications Needed

**Q1: Stub Data Source**
- Where do stubs live? In orchestrator or in target projects?
- Should I hardcode 5 stubs (STUB-082, 054, 055, 056, 057) or scan from filesystem?
- **Assumption:** Hardcode 5 stubs for MVP (Phase 1 doc says "hardcoded stubs")

**Q2: Agent Roster Source**
- Where do I get available agents list? From communication.json template?
- **Assumption:** Read from target project's existing communication.json or use default roster

**Q3: Context Discovery Algorithm**
- How to implement keyword matching for relevance scoring?
- **Assumption:** Simple keyword frequency matching (0-100 score), suggest files >= 90%

**Q4: File Permissions**
- Will API routes have write access to .coderef/sessions/ directories?
- **Mitigation:** Test early in Sprint 4, document permission requirements

---

## Component Names Match Design

✅ All component names align with Phase 1 design document:
- StubSelector ✅
- InstructionEditor ✅
- InstructionBlock ✅
- AttachmentManager ✅ (reused from PromptingWorkflow)
- AgentAssigner ✅
- SessionGenerator ✅
- SessionCreation ✅ (container)

✅ Data structures match established schemas:
- Attachment interface ✅ (from PromptingWorkflow)
- InstructionBlock interface ✅ (defined in Phase 1)
- AgentAssignment interface ✅ (defined in Phase 1)

✅ UI patterns follow existing conventions:
- Industrial theme with ind-* tokens ✅
- Mobile-first responsive design ✅
- Card-based layouts ✅
- Tailwind utility classes ✅

---

## Forbidden Files (DO NOT TOUCH)

**Agent 2's Territory:**
- `packages/dashboard/src/components/SessionsHub/SessionMonitoring/**`
- `packages/dashboard/src/lib/api/sessions.ts`

**My Territory:**
- `packages/dashboard/src/components/SessionsHub/SessionCreation/**`
- `packages/dashboard/src/app/api/sessions/create/**`
- `packages/dashboard/src/app/api/sessions/context-discovery/**`

---

## Next Steps

1. ✅ Research complete
2. ⏭️ Run `mcp__coderef-workflow__gather_context` to create context.json
3. ⏭️ Run `mcp__coderef-workflow__create_plan` to generate plan.json
4. ⏭️ Run `mcp__coderef-workflow__execute_plan` to generate TodoWrite checklist
5. ⏭️ Begin Sprint 1 implementation (StubSelector + InstructionEditor)

---

**Research Status:** ✅ Complete
**Ready for Phase 1 Planning:** Yes
