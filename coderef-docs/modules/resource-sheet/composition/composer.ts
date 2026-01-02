/**
 * Composition Engine - Assembles selected modules into cohesive documentation
 *
 * WO-RESOURCE-SHEET-MCP-TOOL-001/COMPOSE-001
 *
 * Takes selected modules and composes them into unified documentation with
 * variable substitution and template rendering.
 */

import * as fs from 'fs';
import * as path from 'path';
import { ElementCharacteristics, ModuleName, ComposedDocumentation } from '../types';

/**
 * Compose documentation from selected modules
 */
export async function composeDocumentation(
  element: ElementCharacteristics,
  selectedModules: ModuleName[],
  options: {
    workorderId?: string;
    featureId?: string;
    category: string;
  }
): Promise<ComposedDocumentation> {
  const modulesDir = path.join(__dirname, '..');

  // Read module templates
  const moduleContents = await readModuleTemplates(modulesDir, selectedModules);

  // Extract auto-fill data from element
  const autoFillData = extractAutoFillData(element);

  // Compose markdown
  const markdown = composeMarkdown(
    element,
    selectedModules,
    moduleContents,
    autoFillData,
    options
  );

  // Compose JSON schema
  const schema = composeSchema(element, selectedModules, autoFillData);

  // Compose JSDoc
  const jsdoc = composeJSDoc(element, selectedModules, autoFillData);

  // Calculate auto-fill rate
  const autoFillRate = calculateActualAutoFillRate(markdown);

  // Identify sections needing review
  const reviewFlags = identifyReviewFlags(markdown);

  return {
    elementName: element.name,
    category: options.category,
    modulesUsed: selectedModules,
    markdown,
    schema,
    jsdoc,
    autoFillRate,
    reviewFlags,
    uds: {
      workorder_id: options.workorderId,
      feature_id: options.featureId,
      generated_by: 'Resource Sheet MCP Tool v1.0.0',
      timestamp: new Date().toISOString(),
    },
  };
}

/**
 * Read module template files
 */
async function readModuleTemplates(
  modulesDir: string,
  selectedModules: ModuleName[]
): Promise<Map<ModuleName, string>> {
  const moduleContents = new Map<ModuleName, string>();

  for (const module of selectedModules) {
    const isUniversal = ['architecture', 'integration', 'testing', 'performance'].includes(module);
    const moduleSubdir = isUniversal ? '_universal' : 'conditional';
    const modulePath = path.join(modulesDir, moduleSubdir, `${module}.md`);

    if (fs.existsSync(modulePath)) {
      const content = fs.readFileSync(modulePath, 'utf-8');
      moduleContents.set(module, content);
    } else {
      console.warn(`Module template not found: ${modulePath}`);
    }
  }

  return moduleContents;
}

/**
 * Extract auto-fill data from element characteristics
 */
function extractAutoFillData(element: ElementCharacteristics): Record<string, any> {
  return {
    // Basic element info
    elementName: element.name,
    elementType: element.type,
    filePath: element.file,

    // Imports & exports
    imports: element.imports,
    exports: element.exports,
    internalImports: element.imports.filter((i) => i.startsWith('.') || i.startsWith('@/')),
    externalImports: element.imports.filter((i) => !i.startsWith('.') && !i.startsWith('@/')),

    // React-specific
    hasJSX: element.metadata.hasJSX,
    hooks: element.metadata.hooks || [],

    // Props
    props: element.metadata.props || [],
    propsCount: element.metadata.props?.length || 0,

    // State
    stateVariables: element.metadata.stateVariables || [],
    stateCount: element.metadata.stateVariables?.length || 0,

    // Events
    eventHandlers: element.metadata.eventHandlers || [],
    eventsCount: element.metadata.eventHandlers?.length || 0,

    // API calls
    apiCalls: element.metadata.apiCalls || [],
    apiCallsCount: element.metadata.apiCalls?.length || 0,

    // All metadata (for custom access)
    metadata: element.metadata,
  };
}

/**
 * Compose markdown documentation
 */
function composeMarkdown(
  element: ElementCharacteristics,
  selectedModules: ModuleName[],
  moduleContents: Map<ModuleName, string>,
  autoFillData: Record<string, any>,
  options: { workorderId?: string; featureId?: string; category: string }
): string {
  let markdown = '';

  // Add UDS header
  markdown += generateUDSHeader(element, options);
  markdown += '\n\n---\n\n';

  // Add executive summary
  markdown += generateExecutiveSummary(element, options.category);
  markdown += '\n\n---\n\n';

  // Add each module's content
  for (const module of selectedModules) {
    const moduleContent = moduleContents.get(module);
    if (!moduleContent) continue;

    // Extract the "Section:" content from module template
    const sectionContent = extractSectionContent(moduleContent);

    // Substitute variables
    const rendered = substituteVariables(sectionContent, autoFillData);

    markdown += rendered;
    markdown += '\n\n---\n\n';
  }

  // Add footer
  markdown += generateFooter(options);

  return markdown;
}

