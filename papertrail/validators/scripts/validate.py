#!/usr/bin/env python3
"""
Script/Test Frontmatter Validator

Validates triangular bidirectional references between:
- Resource sheets
- Scripts
- Tests

Usage:
    python validate.py /path/to/project
    python validate.py /path/to/project --path src/
    python validate.py /path/to/project --verbose
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'


def extract_yaml_frontmatter(content: str, file_type: str) -> Optional[Dict]:
    """Extract YAML frontmatter from script/test file."""

    # Python: """ ... """ or ''' ... '''
    if file_type == 'python':
        match = re.search(r'^"""[\s\n]---\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        if not match:
            match = re.search(r"^'''[\s\n]---\n(.*?)\n---", content, re.DOTALL | re.MULTILINE)

    # Bash: : ' ... '
    elif file_type == 'bash':
        match = re.search(r"^:\s*'[\s\n]---\n(.*?)\n---[\s\n]'", content, re.DOTALL | re.MULTILINE)

    # PowerShell: <# ... #>
    elif file_type == 'powershell':
        match = re.search(r'^<#[\s\n]---\n(.*?)\n---[\s\n]#>', content, re.DOTALL | re.MULTILINE)

    # TypeScript/JavaScript: /** ... */
    elif file_type in ('typescript', 'javascript'):
        match = re.search(r'^/\*\*[\s\n]\*\s*---\n(.*?)\n\*\s*---[\s\n]\*/', content, re.DOTALL | re.MULTILINE)

    else:
        return None

    if not match:
        return None

    yaml_content = match.group(1)
    try:
        return yaml.safe_load(yaml_content)
    except yaml.YAMLError:
        return None


def get_file_type(file_path: Path) -> Optional[str]:
    """Determine file type from extension."""
    suffix = file_path.suffix.lower()
    if suffix == '.py':
        return 'python'
    elif suffix == '.sh':
        return 'bash'
    elif suffix == '.ps1':
        return 'powershell'
    elif suffix == '.ts':
        return 'typescript'
    elif suffix == '.js':
        return 'javascript'
    return None


def find_scripts_and_tests(project_path: Path, subpath: Optional[str] = None) -> Tuple[List[Path], List[Path]]:
    """Find all scripts and test files in project."""
    search_path = project_path / subpath if subpath else project_path

    # Exclude patterns
    exclude_patterns = ['node_modules', '.venv', 'venv', 'dist', 'build', '.git', '__pycache__']

    scripts = []
    tests = []

    for pattern in ['**/*.py', '**/*.sh', '**/*.ps1', '**/*.ts', '**/*.js']:
        for file_path in search_path.glob(pattern):
            # Skip excluded directories
            if any(excl in file_path.parts for excl in exclude_patterns):
                continue

            # Classify as test or script
            if 'test' in file_path.stem.lower() or 'tests' in file_path.parts:
                tests.append(file_path)
            else:
                scripts.append(file_path)

    return scripts, tests


