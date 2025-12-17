# MCP SaaS Platform - Product Specification

**Codename:** Lloyd.ai
**Version:** 1.0 Spec
**Date:** 2025-12-16
**Status:** Draft

---

## 1. Executive Summary

### Vision
An AI-native development workflow platform that transforms how teams plan, build, and ship software. Not just project tracking—actual AI agents executing tasks with full context awareness.

### Value Proposition
- **For Developers:** AI pair programming with persistent context across sessions
- **For Teams:** Visibility into AI-assisted development workflows
- **For Managers:** Metrics on AI productivity gains and feature velocity

### Unique Differentiators
1. **MCP-Native:** Built on Model Context Protocol for universal AI tool access
2. **Workorder System:** Traceable AI work with unique IDs (WO-FEATURE-001)
3. **Context Persistence:** AI agents resume with full project understanding
4. **Multi-Agent Coordination:** Parallel AI workers on complex features

---

## 2. Target Users

### Primary Personas

| Persona | Role | Pain Points | Value |
|---------|------|-------------|-------|
| **Solo Developer** | Indie hacker, freelancer | Context loss between AI sessions, manual docs | Persistent AI context, auto-documentation |
| **Tech Lead** | Team lead, architect | Visibility into AI work, consistency | Dashboard, standards enforcement |
| **Engineering Manager** | Director, VP Eng | ROI on AI tools, team productivity | Analytics, time-saved metrics |
| **Enterprise Architect** | Large org | Security, compliance, audit trails | SSO, audit logs, self-hosted option |

### Use Cases
1. Feature planning with AI-generated implementation plans
2. Multi-agent parallel development on large features
3. Automated documentation generation and maintenance
4. Code consistency auditing against project standards
5. Team collaboration with shared AI context

---

## 3. Core Features

