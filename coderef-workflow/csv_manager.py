"""
CSV Manager - Automated CSV Maintenance Utilities

Provides functions for coderef-workflow tools to automatically update
tools-and-commands.csv when creating/modifying resources.

Part of WO-CSV-ECOSYSTEM-SYNC-001 Phase 3 Task 2.
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import threading

# Thread lock for CSV file access
_csv_lock = threading.Lock()

# CSV path - global single source of truth
CSV_PATH = Path(r"C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\resources\coderef\tools-and-commands.csv")

# CSV field names
CSV_FIELDS = ['Type', 'Server', 'Category', 'Name', 'Description', 'Status', 'Path', 'Created', 'LastUpdated']


def get_csv_path() -> Path:
    """Get CSV file path, verify it exists."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found at: {CSV_PATH}")
    return CSV_PATH


def read_csv() -> List[Dict[str, str]]:
    """Read CSV file and return list of dictionaries."""
    csv_path = get_csv_path()
    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv(entries: List[Dict[str, str]]) -> None:
    """Write entries to CSV file."""
    csv_path = get_csv_path()

    # Backup existing CSV before writing
    backup_path = csv_path.parent / f"{csv_path.stem}.backup{csv_path.suffix}"
    if csv_path.exists():
        import shutil
        shutil.copy2(csv_path, backup_path)

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(entries)


def add_csv_entry(
    type: str,
    server: str,
    category: str,
    name: str,
    description: str,
    status: str = 'active',
    path: str = '',
    created: Optional[str] = None,
    last_updated: Optional[str] = None
) -> Dict[str, str]:
    """
    Add new entry to CSV.

    Args:
        type: Resource type (Tool, Command, Script, Output, etc.)
        server: Server name (coderef-workflow, coderef-docs, etc.)
        category: Category (Documentation, Workflow, Planning, etc.)
        name: Resource name
        description: Brief description
        status: Resource status (active, archived, deprecated)
        path: File path (absolute or relative)
        created: ISO 8601 timestamp (auto-generated if None)
        last_updated: ISO 8601 timestamp (auto-generated if None)

    Returns:
        Dict with the entry that was added

    Raises:
        ValueError: If required fields missing or invalid
        FileNotFoundError: If CSV not found
    """
    # Validate required fields
    if not all([type, server, category, name, description]):
        raise ValueError("Missing required fields: type, server, category, name, description")

    # Auto-generate timestamps if not provided
    now = datetime.now().isoformat()
    if created is None:
        created = now
    if last_updated is None:
        last_updated = now

    # Create entry
    entry = {
        'Type': type,
        'Server': server,
        'Category': category,
        'Name': name,
        'Description': description,
        'Status': status,
        'Path': path,
        'Created': created,
        'LastUpdated': last_updated
    }

    # Thread-safe CSV append
    with _csv_lock:
        # Check if entry already exists (prevent duplicates)
        if check_csv_exists(name, server):
            raise ValueError(f"Entry already exists: {name} (Server: {server})")

        # Read existing entries
        entries = read_csv()

        # Append new entry
        entries.append(entry)

        # Write back to CSV
        write_csv(entries)

    return entry


def update_csv_status(resource_name: str, new_status: str, server: Optional[str] = None) -> int:
    """
    Update status for existing resource(s).

    Args:
        resource_name: Name of resource to update
        new_status: New status value (active, archived, deprecated)
        server: Optional server filter (if None, updates all matches)

    Returns:
        Number of entries updated

    Raises:
        FileNotFoundError: If CSV not found
        ValueError: If no matching entries found
    """
    # Thread-safe CSV update
    with _csv_lock:
        entries = read_csv()

        updated_count = 0
        now = datetime.now().isoformat()

        for entry in entries:
            # Match by name and optionally server
            if entry['Name'] == resource_name:
                if server is None or entry['Server'] == server:
                    entry['Status'] = new_status
                    entry['LastUpdated'] = now
                    updated_count += 1

        if updated_count == 0:
            raise ValueError(f"No matching entries found for: {resource_name}")

        # Write updated entries back
        write_csv(entries)

    return updated_count


