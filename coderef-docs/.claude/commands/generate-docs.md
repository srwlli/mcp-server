Generate foundation documentation for the current project using the docs-mcp POWER framework templates.

This command generates 5 foundation documents sequentially to avoid timeout errors:
1. README.md
2. ARCHITECTURE.md
3. API.md
4. COMPONENTS.md
5. SCHEMA.md

## Workflow

For each template, call the `mcp__coderef-docs__generate_individual_doc` tool with:
- project_path: current working directory
- template_name: readme, architecture, api, components, or schema

### Step 1: README.md (1/5)
Status: Generating README.md template...
Call the `mcp__coderef-docs__generate_individual_doc` tool with:
- project_path: current working directory
- template_name: readme

Then analyze the project and generate comprehensive README.md content, saving to project root.

### Step 2: ARCHITECTURE.md (2/5)
Status: Generating ARCHITECTURE.md template...
Call the `mcp__coderef-docs__generate_individual_doc` tool with:
- project_path: current working directory
- template_name: architecture

Then analyze project architecture and generate ARCHITECTURE.md, saving to coderef/foundation-docs/.

### Step 3: API.md (3/5)
Status: Generating API.md template...
Call the `mcp__coderef-docs__generate_individual_doc` tool with:
- project_path: current working directory
- template_name: api

Then analyze project APIs and endpoints, generate API.md, saving to coderef/foundation-docs/.

### Step 4: COMPONENTS.md (4/5)
Status: Generating COMPONENTS.md template...
Call the `mcp__coderef-docs__generate_individual_doc` tool with:
- project_path: current working directory
- template_name: components

Then analyze project components and generate COMPONENTS.md, saving to coderef/foundation-docs/.

### Step 5: SCHEMA.md (5/5)
Status: Generating SCHEMA.md template...
Call the `mcp__coderef-docs__generate_individual_doc` tool with:
- project_path: current working directory
- template_name: schema

Then analyze project data models and schemas, generate SCHEMA.md, saving to coderef/foundation-docs/.

## Completion

After all 5 documents are generated successfully:
- Verify README.md exists in project root
- Verify ARCHITECTURE.md, API.md, COMPONENTS.md, SCHEMA.md exist in coderef/foundation-docs/
- All documents should have project-specific content (not generic templates)

Success! Foundation documentation has been generated for your project. Each document references the others as indicated in the templates for a cohesive documentation suite.
