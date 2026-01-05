export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  normalizedPath?: string;
}

export class PathValidationService {
  private readonly MAX_PATH_LENGTH = 260; // Windows MAX_PATH
  private readonly INVALID_CHARS = /[<>:"|?*]/;

  async validatePath(path: string): Promise<ValidationResult> {
    const errors: string[] = [];

    // Check for invalid characters
    if (this.INVALID_CHARS.test(path)) {
      errors.push('Path contains invalid characters');
    }

    // Check path length
    if (path.length > this.MAX_PATH_LENGTH) {
      errors.push('Path exceeds maximum length');
    }

    // Check for empty path
    if (!path.trim()) {
      errors.push('Path cannot be empty');
    }

    // Check for relative path components
    if (path.includes('..')) {
      errors.push('Path contains relative components (..)');
    }

    return {
      isValid: errors.length === 0,
      errors,
      normalizedPath: this.normalizePath(path)
    };
  }

  normalizePath(path: string): string {
    // Convert all slashes to backslashes for Windows
    let normalized = path.replace(/\//g, '\\');

    // Remove trailing slashes
    normalized = normalized.replace(/\\+$/, '');

    // Remove duplicate slashes
    normalized = normalized.replace(/\\+/g, '\\');

    return normalized;
  }
} 