### 3.1 Project Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│ myproject                                        Settings  ▼    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Active       │  │ Completed    │  │ Archived     │          │
│  │ Workorders   │  │ This Week    │  │ Total        │          │
│  │     3        │  │     12       │  │     47       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  Active Features                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ WO-AUTH-001  │ JWT Authentication    │ ████████░░ 80%   │   │
│  │ WO-CACHE-002 │ Redis Caching Layer   │ ████░░░░░░ 40%   │   │
│  │ WO-UI-003    │ Dashboard Components  │ ██░░░░░░░░ 20%   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [+ New Feature]  [Run Scan]  [Generate Docs]  [View Reports]  │
└─────────────────────────────────────────────────────────────────┘
```

**Capabilities:**
- Real-time workorder status tracking
- Progress visualization per feature
- Quick actions for common workflows
- Activity feed with AI agent actions

### 3.2 Feature Workspace

```
┌─────────────────────────────────────────────────────────────────┐
│ WO-AUTH-001: JWT Authentication                    [Archive] ▼  │
├─────────────────────────────────────────────────────────────────┤
│ Tabs: [Overview] [Plan] [Tasks] [Docs] [Activity] [Agents]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Status: Implementation    Phase: 2 of 4    Due: Dec 20        │
│  ═══════════════════════════════════════════════════════════   │
│  Planning ✓ → Implementation ◉ → Testing → Review              │
│                                                                 │
│  Current Tasks                          Assigned Agents         │
│  ┌────────────────────────────────┐    ┌──────────────────┐    │
│  │ ☑ SETUP-001: Install deps     │    │ Agent 1: VERIFIED│    │
│  │ ☑ SETUP-002: Create structure │    │ Agent 2: WORKING │    │
│  │ ⏳ IMPL-001: JWT service       │    │ Agent 3: IDLE    │    │
│  │ ☐ IMPL-002: Middleware        │    └──────────────────┘    │
│  │ ☐ TEST-001: Unit tests        │                             │
│  └────────────────────────────────┘    [Assign Agent]          │
│                                                                 │
│  Files Modified (12)        Commits (5)       LOC (+450/-120)  │
└─────────────────────────────────────────────────────────────────┘
```

**Capabilities:**
- Full feature lifecycle management
- Task checklist with real-time updates
- Multi-agent assignment and tracking
- Git integration (commits, PRs, branches)
- Metrics collection (LOC, time, velocity)

### 3.3 AI Chat Interface

```
┌─────────────────────────────────────────────────────────────────┐
│ Chat: WO-AUTH-001                              [Context: Full]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  You: Create the JWT validation middleware                      │
│                                                                 │
│  Lloyd: I'll create the JWT validation middleware based on      │
│  the plan in WO-AUTH-001. Let me check the current state...    │
│                                                                 │
│  📁 Reading: src/auth/jwt_service.py                           │
│  📁 Reading: plan.json (Phase 2, Task IMPL-002)                │
│                                                                 │
│  I'll create the middleware with these specs:                   │
│  - Token extraction from Authorization header                   │
│  - Signature verification using RS256                          │
│  - Claims validation (exp, iat, iss)                           │
│  - User context injection                                       │
│                                                                 │
│  [View Code] [Apply Changes] [Modify Approach]                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ > Type a message...                              [Send] [Tools]│
└─────────────────────────────────────────────────────────────────┘
```

**Capabilities:**
- Context-aware AI chat per feature/project
- Tool execution with visual feedback
- Code preview before applying
- Conversation history with full context
- Voice input option

### 3.4 Standards & Auditing

```
┌─────────────────────────────────────────────────────────────────┐
│ Code Standards                                    [Scan Now]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Compliance Score: 87/100  Grade: B+  ██████████████████░░░    │
│                                                                 │
│  Category Breakdown                                             │
│  ├── UI Patterns      92%  ████████████████████░░               │
│  ├── Behavior         85%  █████████████████░░░░                │
│  └── UX/A11y          84%  ████████████████░░░░░                │
│                                                                 │
│  Recent Violations (3)                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ⚠ MAJOR  Button.tsx:42  Non-standard button size       │   │
│  │ ⚠ MINOR  Form.tsx:18   Missing aria-label              │   │
│  │ ⚠ MINOR  Modal.tsx:55  Inconsistent close behavior     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [View Full Report]  [Auto-Fix]  [Configure Rules]             │
└─────────────────────────────────────────────────────────────────┘
```

### 3.5 Team Collaboration

```
┌─────────────────────────────────────────────────────────────────┐
│ Team: Acme Engineering                          [Invite] [+]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Members (5)                    Activity Today                  │
│  ┌────────────────────────┐    ┌────────────────────────────┐  │
│  │ 🟢 Alice (Admin)       │    │ Alice archived WO-CACHE    │  │
│  │ 🟢 Bob (Developer)     │    │ Bob started WO-UI-003      │  │
│  │ 🟡 Carol (Developer)   │    │ Agent completed 12 tasks   │  │
│  │ ⚫ Dave (Viewer)       │    │ Carol ran coderef-scan     │  │
│  │ 🟢 Eve (Developer)     │    └────────────────────────────┘  │
│  └────────────────────────┘                                     │
│                                                                 │
│  Shared Resources                                               │
│  • 3 Active Projects    • 15 Shared Templates                  │
│  • 2 Custom Personas    • 47 Archived Features                 │
│                                                                 │
│  [Manage Permissions]  [Usage Analytics]  [Billing]            │
└─────────────────────────────────────────────────────────────────┘
```

### 3.6 Analytics Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│ Analytics: Last 30 Days                         [Export CSV]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Key Metrics                                                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Features     │ │ Time Saved   │ │ Code Quality │            │
│  │ Shipped: 23  │ │ 120 hrs      │ │ +15% vs avg  │            │
│  │ +28% ▲       │ │ $18,000 val  │ │ 87 → 92      │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                 │
│  Feature Velocity                    AI Agent Utilization       │
│  ┌─────────────────────────┐        ┌─────────────────────┐    │
│  │     ╭───╮               │        │  Planning    ███░░  │    │
│  │   ╭─╯   ╰─╮   ╭──      │        │  Coding      █████  │    │
│  │ ──╯       ╰───╯        │        │  Docs        ██░░░  │    │
│  │  W1   W2   W3   W4     │        │  Review      █░░░░  │    │
│  └─────────────────────────┘        └─────────────────────┘    │
│                                                                 │
│  [Detailed Reports]  [Set Goals]  [Compare Periods]            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Technical Architecture

### 4.1 High-Level Architecture

```
                                 ┌─────────────────┐
                                 │   CDN/Edge      │
                                 │   (Vercel)      │
                                 └────────┬────────┘
                                          │