/**
 * Generate UDS header (Papertrail integration)
 */
function generateUDSHeader(
  element: ElementCharacteristics,
  options: { workorderId?: string; featureId?: string; category: string }
): string {
  const timestamp = new Date().toISOString();

  return `# ${element.name} - Resource Sheet

**Category:** ${options.category}
**Type:** ${element.type}
**File:** \`${element.file}\`
**Created:** ${timestamp.split('T')[0]}
${options.workorderId ? `**Workorder:** ${options.workorderId}` : ''}
${options.featureId ? `**Feature:** ${options.featureId}` : ''}

---

**Generated by:** Resource Sheet MCP Tool v1.0.0
**Timestamp:** ${timestamp}`;
}

/**
 * Generate executive summary
 */
function generateExecutiveSummary(element: ElementCharacteristics, category: string): string {
  return `## Executive Summary

**Element:** ${element.name}
**Category:** ${category}
**Purpose:** ${element.metadata.description || '⚠️ MANUAL: Add brief description of what this element does'}

**Key Responsibilities:**
${element.metadata.responsibilities ? element.metadata.responsibilities.map((r: string) => `- ${r}`).join('\n') : '⚠️ MANUAL: List 3-5 key responsibilities'}

**Not Responsible For:**
⚠️ MANUAL: Explicitly state what this element does NOT do`;
}

/**
 * Extract section content from module template
 */
