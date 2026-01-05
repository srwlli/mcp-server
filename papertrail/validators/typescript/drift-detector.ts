// coderef-cli/src/drift-detector.ts
import fs from 'fs';
import path from 'path';
import { parseCoderefTag } from '@coderef/core';
import { normalizeCoderefPath, loadJsonFile as coreLoadJsonFile } from '@coderef/core';
import { scanCurrentElements } from '@coderef/core';
import { 
  IndexedCoderef, 
  DriftStatus, 
  DriftReport, 
  ElementData,
  DriftDetectionOptions
} from '@coderef/core';

/**
 * Detects drift between the Coderef index and the current codebase
 * @param indexPath Path to the coderef-index.json file
 * @param sourceDir Directory to scan for current code state
 * @param options Configuration options
 * @returns A report of all drift detected
 */
export async function detectDrift(
  indexPath: string, 
  sourceDir: string, 
  options: DriftDetectionOptions = {}
): Promise<DriftReport[]> {
  const { 
    lang = 'ts', 
    fixThreshold = 0.7, 
    verbose = false,
    scanOptions = {}
  } = options;
  
  // 1. Load the index file
  if (!fs.existsSync(indexPath)) {
    throw new Error(`Index file not found: ${indexPath}`);
  }

  const index = coreLoadJsonFile<Record<string, { file: string; line: number }>>(
    indexPath, 
    {}
  );
  
  if (verbose) console.log(`📊 Loaded ${Object.keys(index).length} references from index`);
  
  // 2. Parse index into structured references
  const parsedRefs: IndexedCoderef[] = [];
  
  for (const [coderef, info] of Object.entries(index)) {
    try {
      const parsed = parseCoderefTag(coderef);
      parsedRefs.push({
        ...parsed,
        file: info.file,
        indexLine: info.line,
      });
    } catch (error) {
      if (verbose) console.warn(`⚠️ Invalid coderef in index: ${coderef}`);
    }
  }
  
  // 3. Scan the current code state
  const currentElements = await scanCurrentElements(sourceDir, lang, scanOptions);
  if (verbose) console.log(`🔍 Found ${currentElements.length} code elements in current codebase`);
  
  // 4. Compare and detect drift
  const driftReports: DriftReport[] = [];
  
  for (const ref of parsedRefs) {
    const refString = `@${ref.type}/${ref.path}${ref.element ? `#${ref.element}` : ''}${ref.line ? `:${ref.line}` : ''}`;
    const report: DriftReport = {
      coderef: refString,
      status: 'unknown',
      originalFile: ref.file,
      originalLine: ref.indexLine,
      confidence: 1.0,
    };

    // First check if the file still exists
    if (!fs.existsSync(ref.file)) {
      report.status = 'missing';
      report.suggestedFix = `File no longer exists. Consider removing this reference.`;
      driftReports.push(report);
      continue;
    }

    // Try to find the element by name first (most accurate match)
    const nameMatches = currentElements.filter(
      el => el.name === ref.element && normalizeCoderefPath(el.file) === normalizeCoderefPath(ref.file)
    );

    if (nameMatches.length === 1) {
      // Found an exact match by name and file
      const match = nameMatches[0];
      
      if (match.line === ref.line) {
        // Element is in the exact same position
        report.status = 'unchanged';
        report.currentFile = match.file;
        report.currentLine = match.line;
      } else {
        // Element moved to a different line
        report.status = 'moved';
        report.currentFile = match.file;
        report.currentLine = match.line;
        report.suggestedFix = `Update line number: ${refString.replace(`:${ref.line}`, `:${match.line}`)}`;
      }
    } else if (nameMatches.length === 0) {
      // No exact name match, try to find by line position
      const lineMatches = currentElements.filter(
        el => el.line === ref.line && normalizeCoderefPath(el.file) === normalizeCoderefPath(ref.file)
      );

      if (lineMatches.length === 1) {
        // Something else is at the same position
        const match = lineMatches[0];
        
        // Check similarity between element names
        const similarity = calculateNameSimilarity(String(ref.element), match.name);
        
        if (similarity > fixThreshold) {
          // Likely renamed
          report.status = 'renamed';
          report.currentFile = match.file;
          report.currentLine = match.line;
          report.confidence = similarity;
          report.suggestedFix = `Update element name: ${refString.replace(`#${ref.element}`, `#${match.name}`)}`;
        } else {
          // Completely different element
          report.status = 'missing';
          report.suggestedFix = `Element not found. New element '${match.name}' is at this position.`;
        }
      } else {
        // Nothing at position and no name match
        report.status = 'missing';
        
        // Try to find similar named elements in the same file
        const fileElements = currentElements.filter(
          el => normalizeCoderefPath(el.file) === normalizeCoderefPath(ref.file)
        );
        
        if (fileElements.length > 0) {
          // Find most similar named element
          let bestMatch = fileElements[0];
          let bestSimilarity = calculateNameSimilarity(String(ref.element), bestMatch.name);
          
          for (const el of fileElements.slice(1)) {
            const similarity = calculateNameSimilarity(String(ref.element), el.name);
            if (similarity > bestSimilarity) {
              bestSimilarity = similarity;
              bestMatch = el;
            }
          }
          
          if (bestSimilarity > fixThreshold) {
            report.confidence = bestSimilarity;
            report.suggestedFix = `Element may have been renamed and moved. Consider: @${ref.type}/${ref.path}#${bestMatch.name}:${bestMatch.line}`;
          } else {
            report.suggestedFix = `Element not found. Consider removing this reference.`;
          }
        } else {
          report.suggestedFix = `Element not found. Consider removing this reference.`;
        }
      }
    } else {
      // Multiple elements with same name - ambiguous
      report.status = 'unknown';
      report.suggestedFix = `Multiple elements with name '${ref.element}' found. Manual inspection needed.`;
    }
    
    driftReports.push(report);
  }
  
  return driftReports;
}

