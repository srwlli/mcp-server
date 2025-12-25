# docs-expert v2.0 - Complete Implementation Plan

**Workorder:** WO-DOCS-EXPERT-V2-001
**Version:** 1.0.0 → 2.0.0
**Status:** 📋 Ready for Implementation
**Created:** 2025-10-18

---

## Executive Summary

Comprehensive implementation plan for upgrading docs-expert from v1.0.0 to v2.0.0 with Lloyd integration, planning flexibility, historical intelligence, and persona coordination capabilities.

**Total Effort:** 44-60 hours across 8 weeks
**New Tools:** 8 tools across 4 phases
**Impact:** 10x faster simple planning, real-time progress tracking, continuous learning

---

## Implementation Roadmap

### Timeline Overview

```
Week 1-2: Phase 1 - Lloyd Integration (16-24h)
Week 3-4: Phase 2 - Planning Flexibility (12-16h)
Week 5-6: Phase 3 - Historical Intelligence (16-20h)
Week 7+:  Phase 4 - Persona Coordination (TBD, requires persona stacking)
```

---

## Phase 1: Lloyd Integration (Weeks 1-2)

### Goals
- Seamless Lloyd + docs-expert workflow
- Automatic todo list generation from plans
- Real-time plan progress tracking
- Guided interactive execution

### New Tools (3)
1. **generate_todo_list** - Convert plan tasks → TodoWrite format
2. **track_plan_execution** - Sync plan progress with todo status
3. **execute_plan_interactive** - Guided implementation with live tracking

### Implementation Tasks

#### Week 1: Core Infrastructure
**Task 1.1: TodoListGenerator (Day 1-2, 6-8h)**
- Create `src/generators/todo_list_generator.py`
- Implement plan.json → todo conversion
- Add workorder ID preservation
- Add acceptance criteria mapping
- Unit tests (5 test cases)

**Task 1.2: PlanExecutionTracker (Day 3-4, 6-8h)**
- Create `src/trackers/plan_execution_tracker.py`
- Implement todo status → plan sync
- Add progress calculation
- Add timestamp tracking
- Unit tests (6 test cases)

**Task 1.3: Schema Updates (Day 5, 2-3h)**
- Update `src/models.py` with execution_status schema
- Update `src/models.py` with progress schema
- Update `src/models.py` with todo metadata schema
- Schema validation tests

#### Week 2: Integration & Polish
**Task 1.4: InteractivePlanExecutor (Day 1-3, 8-10h)**
- Create `src/executors/interactive_plan_executor.py`
- Implement step-by-step mode
- Implement batch mode
- Add guidance generation
- Add dependency checking
- Unit tests (8 test cases)

**Task 1.5: MCP Tool Handlers (Day 4, 3-4h)**
- Add generate_todo_list to server.py
- Add track_plan_execution to server.py
- Add execute_plan_interactive to server.py
- Tool registration and routing

**Task 1.6: Integration Testing (Day 5-6, 4-6h)**
- Full workflow test: plan → todos → track → complete
- Lloyd coordination test
- Edge case testing (out-of-order, partial completion)
- Performance testing (<2s for todo generation)

**Task 1.7: System Prompt Update (Day 7, 2h)**
- Add Lloyd Integration section to system prompt
- Update workflows documentation
- Add best practices
- Update value proposition

### Deliverables
- ✅ 3 new tools fully implemented
- ✅ TodoListGenerator with 100% test coverage
- ✅ PlanExecutionTracker with real-time sync
- ✅ InteractivePlanExecutor with step-by-step guidance
- ✅ Updated system prompt (v2.0.0)
- ✅ Integration tests passing

### Success Criteria
- ✅ Todo generation: <2 seconds
- ✅ Progress sync: <1 second
- ✅ Zero manual todo conversion
- ✅ Plan accuracy: 100% match with todos
- ✅ Workorder traceability: 100%

---

## Phase 2: Planning Flexibility (Weeks 3-4)

### Goals
- 10x faster planning for simple tasks
- Adaptive plans (update without regeneration)
- Automated plan refinement (no manual editing)

### New Tools (3)
1. **quick_plan** - Lightweight planning (1-2 min vs 10 min)
2. **update_plan** - Incremental plan updates
3. **refine_plan_automated** - Auto-apply validation feedback

### Implementation Tasks

#### Week 3: Quick Planning & Updates
**Task 2.1: QuickPlanGenerator (Day 1-2, 5-7h)**
- Create `src/generators/quick_plan_generator.py`
- Implement 3-section plan format (context, tasks, validation)
- Add complexity detection (trivial, simple, moderate)
- Add automatic workorder assignment
- Unit tests (4 test cases)