function extractSectionContent(moduleTemplate: string): string {
  // Find "## Section:" heading
  const sectionMatch = moduleTemplate.match(/## Section:.*?\n\n([\s\S]*?)(?=\n---\n\n## Metadata|$)/);
  if (sectionMatch) {
    return sectionMatch[1];
  }

  // Fallback: return everything after first ## heading
  const firstHeading = moduleTemplate.indexOf('##');
  if (firstHeading !== -1) {
    return moduleTemplate.substring(firstHeading);
  }

  return moduleTemplate;
}

/**
 * Substitute variables in template
 * Supports: {{variable}}, {{#each array}}, {{#if condition}}
 */
function substituteVariables(template: string, data: Record<string, any>): string {
  let result = template;

  // Simple variable substitution: {{elementName}}
  result = result.replace(/\{\{([^}#/]+)\}\}/g, (match, varName) => {
    const trimmed = varName.trim();
    const value = getNestedValue(data, trimmed);
    return value !== undefined ? String(value) : match;
  });

  // Handle {{#each array}} blocks
  result = substituteEachBlocks(result, data);

  // Handle {{#if condition}} blocks
  result = substituteIfBlocks(result, data);

  // Mark remaining template variables as manual sections
  result = result.replace(/\{\{MANUAL:(.*?)\}\}/g, '⚠️ **MANUAL:** $1');
  result = result.replace(/\{\{AUTO_FILL:(.*?)\}\}/g, '✅ **AUTO-FILLED** (from code analysis)');

  return result;
}

/**
 * Get nested value from object (e.g., "element.metadata.hasJSX")
 */
function getNestedValue(obj: any, path: string): any {
  const parts = path.split('.');
  let current = obj;

  for (const part of parts) {
    if (current && typeof current === 'object' && part in current) {
      current = current[part];
    } else {
      return undefined;
    }
  }

  return current;
}

/**
 * Substitute {{#each array}} blocks
 */
function substituteEachBlocks(template: string, data: Record<string, any>): string {
  const eachRegex = /\{\{#each\s+([^}]+)\}\}([\s\S]*?)\{\{\/each\}\}/g;

  return template.replace(eachRegex, (match, arrayPath, blockContent) => {
    const array = getNestedValue(data, arrayPath.trim());

    if (!Array.isArray(array) || array.length === 0) {
      return ''; // Empty array - remove block
    }

    // Render block for each item
    return array
      .map((item) => {
        let rendered = blockContent;

        // Substitute {{this.property}} with item values
        rendered = rendered.replace(/\{\{this\.([^}]+)\}\}/g, (_, prop) => {
          const value = item[prop.trim()];
          return value !== undefined ? String(value) : '';
        });

        return rendered;
      })
      .join('\n');
  });
}

/**
 * Substitute {{#if condition}} blocks
 */
function substituteIfBlocks(template: string, data: Record<string, any>): string {
  const ifRegex = /\{\{#if\s+([^}]+)\}\}([\s\S]*?)(?:\{\{else\}\}([\s\S]*?))?\{\{\/if\}\}/g;

  return template.replace(ifRegex, (match, condition, truthyBlock, falsyBlock = '') => {
    const value = getNestedValue(data, condition.trim());
    const isTrue = Boolean(value);

    return isTrue ? truthyBlock : falsyBlock;
  });
}

/**
 * Compose JSON Schema
 */
function composeSchema(
  element: ElementCharacteristics,
  selectedModules: ModuleName[],
  autoFillData: Record<string, any>
): string {
  const schema: any = {
    $schema: 'http://json-schema.org/draft-07/schema#',
    title: `${element.name} Schema`,
    description: `Type definitions for ${element.name}`,
    definitions: {},
    metadata: {
      category: autoFillData.category || 'unknown',
      generated_by: 'Resource Sheet MCP Tool',
      timestamp: new Date().toISOString(),
    },
  };

  // Add props schema if props module selected
  if (selectedModules.includes('props') && autoFillData.props.length > 0) {
    schema.definitions[`${element.name}Props`] = generatePropsSchema(autoFillData.props);
  }

  // Add state schema if state module selected
  if (selectedModules.includes('state') && autoFillData.stateVariables.length > 0) {
    schema.definitions.StateVariables = generateStateSchema(autoFillData.stateVariables);
  }

  return JSON.stringify(schema, null, 2);
}

/**
 * Generate props schema from props metadata
 */
function generatePropsSchema(props: any[]): any {
  const properties: any = {};
  const required: string[] = [];

  props.forEach((prop) => {
    properties[prop.name] = {
      type: inferSchemaType(prop.type),
      description: prop.description || '',
    };

    if (prop.required) {
      required.push(prop.name);
    }
  });

  return {
    type: 'object',
    properties,
    required,
  };
}

/**
 * Generate state schema from state variables
 */
function generateStateSchema(stateVars: any[]): any {
  const properties: any = {};

  stateVars.forEach((stateVar) => {
    properties[stateVar.name] = {
      type: inferSchemaType(stateVar.type),
      description: `State variable: ${stateVar.name}`,
    };
  });

  return {
    type: 'object',
    properties,
  };
}

/**
 * Infer JSON Schema type from TypeScript type string
 */
function inferSchemaType(tsType: string): string {
  if (tsType.includes('string')) return 'string';
  if (tsType.includes('number')) return 'number';
  if (tsType.includes('boolean')) return 'boolean';
  if (tsType.includes('[]') || tsType.includes('Array')) return 'array';
  if (tsType.includes('object') || tsType.includes('{}')) return 'object';
  return 'string'; // Default fallback
}

/**
 * Compose JSDoc comments
 */
function composeJSDoc(
  element: ElementCharacteristics,
  selectedModules: ModuleName[],
  autoFillData: Record<string, any>
): string {
  let jsdoc = `/**\n * ${element.name}\n *\n`;

  // Add description
  jsdoc += ` * ${autoFillData.metadata.description || 'TODO: Add description'}\n *\n`;

  // Add @component tag if React component
  if (autoFillData.hasJSX) {
    jsdoc += ` * @component\n`;
  }

  // Add @example if available
  jsdoc += ` * @example\n`;
  jsdoc += ` * // TODO: Add usage example\n *\n`;

  // Add @param for props
  if (selectedModules.includes('props') && autoFillData.props.length > 0) {
    autoFillData.props.forEach((prop: any) => {
      jsdoc += ` * @param {${prop.type}} props.${prop.name} - ${prop.description || 'TODO: Add description'}\n`;
    });
    jsdoc += ` *\n`;
  }

  // Add @returns
  if (autoFillData.hasJSX) {
    jsdoc += ` * @returns {JSX.Element} Rendered component\n`;
  } else {
    jsdoc += ` * @returns TODO: Add return type\n`;
  }

  jsdoc += ` */`;

  return jsdoc;
}

/**
 * Calculate actual auto-fill rate from rendered markdown
 */
function calculateActualAutoFillRate(markdown: string): number {
  const manualMarkers = (markdown.match(/⚠️ \*\*MANUAL:\*\*/g) || []).length;
  const autoFilledMarkers = (markdown.match(/✅ \*\*AUTO-FILLED\*\*/g) || []).length;

  const total = manualMarkers + autoFilledMarkers;
  if (total === 0) return 0;

  return Math.round((autoFilledMarkers / total) * 100);
}

/**
 * Identify sections needing human review
 */
function identifyReviewFlags(markdown: string): { section: string; reason: string }[] {
  const flags: { section: string; reason: string }[] = [];

  // Find all manual sections
  const manualMatches = markdown.matchAll(/## (.*?)\n[\s\S]*?⚠️ \*\*MANUAL:\*\* (.*?)(?=\n|$)/g);

  for (const match of manualMatches) {
    flags.push({
      section: match[1],
      reason: `Manual input required: ${match[2]}`,
    });
  }

  return flags;
}

/**
 * Generate footer
 */
function generateFooter(options: { workorderId?: string; featureId?: string }): string {
  return `---

**Generated by:** Resource Sheet MCP Tool v1.0.0
${options.workorderId ? `**Workorder:** ${options.workorderId}` : ''}
**Timestamp:** ${new Date().toISOString()}

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>`;
}
