# Enhanced /stub Command - Implementation Guide

**Version:** 1.0.0
**Status:** ✅ Implemented
**Date:** December 26, 2025
**Purpose:** Document the enhanced `/stub` command that captures optional conversation context

---

## Overview

The `/stub` command is a lightweight way to capture a feature idea quickly while preserving relevant discussion context from the current conversation. It creates a `stub.json` file that serves as initial seed data for the full `/create-workorder` workflow.

**Key Feature:** Single command with *optional* context field - context is captured if the conversation has relevant discussion, omitted if the conversation is fresh.

---

## How It Works

### Flow Diagram

```
User: /stub
    ↓
Command: Ask for 4 fields (name, description, category, priority)
    ↓
Command: Scan conversation history for relevant context
    ↓
Decision: Is there relevant discussion in the conversation?
    ├─ YES → Include "context" field in stub.json
    └─ NO → Omit "context" field from stub.json
    ↓
File: Create coderef/workorder/{feature-name}/stub.json
    ↓
User: Later runs /create-workorder
    ↓
Workflow: Reads stub.json as seed data
    ↓
Workflow: Runs full gathering phase (still asks all questions)
    ↓
Complete: Feature context ready for planning
```

---

## Implementation Steps

### Step 1: Ask User for Feature Details

The command asks the user for 4 required fields:

1. **Feature name** - Slug format (lowercase, hyphens)
   - Example: `dark-mode-toggle`, `payment-retry-logic`, `user-profile-avatar`

2. **Description** - Brief 1-2 sentence summary
   - Example: `Allows users to toggle dark/light theme globally`

3. **Category** - Type of work (default: `idea`)
   - Options: `feature`, `fix`, `improvement`, `idea`, `refactor`

4. **Priority** - Importance level (default: `medium`)
   - Options: `low`, `medium`, `high`

### Step 2: Extract Context from Conversation

**CRITICAL STEP:** Before creating stub.json, the command must scan the entire conversation history.

**What to look for:**
- **Goals**: "the goal is...", "we want to...", "purpose is..."
- **Requirements**: "needs to...", "should...", "must...", requirement lists
- **Constraints**: "limitation:", "can't...", "must not...", technical constraints
- **Decisions**: "decided to...", "we chose...", technical decisions made
- **Discussion Points**: Alternative approaches considered, specific insights

**Context Extraction Examples:**

Example 1 - Relevant discussion found:
```
Conversation history:
- User: "We need a payment retry system"
- User: "It should retry 3 times with exponential backoff"
- User: "Must not retry if customer cancels"
- User: "Should update order status after each attempt"

Context extracted:
"Retry mechanism with 3 attempts and exponential backoff. Must not retry if customer cancels. Updates order status after each attempt."
```

Example 2 - No relevant discussion:
```
Conversation history:
- User: "/stub"
- (no prior discussion)

Context: OMITTED (conversation just started)
```

Example 3 - Partial discussion:
```
Conversation history:
- User: "I want to add analytics tracking"
- User: "Maybe we need this for the dashboard?"

Context extracted:
"Analytics tracking feature for dashboard visibility."
```

### Step 3: Create stub.json File

**Location:** `coderef/workorder/{feature-name}/stub.json`

**Format WITH context:**
```json
{
  "feature_name": "dark-mode-toggle",
  "description": "Allows users to toggle between dark and light themes globally across the application",
  "category": "feature",
  "priority": "medium",
  "context": "Discussion covered need for theme persistence across sessions, CSS variable approach preferred, must support system preference detection, accessibility requirements for contrast ratios",
  "created": "2025-12-26T10:30:00Z",
  "status": "stub"
}
```

**Format WITHOUT context:**
```json
{
  "feature_name": "quick-idea",
  "description": "A quick feature idea that came up",
  "category": "idea",
  "priority": "low",
  "created": "2025-12-26T10:30:00Z",
  "status": "stub"
}
```

### Step 4: Confirm to User

**Response message:**
```
Stubbed: coderef/workorder/{feature-name}/stub.json
Context captured from conversation.
```

