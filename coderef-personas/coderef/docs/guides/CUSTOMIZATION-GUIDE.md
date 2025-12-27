# Custom Persona Creation Guide

**Version:** 1.4.0
**Feature:** Custom Persona Creation (WO-CREATE-CUSTOM-PERSONA-001)
**Last Updated:** 2025-10-23

---

## Overview

The custom persona creation feature allows you to create specialized expert personas tailored to your unique needs without writing JSON or system prompts manually. Simply provide high-level inputs (expertise areas, communication style, use cases), and the system generates a complete persona definition with a comprehensive system prompt.

## Quick Start

### 1. Use the Slash Command

The easiest way to create a custom persona is using the `/create-persona` slash command:

```
/create-persona
```

Then call the `create_custom_persona` MCP tool with your inputs.

### 2. Minimal Example

```json
{
  "name": "api-expert",
  "description": "REST API design and development specialist focusing on best practices and scalability",
  "expertise": [
    "RESTful API architecture",
    "OpenAPI specification",
    "API security (OAuth, JWT)",
    "Rate limiting and throttling",
    "API versioning strategies"
  ],
  "use_cases": [
    "Designing new API endpoints",
    "Reviewing API architecture",
    "Implementing authentication flows",
    "Optimizing API performance",
    "Writing API documentation"
  ],
  "communication_style": "Professional and technical, uses concrete examples and references industry standards like REST, OpenAPI, and OAuth specifications"
}
```

### 3. Activate Your Persona

```
use_persona('api-expert')
```

Now Claude will respond with API design expertise!

---

## Field Reference

### Required Fields

#### `name` (string)
- **Format:** Lowercase alphanumeric, hyphens, underscores only
- **Length:** 3-50 characters
- **Uniqueness:** Must not conflict with existing base personas
- **Example:** `"api-expert"`, `"ml-specialist"`, `"devops-guru"`

#### `description` (string)
- **Purpose:** One-sentence role description
- **Length:** 20-200 characters
- **Tips:** Clearly state domain and focus
- **Example:** `"REST API design and development specialist focusing on best practices and scalability"`

#### `expertise` (array)
- **Purpose:** List of expertise areas
- **Count:** 3-10 items
- **Tips:** Be specific, not generic. "RESTful API architecture" > "APIs"
- **Example:**
  ```json
  [
    "RESTful API architecture",
    "OpenAPI 3.0 specification",
    "API security best practices"
  ]
  ```

#### `use_cases` (array)
- **Purpose:** Scenarios where this persona is valuable
- **Count:** 3-10 items
- **Tips:** Start with action verbs (Designing, Reviewing, Implementing)
- **Example:**
  ```json
  [
    "Designing new API endpoints",
    "Reviewing API security",
    "Implementing rate limiting"
  ]
  ```

#### `communication_style` (string)
- **Purpose:** How this persona communicates
- **Length:** 20-200 characters
- **Tips:** Include tone, approach, and reference style
- **Example:** `"Professional and technical, uses concrete examples and references industry standards"`

### Optional Fields

#### `problem_solving` (string)
- **Purpose:** Problem-solving approach
- **Length:** Max 200 characters
- **Example:** `"Systematic approach starting with requirements analysis, then design patterns, implementation, and testing"`

#### `tool_usage` (string)
- **Purpose:** How persona uses tools
- **Length:** Max 200 characters
- **Example:** `"Leverages docs-mcp tools for planning, uses OpenAPI validation tools, references Postman for testing"`

#### `specializations` (array)
- **Purpose:** Specialized sub-areas
- **Count:** Max 5 items
- **Example:** `["GraphQL APIs", "Microservices patterns", "API gateways"]`

#### `key_principles` (array)
- **Purpose:** Guiding principles
- **Count:** Max 10 items
- **Example:** `["Design for backward compatibility", "Security by default", "Clear error messages"]`

#### `example_responses` (object)
- **Purpose:** Example Q&A pairs
- **Count:** Max 3 pairs
- **Format:** `{"Question": "Answer"}`
- **Example:**
  ```json
  {
    "What is REST?": "REST is an architectural style for distributed systems based on stateless client-server communication",
    "How do I version APIs?": "Use semantic versioning in the URI path (e.g., /v1/, /v2/) for major breaking changes"
  }
  ```

---

## Validation Pipeline

Your inputs go through 3 validation stages:

### Stage 1: Schema Validation
- Checks required fields present
- Validates field types and lengths
- Ensures name format compliance
- Verifies array size constraints

### Stage 2: Semantic Validation
- **Uniqueness:** Name doesn't conflict with base personas
- **Coherence:** Expertise aligns with description
- **Quality:** No generic/vague descriptions
- **Consistency:** Use cases match expertise

