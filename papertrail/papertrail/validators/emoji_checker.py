"""
Emoji Detection for UDS Validators

Detects emoji characters in documents and returns validation errors.
Enforces strict no-emoji policy for all generated documentation,
with exception for coderef/user/ documents.

Policy:
- NO emojis in foundation docs, workorder docs, system docs, standards docs
- Emojis ALLOWED in coderef/user/ documents only
- Uses same regex pattern as scripts/remove-emojis.py
"""

import re
from pathlib import Path
from typing import Optional


# Emoji pattern - matches most emoji characters
# Same pattern as scripts/remove-emojis.py for consistency
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


def is_user_document(file_path: Optional[Path]) -> bool:
    """
    Check if document is in coderef/user/ directory (emoji exception).
    
    Args:
        file_path: Path to document being validated
        
    Returns:
        bool: True if in coderef/user/, False otherwise
    """
    if file_path is None:
        return False
        
    path_str = str(file_path).replace("\\", "/")
    return "/coderef/user/" in path_str.lower()


def detect_emojis(content: str) -> list[dict]:
    """
    Detect all emojis in content and return their locations.
    
    Args:
        content: Document content to check
        
    Returns:
        List of dicts with {emoji, line_number, line_text}
    """
    emojis_found = []
    lines = content.split("\n")
    
    for line_num, line_text in enumerate(lines, start=1):
        matches = EMOJI_PATTERN.finditer(line_text)
        for match in matches:
            emojis_found.append({
                "emoji": match.group(),
                "line_number": line_num,
                "line_text": line_text.strip()
            })
    
    return emojis_found


def check_emojis(content: str, file_path: Optional[Path] = None) -> tuple[int, list[str]]:
    """
    Check content for emojis and return count + warning messages.
    
    Enforces no-emoji policy unless document is in coderef/user/.
    
    Args:
        content: Document content to validate
        file_path: Optional path to document (for user directory exception)
        
    Returns:
        (emoji_count, warnings)
    """
    # User documents are exempt from emoji policy
    if is_user_document(file_path):
        return (0, [])
    
    emojis_found = detect_emojis(content)
    emoji_count = len(emojis_found)
    
    if emoji_count == 0:
        return (0, [])
    
    # Generate warnings
    warnings = []
    
    # Summary warning
    unique_emojis = set(e["emoji"] for e in emojis_found)
    warnings.append(
        f"Document contains {emoji_count} emoji(s): {', '.join(unique_emojis)}. "
        f"Remove emojis for UDS compliance (use text markers like [PASS], [FAIL], [INFO])"
    )
    
    # Detailed line-by-line warnings (limit to first 5)
    for emoji_info in emojis_found[:5]:
        warnings.append(
            f"  Line {emoji_info['line_number']}: '{emoji_info['emoji']}' in \"{emoji_info['line_text'][:60]}...\""
        )
    
    if emoji_count > 5:
        warnings.append(f"  ... and {emoji_count - 5} more emoji(s)")
    
    return (emoji_count, warnings)
