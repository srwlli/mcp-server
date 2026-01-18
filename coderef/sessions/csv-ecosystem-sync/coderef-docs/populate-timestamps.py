#!/usr/bin/env python3
"""
Step 10: Populate Timestamps from Git Log
WO-CSV-ECOSYSTEM-SYNC-001

Auto-fills Created and LastUpdated fields for 174+ empty timestamp entries
using git log data.
"""

import csv
import subprocess
from pathlib import Path
from datetime import datetime
import os

# CSV paths
CSV_PATH = Path(r"C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\resources\coderef\tools-and-commands.csv")

def run_git_command(cmd, cwd=None):
    """Run git command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        return None

def get_file_timestamps(file_path):
    """Get Created and LastUpdated timestamps from git log or file system"""
    if not Path(file_path).exists():
        return None, None

    file_path_obj = Path(file_path)

    # Try to find git root
    repo_root = None
    current = file_path_obj.parent
    while current != current.parent:
        if (current / ".git").exists():
            repo_root = current
            break
        current = current.parent

    # Try git timestamps first
    if repo_root:
        try:
            rel_path = file_path_obj.relative_to(repo_root)

            # Get first commit date (Created)
            created_cmd = f'git log --follow --format=%aI --diff-filter=A --reverse -- "{rel_path}" | head -1'
            created = run_git_command(created_cmd, cwd=str(repo_root))

            # Get last commit date (LastUpdated)
            updated_cmd = f'git log --follow --format=%aI -1 -- "{rel_path}"'
            updated = run_git_command(updated_cmd, cwd=str(repo_root))

            # Clean up timestamps (keep just date portion for CSV)
            if created:
                created = created[:10] if 'T' in created else created
            if updated:
                updated = updated[:10] if 'T' in updated else updated

            if created or updated:
                return created, updated
        except ValueError:
            pass  # File not in repo

    # Fallback to file system timestamps if no git data
    try:
        stat = os.stat(file_path)
        created_ts = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d')
        updated_ts = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
        return created_ts, updated_ts
    except Exception:
        return None, None

def populate_timestamps():
    """Read CSV, populate timestamps, write back"""
    # Read CSV
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"[DATA] Total resources in CSV: {len(rows)}")

    # Count empty timestamps
    empty_created = sum(1 for row in rows if not row['Created'])
    empty_updated = sum(1 for row in rows if not row['LastUpdated'])
    print(f"[DATA] Empty Created: {empty_created}, Empty LastUpdated: {empty_updated}")

    # Process each row
    updated_count = 0
    skipped_count = 0

    for i, row in enumerate(rows):
        if not row['Created'] or not row['LastUpdated']:
            file_path = row['Path']

            if not file_path or file_path == 'N/A':
                skipped_count += 1
                continue

            # Only print every 20th entry to reduce output
            if (i+1) % 20 == 0 or (i+1) <= 10:
                print(f"[{i+1}/{len(rows)}] Processing: {row['Name'][:40]}")

            created, updated = get_file_timestamps(file_path)

            if created or updated:
                if not row['Created'] and created:
                    row['Created'] = created
                if not row['LastUpdated'] and updated:
                    row['LastUpdated'] = updated
                updated_count += 1
            else:
                skipped_count += 1

    # Write CSV
    fieldnames = ['Type', 'Server', 'Category', 'Name', 'Description', 'Status', 'Path', 'Created', 'LastUpdated']
    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[OK] Timestamp population complete!")
    print(f"[DATA] Updated: {updated_count} resources")
    print(f"[DATA] Skipped: {skipped_count} resources (no git history or invalid path)")

    # Final count
    final_empty_created = sum(1 for row in rows if not row['Created'])
    final_empty_updated = sum(1 for row in rows if not row['LastUpdated'])
    print(f"[DATA] Remaining empty Created: {final_empty_created}, LastUpdated: {final_empty_updated}")

if __name__ == '__main__':
    populate_timestamps()