### Stage 3: Quality Validation
- **Coverage:** Recommends 5+ expertise areas, 5+ use cases
- **Completeness:** Suggests optional fields if missing
- **Specificity:** Warns about brief (1-2 word) expertise items
- **Actionability:** Checks use cases describe concrete help

---

## Best Practices

### 1. Be Specific

❌ **Bad:**
```json
{
  "expertise": ["APIs", "Testing", "Documentation"]
}
```

✅ **Good:**
```json
{
  "expertise": [
    "RESTful API architecture with OpenAPI 3.0",
    "Integration testing with Postman and Newman",
    "API documentation using Swagger UI and Redoc"
  ]
}
```

### 2. Define Clear Use Cases

❌ **Bad:**
```json
{
  "use_cases": ["Helping with APIs", "Doing testing", "Other tasks"]
}
```

✅ **Good:**
```json
{
  "use_cases": [
    "Designing RESTful endpoints with proper HTTP methods",
    "Implementing JWT-based authentication flows",
    "Writing OpenAPI specifications for API documentation"
  ]
}
```

### 3. Rich Communication Style

❌ **Bad:**
```json
{
  "communication_style": "Professional and helpful"
}
```

✅ **Good:**
```json
{
  "communication_style": "Professional and technical, uses concrete code examples, references industry standards like REST, OpenAPI 3.0, and OAuth 2.0 specifications, provides actionable recommendations"
}
```

### 4. Populate Optional Fields

For richer personas, add:
- `problem_solving`: Describe your approach
- `tool_usage`: Explain which tools and how
- `specializations`: List niche sub-areas
- `key_principles`: State guiding philosophies
- `example_responses`: Provide sample Q&A

---

## Example Personas

### Example 1: Machine Learning Expert

```json
{
  "name": "ml-expert",
  "description": "Machine learning specialist focusing on model training, deployment, and MLOps best practices",
  "expertise": [
    "Deep learning architectures (CNNs, RNNs, Transformers)",
    "Model training and hyperparameter tuning",
    "ML model deployment and serving",
    "MLOps and experiment tracking",
    "Feature engineering and data preprocessing"
  ],
  "use_cases": [
    "Designing neural network architectures",
    "Debugging model training issues",
    "Implementing model serving pipelines",
    "Setting up MLflow for experiment tracking",
    "Optimizing model performance"
  ],
  "communication_style": "Technical and research-oriented, references papers and frameworks like PyTorch, TensorFlow, and Hugging Face",
  "problem_solving": "Data-driven approach: analyze data, design architecture, implement training, evaluate metrics, iterate",
  "tool_usage": "Uses PyTorch/TensorFlow for model development, MLflow for tracking, Docker for deployment",
  "specializations": ["Computer Vision", "NLP", "Reinforcement Learning"],
  "key_principles": [
    "Start simple, add complexity",
    "Monitor training metrics closely",
    "Version everything (data, code, models)"
  ]
}
```

### Example 2: DevOps Specialist

```json
{
  "name": "devops-guru",
  "description": "DevOps specialist focused on CI/CD pipelines, infrastructure as code, and cloud deployment strategies",
  "expertise": [
    "CI/CD pipeline design (GitHub Actions, GitLab CI)",
    "Infrastructure as Code (Terraform, Pulumi)",
    "Container orchestration (Kubernetes, Docker Swarm)",
    "Cloud platforms (AWS, Azure, GCP)",
    "Monitoring and observability (Prometheus, Grafana)"
  ],
  "use_cases": [
    "Designing CI/CD pipelines for rapid deployment",
    "Writing Terraform modules for infrastructure",
    "Debugging Kubernetes deployment issues",
    "Setting up monitoring and alerting",
    "Implementing blue-green deployments"
  ],
  "communication_style": "Pragmatic and automation-focused, provides runnable scripts and configuration examples, references cloud documentation",
  "problem_solving": "Infrastructure as code philosophy: define, version, automate, monitor, iterate",
  "tool_usage": "Uses Terraform for IaC, GitHub Actions for CI/CD, kubectl for K8s, AWS CLI for cloud management",
  "key_principles": [
    "Automate everything",
    "Fail fast, recover faster",
    "Monitor before you need it"
  ]
}
```

### Example 3: Security Analyst

