// coderef-cli/src/validator.ts
import fs from 'fs';
import { parseCoderefTag } from '@coderef/core/parser.js';
import path from 'path';

export function validateTagsInFile(filePath: string): string[] {
  const issues: string[] = [];
  const lines = fs.readFileSync(filePath, 'utf-8').split('\n');

  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    if (trimmed.startsWith('@')) {
      try {
        parseCoderefTag(trimmed);
      } catch (err: any) {
        issues.push(`❌ Invalid tag at ${filePath}:${idx + 1} → ${trimmed}`);
      }
    }
  });

  return issues;
}

export function validateTagsInDirectory(dir: string, lang = 'ts'): string[] {
  const results: string[] = [];
  const files = fs.readdirSync(dir);

  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      results.push(...validateTagsInDirectory(fullPath, lang));
    } else if (file.endsWith(`.${lang}`)) {
      results.push(...validateTagsInFile(fullPath));
    }
  }

  return results;
}