or

```
Stubbed: coderef/workorder/{feature-name}/stub.json
No conversation context found (starting fresh).
```

---

## Example Usage Scenarios

### Scenario 1: Mid-Conversation Feature Idea (WITH Context)

```
User conversation:
"I'm thinking we need better error handling for API calls.
Specifically, we should show user-friendly messages instead of
raw error codes. And maybe log errors to a monitoring service?"

User: /stub

Command prompt:
- Feature name: api-error-handling
- Description: Improve error handling with user-friendly messages and monitoring
- Category: improvement
- Priority: high

Command action:
[Scans conversation, finds discussion about user-friendly messages and monitoring]

Creates: coderef/workorder/api-error-handling/stub.json
{
  "feature_name": "api-error-handling",
  "description": "Improve error handling with user-friendly messages and monitoring",
  "category": "improvement",
  "priority": "high",
  "context": "Need user-friendly error messages instead of raw codes. Should log errors to monitoring service for visibility. Discussed improving error UX.",
  "created": "2025-12-26T14:45:00Z",
  "status": "stub"
}

Response:
Stubbed: coderef/workorder/api-error-handling/stub.json
Context captured from conversation.
```

### Scenario 2: Fresh Start (WITHOUT Context)

```
User: /stub

Command prompt:
- Feature name: experimental-caching-layer
- Description: Explore Redis-based caching for performance
- Category: idea
- Priority: low

Command action:
[Scans conversation, finds no prior discussion about this feature]

Creates: coderef/workorder/experimental-caching-layer/stub.json
{
  "feature_name": "experimental-caching-layer",
  "description": "Explore Redis-based caching for performance",
  "category": "idea",
  "priority": "low",
  "created": "2025-12-26T14:50:00Z",
  "status": "stub"
}

Response:
Stubbed: coderef/workorder/experimental-caching-layer/stub.json
No conversation context found (starting fresh).
```

### Scenario 3: Complex Feature with Rich Context (WITH Context)

```
User conversation:
"We need to implement JWT-based authentication with refresh tokens.
Requirements:
- Access tokens valid for 15 minutes
- Refresh tokens valid for 7 days
- Must revoke tokens on logout
- Should support multi-device sessions
- Need to handle token rotation securely
Can't use third-party auth providers due to compliance constraints."

User: /stub

Command creates: coderef/workorder/jwt-auth-system/stub.json
{
  "feature_name": "jwt-auth-system",
  "description": "Implement JWT-based authentication with refresh tokens",
  "category": "feature",
  "priority": "high",
  "context": "Access tokens 15min, refresh tokens 7 days. Must revoke on logout, support multi-device sessions, handle token rotation securely. Cannot use third-party providers due to compliance. Specific timing and security requirements documented.",
  "created": "2025-12-26T15:00:00Z",
  "status": "stub"
}

Response:
Stubbed: coderef/workorder/jwt-auth-system/stub.json
Context captured from conversation.
```

---

## Integration with /create-workorder

When user later runs `/create-workorder {feature-name}`:

1. **Detection**: System detects existing `stub.json` in `coderef/workorder/{feature-name}/`

2. **Seed Data**: Uses stub.json as initial seed:
   - Pre-fills description field
   - Pre-sets category and priority
   - References context field for context

3. **Gathering Phase**: **STILL RUNS NORMALLY**
   - Asks all standard questions (may be prefilled from stub)
   - Allows user to modify/expand requirements
   - Captures constraints and out-of-scope items
   - Collects success criteria

4. **Result**: Complete context.json with full requirements

```
/create-workorder jwt-auth-system
    ↓
[Detects stub.json]
    ↓
[Uses stub fields as defaults/context]
    ↓
Gathering Phase (full questions still asked):
- Feature name: jwt-auth-system [prefilled]
- Description: [can be modified]
- Goal: [blank - user fills]
- Requirements: [blank - user lists]
- Constraints: [blank - user lists]
- Out of scope: [blank - user specifies]
    ↓
[System remembers: context field from stub.json for reference]
    ↓
Complete: context.json ready for analysis and planning
```