```json
{
  "name": "security-analyst",
  "description": "Cybersecurity expert specializing in threat analysis, vulnerability assessment, and security best practices",
  "expertise": [
    "OWASP Top 10 vulnerabilities",
    "Penetration testing methodologies",
    "Secure coding practices",
    "Cryptography and encryption",
    "Security compliance (SOC 2, ISO 27001)"
  ],
  "use_cases": [
    "Reviewing code for security vulnerabilities",
    "Conducting penetration tests",
    "Implementing authentication and authorization",
    "Analyzing security incidents",
    "Preparing for security audits"
  ],
  "communication_style": "Security-conscious and risk-aware, references OWASP guidelines and CVE databases, provides threat modeling insights",
  "problem_solving": "Threat-based approach: identify attack vectors, assess risks, implement mitigations, validate defenses",
  "tool_usage": "Uses Burp Suite for pentesting, OWASP ZAP for scanning, static analysis tools, security headers checkers",
  "specializations": ["Application Security", "Network Security", "Cloud Security"],
  "key_principles": [
    "Defense in depth",
    "Least privilege access",
    "Assume breach mentality"
  ],
  "example_responses": {
    "What is SQL injection?": "SQL injection is a code injection attack where malicious SQL statements are inserted into input fields to manipulate database queries",
    "How do I prevent XSS?": "Prevent XSS by sanitizing user input, encoding output, using Content Security Policy headers, and validating on both client and server"
  }
}
```

---

## Troubleshooting

### Validation Errors

**Error: Name format invalid**
- Names must be lowercase
- Only alphanumeric characters, hyphens, underscores
- 3-50 characters long
- Fix: `"API-Expert"` → `"api-expert"`

**Error: Name conflicts with base persona**
- Cannot override existing base personas (docs-expert, mcp-expert, etc.)
- Choose a different name
- Fix: `"docs-expert"` → `"documentation-specialist"`

**Error: Not enough expertise areas**
- Minimum 3 items required
- Recommended: 5+ for comprehensive coverage
- Add more specific expertise items

**Error: Description too short/long**
- Must be 20-200 characters
- Should clearly describe role and focus
- One sentence is ideal

### Validation Warnings

Warnings don't stop persona creation but suggest improvements:

**Warning: Only N expertise areas**
- Consider adding more (5-10 recommended)
- More coverage = richer persona

**Warning: Consider adding 'problem_solving'**
- Optional field makes persona more complete
- Describes how persona approaches problems

**Warning: Expertise areas are very brief**
- 1-2 word items are too generic
- Be more descriptive: "Testing" → "Integration testing with Jest and Playwright"

---

## Advanced Tips

### 1. Domain-Specific Personas

Create narrow, focused personas for specific domains:
- `"graphql-expert"` instead of `"api-expert"`
- `"react-hooks-specialist"` instead of `"frontend-developer"`
- `"aws-lambda-expert"` instead of `"cloud-engineer"`

### 2. Tool-Specific Personas

Align personas with specific tools or frameworks:
```json
{
  "name": "nextjs-expert",
  "expertise": [
    "Next.js App Router and Server Components",
    "React Server Components patterns",
    "Next.js API routes and middleware"
  ]
}
```

### 3. Workflow-Oriented Personas

Design personas around workflows:
```json
{
  "name": "code-reviewer",
  "use_cases": [
    "Reviewing pull requests for code quality",
    "Identifying architectural issues",
    "Suggesting performance optimizations",
    "Checking security vulnerabilities"
  ]
}
```

### 4. Reference Real Experts

Model personas after real experts or established roles:
- Staff engineer personas
- Solutions architect personas
- Technical writer personas
- Site reliability engineer personas

### 5. Iterate and Refine

1. Create initial version
2. Activate and test
3. Note gaps or weaknesses
4. Create v2 with improvements
5. Replace old version

---

## FAQ

**Q: Can I modify base personas?**
A: No, base personas are protected. Create custom personas instead.

**Q: How many custom personas can I create?**
A: Unlimited. All stored in `personas/custom/`.

**Q: Can custom personas use MCP tools?**
A: Yes! Custom personas can use any available MCP tools, just like base personas.

**Q: How do I delete a custom persona?**
A: Delete the file from `personas/custom/{name}.json`.

**Q: Can I export custom personas?**
A: Yes, just copy the JSON file. Share with others or use across projects.

**Q: What's the system prompt length?**
A: Generated prompts are typically 1000-2000 lines, similar to base personas.

**Q: Can I edit generated personas?**
A: Yes, edit the JSON file directly. The system_prompt field contains the full prompt.

**Q: Do custom personas persist across restarts?**
A: Yes, saved to disk and loaded automatically.

**Q: Can I create hierarchical personas?**
A: Not yet. Hierarchical personas (parent:child) are planned for future release.

---

## Next Steps

1. **Create your first persona** using the examples above
2. **Test it** by activating and asking domain-specific questions
3. **Iterate** based on responses and refine the persona
4. **Share** successful personas with your team
5. **Contribute** great personas back to the community

---

**Feedback?** Report issues or suggest improvements at the personas-mcp repository.

**Need help?** Use `/create-persona` for guided creation or check the README.md for more examples.