┌──────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Next.js    │  │  React      │  │  TailwindCSS│              │
│  │  App Router │  │  Components │  │  + shadcn   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└──────────────────────────────────────────────────────────────────┘
                                          │
                                          │ HTTPS/WSS
                                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                         API Gateway                               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  FastAPI  │  Auth (JWT)  │  Rate Limiting  │  WebSockets    │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
          │              │              │              │
          ▼              ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  User       │  │  Project    │  │  Workorder  │  │  Analytics  │
│  Service    │  │  Service    │  │  Service    │  │  Service    │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
          │              │              │              │
          └──────────────┼──────────────┴──────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                      MCP Orchestrator                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  docs-mcp   │  │  coderef-mcp│  │ personas-mcp│              │
│  │  (36 tools) │  │  (8 tools)  │  │  (4 tools)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└──────────────────────────────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  PostgreSQL │  │  Redis      │  │  S3/R2      │
│  (Data)     │  │  (Cache/Q)  │  │  (Files)    │
└─────────────┘  └─────────────┘  └─────────────┘
```

### 4.2 Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | Next.js 14 (App Router) | SSR, RSC, great DX |
| **UI Components** | shadcn/ui + Tailwind | Customizable, accessible |
| **State** | Zustand + React Query | Simple, effective |
| **API** | FastAPI (Python) | Async, MCP compatibility |
| **Auth** | Clerk or Auth.js | Quick setup, enterprise features |
| **Database** | PostgreSQL (Supabase) | Reliable, good tooling |
| **Cache/Queue** | Redis (Upstash) | Session, job queue, pub/sub |
| **File Storage** | Cloudflare R2 | S3-compatible, cheap |
| **AI** | Claude API (Anthropic) | Best coding model |
| **Hosting** | Vercel + Railway | Easy deployment |
| **Monitoring** | Sentry + PostHog | Errors + analytics |

### 4.3 MCP Integration

```python
# MCP Orchestrator - routes requests to appropriate MCP servers

class MCPOrchestrator:
    def __init__(self):
        self.servers = {
            'docs': DocsMCPClient(),
            'coderef': CodeRefMCPClient(),
            'personas': PersonasMCPClient(),
        }

    async def execute_tool(self, server: str, tool: str, args: dict) -> dict:
        """Execute MCP tool and return result."""
        client = self.servers.get(server)
        if not client:
            raise ValueError(f"Unknown server: {server}")

        # Log workorder association
        if workorder_id := args.get('workorder_id'):
            await self.log_tool_execution(workorder_id, server, tool)

        return await client.call_tool(tool, args)

    async def execute_workflow(self, workflow: str, context: dict) -> dict:
        """Execute multi-step workflow (e.g., start-feature)."""
        if workflow == 'start-feature':
            return await self._start_feature_workflow(context)
        # ... other workflows
```

---

## 5. Data Models

### 5.1 Core Entities

```sql
-- Users and Auth
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

-- Organizations (for teams)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE org_members (
    org_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50) DEFAULT 'member', -- admin, member, viewer
    PRIMARY KEY (org_id, user_id)
);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    github_repo TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(org_id, slug)
);

-- Workorders (Features)
CREATE TABLE workorders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    workorder_id VARCHAR(50) NOT NULL, -- WO-AUTH-001
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'planning', -- planning, implementation, testing, review, complete, archived
    priority VARCHAR(20) DEFAULT 'medium',
    context JSONB, -- from gather-context
    plan JSONB, -- from create-plan
    deliverables JSONB, -- metrics
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ,
    UNIQUE(project_id, workorder_id)
);

-- Tasks (within workorders)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workorder_id UUID REFERENCES workorders(id),
    task_id VARCHAR(50) NOT NULL, -- SETUP-001
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, complete, blocked
    assigned_agent INTEGER,
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);

-- Agent Sessions
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workorder_id UUID REFERENCES workorders(id),
    agent_number INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'idle', -- idle, assigned, working, complete, verified
    assigned_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    verification JSONB -- verification results
);