---

## Context Field Guidelines

### When to Include Context

Include the `context` field if the conversation contains:
- ✅ Specific discussion about this feature
- ✅ Goals or objectives mentioned
- ✅ Requirements or constraints listed
- ✅ Design decisions made
- ✅ Technical considerations discussed
- ✅ Alternatives evaluated

### When to Omit Context

Omit the `context` field if:
- ❌ Conversation just started (no prior discussion)
- ❌ Feature is a quick idea with no elaboration
- ❌ Discussion is tangential or unrelated
- ❌ No specific requirements mentioned

### Context Field Best Practices

1. **Length:** 2-4 sentences max
2. **Format:** Plain English, no JSON, no markdown
3. **Focus:** Goals, requirements, constraints, key decisions
4. **Clarity:** Use simple, direct language
5. **Completeness:** Include all important discussion points

---

## Key Differences from Previous Approach

### ❌ OLD APPROACH (Two Versions)
- Two separate implementations of /stub
- One with context capture, one without
- Complex logic branch based on conversation length
- User confusion about which version to use

### ✅ NEW APPROACH (Single Smart Command)
- ONE /stub command
- Automatically detects if context should be included
- Conditionally includes context field based on conversation
- User doesn't need to choose - the command is smart
- Simpler, cleaner, more intuitive

---

## File Structure After /stub Execution

```
coderef/workorder/
├── feature-name-1/
│   └── stub.json                    # Created by /stub
│
├── feature-name-2/
│   └── stub.json                    # Created by /stub
│
└── complex-feature/
    ├── stub.json                    # Created by /stub (with context)
    ├── context.json                 # Created by /create-workorder
    ├── analysis.json               # Created during analysis phase
    ├── plan.json                   # Created during plan creation
    └── DELIVERABLES.md             # Created during execution
```

---

## Technical Implementation Details

### Context Extraction Algorithm

The command should:

1. **Read Conversation History**
   - Access all messages in current conversation
   - Start from earliest message

2. **Pattern Matching**
   - Look for keywords: "goal", "require", "must", "should", "constraint", "decision"
   - Identify discussion blocks related to the feature

3. **Relevance Assessment**
   - If total relevant content > 2 sentences → Include context
   - If total relevant content ≤ 2 sentences or none → Omit context

4. **Summarization**
   - Capture 2-4 key points from discussion
   - Preserve requirements and constraints
   - Skip implementation details (those come in full gathering phase)

5. **JSON Creation**
   - Write stub.json with or without context field
   - Use ISO 8601 timestamp
   - Set status to "stub"

---

## Success Criteria

✅ **Implementation Complete When:**

1. `/stub` command asks for 4 required fields
2. Command scans conversation history for context
3. Context field conditionally included in stub.json
4. stub.json created in correct directory
5. User receives confirmation with context capture status
6. `/create-workorder` detects and uses stub.json as seed
7. Full gathering phase still runs (stub doesn't skip it)
8. No breaking changes to existing workflows

---

## Testing Checklist

- [ ] /stub works with fresh conversation (no context)
- [ ] /stub works with prior discussion (with context)
- [ ] Context field conditionally present/absent in JSON
- [ ] stub.json created in coderef/workorder/{feature}/
- [ ] /create-workorder detects stub.json
- [ ] Gathering phase still runs fully
- [ ] User confirmation message includes context status
- [ ] Multiple stubs can be created in same session
- [ ] Context extraction handles various discussion styles
- [ ] Timestamp format is ISO 8601

---

## Document Status

**Created:** 2025-12-26
**Status:** Implementation Guide for Enhanced /stub Command v1.0.0
**Author:** Claude Code AI
**References:**
- stub.md (slash command definition)
- gather_context tool (coderef-workflow)
- create_plan workflow

---

## Next Steps

After this implementation:

1. ✅ Enhanced /stub command deployed
2. ⏳ User tests with various conversation scenarios
3. ⏳ Refinement based on real-world usage
4. ⏳ Integration with other ecosystem tools