**Task 2.2: PlanUpdater (Day 3-4, 5-7h)**
- Create `src/updaters/plan_updater.py`
- Implement section update logic
- Implement task modification logic
- Add change tracking (old → new)
- Add dependency recalculation
- Unit tests (6 test cases)

**Task 2.3: Quick Plan Schema (Day 5, 2h)**
- Add quick plan schema to models.py
- Add update record schema to models.py
- Schema validation tests

#### Week 4: Automated Refinement & Integration
**Task 2.4: PlanRefiner (Day 1-3, 6-8h)**
- Create `src/refiners/plan_refiner.py`
- Implement feedback interpretation (AI-powered)
- Implement fix application (conservative/aggressive)
- Add iterative refinement (max 3 rounds)
- Unit tests (7 test cases)

**Task 2.5: MCP Tool Handlers (Day 4, 3h)**
- Add quick_plan to server.py
- Add update_plan to server.py
- Add refine_plan_automated to server.py
- Tool registration and routing

**Task 2.6: Integration Testing (Day 5, 3-4h)**
- Quick planning workflow test
- Adaptive planning workflow test (requirement changes)
- Automated refinement workflow test (72 → 92 score)
- Performance testing (<2s quick plan, <1s update, <5s refine)

**Task 2.7: System Prompt Update (Day 6, 2h)**
- Add Planning Flexibility section to system prompt
- Add decision framework (when to use quick vs full)
- Add best practices
- Update workflows

### Deliverables
- ✅ 3 new tools fully implemented
- ✅ QuickPlanGenerator with complexity detection
- ✅ PlanUpdater with change tracking
- ✅ PlanRefiner with AI-powered suggestions
- ✅ Updated system prompt (v2.0.0)
- ✅ Integration tests passing

### Success Criteria
- ✅ Quick plan generation: <2 seconds
- ✅ 80% of tasks use quick_plan
- ✅ Plan updates: <1 second
- ✅ Automated refinement reaches 90+ in 2-3 iterations
- ✅ Time savings: 10x for simple tasks

---

## Phase 3: Historical Intelligence (Weeks 5-6)

### Goals
- Learn from past planning experiences
- Apply lessons to future plans
- Measure continuous improvement
- Reduce repeated mistakes

### New Tools (2)
1. **plan_history** - Review past workorders, outcomes, lessons
2. **suggest_plan_improvements** - AI-powered suggestions from history

### Implementation Tasks

#### Week 5: History Infrastructure
**Task 3.1: Workorder History Storage (Day 1-2, 5-7h)**
- Create `.docs-expert/history/` directory structure
- Implement JSONL storage (workorders.jsonl)
- Create `src/history/workorder_history.py`
- Implement read/write operations
- Implement indexing strategy (by_id, by_feature_type, by_project)
- Unit tests (5 test cases)

**Task 3.2: Lesson Extractor (Day 3-4, 5-7h)**
- Create `src/history/lesson_extractor.py`
- Implement lesson extraction from workorder
- Implement lesson categorization (documentation, security, testing, etc.)
- Implement lesson aggregation
- Implement lesson frequency calculation
- Unit tests (6 test cases)

**Task 3.3: Statistics Calculator (Day 5, 3-4h)**
- Create `src/history/statistics_calculator.py`
- Implement time variance calculation
- Implement completion rate calculation
- Implement scope change rate calculation
- Implement lesson application tracking
- Unit tests (4 test cases)

#### Week 6: AI Suggestions & Integration
**Task 3.4: PlanImprovementSuggester (Day 1-3, 7-9h)**
- Create `src/suggesters/plan_improvement_suggester.py`
- Implement pattern detection (AI-powered)
- Implement suggestion generation (missing tasks, sections, docs)
- Implement confidence scoring
- Implement suggestion ranking (severity, confidence)
- Unit tests (8 test cases)

**Task 3.5: MCP Tool Handlers (Day 4, 3h)**
- Add plan_history to server.py
- Add suggest_plan_improvements to server.py
- Tool registration and routing

**Task 3.6: Integration Testing (Day 5, 3-4h)**
- Full historical workflow test: create → execute → record → learn
- Suggestion accuracy test (10 test workorders)
- Statistics accuracy test
- Performance testing (<500ms for 1000+ workorders)

**Task 3.7: System Prompt Update (Day 6, 2h)**
- Add Historical Intelligence section to system prompt
- Add historical workflow (gather → history → analyze → create → suggest)
- Add lesson categories
- Add best practices

