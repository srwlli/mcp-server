# CodeRef Persona - Context Gathering Questionnaire

**Purpose:** Gather detailed context about the coderef-mcp system to create a specialized "mcp-expert:coderef" persona.

**Date:** 2025-10-18
**Target Persona:** mcp-expert:coderef (specialized MCP expert for CodeRef system)

---

## Section 1: System Overview

**Q1.1:** What is the primary purpose of the coderef-mcp server?
- [ ] Semantic code reference analysis and validation
- [ ] Code navigation and relationship mapping
- [ ] Code documentation generation
- [ ] Other: ___________

**Q1.2:** What problem does CodeRef solve?
```
[Brief description of the core problem]
```

**Q1.3:** What are the key use cases for coderef-mcp?
```
1.
2.
3.
```

**Q1.4:** What is the CodeRef reference format/syntax?
```
Example: REF-001, ARCH-042, QUA-003, etc.
Pattern: [TYPE]-[NUMBER]
```

---

## Section 2: Tools & Capabilities

**Q2.1:** List all 6 coderef-mcp tools and their purposes:

1. **mcp__coderef__query**
   - Purpose: ___________
   - Key parameters: ___________
   - Output format: ___________

2. **mcp__coderef__analyze**
   - Purpose: ___________
   - Analysis types: [impact, deep, coverage, complexity]
   - Depth range: 1-10
   - When to use: ___________

3. **mcp__coderef__validate**
   - Purpose: ___________
   - Validates: [format, structure, existence?]
   - Use cases: ___________

4. **mcp__coderef__batch_validate**
   - Purpose: ___________
   - Parallel vs sequential: ___________
   - Max workers: ___________

5. **mcp__coderef__generate_docs**
   - Purpose: ___________
   - Doc types: [summary, detailed, api]
   - When to use each type: ___________

6. **mcp__coderef__audit**
   - Purpose: ___________
   - Audit types: [validation, coverage, performance]
   - Scope options: [all, element, path, type]

**Q2.2:** Which tools are most commonly used together?
```
Common workflows:
1. Tool A → Tool B → Tool C
2.
```

**Q2.3:** What are the performance characteristics of each tool?
```
- query: Fast/Medium/Slow
- analyze: Fast/Medium/Slow (varies by depth)
- validate: Fast/Medium/Slow
- batch_validate: Fast/Medium/Slow (parallel vs sequential)
- generate_docs: Fast/Medium/Slow
- audit: Fast/Medium/Slow (varies by scope)
```

---

## Section 3: CodeRef Reference System

**Q3.1:** What are the different CodeRef reference types/designators?
```
Examples:
- REF-XXX: [Description]
- ARCH-XXX: [Description]
- QUA-XXX: [Description]
- [Other types]
```

**Q3.2:** What is the structure of a CodeRef reference?
```
Format: [TYPE]-[NUMBER]
Type: [Pattern/Rules]
Number: [Pattern/Rules]
Examples: REF-001, ARCH-042
```

**Q3.3:** What metadata is associated with CodeRef elements?
```
- File path
- Line number
- Element type (function, class, module, etc.)
- Relationships (calls, imports, dependencies)
- Documentation status
- Other: ___________
```

**Q3.4:** What kinds of relationships can CodeRef track?
```
- Calls (function A calls function B)
- Imports (module A imports module B)
- Dependencies (component A depends on component B)
- Inheritance (class A extends class B)
- Other: ___________
```

---

## Section 4: Common Workflows

**Q4.1:** Describe the typical workflow for querying CodeRef elements:
```
Step 1:
Step 2:
Step 3:
```

**Q4.2:** Describe the workflow for impact analysis:
```
Step 1:
Step 2:
Step 3:
Common depth level: ___________
Include test impact? Yes/No
```

**Q4.3:** Describe the workflow for validating references:
```
Single reference: Use mcp__coderef__validate
Multiple references: Use mcp__coderef__batch_validate
Validate existence? Yes/No
When to use parallel vs sequential: ___________
```

**Q4.4:** Describe the workflow for auditing a codebase:
```
Scope options: all, element, path, type
Audit types: validation, coverage, performance
When to run full audit vs targeted audit: ___________
```

---

## Section 5: Best Practices

**Q5.1:** What are the best practices for using the query tool?
```
- Pattern syntax: ___________
- Filter usage: ___________
- Result limits: ___________
- Include relationships: Yes/No (when?)
- Include metadata: Yes/No (when?)
- Include source: Yes/No (when?)
```

**Q5.2:** What are the best practices for analysis depth selection?
```
- Depth 1-3: [Use case]
- Depth 4-6: [Use case]
- Depth 7-10: [Use case]
Performance implications: ___________
```

**Q5.3:** What are common pitfalls or anti-patterns to avoid?
```
1.
2.
3.
```

**Q5.4:** What are the performance optimization strategies?
```
- When to use batch operations: ___________
- Parallel vs sequential: ___________
- Caching considerations: ___________
- Query optimization: ___________
```

---

## Section 6: Integration & Dependencies

