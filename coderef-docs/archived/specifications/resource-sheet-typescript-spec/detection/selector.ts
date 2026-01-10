/**
 * Module Selector - Selects documentation modules based on element characteristics
 *
 * WO-RESOURCE-SHEET-MCP-TOOL-001/SELECT-001
 *
 * Given category and characteristics, selects which modules to include in documentation.
 */

import { ElementCharacteristics, ElementCategory, ModuleName, SelectionResult } from '../types';
import { analyzeCodeCharacteristics } from './analyzer';

/**
 * Select modules for element documentation
 */
export function selectModules(
  element: ElementCharacteristics,
  category: ElementCategory
): SelectionResult {
  const characteristics = analyzeCodeCharacteristics(element);

  // Universal modules (always included)
  const modules: ModuleName[] = [
    'architecture',
    'integration',
    'testing',
    'performance',
  ];

  // Conditional modules based on characteristics
  const conditionalModules = selectConditionalModules(characteristics, category);
  modules.push(...conditionalModules);

  // Generate rationale for each module
  const rationale = generateRationale(modules, characteristics, category);

  // Estimate auto-fill rate
  const estimatedAutoFill = estimateAutoFillRate(modules, element);

  return {
    modules,
    rationale,
    estimatedAutoFill,
  };
}

/**
 * Select conditional modules based on characteristics
 */
function selectConditionalModules(
  characteristics: ReturnType<typeof analyzeCodeCharacteristics>,
  category: ElementCategory
): ModuleName[] {
  const modules: ModuleName[] = [];

  // State management
  if (characteristics.usesState) {
    modules.push('state');
  }

  // Props (React/Vue components)
  if (characteristics.hasProps) {
    modules.push('props');
  }

  // Lifecycle (components with effects)
  if (characteristics.hasLifecycle) {
    modules.push('lifecycle');
  }

  // Events (UI components with handlers)
  if (characteristics.hasEvents) {
    modules.push('events');
  }

  // API endpoints
  if (characteristics.isAPI) {
    modules.push('endpoints');
  }

  // Authentication
  if (characteristics.hasAuth) {
    modules.push('auth');
  }

  // Error handling (all elements, but only if significant error logic)
  if (category.startsWith('services/') || category.startsWith('state/')) {
    modules.push('errors');
  }

  // Validation
  if (characteristics.hasValidation) {
    modules.push('validation');
  }

  // Persistence
  if (characteristics.hasPersistence) {
    modules.push('persistence');
  }

  // Routing
  if (characteristics.hasRouting || category === 'ui/pages') {
    modules.push('routing');
  }

  // Accessibility (UI components)
  if (
    characteristics.hasAccessibility ||
    category.startsWith('ui/')
  ) {
    modules.push('accessibility');
  }

  return modules;
}

/**
 * Generate rationale for each selected module
 */
function generateRationale(
  modules: ModuleName[],
  characteristics: ReturnType<typeof analyzeCodeCharacteristics>,
  category: ElementCategory
): Record<ModuleName, string> {
  const rationale: Record<ModuleName, string> = {};

  modules.forEach((module) => {
    switch (module) {
      case 'architecture':
        rationale[module] = 'Universal module - documents component structure and dependencies';
        break;

      case 'integration':
        rationale[module] = 'Universal module - documents how element connects to other code';
        break;

      case 'testing':
        rationale[module] = 'Universal module - documents test strategy and coverage';
        break;

      case 'performance':
        rationale[module] = 'Universal module - documents performance budgets and bottlenecks';
        break;

      case 'state':
        rationale[module] = characteristics.usesState
          ? 'Element manages state (useState/useReducer/store detected)'
          : 'State module included for category';
        break;

      case 'props':
        rationale[module] = `Element has ${characteristics.hasProps ? 'props interface' : 'parameters'}`;
        break;

      case 'lifecycle':
        rationale[module] = 'Element has lifecycle hooks (useEffect/componentDidMount detected)';
        break;

      case 'events':
        rationale[module] = 'Element handles user interactions (event handlers detected)';
        break;

      case 'endpoints':
        rationale[module] = characteristics.isAPI
          ? 'Element is an API endpoint or makes API calls'
          : 'API interactions detected';
        break;

      case 'auth':
        rationale[module] = 'Authentication logic detected (JWT/tokens/auth imports)';
        break;

      case 'errors':
        rationale[module] = `Error handling important for ${category} elements`;
        break;

      case 'validation':
        rationale[module] = 'Validation schema detected (Zod/Yup/custom validators)';
        break;

      case 'persistence':
        rationale[module] = 'Data persistence detected (localStorage/IndexedDB/API)';
        break;

      case 'routing':
        rationale[module] = characteristics.hasRouting
          ? 'Routing logic detected (router imports/navigation)'
          : 'Page component - routing module included';
        break;

      case 'accessibility':
        rationale[module] = characteristics.hasAccessibility
          ? 'ARIA attributes or keyboard handlers detected'
          : 'UI component - accessibility documentation important';
        break;

      default:
        rationale[module] = `Module selected for ${category}`;
    }
  });

  return rationale;
}

