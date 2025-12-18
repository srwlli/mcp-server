# Lloyd GPT Setup Guide

Step-by-step instructions for configuring the Lloyd Custom GPT in OpenAI's GPT Builder.

## Prerequisites

- OpenAI ChatGPT Plus or Enterprise subscription
- Access to GPT Builder (chat.openai.com/gpts/editor)
- Files from this repository ready for upload

## Setup Steps

### Step 1: Create New GPT

1. Go to [chat.openai.com/gpts/editor](https://chat.openai.com/gpts/editor)
2. Click "Create a GPT"
3. Select the "Configure" tab (not "Create")

### Step 2: Basic Information

| Field | Value |
|-------|-------|
| **Name** | `lloyd` |
| **Description** | Lloyd guides you through structured project planning - from scoping to context gathering to implementation plans to deliverables. It replicates the /start-feature workflow in a conversational format. |

### Step 3: Instructions

1. Open `INSTRUCTIONS.md` from this repository
2. Copy everything between the `---` markers (the actual instructions content)
3. Paste into the Instructions field in GPT Builder

**Character limit**: ~8,000 characters. The provided instructions should fit.

### Step 4: Conversation Starters

Add these conversation starters (copy from `lloyd-gpt-config.json`):

1. `Help me plan a new feature from scratch - let's start with scoping.`
2. `I have a project idea. Guide me through creating context, requirements, and a plan.`
3. `Review my project requirements and help structure them into an implementation plan.`
4. `Create a deliverables checklist for my feature based on these requirements.`
5. `Walk me through the full planning workflow: scope → context → plan → deliverables.`

### Step 5: Knowledge Files

1. Click "Upload files" in the Knowledge section
2. Upload files listed in `KNOWLEDGE-FILES.md`:
   - start-feature-workflow.md
   - gather-context-workflow.md
   - plan-template.json
   - deliverables-template.md
3. Optional: Add example-context.json and example-plan.json

### Step 6: Capabilities

Configure capabilities as follows:

| Capability | Setting | Reason |
|------------|---------|--------|
| **Web Search** | ON | Fetch best practices, documentation |
| **Canvas** | ON | Edit plans, checklists interactively |
| **DALL-E Image Generation** | OFF | Not needed for planning |
| **Code Interpreter** | ON | Parse uploaded files, generate JSON |

### Step 7: Model Selection

- **Recommended**: GPT-4o (default)
- **Alternative**: GPT-4o mini (faster, cheaper)

Leave as default unless you have specific requirements.

### Step 8: Actions (Optional)

Leave empty unless you have internal APIs to connect.

Future integration possibilities:
- `POST /gather-context` - Submit context to your backend
- `POST /create-plan` - Generate plans via API
- `GET /templates` - Fetch latest templates

### Step 9: Save and Test

1. Click "Save" (or "Update" if editing)
2. Choose visibility:
   - **Only me**: Private testing
   - **Anyone with link**: Share with team
   - **Public**: List in GPT store
3. Click "Confirm"

## Testing Checklist

After saving, verify Lloyd works correctly:

- [ ] Start a new chat with Lloyd
- [ ] Try conversation starter #1 (scoping)
- [ ] Verify Lloyd asks targeted questions
- [ ] Complete Phase 1 (Scoping)
- [ ] Verify Lloyd summarizes before moving on
- [ ] Complete Phase 2 (Context Gathering)
- [ ] Verify structured output format
- [ ] Request implementation plan
- [ ] Verify tasks have IDs and structure
- [ ] Request deliverables checklist
- [ ] Verify checklist format is correct

## Troubleshooting

### GPT doesn't follow workflow
- Check Instructions were copied completely
- Verify no character limit truncation
- Re-paste instructions

### GPT doesn't reference knowledge files
- Ensure files uploaded successfully
- Try asking "What files do you have access to?"
- Re-upload if needed

### Conversation starters don't appear
- Ensure you added at least 2 starters
- Save and refresh the page

### Output format is wrong
- Check INTERACTION STYLE section in instructions
- Add more explicit format examples

## Updating Lloyd

When workflow changes:

1. Update `INSTRUCTIONS.md` with new content
2. Re-copy to GPT Instructions field
3. Update knowledge files if templates changed
4. Save GPT
5. Test with checklist above

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-06 | Initial release |