**Q6.1:** How does coderef-mcp integrate with docs-mcp?
```
- Shared workflows: ___________
- Tool combinations: ___________
- Reference tracking in documentation: ___________
```

**Q6.2:** How does coderef-mcp integrate with other MCP servers?
```
- personas-mcp: ___________
- hello-world-mcp: ___________
```

**Q6.3:** What external dependencies does coderef-mcp have?
```
- Python packages: ___________
- Database/storage: ___________
- File system requirements: ___________
```

**Q6.4:** What are the storage/data formats used?
```
- CodeRef index format: ___________
- Metadata storage: ___________
- Cache format: ___________
```

---

## Section 7: Error Handling & Edge Cases

**Q7.1:** What are common error scenarios?
```
1. Reference not found: ___________
2. Invalid reference format: ___________
3. Circular dependencies: ___________
4. Missing metadata: ___________
```

**Q7.2:** How should the persona guide users when errors occur?
```
- Reference not found → Action: ___________
- Format validation fails → Action: ___________
- Analysis depth too high → Action: ___________
```

**Q7.3:** What are edge cases to be aware of?
```
1.
2.
3.
```

---

## Section 8: Persona Behavior Definition

**Q8.1:** What communication style should the coderef persona use?
```
- Technical level: Expert/Intermediate/Beginner-friendly
- Tone: Formal/Professional/Conversational
- Reference format examples: Always/Sometimes/Never
- Tool recommendations: Proactive/Reactive
```

**Q8.2:** What problem-solving approach should the persona take?
```
- Query first, analyze second? Yes/No
- Validate before analysis? Yes/No
- Always check coverage? Yes/No
- Default analysis depth: ___________
```

**Q8.3:** What are the persona's preferred tool usage patterns?
```
1. For finding code elements → Use: ___________
2. For understanding impact → Use: ___________
3. For validation → Use: ___________
4. For documentation → Use: ___________
5. For auditing → Use: ___________
6. For batch operations → Use: ___________
```

**Q8.4:** What expertise areas should the persona emphasize?
```
- CodeRef reference syntax and structure
- Tool selection and workflow optimization
- Impact analysis and dependency mapping
- Validation strategies (single vs batch)
- Documentation generation patterns
- Audit scoping and interpretation
- Performance optimization
- Integration with docs-mcp and other tools
- Error handling and troubleshooting
- Other: ___________
```

---

## Section 9: Example Scenarios

**Q9.1:** Scenario: User wants to find all usages of a function
```
Recommended workflow:
1. Tool: ___________
2. Parameters: ___________
3. Follow-up: ___________
```

**Q9.2:** Scenario: User wants to assess impact of changing a component
```
Recommended workflow:
1. Tool: ___________
2. Analysis type: ___________
3. Depth: ___________
4. Include test impact: Yes/No
```

**Q9.3:** Scenario: User has 50 references to validate
```
Recommended workflow:
1. Tool: ___________
2. Parallel: Yes/No
3. Max workers: ___________
4. Timeout: ___________
```

**Q9.4:** Scenario: User wants comprehensive codebase health check
```
Recommended workflow:
1. Tool: ___________
2. Audit type: ___________
3. Scope: ___________
4. Include issues: Yes/No
```

---

## Section 10: Persona System Prompt Elements

**Q10.1:** What should the persona's opening identity statement be?
```
Example: "I am an MCP expert specializing in the CodeRef semantic analysis system, with deep knowledge of reference formats, impact analysis, and validation workflows."
```

**Q10.2:** What are the persona's core competencies (5-7 bullet points)?
```
1.
2.
3.
4.
5.
```

**Q10.3:** What are the persona's key use cases (3-5 examples)?
```
1.
2.
3.
```

**Q10.4:** What is the persona's unique value proposition?
```
[What makes this persona uniquely valuable compared to base mcp-expert?]
```

---

## Section 11: Additional Context

**Q11.1:** Are there any coderef-mcp documentation files to reference?
```
- README: Yes/No (path: _________)
- Architecture docs: Yes/No (path: _________)
- API docs: Yes/No (path: _________)
- Examples: Yes/No (path: _________)
```

**Q11.2:** Are there specific coding patterns or conventions in coderef-mcp?
```
- Error handling patterns: ___________
- Response formats: ___________
- Logging conventions: ___________
```

**Q11.3:** What are the future planned features or enhancements?
```
1.
2.
3.
```

**Q11.4:** Any other context the persona should know?
```
[Free-form notes]
```

---

## Next Steps

Once this questionnaire is completed:

1. ✅ Review answers for completeness
2. ✅ Generate persona definition JSON file
3. ✅ Create persona system prompt from answers
4. ✅ Define expertise areas list
5. ✅ Define use cases list
6. ✅ Define behavior patterns (communication, problem-solving, tool usage)
7. ✅ Save to `personas-mcp/personas/specialized/mcp-expert-coderef.json`
8. ✅ Test persona activation
9. ✅ Validate persona guides users effectively

---

**Questionnaire Completed By:** _____________
**Date:** _____________
**Reviewed By:** _____________
**Persona Version:** 1.0.0
