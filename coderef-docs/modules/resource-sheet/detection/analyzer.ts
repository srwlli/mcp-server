/**
 * Detection Engine - Analyzes code elements from .coderef/index.json
 *
 * WO-RESOURCE-SHEET-MCP-TOOL-001/DETECT-001
 *
 * Reads .coderef/index.json and extracts element characteristics for classification.
 */

import * as fs from 'fs';
import * as path from 'path';
import { ElementCharacteristics, DetectionResult } from '../types';

/**
 * Read .coderef/index.json and find element by name
 */
export async function analyzeElement(
  projectPath: string,
  elementName: string
): Promise<ElementCharacteristics> {
  const indexPath = path.join(projectPath, '.coderef', 'index.json');

  // Check if .coderef/index.json exists
  if (!fs.existsSync(indexPath)) {
    throw new Error(
      `No .coderef/index.json found at ${indexPath}. ` +
      `Run 'coderef scan --project-path ${projectPath}' first.`
    );
  }

  // Read and parse index.json
  const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));

  if (!indexData.elements || !Array.isArray(indexData.elements)) {
    throw new Error('Invalid .coderef/index.json format - missing elements array');
  }

  // Find element by name (exact match or fuzzy match)
  const element = findElement(indexData.elements, elementName);

  if (!element) {
    throw new Error(
      `Element "${elementName}" not found in .coderef/index.json. ` +
      `Available elements: ${indexData.elements.map((e: any) => e.name).slice(0, 10).join(', ')}...`
    );
  }

  // Extract characteristics
  return extractCharacteristics(element);
}

/**
 * Find element in index by name
 * Supports exact match, file path match, and fuzzy matching
 */
function findElement(elements: any[], elementName: string): any | null {
  // Try exact name match
  let element = elements.find((e) => e.name === elementName);
  if (element) return element;

  // Try case-insensitive match
  element = elements.find(
    (e) => e.name.toLowerCase() === elementName.toLowerCase()
  );
  if (element) return element;

  // Try file path match (e.g., "src/components/FileTree.tsx")
  element = elements.find((e) => e.file === elementName);
  if (element) return element;

  // Try file path partial match (e.g., "FileTree.tsx")
  element = elements.find((e) => e.file.endsWith(elementName));
  if (element) return element;

  // Try ID match (e.g., "FileTree.tsx#FileTree")
  element = elements.find((e) => e.id === elementName);
  if (element) return element;

  return null;
}

/**
 * Extract characteristics from .coderef element
 */
function extractCharacteristics(element: any): ElementCharacteristics {
  return {
    name: element.name || '',
    type: element.type || 'unknown',
    file: element.file || '',
    imports: element.imports || [],
    exports: element.exports || [],
    metadata: {
      // React-specific
      hasJSX: element.metadata?.hasJSX || false,
      hooks: element.metadata?.hooks || [],
      props: element.metadata?.props?.map((p: any) => ({
        name: p.name,
        type: p.type,
        required: p.required || false,
        default: p.default,
        description: p.description,
      })) || [],

      // State management
      stateVariables: element.metadata?.stateVariables?.map((s: any) => ({
        name: s.name,
        type: s.type,
        initialValue: s.initialValue,
        persisted: s.persisted || false,
        persistenceKey: s.persistenceKey,
      })) || [],

      // Event handlers
      eventHandlers: element.metadata?.eventHandlers?.map((e: any) => ({
        name: e.name,
        type: e.type,
        description: e.description,
      })) || [],

      // API calls
      apiCalls: element.metadata?.apiCalls?.map((a: any) => ({
        method: a.method || 'GET',
        endpoint: a.endpoint,
        library: a.library || 'fetch',
      })) || [],

      // Additional metadata
      ...element.metadata,
    },
  };
}

/**
 * Analyze element and extract code characteristics
 * Used for detection heuristics when .coderef metadata is incomplete
 */