-- Activity Log
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    workorder_id UUID REFERENCES workorders(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat History
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workorder_id UUID REFERENCES workorders(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 5.2 Indexes

```sql
CREATE INDEX idx_workorders_project ON workorders(project_id);
CREATE INDEX idx_workorders_status ON workorders(status);
CREATE INDEX idx_tasks_workorder ON tasks(workorder_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_activity_project ON activity_log(project_id, created_at DESC);
CREATE INDEX idx_chat_workorder ON chat_messages(workorder_id, created_at);
```

---

## 6. API Design

### 6.1 REST Endpoints

```yaml
# Authentication
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me

# Organizations
GET    /api/orgs
POST   /api/orgs
GET    /api/orgs/:slug
PATCH  /api/orgs/:slug
DELETE /api/orgs/:slug

# Projects
GET    /api/orgs/:slug/projects
POST   /api/orgs/:slug/projects
GET    /api/projects/:id
PATCH  /api/projects/:id
DELETE /api/projects/:id

# Workorders
GET    /api/projects/:id/workorders
POST   /api/projects/:id/workorders
GET    /api/workorders/:id
PATCH  /api/workorders/:id
POST   /api/workorders/:id/archive

# Tasks
GET    /api/workorders/:id/tasks
PATCH  /api/tasks/:id
POST   /api/tasks/:id/complete

# MCP Tools
POST   /api/mcp/execute
GET    /api/mcp/tools
GET    /api/mcp/servers

# Chat
GET    /api/workorders/:id/chat
POST   /api/workorders/:id/chat
DELETE /api/chat/:id

# Analytics
GET    /api/orgs/:slug/analytics
GET    /api/projects/:id/analytics
```

### 6.2 WebSocket Events

```typescript
// Client → Server
interface ClientEvents {
  'chat:message': { workorder_id: string; content: string };
  'task:update': { task_id: string; status: string };
  'workorder:subscribe': { workorder_id: string };
  'workorder:unsubscribe': { workorder_id: string };
}

// Server → Client
interface ServerEvents {
  'chat:response': { message: ChatMessage; tool_calls?: ToolCall[] };
  'chat:streaming': { chunk: string; done: boolean };
  'task:updated': { task: Task };
  'workorder:updated': { workorder: Workorder };
  'agent:status': { agent_number: number; status: string };
  'error': { code: string; message: string };
}
```

---

## 7. Security

### 7.1 Authentication & Authorization

| Feature | Implementation |
|---------|----------------|
| **Auth Provider** | Clerk (SSO, MFA, social login) |
| **Session** | JWT with short expiry (15min) + refresh tokens |
| **API Auth** | Bearer tokens for API, session cookies for web |
| **RBAC** | Admin, Member, Viewer roles per org |
| **Project Access** | Org membership + explicit project grants |

### 7.2 Data Security

| Concern | Mitigation |
|---------|------------|
| **Data at Rest** | PostgreSQL encryption, R2 encryption |
| **Data in Transit** | TLS 1.3 everywhere |
| **Secrets** | Environment variables, no code storage |
| **API Keys** | User-scoped, rotatable, rate-limited |
| **Audit Log** | All actions logged with user/timestamp |
| **PII** | GDPR compliant, data export/deletion |

### 7.3 Enterprise Features

- SSO (SAML, OIDC)
- SCIM provisioning
- IP allowlisting
- Audit log export
- Data residency options
- Self-hosted deployment

---

## 8. Pricing & Monetization

### 8.1 Pricing Tiers

| Tier | Price | Limits | Features |
|------|-------|--------|----------|
| **Free** | $0/mo | 1 project, 5 features/mo, 1 user | Basic dashboard, docs generation, community support |
| **Pro** | $29/user/mo | Unlimited projects, 50 features/mo | Team collaboration, analytics, priority support |
| **Team** | $79/user/mo | Unlimited everything | Custom personas, API access, SSO, dedicated support |
| **Enterprise** | Custom | Unlimited | Self-hosted, SLA, audit logs, SCIM, custom integrations |

### 8.2 Usage-Based Add-ons

| Add-on | Price |
|--------|-------|
| Additional features | $2/feature over limit |
| AI chat tokens | $10/100K tokens |
| File storage | $5/10GB/mo |
| API calls | $20/10K calls/mo |

### 8.3 Revenue Projections

| Milestone | Users | MRR | Timeline |
|-----------|-------|-----|----------|
| Beta | 100 | $0 | Month 1-3 |
| Launch | 500 | $5K | Month 4-6 |
| Growth | 2,000 | $30K | Month 7-12 |
| Scale | 10,000 | $200K | Year 2 |

---

## 9. MVP Scope

### 9.1 MVP Features (v1.0)

**Must Have:**
- [ ] User auth (email + GitHub OAuth)
- [ ] Single-user projects (no teams yet)
- [ ] Project dashboard with workorder list
- [ ] Feature workspace with task tracking
- [ ] Basic AI chat per workorder
- [ ] MCP tool execution (docs-mcp subset)
- [ ] GitHub repo connection

**Won't Have (v1.0):**
- Team collaboration
- Multi-agent coordination
- Analytics dashboard
- Custom personas
- Standards auditing
- Enterprise features

### 9.2 MVP Timeline

| Week | Milestone |
|------|-----------|
| 1-2 | Auth + basic UI shell |
| 3-4 | Project/workorder CRUD |
| 5-6 | MCP integration + tool execution |
| 7-8 | AI chat interface |
| 9-10 | GitHub integration |
| 11-12 | Polish + beta launch |

### 9.3 MVP Tech Choices

```
Frontend:  Next.js 14 + shadcn/ui + Tailwind
Backend:   FastAPI on Railway
Database:  Supabase (PostgreSQL)
Auth:      Clerk
AI:        Claude API (Anthropic)
MCP:       docs-mcp hosted on Railway
```

---

## 10. Roadmap

### Phase 1: Foundation (Months 1-3)
- MVP launch
- Single-user experience
- Core MCP tools (docs-mcp)
- Basic analytics

### Phase 2: Teams (Months 4-6)
- Team workspaces
- Role-based access
- Shared projects
- Activity feeds

### Phase 3: Intelligence (Months 7-9)
- Multi-agent coordination
- coderef-mcp integration
- Standards auditing
- Advanced analytics

### Phase 4: Enterprise (Months 10-12)
- SSO/SCIM
- Audit logs
- Self-hosted option
- Custom integrations

### Phase 5: Marketplace (Year 2)
- Template marketplace
- Custom persona sharing
- Third-party MCP servers
- Plugin ecosystem

---

## 11. Success Metrics

### Product Metrics
| Metric | Target (Month 6) |
|--------|------------------|
| MAU | 1,000 |
| Features shipped/user/mo | 5 |
| DAU/MAU ratio | 40% |
| Retention (M1) | 60% |
| NPS | 50+ |

### Business Metrics
| Metric | Target (Month 6) |
|--------|------------------|
| MRR | $15K |
| Paid conversion | 5% |
| CAC | <$50 |
| LTV | >$500 |
| Churn | <5%/mo |

---

## 12. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Claude API costs too high | Medium | High | Usage limits, caching, prompt optimization |
| MCP adoption slow | Medium | Medium | Focus on standalone value first |
| GitHub integration complexity | High | Medium | Start with read-only, expand gradually |
| Security breach | Low | Critical | Third-party audit, bug bounty |
| Competition from big players | Medium | High | Focus on niche (MCP-native), move fast |

---

## 13. Open Questions

1. **Self-hosted vs. Cloud-only?** Enterprise wants self-hosted, but maintenance burden is high.
2. **Free tier limits?** Too generous = no conversion, too stingy = no adoption.
3. **AI model choice?** Claude-only or multi-model support?
4. **MCP server hosting?** User brings own vs. we host shared instances.
5. **Offline mode?** CLI sync for developers who want local-first.

---

## Appendix A: Competitive Analysis

| Competitor | Positioning | Weakness | Our Advantage |
|------------|-------------|----------|---------------|
| Cursor | AI IDE | IDE-locked, no workflow | MCP-native, tool ecosystem |
| GitHub Copilot | Code completion | No planning, no context | Full feature lifecycle |
| Linear | Project mgmt | No AI execution | AI agents do the work |
| Notion AI | Docs + AI | No code integration | Deep code understanding |
| Replit Agent | AI coding | New, unproven | Proven MCP tools |

---

## Appendix B: User Research Needed

1. Interview 10 solo developers using Claude Code
2. Interview 5 tech leads managing AI-assisted teams
3. Survey on pricing sensitivity
4. A/B test onboarding flows
5. Usability testing on core workflows

---

**Document Status:** Draft
**Next Review:** After user feedback
**Owner:** Will H
