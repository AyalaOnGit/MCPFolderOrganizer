"""Validation utilities."""
from typing import Any, Optional


def is_valid_folder_name(name: str) -> bool:
    """Check if name is valid for a folder."""
    if not name or len(name) == 0:
        return False
    
    invalid_chars = r'<>:"/\|?*'
    return not any(char in name for char in invalid_chars)


def sanitize_folder_name(name: str) -> str:
    """Sanitize name to be valid for folder creation."""
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    name = name.strip('. ')
    
    # Limit length
    if len(name) > 200:
        name = name[:200]
    
    return name or "folder"


def truncate_string(text: str, max_length: int = 200) -> str:
    """Truncate string to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