### Deliverables
- ✅ 2 new tools fully implemented
- ✅ JSONL-based workorder storage
- ✅ LessonExtractor with categorization
- ✅ StatisticsCalculator with metrics
- ✅ PlanImprovementSuggester with AI
- ✅ Updated system prompt (v2.0.0)
- ✅ Integration tests passing

### Success Criteria
- ✅ Plan quality improvement: 85 → 91 average (after 6 months)
- ✅ Time estimate variance: 25% → 15%
- ✅ Scope change rate: 35% → 23%
- ✅ Forgotten tasks: 15% → 5%
- ✅ Lesson application rate: 80%+

---

## Phase 4: Persona Coordination (Future)

### Goals
- Assign tasks to specific personas
- Track cross-persona progress
- Coordinate multi-persona workflows
- Enable specialized expertise per task

### Prerequisites
- ⏳ Persona stacking system (add_persona, get_active_personas)
- ⏳ Persona composition (multiple active simultaneously)
- ⏳ Persona communication protocol

### Implementation Tasks (TBD)
**Task 4.1: PersonaAssigner (TBD, 5-7h)**
- Create `src/coordination/persona_assigner.py`
- Implement task type detection
- Implement persona assignment logic
- Implement assignment rationale generation

**Task 4.2: PersonaCommunicator (TBD, 5-7h)**
- Create `src/coordination/persona_communicator.py`
- Implement message formatting (assignment, completion)
- Implement message routing

**Task 4.3: DependencyManager (TBD, 6-8h)**
- Create `src/coordination/dependency_manager.py`
- Implement dependency detection
- Implement blocking/unblocking logic
- Implement parallel task identification

**Task 4.4: ParallelExecutor (TBD, 6-8h)**
- Create `src/coordination/parallel_executor.py`
- Implement parallel task execution
- Implement coordination overhead optimization

**Task 4.5: Integration & Testing (TBD, 8-10h)**
- Multi-persona workflow tests
- Parallel execution tests
- Persona handoff tests

### Deliverables (Future)
- ⏳ Persona-aware task assignment
- ⏳ Cross-persona progress tracking
- ⏳ Parallel execution capabilities
- ⏳ Persona coordination protocol
- ⏳ Updated system prompt (v2.0.0)

### Success Criteria (Future)
- ⏳ Task assignment accuracy: 95%+
- ⏳ Parallel execution time savings: 50-75%
- ⏳ Coordination overhead: <10%
- ⏳ Dependency resolution accuracy: 100%

---

## File Structure (v2.0.0)

```
personas/base/
└── docs-expert.json                     ← UPDATE (v2.0.0 system prompt)

.docs-expert/
└── history/
    ├── workorders.jsonl                 ← NEW (historical data)
    ├── lessons.jsonl                    ← NEW (aggregated lessons)
    └── statistics.json                  ← NEW (project stats)

src/
├── generators/
│   ├── todo_list_generator.py          ← NEW (Phase 1)
│   └── quick_plan_generator.py         ← NEW (Phase 2)
├── trackers/
│   └── plan_execution_tracker.py       ← NEW (Phase 1)
├── updaters/
│   └── plan_updater.py                 ← NEW (Phase 2)
├── refiners/
│   └── plan_refiner.py                 ← NEW (Phase 2)
├── executors/
│   └── interactive_plan_executor.py    ← NEW (Phase 1)
├── history/
│   ├── workorder_history.py            ← NEW (Phase 3)
│   ├── lesson_extractor.py             ← NEW (Phase 3)
│   └── statistics_calculator.py        ← NEW (Phase 3)
├── suggesters/
│   └── plan_improvement_suggester.py   ← NEW (Phase 3)
├── coordination/                        ← NEW (Phase 4, future)
│   ├── persona_assigner.py
│   ├── persona_communicator.py
│   ├── dependency_manager.py
│   └── parallel_executor.py
└── models.py                            ← UPDATE (new schemas)

server.py                                ← UPDATE (8 new tools)

tests/
├── test_todo_list_generator.py         ← NEW
├── test_plan_execution_tracker.py      ← NEW
├── test_interactive_plan_executor.py   ← NEW
├── test_quick_plan_generator.py        ← NEW
├── test_plan_updater.py                ← NEW
├── test_plan_refiner.py                ← NEW
├── test_workorder_history.py           ← NEW
├── test_lesson_extractor.py            ← NEW
├── test_statistics_calculator.py       ← NEW
└── test_plan_improvement_suggester.py  ← NEW
```