def validate_triangular_references(
    project_path: Path,
    file_path: Path,
    frontmatter: Dict,
    is_test: bool,
    verbose: bool = False
) -> Tuple[bool, List[str]]:
    """Validate triangular bidirectional references."""
    errors = []

    # Check required fields
    if 'resource_sheet' not in frontmatter:
        errors.append("Missing required field: resource_sheet")
        return False, errors

    if is_test:
        if 'related_script' not in frontmatter:
            errors.append("Test file missing required field: related_script")
    else:
        if 'related_test' not in frontmatter:
            errors.append("Script file missing required field: related_test")

    if errors:
        return False, errors

    # Validate resource sheet exists
    resource_sheet_path = project_path / frontmatter['resource_sheet']
    if not resource_sheet_path.exists():
        errors.append(f"Resource sheet not found: {frontmatter['resource_sheet']}")
        return False, errors

    # Validate related file exists
    related_field = 'related_script' if is_test else 'related_test'
    related_path = project_path / frontmatter[related_field]
    if not related_path.exists():
        errors.append(f"{related_field} file not found: {frontmatter[related_field]}")
        return False, errors

    # Check resource sheet has this file in related_files
    try:
        sheet_content = resource_sheet_path.read_text(encoding='utf-8-sig')
        if sheet_content.startswith('---'):
            yaml_match = re.search(r'^---\s*\n(.*?)\n---', sheet_content, re.DOTALL)
            if yaml_match:
                sheet_frontmatter = yaml.safe_load(yaml_match.group(1))
                related_files = sheet_frontmatter.get('related_files', [])

                file_rel_path = str(file_path.relative_to(project_path)).replace('\\', '/')
                if file_rel_path not in related_files:
                    errors.append(f"Resource sheet missing this file in related_files: {file_rel_path}")
    except Exception as e:
        errors.append(f"Error reading resource sheet: {e}")

    # Check bidirectional reference (script ↔ test)
    try:
        related_content = related_path.read_text(encoding='utf-8-sig')
        related_type = get_file_type(related_path)
        if related_type:
            related_frontmatter = extract_yaml_frontmatter(related_content, related_type)
            if related_frontmatter:
                # For script → test check
                if not is_test:
                    expected_field = 'related_script'
                    file_rel_path = str(file_path.relative_to(project_path)).replace('\\', '/')
                    if expected_field not in related_frontmatter:
                        errors.append(f"Test file missing {expected_field} field")
                    elif related_frontmatter[expected_field] != file_rel_path:
                        errors.append(f"Test file {expected_field} doesn't point back to this script")

                # For test → script check
                else:
                    expected_field = 'related_test'
                    file_rel_path = str(file_path.relative_to(project_path)).replace('\\', '/')
                    if expected_field not in related_frontmatter:
                        errors.append(f"Script file missing {expected_field} field")
                    elif related_frontmatter[expected_field] != file_rel_path:
                        errors.append(f"Script file {expected_field} doesn't point back to this test")
    except Exception as e:
        errors.append(f"Error validating bidirectional reference: {e}")

    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(description='Validate script/test frontmatter and triangular references')
    parser.add_argument('project_path', help='Path to project root')
    parser.add_argument('--path', help='Subpath to validate (optional)')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')

    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"{Colors.RED}Error: Project path not found: {project_path}{Colors.RESET}")
        sys.exit(1)

    print(f"\n{Colors.CYAN}Script/Test Frontmatter Validator{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")

    # Find scripts and tests
    scripts, tests = find_scripts_and_tests(project_path, args.path)

    total_files = len(scripts) + len(tests)
    if total_files == 0:
        print(f"{Colors.YELLOW}No scripts or tests found{Colors.RESET}")
        sys.exit(0)

    print(f"Found {len(scripts)} script(s) and {len(tests)} test(s) to validate\n")

    # Validation tracking
    passed = 0
    failed = 0
    missing_frontmatter = 0
    errors_by_file = {}

    # Validate scripts
    for script_path in scripts:
        rel_path = script_path.relative_to(project_path)
        file_type = get_file_type(script_path)

        if args.verbose or failed > 0 or missing_frontmatter > 0:
            print(f"{Colors.CYAN}Validating script: {rel_path}{Colors.RESET}")

        if not file_type:
            if args.verbose:
                print(f"  {Colors.YELLOW}Unknown file type{Colors.RESET}\n")
            continue

        content = script_path.read_text(encoding='utf-8-sig')
        frontmatter = extract_yaml_frontmatter(content, file_type)

        if not frontmatter:
            missing_frontmatter += 1
            errors_by_file[str(rel_path)] = ["Missing YAML frontmatter"]
            print(f"  {Colors.RED}FAILED: Missing YAML frontmatter{Colors.RESET}\n")
            continue

        # Validate triangular references
        valid, errors = validate_triangular_references(project_path, script_path, frontmatter, False, args.verbose)

        if valid:
            passed += 1
            if args.verbose:
                print(f"  {Colors.GREEN}PASSED: Valid{Colors.RESET}\n")
        else:
            failed += 1
            errors_by_file[str(rel_path)] = errors
            print(f"  {Colors.RED}FAILED: Validation failed:{Colors.RESET}")
            for error in errors:
                print(f"     - {error}")
            print()

    # Validate tests
    for test_path in tests:
        rel_path = test_path.relative_to(project_path)
        file_type = get_file_type(test_path)

        if args.verbose or failed > 0 or missing_frontmatter > 0:
            print(f"{Colors.CYAN}Validating test: {rel_path}{Colors.RESET}")

        if not file_type:
            if args.verbose:
                print(f"  {Colors.YELLOW}Unknown file type{Colors.RESET}\n")
            continue

        content = test_path.read_text(encoding='utf-8-sig')
        frontmatter = extract_yaml_frontmatter(content, file_type)

        if not frontmatter:
            missing_frontmatter += 1
            errors_by_file[str(rel_path)] = ["Missing YAML frontmatter"]
            print(f"  {Colors.RED}FAILED: Missing YAML frontmatter{Colors.RESET}\n")
            continue

        # Validate triangular references
        valid, errors = validate_triangular_references(project_path, test_path, frontmatter, True, args.verbose)

        if valid:
            passed += 1
            if args.verbose:
                print(f"  {Colors.GREEN}PASSED: Valid{Colors.RESET}\n")
        else:
            failed += 1
            errors_by_file[str(rel_path)] = errors
            print(f"  {Colors.RED}FAILED: Validation failed:{Colors.RESET}")
            for error in errors:
                print(f"     - {error}")
            print()

    # Summary
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.CYAN}Validation Summary{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"   Total Files: {total_files}")
    print(f"   {Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"   {Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"   {Colors.YELLOW}Missing Frontmatter: {missing_frontmatter}{Colors.RESET}")

    if failed > 0 or missing_frontmatter > 0:
        print(f"\n{Colors.RED}Validation failed{Colors.RESET}")
        sys.exit(1)
    else:
        print(f"\n{Colors.GREEN}All files validated successfully!{Colors.RESET}")
        sys.exit(0)


if __name__ == '__main__':
    main()
