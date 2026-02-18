"""Path utilities and validation."""
from pathlib import Path
from typing import Optional
from .errors import InvalidPathError


def validate_path(path: str) -> Path:
    """
    Validate and convert string path to Path object.
    
    Args:
        path: String representation of path
        
    Returns:
        Path object if valid
        
    Raises:
        InvalidPathError: If path is invalid or not accessible
    """
    try:
        p = Path(path)
        if not p.exists():
            raise InvalidPathError(f"Path does not exist: {path}")
        if not p.is_dir():
            raise InvalidPathError(f"Path is not a directory: {path}")
        return p
    except (OSError, ValueError) as e:
        raise InvalidPathError(f"Invalid path '{path}': {str(e)}")


def get_relative_path(file_path: Path, base_path: Path) -> str:
    """Get relative path from base directory."""
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        return str(file_path)


def is_text_file(file_path: Path, max_size_mb: int = 10) -> bool:
    """Check if file is readable text."""
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.ts', '.json', '.yaml', '.yml',
        '.xml', '.html', '.css', '.sql', '.java', '.cpp', '.c', '.h',
        '.sh', '.bash', '.log', '.csv', '.ini', '.conf', '.config'
    }
    
    if file_path.suffix.lower() not in text_extensions:
        return False
    
    # Check file size
    try:
        if file_path.stat().st_size > max_size_mb * 1024 * 1024:
            return False
    except (OSError, ValueError):
        return False
    
    return True
