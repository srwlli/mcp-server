"""
Timestamp Utility for CodeRef Document Generation

Provides standardized timestamp functions for YAML front matter in documentation,
resource sheets, and planning documents. Ensures compliance with Papertrail RSMS v2.0
and UDS timestamp requirements.

Schema Compliance:
- RSMS v2.0 (resource-sheet-metadata-schema.json):
  - date: YYYY-MM-DD format (required)
  - timestamp: ISO 8601 with timezone (optional)
- Plan Schema (plan.schema.json):
  - generated_at: date format (YYYY-MM-DD)
  - updated_at: date-time format (ISO 8601)

Usage:
    from utils.timestamp import get_date, get_timestamp, get_iso_timestamp

    # For YAML front matter (RSMS date field)
    date: {get_date()}

    # For YAML front matter (RSMS timestamp field)
    timestamp: {get_timestamp()}

    # For plan.json updated_at fields
    updated_at: {get_iso_timestamp()}
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def get_date() -> str:
    """
    Get current date in YYYY-MM-DD format for YAML front matter.

    Compliant with:
    - RSMS v2.0 'date' field (required)
    - Plan schema 'generated_at' field (format: date)

    Returns:
        str: Date string in YYYY-MM-DD format (e.g., "2026-01-08")

    Example:
        >>> date = get_date()
        >>> print(date)
        2026-01-08
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_timestamp(tz: str = "America/New_York") -> str:
    """
    Get current timestamp in ISO 8601 format with timezone for YAML front matter.

    Compliant with:
    - RSMS v2.0 'timestamp' field (optional)
    - Pattern: ^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}([+-]\\d{2}:\\d{2}|Z)$

    Args:
        tz: Timezone name (default: "America/New_York" for EST/EDT -05:00/-04:00)
            Use "UTC" for Zulu time (Z suffix)

    Returns:
        str: ISO 8601 timestamp with timezone offset (e.g., "2026-01-08T14:30:45-05:00")

    Examples:
        >>> timestamp = get_timestamp()  # EST/EDT
        >>> print(timestamp)
        2026-01-08T14:30:45-05:00

        >>> timestamp_utc = get_timestamp(tz="UTC")
        >>> print(timestamp_utc)
        2026-01-08T19:30:45Z
    """
    if tz == "UTC":
        dt = datetime.now(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        dt = datetime.now(ZoneInfo(tz))
        return dt.isoformat(timespec='seconds')


def get_iso_timestamp() -> str:
    """
    Get current UTC timestamp in ISO 8601 format for plan.json fields.

    Compliant with:
    - Plan schema 'updated_at' field (format: date-time)
    - JSON standard ISO 8601 format with Z suffix

    Returns:
        str: ISO 8601 timestamp in UTC with Z suffix (e.g., "2026-01-08T19:30:45Z")

    Example:
        >>> iso_ts = get_iso_timestamp()
        >>> print(iso_ts)
        2026-01-08T19:30:45Z
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_date(dt: datetime) -> str:
    """
    Format a datetime object to YYYY-MM-DD string.

    Args:
        dt: datetime object to format

    Returns:
        str: Date string in YYYY-MM-DD format

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2026, 1, 8, 14, 30, 45)
        >>> formatted = format_date(dt)
        >>> print(formatted)
        2026-01-08
    """
    return dt.strftime("%Y-%m-%d")


def format_timestamp(dt: datetime, tz: str = "America/New_York") -> str:
    """
    Format a datetime object to ISO 8601 string with timezone.

    Args:
        dt: datetime object to format
        tz: Timezone name (default: "America/New_York")

    Returns:
        str: ISO 8601 timestamp with timezone offset

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2026, 1, 8, 14, 30, 45)
        >>> formatted = format_timestamp(dt)
        >>> print(formatted)
        2026-01-08T14:30:45-05:00
    """
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo(tz))
    return dt.isoformat(timespec='seconds')


def validate_date_format(date_str: str) -> bool:
    """
    Validate if a string matches YYYY-MM-DD format.

    Args:
        date_str: Date string to validate

    Returns:
        bool: True if valid YYYY-MM-DD format, False otherwise

    Examples:
        >>> validate_date_format("2026-01-08")
        True
        >>> validate_date_format("2026-1-8")
        False
        >>> validate_date_format("01/08/2026")
        False
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_iso_timestamp(timestamp_str: str) -> bool:
    """
    Validate if a string matches ISO 8601 timestamp format.

    Validates against RSMS v2.0 timestamp pattern:
    ^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}([+-]\\d{2}:\\d{2}|Z)$

    Args:
        timestamp_str: Timestamp string to validate

    Returns:
        bool: True if valid ISO 8601 format, False otherwise

    Examples:
        >>> validate_iso_timestamp("2026-01-08T14:30:45-05:00")
        True
        >>> validate_iso_timestamp("2026-01-08T19:30:45Z")
        True
        >>> validate_iso_timestamp("2026-01-08 14:30:45")
        False
    """
    import re
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2}|Z)$'
    return bool(re.match(pattern, timestamp_str))


# Convenience exports for common use cases
def get_rsms_timestamps() -> dict:
    """
    Get both date and timestamp for RSMS v2.0 YAML front matter.

    Returns:
        dict: Dictionary with 'date' and 'timestamp' keys

    Example:
        >>> timestamps = get_rsms_timestamps()
        >>> print(timestamps)
        {'date': '2026-01-08', 'timestamp': '2026-01-08T14:30:45-05:00'}

        # In YAML template:
        # ---
        # date: {{ timestamps['date'] }}
        # timestamp: {{ timestamps['timestamp'] }}
        # ---
    """
    return {
        'date': get_date(),
        'timestamp': get_timestamp()
    }


def get_plan_timestamps() -> dict:
    """
    Get timestamps for plan.json META_DOCUMENTATION section.

    Returns:
        dict: Dictionary with 'generated_at' key

    Example:
        >>> plan_ts = get_plan_timestamps()
        >>> print(plan_ts)
        {'generated_at': '2026-01-08'}

        # In plan.json:
        # "META_DOCUMENTATION": {
        #   "generated_at": "2026-01-08"
        # }
    """
    return {
        'generated_at': get_date()
    }


if __name__ == "__main__":
    # Demo output
    print("=== Timestamp Utility Demo ===\n")

    print("RSMS v2.0 YAML Front Matter:")
    rsms = get_rsms_timestamps()
    print(f"  date: {rsms['date']}")
    print(f"  timestamp: {rsms['timestamp']}")

    print("\nPlan Schema Timestamps:")
    plan = get_plan_timestamps()
    print(f"  generated_at: {plan['generated_at']}")
    print(f"  updated_at: {get_iso_timestamp()}")

    print("\nValidation Examples:")
    print(f"  Valid date '2026-01-08': {validate_date_format('2026-01-08')}")
    print(f"  Invalid date '2026-1-8': {validate_date_format('2026-1-8')}")
    print(f"  Valid ISO timestamp: {validate_iso_timestamp(get_timestamp())}")
    print(f"  Valid UTC timestamp: {validate_iso_timestamp(get_iso_timestamp())}")
