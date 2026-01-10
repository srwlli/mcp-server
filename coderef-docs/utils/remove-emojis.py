#!/usr/bin/env python3
"""
remove-emojis.py - Remove emoji characters from files

Removes emoji characters from text files while preserving all other content.
Useful for cleaning documentation, code comments, or standardizing text output.

Usage:
    python scripts/remove-emojis.py [file_or_directory] [options]
    python scripts/remove-emojis.py C:/Users/willh/Desktop/projects/my-file.md
    python scripts/remove-emojis.py C:/Users/willh/Desktop/projects/my-project --recursive
"""

import sys
import re
from pathlib import Path


# Emoji pattern - matches most emoji characters
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed characters
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
    "]+",
    flags=re.UNICODE
)


def remove_emojis(text: str) -> tuple[str, int]:
    """
    Remove emojis from text.

    Returns:
        (cleaned_text, emoji_count)
    """
    # Count emojis
    emojis = EMOJI_PATTERN.findall(text)
    count = len(emojis)

    # Remove emojis
    cleaned = EMOJI_PATTERN.sub('', text)

    return cleaned, count


def process_file(file_path: Path, dry_run: bool = False) -> dict:
    """
    Process a single file to remove emojis.

    Returns:
        {
            'path': Path,
            'emoji_count': int,
            'success': bool,
            'error': str or None
        }
    """
    result = {
        'path': file_path,
        'emoji_count': 0,
        'success': False,
        'error': None
    }

    try:
        # Read file
        content = file_path.read_text(encoding='utf-8')

        # Remove emojis
        cleaned, count = remove_emojis(content)
        result['emoji_count'] = count

        # Write back if not dry run and emojis were found
        if not dry_run and count > 0:
            file_path.write_text(cleaned, encoding='utf-8')
            result['success'] = True
        elif count == 0:
            result['success'] = True  # No changes needed
        else:
            result['success'] = True  # Dry run

    except Exception as e:
        result['error'] = str(e)

    return result


def process_directory(dir_path: Path, recursive: bool = False, dry_run: bool = False,
                     pattern: str = "*.md") -> list:
    """
    Process all files in a directory.

    Args:
        dir_path: Directory to process
        recursive: Process subdirectories
        dry_run: Don't write changes
        pattern: File pattern to match (default: *.md)

    Returns:
        List of result dictionaries
    """
    results = []

    if recursive:
        files = dir_path.rglob(pattern)
    else:
        files = dir_path.glob(pattern)

    for file_path in files:
        if file_path.is_file():
            result = process_file(file_path, dry_run)
            results.append(result)

    return results


def print_summary(results: list):
    """Print summary of processing results."""
    total_files = len(results)
    files_with_emojis = sum(1 for r in results if r['emoji_count'] > 0)
    total_emojis = sum(r['emoji_count'] for r in results)
    errors = [r for r in results if r['error']]

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Files processed: {total_files}")
    print(f"Files with emojis: {files_with_emojis}")
    print(f"Total emojis removed: {total_emojis}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for r in errors:
            print(f"  - {r['path']}: {r['error']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Remove emoji characters from files"
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="File or directory path to process"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Process directories recursively"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Show what would be changed without writing"
    )
    parser.add_argument(
        "--pattern", "-p",
        default="*.md",
        help="File pattern to match (default: *.md)"
    )

    args = parser.parse_args()

    # Get path
    if args.path:
        path = Path(args.path).resolve()
    else:
        path_input = input("Enter file or directory path: ").strip()
        if not path_input:
            print("No path provided")
            sys.exit(1)
        path = Path(path_input).resolve()

    if not path.exists():
        print(f"[ERROR] Path does not exist: {path}")
        sys.exit(1)

    # Process
    print(f"\n[*] Processing: {path}")
    if args.dry_run:
        print("[*] DRY RUN MODE - No files will be modified")
    print()

    if path.is_file():
        result = process_file(path, args.dry_run)
        results = [result]

        if result['success']:
            if result['emoji_count'] > 0:
                status = "[DRY RUN]" if args.dry_run else "[OK]"
                print(f"{status} {path.name}: {result['emoji_count']} emojis removed")
            else:
                print(f"[SKIP] {path.name}: No emojis found")
        else:
            print(f"[ERROR] {path.name}: {result['error']}")
    else:
        results = process_directory(path, args.recursive, args.dry_run, args.pattern)

        for result in results:
            rel_path = result['path'].relative_to(path)
            if result['success']:
                if result['emoji_count'] > 0:
                    status = "[DRY RUN]" if args.dry_run else "[OK]"
                    print(f"{status} {rel_path}: {result['emoji_count']} emojis")
                else:
                    print(f"[SKIP] {rel_path}: No emojis")
            else:
                print(f"[ERROR] {rel_path}: {result['error']}")

    print_summary(results)
