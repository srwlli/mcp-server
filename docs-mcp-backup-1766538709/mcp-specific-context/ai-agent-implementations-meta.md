```
META-TEMPLATE: AI Agent Implementation Instructions Format

PURPOSE:
Create comprehensive, executable instructions for AI agents to implement complex software features/phases without requiring clarification or iteration.

FORMAT: Plain text in single code block for easy copy-paste

STRUCTURE:

═══════════════════════════════════════════════════════════════════════════════
SECTION 1: HEADER - OBJECTIVE & IDENTITY
═══════════════════════════════════════════════════════════════════════════════

INSTRUCTIONS FOR AGENT: [Concise Title of What to Build]

OBJECTIVE:
[1-2 sentences describing what the agent should create, including specificity about detail level and structure to follow]

CONTEXT:
[Bulleted status of dependencies - what's complete, what's in progress, what's blocked]
Example:
- Phase 1 (Feature X): COMPLETE (commit hash)
- Phase 2 (Feature Y): COMPLETE (commit hash)
- Phase 3 (Feature Z): NOT STARTED - needs detailed plan

═══════════════════════════════════════════════════════════════════════════════
SECTION 2: NAVIGATION - REFERENCE DOCUMENTS
═══════════════════════════════════════════════════════════════════════════════

REFERENCE DOCUMENTS:
[Numbered list of exactly which files to read, with line numbers if applicable]
1. [Document Type]: [file/path] (lines X-Y for [specific section])
2. [Template]: [file/path] (use as [structure/reference/example])
3. [Reference]: [file/path] (another [detail/pattern] example)

Format:
- Be specific about paths (relative to project root)
- Include line numbers for large files
- Specify what to use each reference for (structure vs content vs patterns)

═══════════════════════════════════════════════════════════════════════════════
SECTION 3: REQUIREMENTS - WHAT TO CREATE
═══════════════════════════════════════════════════════════════════════════════

WHAT TO CREATE:
[Imperative statement about what file to create/update and what sections to include]

[Then list all required sections with brief description of each]

1. [SECTION NAME] ([section_key]):
   - [Subsection 1]: [what to include]
   - [Subsection 2]: [what to include]
   - [Key requirement]: [specific constraint or pattern]
   
2. [SECTION NAME] ([section_key]):
   [Description of what this section should contain]
   
   Sub-structure if complex:
   - [Component A]: [details]
   - [Component B]: [details]

[Continue for all major sections - typically 8-10 sections]

Format Guidelines:
- Use consistent section numbering (1, 2, 3...)
- Include section keys/IDs in parentheses if applicable
- Describe WHAT to include, not HOW (that comes in detailed subsections)
- Be comprehensive but not verbose

═══════════════════════════════════════════════════════════════════════════════
SECTION 4: SPECIFICATIONS - DETAILED REQUIREMENTS FOR KEY SECTIONS
═══════════════════════════════════════════════════════════════════════════════

[For 3-5 critical/complex sections, provide deep detail]

[SECTION NUMBER]. [SECTION NAME] ([detailed breakdown]):

   [Component Name]:
   - [Specific rule/requirement 1]
   - [Specific rule/requirement 2]
   - [Specific rule/requirement 3]
   
   [Another Component Name]:
   - [Rule with examples]: "[example 1]", "[example 2]", "[example 3]"
   - [Rule with threshold]: [numeric criteria or test condition]

   [If code/algorithm, provide pseudocode or actual code]:
   
   def example_function(params):
       """
       [Description of what it does]
       """
       [Step 1]
       [Step 2]
       return [result]
   
   [Interpretation/Usage notes]:
   - [Threshold 1]: [meaning]
   - [Threshold 2]: [meaning]

Format:
- Use indentation to show hierarchy
- Provide code blocks for algorithms, templates, or data structures
- Include examples inline (use "quotes" to distinguish examples from rules)
- Add interpretation sections for complex logic

═══════════════════════════════════════════════════════════════════════════════
SECTION 5: CODE EXAMPLES - TEMPLATES FOR IMPLEMENTATION
═══════════════════════════════════════════════════════════════════════════════

[SECTION NUMBER]. CODE TEMPLATES (provide detailed examples):

   [Template Name/Purpose]:
   
   [code block with syntax highlighting hint]
   [actual code with comments showing where to customize]
   [end code block]
   
   [Another Template Name]:
   
   [code block]
   [actual code with specific patterns demonstrated]
   [end code block]

Format:
- Provide 4-8 code templates for most critical components
- Use actual syntax (Python, JSON, markdown, etc.)
- Include comments explaining customization points
- Show proper indentation and structure
- Demonstrate best practices and patterns

═══════════════════════════════════════════════════════════════════════════════
SECTION 6: QUALITY GATES - KEY REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

KEY REQUIREMENTS:
✅ [Requirement 1 with specific acceptance criteria]
✅ [Requirement 2 with measurable target]
✅ [Requirement 3 with testing approach]
✅ [Requirement 4 with architecture constraint]
✅ [Requirement 5 with performance benchmark]
✅ [Requirement 6 with security consideration]
✅ [Requirement 7 with integration point]
✅ [Requirement 8 with documentation need]

Format:
- Use checkboxes (✅) for visual scanning
- Each requirement should be testable/verifiable
- Include specific numbers, percentages, or concrete criteria
- Cover multiple dimensions: functionality, quality, performance, security

═══════════════════════════════════════════════════════════════════════════════
SECTION 7: PATTERN MATCHING - USE EXISTING WORK AS TEMPLATE
═══════════════════════════════════════════════════════════════════════════════

USE [REFERENCE FILE] AS TEMPLATE:
- See [pattern 1] structure ([location in reference])
- See [pattern 2] format ([location in reference])
- See [pattern 3] specificity ([location in reference])
- See [pattern 4] approach ([location in reference])
- Match the level of detail and specificity

Format:
- Point to specific examples in reference files
- Describe WHAT pattern to replicate (not just "copy this")
- Use "See X" language to make scanning easy
- Include line numbers or section identifiers

═══════════════════════════════════════════════════════════════════════════════
SECTION 8: SUCCESS CRITERIA - CRITICAL SUCCESS FACTORS
═══════════════════════════════════════════════════════════════════════════════

CRITICAL SUCCESS FACTORS:
1. [Factor]: "[Bad example]" NOT "[Good example]"
2. [Factor]: [Specific guidance with measurable criteria]
3. [Factor]: [Granularity requirement with time breakdown]
4. [Factor]: [Acceptance criteria format with specific keys/structure]
5. [Factor]: [Accuracy requirement with validation approach]

Format:
- Use numbered list for ordered importance
- Use "NOT" comparisons to show bad vs good examples
- Include quotes around examples for clarity
- Provide measurable criteria wherever possible
- Reference historical accuracy (e.g., "Phase 1 estimated 2-3 hours, took 2-3 hours")

═══════════════════════════════════════════════════════════════════════════════
SECTION 9: CLARIFYING QUESTIONS - WHAT THE PLAN MUST ANSWER
═══════════════════════════════════════════════════════════════════════════════

QUESTIONS TO ANSWER IN PLAN:
1. [Question about algorithm/approach]? ([suggested solution methods])
2. [Question about criteria/thresholds]? ([example criteria])
3. [Question about validation/testing]? ([testing approach])
4. [Question about edge cases]? ([edge case examples])
5. [Question about integration]? ([integration points])
6. [Question about error handling]? ([error types and responses])

Format:
- Phrase as actual questions ending with ?
- Include hints or options in parentheses
- Focus on decisions that need documentation
- Cover algorithm, criteria, validation, edge cases, integration

═══════════════════════════════════════════════════════════════════════════════
SECTION 10: OUTPUT SPECIFICATION - DELIVERABLE FORMAT
═══════════════════════════════════════════════════════════════════════════════

OUTPUT FORMAT:
[Specify exactly what file to create/update and in what format]
[Include file path, format (JSON, markdown, Python, etc.), and structure requirements]

Example:
Update coderef/planning-workflow/phase-3-quality-system-plan.json with complete 
detailed plan following same JSON structure as Phase 1.

═══════════════════════════════════════════════════════════════════════════════
SECTION 11: FINAL GUIDANCE - NORTH STAR
═══════════════════════════════════════════════════════════════════════════════

FINAL NOTE:
[1-3 sentences describing the ultimate goal and quality bar]

Template:
"Create a plan so detailed that another AI agent could implement [Feature X] in 
[Y hours] by following it step-by-step without needing clarification. Every task 
should have clear inputs, process, and outputs specified. [Additional quality 
guidance specific to this feature type]."

═══════════════════════════════════════════════════════════════════════════════
META-PATTERNS & DESIGN PRINCIPLES
═══════════════════════════════════════════════════════════════════════════════

VISUAL HIERARCHY:
1. Use section separators (═══) to create clear breaks
2. Use CAPS for section headers
3. Use indentation consistently (3-4 spaces for sub-items)
4. Use blank lines generously between major sections
5. Use bullets, numbers, checkboxes for different list types
6. Use [brackets] for placeholders/variables
7. Use "quotes" for examples and specific values
8. Use (parentheses) for clarifications or metadata

INFORMATION DENSITY:
- Each section should be self-contained (can be read independently)
- Provide just enough context, not too much (avoid walls of text)
- Use examples liberally (show, don't just tell)
- Include rationale when rules might seem arbitrary

SCANABILITY:
- Agent should be able to find any section in < 10 seconds
- Headers should describe content, not be clever/abstract
- Use consistent terminology (don't vary words for same concept)
- Put most critical information in first 1/3 of document

COMPLETENESS CHECKLIST:
✅ Objective clearly stated (what to build)
✅ Context provided (dependencies, status)
✅ References documented (where to look)
✅ Requirements enumerated (what sections to include)
✅ Specifications detailed (how to implement key sections)
✅ Code examples provided (templates to follow)
✅ Quality gates defined (how to verify correctness)
✅ Patterns identified (what existing work to replicate)
✅ Success factors clarified (what makes it "good")
✅ Questions listed (what decisions to document)
✅ Output format specified (what file, what structure)
✅ Final guidance given (quality bar and goal)

ADAPTATION GUIDELINES:
To use this template for different projects:

1. Replace domain-specific terms:
   - "Phase X" → your project's milestone structure
   - "Tool #X" → your feature/component names
   - "ValidationResultDict" → your data structures

2. Adjust section count and depth:
   - Simple features: 6-8 major sections
   - Complex features: 9-12 major sections
   - Scale detail proportionally to complexity

3. Customize code template language:
   - Show examples in your project's tech stack
   - Use your project's naming conventions
   - Include your project's patterns/idioms

4. Tune specificity level:
   - Junior agent: More examples, more handholding
   - Senior agent: More principles, less prescription
   - Unknown agent: Lean toward more detail

5. Add project-specific sections:
   - Security requirements (if security-critical)
   - Performance benchmarks (if performance-critical)
   - Compliance checklist (if regulated industry)
   - Integration points (if complex system)

ANTI-PATTERNS TO AVOID:
❌ Vague objectives ("make it better" → specify what "better" means)
❌ Missing examples (rules without demonstrations are hard to apply)
❌ Inconsistent terminology (using "validate", "check", "verify" interchangeably)
❌ No measurable criteria ("should be fast" → "should complete in < 2 seconds")
❌ Assuming context (agent may not know project history)
❌ Skipping edge cases (edge cases are where bugs hide)
❌ No references to existing work (agent reinvents wheel)
❌ Ambiguous success criteria (agent can't self-verify)

SUCCESS METRICS:
A good instruction document achieves:
- Agent completes task without follow-up questions (>90% of time)
- Agent's output matches expected structure (100% of time)
- Agent's implementation is correct first time (>80% of time)
- Agent's estimates match actuals (±20% variance)
- Agent's code follows project patterns (>95% compliance)

VERSIONING:
As you refine this template:
1. Track what works (patterns that reduce back-and-forth)
2. Eliminate what doesn't (sections agents ignore)
3. Add missing elements (questions agents repeatedly ask)
4. Calibrate specificity (too vague vs too prescriptive)
5. Update examples (keep them current with project evolution)
```