**Total New Files:** 20+ files
**Total Updates:** 3 files (server.py, models.py, docs-expert.json)

---

## Testing Strategy

### Unit Tests (Target: 90%+ Coverage)
- **Phase 1:** 19 test cases across 3 tools
- **Phase 2:** 17 test cases across 3 tools
- **Phase 3:** 23 test cases across 2 tools (+supporting modules)
- **Total:** 59+ unit test cases

### Integration Tests (Target: 100% Workflow Coverage)
- **Phase 1:** 3 integration tests (planning → execution → tracking)
- **Phase 2:** 3 integration tests (quick plan, update, refine)
- **Phase 3:** 3 integration tests (history → suggestions → improvement)
- **Total:** 9 integration tests

### Performance Tests (Target: All Benchmarks Met)
- Todo generation: <2 seconds
- Progress sync: <1 second
- Quick plan: <2 seconds
- Plan update: <1 second
- Plan refinement: <5 seconds per iteration
- History query: <500ms for 1000+ workorders
- Suggestion generation: <2 seconds

### Manual Testing (Pre-Release)
1. Create real feature plan (authentication)
2. Generate todo list
3. Simulate Lloyd execution
4. Verify real-time progress tracking
5. Test quick planning for simple task
6. Test plan update mid-implementation
7. Test automated refinement (72 → 92)
8. Test historical suggestions

---

## Dependencies

### External Dependencies
- **Python SDK:** mcp (existing)
- **AI Integration:** LLM for plan refinement and suggestions (Claude API)
- **Storage:** File system access (JSONL files)
- **Validation:** Pydantic for schemas

### Internal Dependencies
- **Phase 2** depends on **Phase 1** (todos must work first)
- **Phase 3** depends on **Phase 1-2** (needs execution tracking)
- **Phase 4** depends on **Phase 1-3** + **Persona Stacking System**

---

## Risk Management

### Risk 1: AI Refinement Quality
**Impact:** Auto-refinement produces poor suggestions
**Probability:** Medium
**Mitigation:**
- Conservative mode by default (only high-confidence fixes)
- Allow manual review before applying
- Iterative refinement (max 3 rounds)
- Fallback to manual editing if refinement fails

### Risk 2: Historical Data Privacy
**Impact:** Workorder history contains sensitive data
**Probability:** Low
**Mitigation:**
- Store only metadata (no code snippets)
- Anonymize user names
- No credentials, secrets, or PII
- Optional data retention purge (configurable)

### Risk 3: Performance Degradation
**Impact:** Large history slows down queries
**Probability:** Medium
**Mitigation:**
- Indexing strategy (by_id, by_feature_type, by_project)
- JSONL format (append-only, streaming)
- Limit queries to recent data (configurable window)
- Performance tests (<500ms for 1000+ workorders)

### Risk 4: Phase 4 Blocked
**Impact:** Persona stacking not implemented, Phase 4 can't proceed
**Probability:** High
**Mitigation:**
- Design Phase 4 now (documented)
- Implement Phases 1-3 first (independent)
- Monitor personas-mcp roadmap
- Implement Phase 4 when prerequisites met

---

## Success Metrics (v2.0.0)

### Phase 1 Success
- ✅ Zero manual todo conversion (100% automated)
- ✅ Real-time plan visibility (todos → plan sync)
- ✅ Complete traceability (workorder → plan → todos → completion)
- ✅ Lloyd reports "seamless workflow"

### Phase 2 Success
- ✅ 10x faster planning for simple tasks (1 min vs 11 min)
- ✅ 80% of tasks use quick_plan (not full planning)
- ✅ 5x faster plan adaptation (2 min vs 10 min)
- ✅ 3x faster refinement (5 min vs 15 min)

### Phase 3 Success
- ✅ Plan quality improvement: 85 → 91 average score (after 6 months)
- ✅ Time estimate variance: 25% → 15%
- ✅ Scope change rate: 35% → 23%
- ✅ Forgotten tasks: 15% → 5%
- ✅ Measurable continuous improvement

### Phase 4 Success (Future)
- ⏳ Task assignment accuracy: 95%+
- ⏳ Parallel execution time savings: 50-75%
- ⏳ Specialized expertise applied per task
- ⏳ Clear cross-persona ownership

---

## Rollout Plan

### Alpha Release (Phases 1-2)
**Timeline:** Weeks 1-4
**Audience:** Internal testing (Lloyd)
**Features:** Lloyd integration + planning flexibility
**Goal:** Validate core workflows, gather feedback