/**
 * Calculate similarity between two names (0-1)
 */
function calculateNameSimilarity(name1: string, name2: string): number {
  // Simple case - exact match
  if (name1 === name2) return 1.0;
  
  // For very short names, be conservative
  if (name1.length < 3 || name2.length < 3) return 0.0;
  
  // Levenshtein distance calculation
  const matrix: number[][] = [];
  
  // Initialize matrix
  for (let i = 0; i <= name1.length; i++) {
    matrix[i] = [i];
  }
  
  for (let j = 0; j <= name2.length; j++) {
    matrix[0][j] = j;
  }
  
  // Fill the matrix
  for (let i = 1; i <= name1.length; i++) {
    for (let j = 1; j <= name2.length; j++) {
      const cost = name1[i - 1] === name2[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,      // deletion
        matrix[i][j - 1] + 1,      // insertion
        matrix[i - 1][j - 1] + cost // substitution
      );
    }
  }
  
  // Get the Levenshtein distance
  const distance = matrix[name1.length][name2.length];
  
  // Convert to similarity score (0-1)
  const maxLength = Math.max(name1.length, name2.length);
  const similarity = 1 - (distance / maxLength);
  
  return similarity;
}

/**
 * Generate a summary of the drift report
 */
export function summarizeDriftReport(reports: DriftReport[]): string {
  const counts = {
    unchanged: 0,
    moved: 0,
    renamed: 0,
    missing: 0,
    unknown: 0,
    total: reports.length
  };
  
  for (const report of reports) {
    counts[report.status]++;
  }
  
  return `
Drift Detection Summary:
-----------------------
✅ Unchanged: ${counts.unchanged} (${Math.round(counts.unchanged / counts.total * 100)}%)
📍 Moved: ${counts.moved} (${Math.round(counts.moved / counts.total * 100)}%)
🔄 Renamed: ${counts.renamed} (${Math.round(counts.renamed / counts.total * 100)}%)
❌ Missing: ${counts.missing} (${Math.round(counts.missing / counts.total * 100)}%)
❓ Unknown: ${counts.unknown} (${Math.round(counts.unknown / counts.total * 100)}%)
-----------------------
Total References: ${counts.total}
  `;
}

/**
 * Print a detailed drift report to console
 */
export function printDriftReport(reports: DriftReport[]): void {
  console.log(summarizeDriftReport(reports));
  
  const changedReports = reports.filter(r => r.status !== 'unchanged');
  
  if (changedReports.length === 0) {
    console.log("🎉 All references are up to date!");
    return;
  }
  
  console.log("\nDetailed Changes:");
  console.log("-----------------");
  
  for (const report of changedReports) {
    let statusEmoji;
    switch (report.status) {
      case 'moved': statusEmoji = '📍'; break;
      case 'renamed': statusEmoji = '🔄'; break;
      case 'missing': statusEmoji = '❌'; break;
      case 'unknown': statusEmoji = '❓'; break;
      default: statusEmoji = ''; break;
    }
    
    console.log(`${statusEmoji} ${report.coderef}`);
    console.log(`   File: ${report.originalFile}`);
    console.log(`   Original Line: ${report.originalLine}`);
    
    if (report.currentFile && report.status !== 'missing') {
      console.log(`   Current Line: ${report.currentLine}`);
    }
    
    if (report.suggestedFix) {
      console.log(`   Suggested Fix: ${report.suggestedFix}`);
    }
    
    console.log(); // Empty line for separation
  }
}

/**
 * Validates a single fix before applying
 */
function validateFix(
  report: DriftReport,
  newRef: string,
  index: Record<string, { file: string; line: number }>
): { valid: boolean; reason?: string } {
  // Check 1: Ensure the new reference is a valid CodeRef format
  try {
    parseCoderefTag(newRef);
  } catch (error) {
    return { valid: false, reason: 'Invalid CodeRef format' };
  }

  // Check 2: Verify the fix won't create a duplicate
  if (index[newRef] && report.coderef !== newRef) {
    return { valid: false, reason: 'Would create duplicate reference' };
  }

  // Check 3: For moved/renamed, ensure we have current file and line
  if (report.status === 'moved' || report.status === 'renamed') {
    if (!report.currentFile || !report.currentLine) {
      return { valid: false, reason: 'Missing current location data' };
    }

    // Check 4: Verify the target file exists
    if (!fs.existsSync(report.currentFile)) {
      return { valid: false, reason: 'Target file does not exist' };
    }

    // Check 5: Validate line number is reasonable (not negative or zero)
    if (report.currentLine < 1) {
      return { valid: false, reason: 'Invalid line number' };
    }
  }

  return { valid: true };
}

