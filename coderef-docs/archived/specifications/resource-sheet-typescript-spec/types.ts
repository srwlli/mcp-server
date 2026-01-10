/**
 * Type definitions for Resource Sheet Module System
 *
 * WO-RESOURCE-SHEET-MCP-TOOL-001/SETUP-003
 *
 * These types define the structure of documentation modules used to compose
 * resource sheets. Modules are small, reusable templates that combine to create
 * comprehensive technical documentation.
 */

/**
 * Element type categories - user-friendly classification
 */
export type ElementCategory =
  | 'tools/cli-commands'
  | 'tools/scripts'
  | 'tools/utilities'
  | 'ui/widgets'
  | 'ui/pages'
  | 'ui/components'
  | 'services/api-endpoints'
  | 'services/api-clients'
  | 'services/data-access'
  | 'state/hooks'
  | 'state/stores'
  | 'state/context'
  | 'data/models'
  | 'data/schemas'
  | 'data/validators'
  | 'generators/scaffolding'
  | 'generators/templates'
  | 'generators/migrations'
  | 'infrastructure/build-scripts'
  | 'infrastructure/deployment'
  | 'infrastructure/ci-cd'
  | 'testing/test-helpers'
  | 'testing/mocks'
  | 'testing/fixtures';

/**
 * Module names - universal and conditional
 */
export type ModuleName =
  // Universal modules (always included)
  | 'architecture'
  | 'integration'
  | 'testing'
  | 'performance'
  // Conditional modules (based on code characteristics)
  | 'state'
  | 'props'
  | 'lifecycle'
  | 'events'
  | 'endpoints'
  | 'auth'
  | 'errors'
  | 'validation'
  | 'persistence'
  | 'routing'
  | 'accessibility';

/**
 * Code element characteristics detected from .coderef/index.json
 */
export interface ElementCharacteristics {
  /** Element name (e.g., "FileTree", "useAuth", "AuthService") */
  name: string;

  /** Element type (function, class, interface, etc.) */
  type: string;

  /** File path */
  file: string;

  /** Imports used by this element */
  imports: string[];

  /** Exports from this element */
  exports: string[];

  /** Element-specific metadata */
  metadata: {
    /** React component with JSX */
    hasJSX?: boolean;

    /** React hooks used */
    hooks?: string[];

    /** Component props */
    props?: PropMetadata[];

    /** State variables */
    stateVariables?: StateMetadata[];

    /** Event handlers */
    eventHandlers?: EventMetadata[];

    /** API calls */
    apiCalls?: ApiCallMetadata[];

    /** Additional metadata */
    [key: string]: any;
  };
}

/**
 * Prop metadata from TypeScript interface
 */
export interface PropMetadata {
  name: string;
  type: string;
  required: boolean;
  default?: string;
  description?: string;
}

/**
 * State variable metadata
 */
export interface StateMetadata {
  name: string;
  type: string;
  initialValue?: string;
  persisted: boolean;
  persistenceKey?: string;
}

/**
 * Event handler metadata
 */
export interface EventMetadata {
  name: string;
  type: string;
  description?: string;
}

/**
 * API call metadata
 */
export interface ApiCallMetadata {
  method: string;
  endpoint?: string;
  library: string; // 'fetch', 'axios', etc.
}

/**
 * Characteristic check function
 * Returns true if the element has the characteristic
 */
export type CharacteristicCheck = (element: ElementCharacteristics) => boolean;

/**
 * Module trigger conditions
 */
export interface ModuleTriggers {
  /** Module name */
  module: ModuleName;

  /** Conditions that activate this module */
  conditions: CharacteristicCheck[];

  /** Human-readable trigger description */
  description: string;
}

/**
 * Module data structure - defines a documentation module
 */
export interface DocumentationModule {
  /** Module name */
  name: ModuleName;

  /** Module type (universal or conditional) */
  type: 'universal' | 'conditional';

  /** Categories this module applies to */
  appliesTo: ElementCategory[];

  /** Trigger conditions for conditional modules */
  triggers?: ModuleTriggers;

  /** Markdown template content */
  markdownTemplate: string;

  /** JSON Schema template content */
  schemaTemplate: string;

  /** JSDoc template content */
  jsdocTemplate: string;

  /** Auto-fill functions - extract data from ElementCharacteristics */
  autoFill: {
    /** Fields that can be auto-filled from code analysis */
    fields: string[];

    /** Extraction function */
    extract: (element: ElementCharacteristics) => Record<string, any>;
  };

  /** Manual sections that require human input */
  manualSections: {
    /** Section name */
    name: string;

    /** Prompt for human to fill */
    prompt: string;

    /** Example content */
    example?: string;
  }[];
}

/**
 * Selected modules for an element
 */
export interface SelectedModules {
  /** Element being documented */
  element: ElementCharacteristics;

  /** Detected category */
  category: ElementCategory;

  /** Selected module names */
  modules: ModuleName[];

  /** Confidence score (0-100) */
  confidence: number;

  /** Reason for selection */
  reason: string;
}

/**
 * Composed documentation output
 */
export interface ComposedDocumentation {
  /** Element name */
  elementName: string;

  /** Category */
  category: ElementCategory;

  /** Modules used */
  modulesUsed: ModuleName[];

  /** Markdown output */
  markdown: string;

  /** JSON Schema output */
  schema: string;

  /** JSDoc output */
  jsdoc: string;

  /** Auto-fill percentage (0-100) */
  autoFillRate: number;

  /** Sections flagged for human review */
  reviewFlags: {
    section: string;
    reason: string;
  }[];

  /** UDS metadata */
  uds: {
    workorder_id?: string;
    feature_id?: string;
    generated_by: string;
    timestamp: string;
  };
}

/**
 * Generation mode
 */
export type GenerationMode =
  | 'reverse-engineer'  // Auto-fill from existing code
  | 'template'          // Empty template for planning
  | 'refresh';          // Update existing docs

/**
 * Tool input parameters
 */
export interface GenerateResourceSheetInput {
  /** Project path */
  project_path: string;

  /** Element name or file path */
  element_name: string;

  /** Generation mode */
  mode: GenerationMode;

  /** Optional: Workorder ID for UDS tracking */
  workorder_id?: string;

  /** Optional: Feature ID for UDS tracking */
  feature_id?: string;

  /** Optional: Custom output path */
  output_path?: string;

  /** Optional: Auto-analyze with coderef_scan */
  auto_analyze?: boolean;

  /** Optional: Validate against code */
  validate_against_code?: boolean;
}

/**
 * Tool output
 */
export interface GenerateResourceSheetOutput {
  /** Success status */
  success: boolean;

  /** Composed documentation */
  documentation?: ComposedDocumentation;

  /** Output file paths */
  files?: {
    markdown: string;
    schema: string;
    jsdoc: string;
  };

  /** Error message if failed */
  error?: string;

  /** Warnings */
  warnings?: string[];
}

/**
 * Detection result
 */
export interface DetectionResult {
  /** Element characteristics */
  element: ElementCharacteristics;

  /** Detected category */
  category: ElementCategory;

  /** Confidence score (0-100) */
  confidence: number;

  /** Alternate categories if ambiguous */
  alternates?: {
    category: ElementCategory;
    confidence: number;
  }[];
}

/**
 * Module selection result
 */
export interface SelectionResult {
  /** Selected modules */
  modules: ModuleName[];

  /** Selection rationale */
  rationale: Record<ModuleName, string>;

  /** Estimated auto-fill rate (0-100) */
  estimatedAutoFill: number;
}
