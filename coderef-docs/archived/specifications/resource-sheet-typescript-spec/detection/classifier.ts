/**
 * Category Classifier - Maps element characteristics to user-friendly categories
 *
 * WO-RESOURCE-SHEET-MCP-TOOL-001/DETECT-002
 *
 * Classifies code elements into 8 user-friendly categories based on their characteristics.
 */

import { ElementCharacteristics, ElementCategory, DetectionResult } from '../types';
import { analyzeCodeCharacteristics, calculateConfidence } from './analyzer';

/**
 * Classify element into category
 * Returns primary category and alternates if ambiguous
 */
export function classifyElement(element: ElementCharacteristics): DetectionResult {
  const characteristics = analyzeCodeCharacteristics(element);
  const category = detectCategory(element, characteristics);
  const confidence = calculateConfidence(characteristics);
  const alternates = detectAlternateCategories(element, characteristics, category);

  return {
    element,
    category,
    confidence,
    alternates: alternates.length > 0 ? alternates : undefined,
  };
}

/**
 * Detect primary category for element
 */
function detectCategory(
  element: ElementCharacteristics,
  characteristics: ReturnType<typeof analyzeCodeCharacteristics>
): ElementCategory {
  const { name, file } = element;

  // Priority 1: Testing (highest priority - tests should be classified first)
  if (characteristics.isTest) {
    if (file.includes('mock') || name.includes('Mock')) return 'testing/mocks';
    if (file.includes('fixture') || name.includes('Fixture')) return 'testing/fixtures';
    return 'testing/test-helpers';
  }

  // Priority 2: Infrastructure
  if (characteristics.isInfrastructure) {
    if (file.includes('build') || name.includes('build')) return 'infrastructure/build-scripts';
    if (file.includes('deploy') || name.includes('deploy')) return 'infrastructure/deployment';
    if (file.includes('ci') || file.includes('.github')) return 'infrastructure/ci-cd';
    return 'infrastructure/build-scripts';
  }

  // Priority 3: Generators
  if (characteristics.isGenerator) {
    if (file.includes('scaffold') || name.includes('Scaffold')) return 'generators/scaffolding';
    if (file.includes('template') || name.includes('Template')) return 'generators/templates';
    if (file.includes('migration') || name.includes('Migration')) return 'generators/migrations';
    return 'generators/scaffolding';
  }

  // Priority 4: UI Components (React/Vue)
  if (characteristics.isReactComponent) {
    if (file.includes('pages/') || file.includes('routes/')) return 'ui/pages';
    if (file.includes('widgets/') || name.includes('Widget')) return 'ui/widgets';
    return 'ui/components';
  }

  // Priority 5: State Management
  if (characteristics.isHook) {
    return 'state/hooks';
  }

  if (characteristics.isStore) {
    if (file.includes('context') || name.includes('Context')) return 'state/context';
    return 'state/stores';
  }

  // Priority 6: Services (API)
  if (characteristics.isAPI) {
    if (file.includes('api/') || file.includes('routes/')) return 'services/api-endpoints';
    if (name.includes('Client') || name.includes('Service')) return 'services/api-clients';
    return 'services/data-access';
  }

  // Priority 7: Data (Models, Schemas, Validators)
  if (characteristics.hasValidation) {
    if (name.includes('Schema')) return 'data/schemas';
    if (name.includes('Validator')) return 'data/validators';
    return 'data/schemas';
  }

  if (file.includes('models/') || file.includes('entities/')) {
    return 'data/models';
  }

  if (file.includes('schemas/')) {
    return 'data/schemas';
  }

  // Priority 8: Tools (CLI, Scripts, Utilities)
  if (characteristics.isCLI) {
    return 'tools/cli-commands';
  }

  if (file.includes('scripts/')) {
    return 'tools/scripts';
  }

  if (file.includes('utils/') || file.includes('helpers/') || file.includes('lib/')) {
    return 'tools/utilities';
  }

  // Default fallback: utilities
  return 'tools/utilities';
}

/**
 * Detect alternate categories for ambiguous elements
 */
