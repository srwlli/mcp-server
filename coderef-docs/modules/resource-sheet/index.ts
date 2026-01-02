/**
 * Resource Sheet System - Main Entry Point
 *
 * WO-RESOURCE-SHEET-MCP-TOOL-001
 *
 * Complete documentation generation system with 3-step workflow:
 * 1. Detect - Analyze code and classify element
 * 2. Select - Choose appropriate documentation modules
 * 3. Assemble - Compose and generate documentation files
 *
 * Usage:
 * ```typescript
 * import { generateResourceSheet } from './modules/resource-sheet';
 *
 * const result = await generateResourceSheet({
 *   project_path: '/path/to/project',
 *   element_name: 'FileTree',
 *   mode: 'reverse-engineer',
 *   output_path: '/path/to/output'
 * });
 * ```
 */

import { analyzeElement } from './detection/analyzer';
import { classifyElement, getCategoryDisplayName } from './detection/classifier';
import { selectModules } from './detection/selector';
import { composeDocumentation } from './composition/composer';
import { generateMarkdown } from './output/markdown-generator';
import { generateSchema } from './output/schema-generator';
import { generateJSDoc } from './output/jsdoc-generator';

import {
  GenerateResourceSheetInput,
  GenerateResourceSheetOutput,
  GenerationMode,
} from './types';

/**
 * Main function: Generate resource sheet documentation
 */
export async function generateResourceSheet(
  input: GenerateResourceSheetInput
): Promise<GenerateResourceSheetOutput> {
  try {
    // Step 1: Detect - Analyze element from .coderef/
    const element = await analyzeElement(input.project_path, input.element_name);

    // Step 2: Classify - Determine category
    const detectionResult = classifyElement(element);

    // Step 3: Select - Choose modules
    const selectionResult = selectModules(element, detectionResult.category);

    // Step 4: Compose - Assemble documentation
    const documentation = await composeDocumentation(
      element,
      selectionResult.modules,
      {
        category: getCategoryDisplayName(detectionResult.category),
        workorderId: input.workorder_id,
        featureId: input.feature_id,
      }
    );

    // Step 5: Generate - Write output files
    const outputPath = input.output_path || `${input.project_path}/coderef/foundation-docs`;

    const markdownPath = await generateMarkdown(documentation, outputPath);
    const schemaPath = await generateSchema(documentation, `${input.project_path}/coderef/schemas`);
    const jsdocPath = await generateJSDoc(documentation, `${outputPath}/.jsdoc`);

    return {
      success: true,
      documentation,
      files: {
        markdown: markdownPath,
        schema: schemaPath,
        jsdoc: jsdocPath,
      },
      warnings:
        documentation.reviewFlags.length > 0
          ? [`${documentation.reviewFlags.length} sections require manual input`]
          : undefined,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
}

/**
 * Preview mode: Generate documentation without writing files
 */
export async function previewResourceSheet(
  input: Omit<GenerateResourceSheetInput, 'output_path'>
): Promise<GenerateResourceSheetOutput> {
  try {
    const element = await analyzeElement(input.project_path, input.element_name);
    const detectionResult = classifyElement(element);
    const selectionResult = selectModules(element, detectionResult.category);

    const documentation = await composeDocumentation(
      element,
      selectionResult.modules,
      {
        category: getCategoryDisplayName(detectionResult.category),
        workorderId: input.workorder_id,
        featureId: input.feature_id,
      }
    );

    return {
      success: true,
      documentation,
      warnings:
        documentation.reviewFlags.length > 0
          ? [`${documentation.reviewFlags.length} sections require manual input`]
          : undefined,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
}

/**
 * Get detection info without generating documentation
 */
export async function detectElement(
  projectPath: string,
  elementName: string
): Promise<{
  element: any;
  category: string;
  confidence: number;
  modules: string[];
  autoFillRate: number;
}> {
  const element = await analyzeElement(projectPath, elementName);
  const detectionResult = classifyElement(element);
  const selectionResult = selectModules(element, detectionResult.category);

  return {
    element,
    category: getCategoryDisplayName(detectionResult.category),
    confidence: detectionResult.confidence,
    modules: selectionResult.modules,
    autoFillRate: selectionResult.estimatedAutoFill,
  };
}

// Export all types and utilities
export * from './types';
export { analyzeElement } from './detection/analyzer';
export { classifyElement, getCategoryDisplayName, getCategoryDescription } from './detection/classifier';
export { selectModules, sortModules } from './detection/selector';
export { composeDocumentation } from './composition/composer';
export { generateMarkdown, validateMarkdown } from './output/markdown-generator';
export { generateSchema, validateSchema } from './output/schema-generator';
export { generateJSDoc, previewJSDoc } from './output/jsdoc-generator';
