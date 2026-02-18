"""Interactive prompts for manual classification via MCP Inspector or CLI."""
import json
from typing import Optional, Tuple


def prompt_for_classification(
    filename: str, file_type: str, content_preview: str
) -> Optional[Tuple[str, float, Optional[str], Optional[str]]]:
    """Interactively prompt user for file classification.

    Returns (category, confidence, subcategory, suggested_name) or None if user skips.
    """
    print(f"\n{'='*70}")
    print(f"Classify file: {filename}")
    print(f"Extension: {file_type}")
    print(f"Preview: {content_preview[:200]}")
    print(f"{'='*70}")

    # Ask for category
    print("\nEnter category (e.g., Code, Data, Documents, Configuration, etc.)")
    print("or press Enter to skip: ", end="", flush=True)
    category = input().strip()
    if not category:
        return None

    # Ask for confidence
    print("Enter confidence (0.0-1.0) [default 0.8]: ", end="", flush=True)
    conf_input = input().strip()
    try:
        confidence = float(conf_input) if conf_input else 0.8
    except ValueError:
        confidence = 0.8

    # Ask for subcategory (optional)
    print("Enter subcategory (optional, e.g., Python, Flask): ", end="", flush=True)
    subcategory = input().strip() or None

    # Ask for suggested filename (optional)
    print("Enter suggested filename (optional): ", end="", flush=True)
    suggested_name = input().strip() or None

    return category, confidence, subcategory, suggested_name


def prompt_for_filename(original_name: str) -> Optional[str]:
    """Interactively prompt user for a new filename.

    Returns suggested filename or None if user declines.
    """
    print(f"\nCurrent filename: {original_name}")
    print("Enter new filename (or press Enter to keep current): ", end="", flush=True)
    new_name = input().strip()
    return new_name if new_name else None


def prompt_for_subcategory(category: str) -> Optional[str]:
    """Interactively prompt user for a subcategory.

    Returns subcategory or None if user declines.
    """
    print(f"\nFor category '{category}':")
    print("Enter subcategory (e.g., Python, SQL, Spring) or press Enter to skip: ", end="", flush=True)
    subcategory = input().strip()
    return subcategory if subcategory else None
