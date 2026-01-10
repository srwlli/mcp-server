/**
 * JSDoc Generator - Generates JSDoc comments for inline documentation
 *
 * WO-RESOURCE-SHEET-MCP-TOOL-001/OUTPUT-003
 *
 * Creates JSDoc suggestions that can be added to source files.
 */

import * as fs from 'fs';
import * as path from 'path';
import { ComposedDocumentation } from '../types';

/**
 * Generate JSDoc file with suggestions
 */
export async function generateJSDoc(
  documentation: ComposedDocumentation,
  outputPath: string
): Promise<string> {
  const filePath = resolveJSDocPath(outputPath, documentation.elementName);

  // Ensure output directory exists
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  // Create JSDoc suggestions file
  const content = formatJSDocSuggestions(documentation);

  fs.writeFileSync(filePath, content, 'utf-8');

  return filePath;
}

/**
 * Resolve JSDoc output path
 */
function resolveJSDocPath(outputPath: string, elementName: string): string {
  // If directory
  if (outputPath.endsWith('/') || (fs.existsSync(outputPath) && fs.statSync(outputPath).isDirectory())) {
    const fileName = `${toKebabCase(elementName)}-jsdoc.txt`;
    return path.join(outputPath, fileName);
  }

  // If has extension
  if (outputPath.endsWith('.txt') || outputPath.endsWith('.md')) {
    return outputPath;
  }

  // Append -jsdoc.txt
  return `${outputPath}-jsdoc.txt`;
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
 * Format JSDoc suggestions as a text file
 */
function formatJSDocSuggestions(documentation: ComposedDocumentation): string {
  let content = `# JSDoc Suggestions for ${documentation.elementName}\n\n`;
  content += `Generated: ${documentation.uds.timestamp}\n`;
  content += `Category: ${documentation.category}\n\n`;
  content += `---\n\n`;

  content += `## Main Element Documentation\n\n`;
  content += `Add this JSDoc comment above the ${documentation.elementName} definition:\n\n`;
  content += `\`\`\`typescript\n`;
  content += documentation.jsdoc;
  content += `\n\`\`\`\n\n`;

  content += `---\n\n`;

  content += `## Instructions\n\n`;
  content += `1. Copy the JSDoc comment above\n`;
  content += `2. Paste it immediately before the ${documentation.elementName} definition in your source file\n`;
  content += `3. Replace any TODO placeholders with actual descriptions\n`;
  content += `4. Verify all @param types match your TypeScript interfaces\n`;
  content += `5. Add @example blocks with real usage examples\n\n`;

  content += `## Additional Sections to Document\n\n`;

  if (documentation.reviewFlags.length > 0) {
    content += `⚠️ **Manual documentation needed:**\n\n`;
    documentation.reviewFlags.forEach((flag) => {
      content += `- **${flag.section}:** ${flag.reason}\n`;
    });
    content += `\n`;
  }

  content += `## Auto-Fill Rate\n\n`;
  content += `${documentation.autoFillRate}% of documentation was auto-filled from code analysis.\n`;
  content += `${100 - documentation.autoFillRate}% requires manual input.\n\n`;

  return content;
}

/**
 * Preview JSDoc (for testing)
 */
export function previewJSDoc(documentation: ComposedDocumentation): string {
  return documentation.jsdoc;
}
