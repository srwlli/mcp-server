#!/usr/bin/env python3
"""
Audit Slash Commands - Find and Remove Duplicates

Scans all MCP servers and projects for duplicate slash commands that already
exist in the global ~/.claude/commands directory. Helps maintain single source
of truth for slash commands.

Usage:
    python audit-slash-commands.py              # Audit only (dry run)
    python audit-slash-commands.py --clean      # Remove duplicates
    python audit-slash-commands.py --clean --backup  # Remove with backup
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


# Paths to scan
GLOBAL_COMMANDS_DIR = Path.home() / ".claude" / "commands"
SCAN_ROOTS = [
    Path.home() / ".mcp-servers",
    Path.home() / "Desktop" / "assistant",
    Path.home() / "Desktop" / "coderef-dashboard",
]


def find_command_directories() -> List[Path]:
    """Find all .claude/commands directories in scan roots."""
    command_dirs = []

    for root in SCAN_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob(".claude/commands"):
            if path.is_dir():
                command_dirs.append(path)

    return command_dirs


def get_commands_in_dir(dir_path: Path) -> Dict[str, Path]:
    """Get all command files in a directory.

    Returns:
        Dict mapping command name to full file path
    """
    commands = {}

    if not dir_path.exists():
        return commands

    for file_path in dir_path.glob("*.md"):
        command_name = file_path.stem
        commands[command_name] = file_path

    return commands


def find_duplicates() -> Tuple[Dict[str, Path], List[Tuple[str, Path, Path]]]:
    """Find duplicate commands across all locations.

    Returns:
        (global_commands, duplicates)
        where duplicates = [(command_name, global_path, duplicate_path), ...]
    """
    # Get global commands (source of truth)
    global_commands = get_commands_in_dir(GLOBAL_COMMANDS_DIR)

    # Find duplicates in project directories
    duplicates = []
    command_dirs = find_command_directories()

    for cmd_dir in command_dirs:
        local_commands = get_commands_in_dir(cmd_dir)

        for cmd_name, local_path in local_commands.items():
            if cmd_name in global_commands:
                global_path = global_commands[cmd_name]
                duplicates.append((cmd_name, global_path, local_path))

    return global_commands, duplicates


def create_backup(file_path: Path, backup_dir: Path) -> Path:
    """Create backup of file before deletion.

    Args:
        file_path: File to backup
        backup_dir: Directory to store backup

    Returns:
        Path to backup file
    """
    # Create timestamped backup directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = backup_dir / f"command-cleanup-{timestamp}"

    # Preserve directory structure
    relative_path = file_path.relative_to(Path.home())
    backup_path = backup_root / relative_path

    # Create parent directories
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy file
    shutil.copy2(file_path, backup_path)

    return backup_path


def print_summary(global_commands: Dict[str, Path], duplicates: List[Tuple]):
    """Print audit summary."""
    print("\n" + "="*80)
    print("SLASH COMMAND AUDIT SUMMARY")
    print("="*80)

    print(f"\nGlobal Commands: {len(global_commands)}")
    print(f"Location: {GLOBAL_COMMANDS_DIR}")

    print(f"\nDuplicates Found: {len(duplicates)}")

    if duplicates:
        print("\nDuplicate Commands:")
        print("-" * 80)

        # Group by location
        by_location = {}
        for cmd_name, global_path, dup_path in duplicates:
            location = dup_path.parent
            if location not in by_location:
                by_location[location] = []
            by_location[location].append(cmd_name)

        for location, commands in sorted(by_location.items()):
            print(f"\n{location}:")
            for cmd in sorted(commands):
                print(f"  - /{cmd}")
    else:
        print("\n[OK] No duplicates found - all commands are global only!")

    print("\n" + "="*80)


def clean_duplicates(duplicates: List[Tuple], backup: bool = False) -> int:
    """Remove duplicate command files.

    Args:
        duplicates: List of (cmd_name, global_path, dup_path) tuples
        backup: Whether to backup files before deletion

    Returns:
        Number of files removed
    """
    if not duplicates:
        print("\n[OK] No duplicates to clean")
        return 0

    backup_dir = None
    if backup:
        backup_dir = Path.home() / "Desktop" / "command-backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

    removed_count = 0

    print("\n" + "="*80)
    print("CLEANING DUPLICATES")
    print("="*80 + "\n")

    for cmd_name, global_path, dup_path in duplicates:
        try:
            # Create backup if requested
            if backup:
                backup_path = create_backup(dup_path, backup_dir)
                print(f"[BACKUP] /{cmd_name}")
                print(f"  From: {dup_path}")
                print(f"  To:   {backup_path}")

            # Remove duplicate
            dup_path.unlink()
            removed_count += 1

            print(f"[REMOVED] /{cmd_name}")
            print(f"  Location: {dup_path}")
            print(f"  Global:   {global_path}")
            print()

        except Exception as e:
            print(f"[ERROR] Failed to remove /{cmd_name}: {e}")
            print(f"  Path: {dup_path}\n")

    print("="*80)
    print(f"[SUCCESS] Removed {removed_count} duplicate command(s)")

    if backup and backup_dir:
        print(f"[BACKUP] Backups saved to: {backup_dir}")

    print("="*80 + "\n")

    return removed_count


def generate_report(global_commands: Dict[str, Path], duplicates: List[Tuple]) -> str:
    """Generate detailed JSON report."""

    # Group duplicates by location
    by_location = {}
    for cmd_name, global_path, dup_path in duplicates:
        location_str = str(dup_path.parent)
        if location_str not in by_location:
            by_location[location_str] = []
        by_location[location_str].append({
            "command": cmd_name,
            "global_path": str(global_path),
            "duplicate_path": str(dup_path)
        })

    report = {
        "audit_date": datetime.now().isoformat(),
        "global_commands_directory": str(GLOBAL_COMMANDS_DIR),
        "global_commands_count": len(global_commands),
        "global_commands": sorted(global_commands.keys()),
        "duplicates_found": len(duplicates),
        "duplicates_by_location": by_location,
        "scan_roots": [str(p) for p in SCAN_ROOTS]
    }

    return json.dumps(report, indent=2)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Audit and clean duplicate slash commands"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove duplicate commands (default: audit only)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Backup files before removal (requires --clean)"
    )
    parser.add_argument(
        "--report",
        type=str,
        help="Save JSON report to file"
    )

    args = parser.parse_args()

    # Validate
    if args.backup and not args.clean:
        print("[ERROR] --backup requires --clean")
        sys.exit(1)

    # Run audit
    print("\n" + "="*80)
    print("SLASH COMMAND AUDIT")
    print("="*80)
    print(f"\nScanning for duplicate commands...")
    print(f"Global commands: {GLOBAL_COMMANDS_DIR}")
    print(f"Scan roots:")
    for root in SCAN_ROOTS:
        print(f"  - {root}")

    # Find duplicates
    global_commands, duplicates = find_duplicates()

    # Print summary
    print_summary(global_commands, duplicates)

    # Save report if requested
    if args.report:
        report = generate_report(global_commands, duplicates)
        report_path = Path(args.report)
        report_path.write_text(report, encoding='utf-8')
        print(f"\n[REPORT] Saved to: {report_path}")

    # Clean if requested
    if args.clean:
        if not duplicates:
            print("\n✅ No duplicates to clean")
            return

        # Confirm
        print("\n[WARNING] This will delete duplicate command files!")
        if args.backup:
            print("[BACKUP ENABLED] Backups will be created before deletion")

        confirm = input("\nProceed with cleanup? (yes/no): ").strip().lower()

        if confirm == "yes":
            removed = clean_duplicates(duplicates, args.backup)

            if removed > 0:
                print("\n[SUCCESS] Cleanup complete!")
                print("\nRecommendation:")
                print("  1. Restart Claude Code to refresh command list")
                print("  2. Verify commands work as expected")
                print("  3. Delete backups if everything works")
        else:
            print("\n[CANCELLED] Cleanup cancelled")
    else:
        print("\n[TIP] Run with --clean to remove duplicates")
        print("[TIP] Run with --clean --backup to keep backups")

    print()


if __name__ == "__main__":
    main()