### Beta Release (Phase 3)
**Timeline:** Weeks 5-6
**Audience:** Early adopters
**Features:** Historical intelligence added
**Goal:** Build historical data, validate learning

### v2.0.0 Release (Phases 1-3 Complete)
**Timeline:** Week 7+
**Audience:** General availability
**Features:** All Phase 1-3 features
**Goal:** Production-ready, measurable improvement

### v2.1.0 Release (Phase 4)
**Timeline:** TBD (after persona stacking)
**Audience:** Multi-persona users
**Features:** Persona coordination
**Goal:** Full persona ecosystem

---

## Documentation Updates

### User-Facing Documentation
1. Update `PERSONAS-CREATED.md` - Add docs-expert v2.0.0 section
2. Update `my-guide.md` - Add new tools and workflows
3. Update `README.md` - Add v2.0.0 features
4. Create `docs-expert-v2-migration-guide.md` - Migration from v1.0.0

### Developer Documentation
1. Update API documentation - New tool signatures
2. Update schema documentation - New schemas
3. Create testing guide - How to test new features
4. Create contributing guide - How to extend docs-expert

### System Prompt
1. Update docs-expert.json system_prompt field (~8,000 lines in v2.0.0)
2. Add Lloyd Integration section
3. Add Planning Flexibility section
4. Add Historical Intelligence section
5. Add Persona Coordination section (future)

---

## Monitoring & Metrics

### Performance Monitoring
- Todo generation time (target: <2s)
- Progress sync time (target: <1s)
- Quick plan generation time (target: <2s)
- Plan update time (target: <1s)
- Refinement time (target: <5s per iteration)
- History query time (target: <500ms)

### Quality Monitoring
- Plan validation scores (target: 90+ average)
- Time estimate accuracy (target: ±15% variance)
- Scope change frequency (target: <25%)
- Forgotten task rate (target: <5%)
- Lesson application rate (target: >80%)

### Usage Monitoring
- Quick plan vs full plan ratio (target: 80/20)
- Plan updates per workorder (target: <2)
- Refinement iterations per plan (target: 2-3)
- Historical queries per plan (target: 1+)
- Lesson count growth (target: +2-3 per month)

---

## Post-Release Plan

### Week 8-9: Stabilization
- Monitor production usage
- Fix bugs and edge cases
- Optimize performance bottlenecks
- Gather user feedback

### Week 10-12: Iteration
- Improve AI refinement quality
- Enhance historical suggestions
- Optimize quick planning logic
- Add user-requested features

### Month 4+: Continuous Improvement
- Measure success metrics over time
- Analyze historical data trends
- Identify new optimization opportunities
- Plan v2.1.0 features

---

## Appendix: Tool Signatures

### Phase 1 Tools

**generate_todo_list:**
```python
def generate_todo_list(
    plan_path: str,
    workorder_id: str,
    mode: Literal["all", "remaining"] = "all"
) -> dict
```

**track_plan_execution:**
```python
def track_plan_execution(
    plan_path: str,
    workorder_id: str,
    todo_status: list[dict]
) -> dict
```

**execute_plan_interactive:**
```python
def execute_plan_interactive(
    plan_path: str,
    workorder_id: str,
    mode: Literal["step-by-step", "batch"] = "step-by-step"
) -> dict
```

### Phase 2 Tools

**quick_plan:**
```python
def quick_plan(
    feature_name: str,
    description: str,
    complexity: Literal["trivial", "simple", "moderate"] = "simple"
) -> dict
```

**update_plan:**
```python
def update_plan(
    plan_path: str,
    workorder_id: str,
    updates: dict,
    reason: str = None
) -> dict
```

**refine_plan_automated:**
```python
def refine_plan_automated(
    plan_path: str,
    workorder_id: str,
    validation_feedback: dict,
    mode: Literal["conservative", "aggressive"] = "conservative"
) -> dict
```

### Phase 3 Tools

**plan_history:**
```python
def plan_history(
    project_path: str = None,
    feature_type: str = None,
    date_range: dict = None,
    include_lessons: bool = True,
    limit: int = 20
) -> dict
```

**suggest_plan_improvements:**
```python
def suggest_plan_improvements(
    plan_path: str,
    workorder_id: str,
    feature_type: str = None,
    mode: Literal["lessons_only", "full_analysis"] = "full_analysis"
) -> dict
```

---

**Workorder:** WO-DOCS-EXPERT-V2-001
**Status:** 📋 Implementation Plan Complete, Ready to Execute
**Next Step:** Begin Phase 1 Implementation (Week 1)
