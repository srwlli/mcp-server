/**
 * JSON Schema Generator - Writes JSON Schema to file
 *
 * WO-RESOURCE-SHEET-MCP-TOOL-001/OUTPUT-002
 *
 * Generates JSON Schema files from composed documentation.
 */

import * as fs from 'fs';
import * as path from 'path';
import { ComposedDocumentation } from '../types';

/**
 * Generate JSON Schema file from composed documentation
 */
export async function generateSchema(
  documentation: ComposedDocumentation,
  outputPath: string
): Promise<string> {
  const filePath = resolveSchemaPath(outputPath, documentation.elementName);

  // Ensure output directory exists
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  // Write schema file with proper formatting
  fs.writeFileSync(filePath, documentation.schema, 'utf-8');

  return filePath;
}

/**
 * Resolve schema output path
 */
function resolveSchemaPath(outputPath: string, elementName: string): string {
  // If outputPath is directory
  if (outputPath.endsWith('/') || (fs.existsSync(outputPath) && fs.statSync(outputPath).isDirectory())) {
    const fileName = `${toKebabCase(elementName)}-schema.json`;
    return path.join(outputPath, fileName);
  }

  // If already has .json extension
  if (outputPath.endsWith('.json')) {
    return outputPath;
  }

  // Append -schema.json
  return `${outputPath}-schema.json`;
}

/**
 * Convert to kebab-case
 */
function toKebabCase(str: string): string {
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase();
}

/**
 * Validate JSON Schema
 */
export function validateSchema(schemaJson: string): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  try {
    const schema = JSON.parse(schemaJson);

    // Check for required top-level fields
    if (!schema.$schema) {
      errors.push('Missing $schema field');
    }

    if (!schema.title) {
      errors.push('Missing title field');
    }

    if (!schema.metadata) {
      errors.push('Missing metadata field');
    }

    // Check metadata structure
    if (schema.metadata) {
      if (!schema.metadata.generated_by) {
        errors.push('Missing metadata.generated_by');
      }

      if (!schema.metadata.timestamp) {
        errors.push('Missing metadata.timestamp');
      }
    }

  } catch (e) {
    errors.push(`Invalid JSON: ${e instanceof Error ? e.message : 'Unknown error'}`);
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
