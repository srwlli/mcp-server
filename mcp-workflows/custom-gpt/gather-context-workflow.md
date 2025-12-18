# Gather Context Workflow

Interactive Q&A flow for capturing feature requirements before implementation planning.

## Purpose

Gather feature requirements and context to create a structured briefing (context.json) that captures WHAT the user wants before diving into HOW to implement it.

## Workflow Steps

### Step 1: Get Feature Name

Ask for the feature name using alphanumeric characters, hyphens, or underscores only.

Examples: "user-authentication", "dark-mode-toggle", "payment-integration"

### Step 2: Get Feature Goal and Description

**Question 1: What's the main goal?**
- Improve UX - Enhance user experience
- Add functionality - New capability or feature
- Fix bugs - Resolve existing issues
- Performance - Speed or efficiency gains

**Question 2: Describe the feature**
User provides a brief description of what they want to build.

### Step 3: Gather Requirements (Multi-Select)

**Question: What are the must-have requirements?**
Select all that apply:
- User authentication - Login/logout functionality
- Data persistence - Save to database
- API integration - Connect to external service
- UI components - Visual interface elements
- File operations - Read/write files
- Real-time updates - WebSocket or SSE
- Search functionality - Search and filter
- Notifications - User alerts or messages

User can add custom requirements as well.

### Step 4: Identify Out of Scope Items

**Question: Are there features explicitly NOT included in this phase?**

If yes, select exclusions:
- OAuth/Social login - Deferred to future phase
- Two-factor auth - Deferred to future phase
- Advanced analytics - Deferred to future phase
- Mobile app - Deferred to future phase
- Internationalization - Deferred to future phase

### Step 5: Gather Constraints (Multi-Select)

**Question: Are there technical or business constraints?**
Select all that apply:
- Must work with PostgreSQL - Database compatibility
- Must work with MySQL - Database compatibility
- Must support mobile - Responsive design required
- Performance < 100ms - Speed requirement
- Backward compatible - Don't break existing features
- Must work offline - Offline-first capability
- Security compliant - GDPR, HIPAA, etc.
- Budget limited - Cost constraints

### Step 6: Generate context.json

After gathering all responses, create the context file:

```json
{
  "feature_name": "user-authentication",
  "description": "Add user login and registration system",
  "goal": "Add functionality - Enable user accounts",
  "requirements": [
    "User authentication",
    "Data persistence",
    "UI components"
  ],
  "out_of_scope": [
    "OAuth/Social login",
    "Two-factor auth"
  ],
  "constraints": [
    "Must work with PostgreSQL",
    "Backward compatible"
  ]
}
```

### Step 7: Present Summary

After creating context.json, summarize:
- Feature name
- Goal
- Requirements count
- Out of scope count
- Constraints count
- File location

## Key Principle

This is REQUIREMENTS GATHERING, not implementation planning.
Keep it simple - just capture WHAT and WHY, not HOW.

## Benefits

- Structured input with clear options
- Multi-select for efficient requirement gathering
- Faster than free-form text discussions
- Validated format ensures consistency
- User-friendly visual choices