function detectAlternateCategories(
  element: ElementCharacteristics,
  characteristics: ReturnType<typeof analyzeCodeCharacteristics>,
  primaryCategory: ElementCategory
): { category: ElementCategory; confidence: number }[] {
  const alternates: { category: ElementCategory; confidence: number }[] = [];

  // Hybrid: React component that makes API calls
  if (
    characteristics.isReactComponent &&
    characteristics.isAPI &&
    primaryCategory.startsWith('ui/')
  ) {
    alternates.push({
      category: 'services/api-clients',
      confidence: 60,
    });
  }

  // Hybrid: Hook that manages state
  if (
    characteristics.isHook &&
    characteristics.usesState &&
    primaryCategory === 'state/hooks'
  ) {
    // This is expected - hooks often manage state
    // No alternate needed
  }

  // Hybrid: CLI that calls APIs
  if (
    characteristics.isCLI &&
    characteristics.isAPI &&
    primaryCategory === 'tools/cli-commands'
  ) {
    alternates.push({
      category: 'services/api-clients',
      confidence: 50,
    });
  }

  // Hybrid: Utility function with validation logic
  if (
    characteristics.hasValidation &&
    !characteristics.hasValidation &&
    primaryCategory === 'tools/utilities'
  ) {
    alternates.push({
      category: 'data/validators',
      confidence: 55,
    });
  }

  return alternates;
}

/**
 * Get category display name (human-readable)
 */
export function getCategoryDisplayName(category: ElementCategory): string {
  const displayNames: Record<ElementCategory, string> = {
    'tools/cli-commands': 'CLI Command',
    'tools/scripts': 'Script',
    'tools/utilities': 'Utility Function',
    'ui/widgets': 'UI Widget',
    'ui/pages': 'Page Component',
    'ui/components': 'UI Component',
    'services/api-endpoints': 'API Endpoint',
    'services/api-clients': 'API Client',
    'services/data-access': 'Data Access Layer',
    'state/hooks': 'React Hook',
    'state/stores': 'State Store',
    'state/context': 'React Context',
    'data/models': 'Data Model',
    'data/schemas': 'Data Schema',
    'data/validators': 'Validator',
    'generators/scaffolding': 'Code Generator',
    'generators/templates': 'Template Generator',
    'generators/migrations': 'Migration Script',
    'infrastructure/build-scripts': 'Build Script',
    'infrastructure/deployment': 'Deployment Script',
    'infrastructure/ci-cd': 'CI/CD Configuration',
    'testing/test-helpers': 'Test Helper',
    'testing/mocks': 'Mock',
    'testing/fixtures': 'Test Fixture',
  };

  return displayNames[category] || category;
}

/**
 * Get category description
 */
export function getCategoryDescription(category: ElementCategory): string {
  const descriptions: Record<ElementCategory, string> = {
    'tools/cli-commands': 'Command-line interface commands for developer tools',
    'tools/scripts': 'Automation scripts and utilities',
    'tools/utilities': 'Helper functions and utility libraries',
    'ui/widgets': 'Complex, self-contained UI widgets with internal state',
    'ui/pages': 'Top-level page components mapped to routes',
    'ui/components': 'Reusable UI components',
    'services/api-endpoints': 'HTTP endpoint handlers (routes)',
    'services/api-clients': 'Client libraries for calling external APIs',
    'services/data-access': 'Database access and query logic',
    'state/hooks': 'React hooks for state management and side effects',
    'state/stores': 'Global state stores (Redux, Zustand, etc.)',
    'state/context': 'React Context providers',
    'data/models': 'Data models and entity definitions',
    'data/schemas': 'Validation schemas (Zod, Yup, etc.)',
    'data/validators': 'Custom validation logic',
    'generators/scaffolding': 'Code generators and scaffolding tools',
    'generators/templates': 'Template generators',
    'generators/migrations': 'Database or code migration scripts',
    'infrastructure/build-scripts': 'Build and compilation scripts',
    'infrastructure/deployment': 'Deployment automation scripts',
    'infrastructure/ci-cd': 'Continuous integration and deployment configs',
    'testing/test-helpers': 'Test utility functions',
    'testing/mocks': 'Mock objects and functions for testing',
    'testing/fixtures': 'Test data fixtures',
  };

  return descriptions[category] || '';
}