/**
 * Apply suggested fixes to the index file with comprehensive validation and safety measures
 */
export function applyFixes(
  reports: DriftReport[],
  indexPath: string,
  options: { dryRun?: boolean; verbose?: boolean } = {}
): { fixed: number; total: number } {
  const { dryRun = false, verbose = false } = options;

  // Load the current index
  const index = coreLoadJsonFile<Record<string, { file: string; line: number }>>(
    indexPath,
    {}
  );

  // Create backup before any modifications (unless in dry-run mode)
  const backupPath = `${indexPath}.bak`;
  if (!dryRun) {
    try {
      fs.copyFileSync(indexPath, backupPath);
      if (verbose) {
        console.log(`💾 Created backup at ${backupPath}`);
      }
    } catch (error: any) {
      throw new Error(`Failed to create backup: ${error.message}`);
    }
  }

  let fixedCount = 0;
  const toFixCount = reports.filter(r =>
    r.status !== 'unchanged' &&
    r.suggestedFix &&
    !r.suggestedFix.includes('Manual inspection')
  ).length;

  // Collect all fixes first for transaction-based application
  const fixesToApply: Array<{
    oldRef: string;
    newRef: string;
    oldData: { file: string; line: number };
    newData: { file: string; line: number };
  }> = [];

  // Validate and prepare all fixes
  for (const report of reports) {
    if (report.status === 'unchanged' || !report.suggestedFix) {
      continue;
    }

    // Skip if manual inspection needed
    if (report.suggestedFix.includes('Manual inspection')) {
      if (verbose && dryRun) {
        console.log(`⏭️  Skipping ${report.coderef}: Requires manual inspection`);
      }
      continue;
    }

    // Extract the new reference from the suggested fix
    const newRefMatch = report.suggestedFix.match(/@[A-Z][A-Za-z0-9]*\/[^#:{}]+(?:#[^:{}]+)?(?::\d+)?/);
    if (!newRefMatch) {
      if (verbose && dryRun) {
        console.log(`⏭️  Skipping ${report.coderef}: Could not parse suggested fix`);
      }
      continue;
    }

    const newRef = newRefMatch[0];

    // Validate the fix
    const validation = validateFix(report, newRef, index);
    if (!validation.valid) {
      if (verbose) {
        console.log(`❌ Skipping ${report.coderef}: ${validation.reason}`);
      }
      continue;
    }

    // In dry-run mode, show what would be changed
    if (dryRun) {
      console.log(`\nWould update: ${report.originalFile}`);
      console.log(`  OLD: ${report.coderef}`);
      console.log(`  NEW: ${newRef}`);
      console.log(`  Reason: ${report.status} (confidence: ${report.confidence.toFixed(2)})`);
      fixedCount++;
    } else {
      // Prepare fix for transaction
      const oldData = index[report.coderef];
      const newData = {
        file: report.currentFile || oldData.file,
        line: report.currentLine || oldData.line
      };

      fixesToApply.push({
        oldRef: report.coderef,
        newRef,
        oldData,
        newData
      });
    }
  }

  // Apply all fixes in a transaction (all or nothing)
  if (!dryRun && fixesToApply.length > 0) {
    try {
      // Apply all fixes to the index
      for (const fix of fixesToApply) {
        delete index[fix.oldRef];
        index[fix.newRef] = fix.newData;

        if (verbose) {
          console.log(`✅ Fixed: ${fix.oldRef} → ${fix.newRef}`);
        }

        fixedCount++;
      }

      // Write the updated index
      const indexContent = JSON.stringify(index, null, 2);

      // Validate it's valid JSON before writing
      JSON.parse(indexContent);

      fs.writeFileSync(indexPath, indexContent, 'utf-8');

      if (verbose) {
        console.log(`💾 Updated index at ${indexPath}`);
      }

      // Remove backup on success
      if (fs.existsSync(backupPath)) {
        fs.unlinkSync(backupPath);
        if (verbose) {
          console.log(`🗑️  Removed backup (operation succeeded)`);
        }
      }
    } catch (error: any) {
      // Rollback on any error
      console.error(`❌ Error applying fixes: ${error.message}`);

      if (fs.existsSync(backupPath)) {
        try {
          fs.copyFileSync(backupPath, indexPath);
          console.log(`♻️  Rolled back to backup from ${backupPath}`);
        } catch (rollbackError: any) {
          console.error(`❌ CRITICAL: Rollback failed: ${rollbackError.message}`);
          console.error(`⚠️  Manual recovery needed from ${backupPath}`);
        }
      }

      throw error;
    }
  }

  return { fixed: fixedCount, total: toFixCount };
}