export function analyzeCodeCharacteristics(
  element: ElementCharacteristics
): {
  isReactComponent: boolean;
  usesState: boolean;
  hasProps: boolean;
  hasLifecycle: boolean;
  hasEvents: boolean;
  isAPI: boolean;
  isCLI: boolean;
  isHook: boolean;
  isStore: boolean;
  isTest: boolean;
  isGenerator: boolean;
  isInfrastructure: boolean;
  hasAuth: boolean;
  hasValidation: boolean;
  hasPersistence: boolean;
  hasRouting: boolean;
  hasAccessibility: boolean;
} {
  const { name, file, imports, metadata } = element;

  // React component detection
  const isReactComponent = metadata.hasJSX === true;

  // State management detection
  const usesState =
    metadata.hooks?.some((h) => h.includes('useState') || h.includes('useReducer')) ||
    imports.some((i) => i.includes('redux') || i.includes('zustand') || i.includes('jotai'));

  // Props detection
  const hasProps = (metadata.props?.length || 0) > 0;

  // Lifecycle detection
  const hasLifecycle =
    metadata.hooks?.some((h) => h.includes('useEffect') || h.includes('useLayoutEffect')) ||
    false;

  // Event handling detection
  const hasEvents = (metadata.eventHandlers?.length || 0) > 0;

  // API detection
  const isAPI =
    file.includes('api/') ||
    file.includes('routes/') ||
    imports.some((i) => i.includes('axios') || i.includes('fetch')) ||
    (metadata.apiCalls?.length || 0) > 0;

  // CLI detection
  const isCLI =
    file.includes('cli/') ||
    name.endsWith('Command') ||
    imports.some((i) => i.includes('commander') || i.includes('yargs'));

  // Hook detection
  const isHook = name.startsWith('use') && name.length > 3;

  // Store detection
  const isStore =
    file.includes('store') ||
    file.includes('context') ||
    imports.some((i) => i.includes('redux') || i.includes('zustand'));

  // Test detection
  const isTest =
    file.includes('.test.') ||
    file.includes('.spec.') ||
    file.includes('__tests__') ||
    imports.some((i) => i.includes('vitest') || i.includes('jest'));

  // Generator detection
  const isGenerator =
    file.includes('generator') ||
    file.includes('scaffold') ||
    name.includes('Generator');

  // Infrastructure detection
  const isInfrastructure =
    file.includes('build') ||
    file.includes('deploy') ||
    file.includes('ci') ||
    file.includes('script');

  // Auth detection
  const hasAuth =
    name.toLowerCase().includes('auth') ||
    imports.some((i) => i.includes('jwt') || i.includes('auth'));

  // Validation detection
  const hasValidation =
    imports.some((i) => i.includes('zod') || i.includes('yup')) ||
    name.includes('Validator') ||
    name.includes('Schema');

  // Persistence detection
  const hasPersistence =
    metadata.stateVariables?.some((s) => s.persisted) ||
    imports.some((i) => i.includes('localStorage') || i.includes('indexeddb'));

  // Routing detection
  const hasRouting =
    file.includes('router') ||
    file.includes('routes') ||
    imports.some((i) => i.includes('react-router') || i.includes('next/navigation'));

  // Accessibility detection
  const hasAccessibility =
    file.includes('a11y') ||
    imports.some((i) => i.includes('aria')) ||
    metadata.ariaAttributes ||
    metadata.keyboardHandlers;

  return {
    isReactComponent,
    usesState,
    hasProps,
    hasLifecycle,
    hasEvents,
    isAPI,
    isCLI,
    isHook,
    isStore,
    isTest,
    isGenerator,
    isInfrastructure,
    hasAuth,
    hasValidation,
    hasPersistence,
    hasRouting,
    hasAccessibility,
  };
}

/**
 * Calculate confidence score for detection
 * Higher confidence = more clear-cut categorization
 */
export function calculateConfidence(
  characteristics: ReturnType<typeof analyzeCodeCharacteristics>
): number {
  let confidence = 50; // Start at 50%

  // Strong signals increase confidence
  if (characteristics.isReactComponent) confidence += 20;
  if (characteristics.isCLI) confidence += 20;
  if (characteristics.isHook) confidence += 20;
  if (characteristics.isAPI) confidence += 15;
  if (characteristics.isStore) confidence += 15;
  if (characteristics.isTest) confidence += 25;
  if (characteristics.isGenerator) confidence += 15;
  if (characteristics.isInfrastructure) confidence += 15;

  // Ambiguous signals decrease confidence
  const ambiguityCount = [
    characteristics.isReactComponent && characteristics.isAPI, // Hybrid component
    characteristics.isHook && characteristics.isStore, // Hook that's also a store
    characteristics.isCLI && characteristics.isAPI, // CLI that calls APIs
  ].filter(Boolean).length;

  confidence -= ambiguityCount * 15;

  // Cap at 0-100
  return Math.max(0, Math.min(100, confidence));
}
