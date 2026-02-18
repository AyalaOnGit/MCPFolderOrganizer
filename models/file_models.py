from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class FileMetadata:
    """Metadata about a file."""
    original_name: str
    suggested_name: str
    file_path: Path
    file_size: int
    file_type: str
    suggested_category: str
    confidence_score: float = 0.0
    content_preview: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class FolderOrganization:
    """Represents organized files by category."""
    category: str
    files: List[FileMetadata] = field(default_factory=list)
    suggested_folder_name: str = ""


@dataclass
class OrganizationResult:
    """Result of file organization operation."""
    source_folder: Path
    total_files: int
    organized_folders: List[FolderOrganization] = field(default_factory=list)
    unorganized_files: List[FileMetadata] = field(default_factory=list)
    suggested_structure: dict = field(default_factory=dict)