def update_csv_entry(
    resource_name: str,
    server: str,
    updates: Dict[str, str]
) -> Dict[str, str]:
    """
    Update multiple fields for a specific resource.

    Args:
        resource_name: Name of resource to update
        server: Server name (for unique identification)
        updates: Dictionary of fields to update (e.g., {'Description': 'new desc', 'Category': 'new cat'})

    Returns:
        Updated entry

    Raises:
        FileNotFoundError: If CSV not found
        ValueError: If resource not found
    """
    # Thread-safe CSV update
    with _csv_lock:
        entries = read_csv()

        updated_entry = None
        now = datetime.now().isoformat()

        for entry in entries:
            if entry['Name'] == resource_name and entry['Server'] == server:
                # Update specified fields
                for field, value in updates.items():
                    if field in CSV_FIELDS:
                        entry[field] = value

                # Always update LastUpdated
                entry['LastUpdated'] = now
                updated_entry = entry
                break

        if updated_entry is None:
            raise ValueError(f"Resource not found: {resource_name} (Server: {server})")

        # Write updated entries back
        write_csv(entries)

    return updated_entry


def check_csv_exists(resource_name: str, server: Optional[str] = None) -> bool:
    """
    Check if resource already exists in CSV.

    Args:
        resource_name: Name of resource to check
        server: Optional server filter (if None, checks all servers)

    Returns:
        True if resource exists, False otherwise
    """
    try:
        entries = read_csv()

        for entry in entries:
            if entry['Name'] == resource_name:
                if server is None or entry['Server'] == server:
                    return True

        return False
    except FileNotFoundError:
        return False


def find_csv_entry(resource_name: str, server: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    Find and return a specific CSV entry.

    Args:
        resource_name: Name of resource to find
        server: Optional server filter

    Returns:
        Entry dictionary if found, None otherwise
    """
    try:
        entries = read_csv()

        for entry in entries:
            if entry['Name'] == resource_name:
                if server is None or entry['Server'] == server:
                    return entry

        return None
    except FileNotFoundError:
        return None


def bulk_add_csv_entries(entries_list: List[Dict[str, str]]) -> int:
    """
    Add multiple entries to CSV in a single operation.

    Args:
        entries_list: List of entry dictionaries (each with required fields)

    Returns:
        Number of entries added

    Raises:
        FileNotFoundError: If CSV not found
        ValueError: If any entry is invalid or duplicate
    """
    # Thread-safe bulk add
    with _csv_lock:
        existing_entries = read_csv()

        # Validate all new entries first
        now = datetime.now().isoformat()
        validated_entries = []

        for new_entry in entries_list:
            # Validate required fields
            required = ['Type', 'Server', 'Category', 'Name', 'Description']
            if not all(field in new_entry for field in required):
                raise ValueError(f"Missing required fields in entry: {new_entry.get('Name', 'unknown')}")

            # Check for duplicates
            name = new_entry['Name']
            server = new_entry['Server']
            if any(e['Name'] == name and e['Server'] == server for e in existing_entries):
                raise ValueError(f"Duplicate entry: {name} (Server: {server})")

            # Fill in defaults
            entry = {
                'Type': new_entry['Type'],
                'Server': new_entry['Server'],
                'Category': new_entry['Category'],
                'Name': new_entry['Name'],
                'Description': new_entry['Description'],
                'Status': new_entry.get('Status', 'active'),
                'Path': new_entry.get('Path', ''),
                'Created': new_entry.get('Created', now),
                'LastUpdated': new_entry.get('LastUpdated', now)
            }

            validated_entries.append(entry)

        # Add all validated entries
        existing_entries.extend(validated_entries)

        # Write back to CSV
        write_csv(existing_entries)

    return len(validated_entries)


def get_csv_stats() -> Dict[str, int]:
    """
    Get statistics about CSV contents.

    Returns:
        Dictionary with counts by type, server, status
    """
    entries = read_csv()

    stats = {
        'total': len(entries),
        'by_type': {},
        'by_server': {},
        'by_status': {},
        'by_category': {}
    }

    for entry in entries:
        # Count by type
        type_val = entry.get('Type', 'Unknown')
        stats['by_type'][type_val] = stats['by_type'].get(type_val, 0) + 1

        # Count by server
        server_val = entry.get('Server', 'Unknown')
        stats['by_server'][server_val] = stats['by_server'].get(server_val, 0) + 1

        # Count by status
        status_val = entry.get('Status', 'Unknown')
        stats['by_status'][status_val] = stats['by_status'].get(status_val, 0) + 1

        # Count by category
        category_val = entry.get('Category', 'Unknown')
        stats['by_category'][category_val] = stats['by_category'].get(category_val, 0) + 1

    return stats