/**
 * Estimate auto-fill rate (percentage of doc that can be filled from code)
 */
function estimateAutoFillRate(
  modules: ModuleName[],
  element: ElementCharacteristics
): number {
  let totalSections = 0;
  let autoFillable = 0;

  modules.forEach((module) => {
    switch (module) {
      case 'architecture':
        totalSections += 5; // Hierarchy, file structure, dependencies, pattern, principles
        autoFillable += 3; // Hierarchy, file structure, dependencies auto-fillable
        break;

      case 'integration':
        totalSections += 4; // Internal, external, data flow, contracts
        autoFillable += 2; // Internal, external auto-fillable
        break;

      case 'testing':
        totalSections += 4; // Existing coverage, gaps, strategy, recommendations
        autoFillable += 1; // Existing coverage auto-fillable
        break;

      case 'performance':
        totalSections += 6; // Budgets, limits, bottlenecks, optimizations, memory, caching
        autoFillable += 2; // Limits (if tested), memory (if profiled)
        break;

      case 'state':
        totalSections += 5; // Ownership, initialization, updates, sync, persistence
        autoFillable += 3; // Ownership, initialization, persistence auto-fillable
        break;

      case 'props':
        totalSections += 3; // Interface, validation, examples
        autoFillable += 2; // Interface, validation auto-fillable
        break;

      case 'lifecycle':
        totalSections += 3; // Initialization, updates, cleanup
        autoFillable += 2; // Hooks detected, cleanup detected
        break;

      case 'events':
        totalSections += 3; // Catalog, flow, contracts
        autoFillable += 1; // Catalog auto-fillable
        break;

      case 'endpoints':
        totalSections += 3; // Catalog, schemas, errors
        autoFillable += 2; // Catalog, schemas auto-fillable
        break;

      case 'auth':
        totalSections += 4; // Strategy, flow, tokens, permissions
        autoFillable += 1; // Token handling if detected
        break;

      case 'errors':
        totalSections += 3; // Taxonomy, boundaries, recovery
        autoFillable += 1; // Error types if detected
        break;

      case 'validation':
        totalSections += 3; // Schema, strategy, messages
        autoFillable += 2; // Schema, strategy auto-fillable
        break;

      case 'persistence':
        totalSections += 4; // Mechanism, data, migration, sync
        autoFillable += 2; // Mechanism, data auto-fillable
        break;

      case 'routing':
        totalSections += 3; // Definitions, flow, guards
        autoFillable += 1; // Definitions auto-fillable
        break;

      case 'accessibility':
        totalSections += 5; // ARIA, keyboard, screen reader, WCAG, gaps
        autoFillable += 2; // ARIA, keyboard auto-fillable if detected
        break;
    }
  });

  // Calculate percentage
  const autoFillRate = totalSections > 0 ? (autoFillable / totalSections) * 100 : 0;

  // Adjust based on element metadata richness
  const metadataRichness = calculateMetadataRichness(element);
  const adjustedRate = autoFillRate * metadataRichness;

  return Math.round(adjustedRate);
}

/**
 * Calculate how rich the element metadata is (0.0 - 1.0)
 * Rich metadata = higher auto-fill rate
 */
function calculateMetadataRichness(element: ElementCharacteristics): number {
  let score = 0.5; // Start at 50%

  // Has props defined
  if (element.metadata.props && element.metadata.props.length > 0) {
    score += 0.1;
  }

  // Has state variables defined
  if (element.metadata.stateVariables && element.metadata.stateVariables.length > 0) {
    score += 0.1;
  }

  // Has event handlers defined
  if (element.metadata.eventHandlers && element.metadata.eventHandlers.length > 0) {
    score += 0.1;
  }

  // Has API calls documented
  if (element.metadata.apiCalls && element.metadata.apiCalls.length > 0) {
    score += 0.1;
  }

  // Has JSX (means coderef analyzed React properly)
  if (element.metadata.hasJSX) {
    score += 0.05;
  }

  // Has hooks list
  if (element.metadata.hooks && element.metadata.hooks.length > 0) {
    score += 0.05;
  }

  // Cap at 1.0
  return Math.min(1.0, score);
}

/**
 * Get module priority (for sorting)
 * Universal modules first, then conditional by importance
 */
export function getModulePriority(module: ModuleName): number {
  const priority: Record<ModuleName, number> = {
    // Universal modules (highest priority)
    architecture: 1,
    integration: 2,
    testing: 3,
    performance: 4,

    // Conditional modules (by importance)
    state: 5,
    props: 6,
    lifecycle: 7,
    events: 8,
    endpoints: 9,
    auth: 10,
    errors: 11,
    validation: 12,
    persistence: 13,
    routing: 14,
    accessibility: 15,
  };

  return priority[module] || 99;
}

/**
 * Sort modules by priority
 */
export function sortModules(modules: ModuleName[]): ModuleName[] {
  return modules.slice().sort((a, b) => getModulePriority(a) - getModulePriority(b));
}
