"""File analysis service for organizing files by topic."""
import os
from pathlib import Path
from typing import List, Dict, Optional
import json

from models import FileMetadata, FolderOrganization, OrganizationResult
from utils import (
    validate_path,
    is_text_file,
    sanitize_folder_name,
    AnalysisError,
    FileAccessError,
)


class FileAnalysisService:
    """Service for analyzing files and suggesting organization."""

    # Category keywords mapping
    CATEGORY_KEYWORDS = {
        "Documents": [
            "document", "doc", "pdf", "word", "text", "report", "essay",
            "article", "paper", "memo", "letter", "contract", "agreement"
        ],
        "Images": [
            "image", "photo", "picture", "img", "graphic", "design",
            "icon", "screenshot", "jpeg", "jpg", "png", "bmp", "gif"
        ],
        "Videos": [
            "video", "movie", "film", "clip", "recording", "mp4",
            "avi", "mkv", "mov", "wmv", "flv"
        ],
        "Audio": [
            "audio", "music", "sound", "song", "podcast", "mp3",
            "wav", "flac", "aac", "ogg", "wma"
        ],
        "Code": [
            "code", "script", "program", "source", "python", "java",
            "javascript", "cpp", "csharp", "ruby", "php", "go", "rust",
            "py", "js", "ts", "java", "cpp", "h", "hpp", "c"
        ],
        "Data": [
            "data", "dataset", "database", "csv", "sql", "json",
            "xml", "excel", "sheet", "table", "database", "backup"
        ],
        "Configuration": [
            "config", "settings", "setup", "configuration", "ini",
            "conf", "yaml", "yml", "env", "properties", "toml"
        ],
        "Archives": [
            "archive", "compressed", "zip", "rar", "7z", "tar",
            "gz", "bz2", "xz"
        ],
        "Backup": [
            "backup", "restore", "recovery", "old", "previous",
            "archive", "copy", "tmp", "temp", "bak"
        ],
        "README": [
            "readme", "guide", "help", "tutorial", "documentation",
            "getting started", "installation", "usage"
        ],
    }

    def __init__(self):
        """Initialize the analysis service."""
        self.analysis_cache: Dict[str, FileMetadata] = {}

    def analyze_folder(self, folder_path: str) -> OrganizationResult:
        """
        Analyze a folder and suggest file organization.

        Args:
            folder_path: Path to folder to analyze

        Returns:
            OrganizationResult with suggested organization
        """
        path = validate_path(folder_path)

        try:
            files = self._get_all_files(path)

            if not files:
                return OrganizationResult(
                    source_folder=path,
                    total_files=0,
                    organized_folders=[],
                    unorganized_files=[],
                )

            # Analyze each file
            analyzed_files = []
            for file_path in files:
                try:
                    metadata = self._analyze_file(file_path, path)
                    analyzed_files.append(metadata)
                except AnalysisError:
                    # Skip files that can't be analyzed
                    continue

            # Organize by category
            organized_folders = self._organize_by_category(analyzed_files)

            return OrganizationResult(
                source_folder=path,
                total_files=len(analyzed_files),
                organized_folders=organized_folders,
                unorganized_files=[
                    f for f in analyzed_files if f.suggested_category == "Uncategorized"
                ],
                suggested_structure=self._build_structure(organized_folders),
            )

        except Exception as e:
            raise AnalysisError(f"Failed to analyze folder: {str(e)}")

    def _get_all_files(self, folder_path: Path) -> List[Path]:
        """Get all files in folder (non-recursively by default)."""
        try:
            files = [f for f in folder_path.iterdir() if f.is_file()]
            return sorted(files, key=lambda x: x.name)
        except (OSError, PermissionError) as e:
            raise FileAccessError(f"Cannot access folder: {str(e)}")

    def _analyze_file(self, file_path: Path, base_path: Path) -> FileMetadata:
        """Analyze a single file."""
        try:
            file_name = file_path.name
            file_size = file_path.stat().st_size
            file_type = file_path.suffix.lower()

            # Read content preview for text files
            content_preview = ""
            if is_text_file(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content_preview = f.read(500)
                except Exception:
                    pass

            # Analyze and suggest category
            category, confidence = self._suggest_category(
                file_name, file_type, content_preview
            )

            # Suggest improved name
            suggested_name = self._suggest_filename(file_name, category)

            tags = self._extract_tags(file_name, content_preview)

            return FileMetadata(
                original_name=file_name,
                suggested_name=suggested_name,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                suggested_category=category,
                confidence_score=confidence,
                content_preview=content_preview[:200],
                tags=tags,
            )

        except Exception as e:
            raise AnalysisError(f"Failed to analyze file {file_path}: {str(e)}")

    def _suggest_category(
        self, filename: str, file_type: str, content: str
    ) -> tuple[str, float]:
        """Suggest category and confidence score."""
        filename_lower = filename.lower()
        content_lower = content.lower()

        scores = {}

        # Check keywords in filename and content
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            matches = sum(
                1 for kw in keywords if kw in filename_lower or kw in content_lower
            )
            if matches > 0:
                scores[category] = matches

        if scores:
            best_category = max(scores, key=scores.get)
            confidence = min(scores[best_category] / 3, 1.0)
            return best_category, confidence

        return "Uncategorized", 0.0

    def _suggest_filename(self, original_name: str, category: str) -> str:
        """Suggest an improved filename."""
        # For now, return the original if it's good, or enhance it
        name_without_ext = Path(original_name).stem
        ext = Path(original_name).suffix

        # If filename is already descriptive, keep it
        if len(name_without_ext) > 5 and "_" in name_without_ext:
            return original_name

        # Otherwise, enhance it with category prefix
        suggested = f"{category}_{name_without_ext}{ext}"
        return suggested

    def _extract_tags(self, filename: str, content: str) -> List[str]:
        """Extract relevant tags from filename and content."""
        tags = []

        # Extract from filename
        parts = Path(filename).stem.split("_")
        tags.extend([p for p in parts if len(p) > 3])

        # Extract from content (simple approach)
        if content:
            words = content.split()[:50]  # First 50 words
            tags.extend(
                [
                    w.lower().strip(".,;:")
                    for w in words
                    if len(w) > 4 and w[0].isupper()
                ][:3]
            )

        return list(set(tags))[:5]  # Unique, max 5 tags

    def _organize_by_category(
        self, files: List[FileMetadata]
    ) -> List[FolderOrganization]:
        """Organize files by category."""
        # Use (top_category, subcategory) as grouping key so we can
        # keep top-level categories like 'Code' while splitting
        # code into more specific subcategories (e.g. Python, SQL, Java).
        organization: Dict[tuple, FolderOrganization] = {}

        for file_metadata in files:
            top_category = file_metadata.suggested_category
            subcategory = self._detect_subcategory(file_metadata)

            key = (top_category, subcategory or "")

            if key not in organization:
                # suggested_folder_name contains both levels when subcategory present
                folder_name = (
                    f"{top_category}/{subcategory}" if subcategory else top_category
                )
                organization[key] = FolderOrganization(
                    category=top_category,
                    suggested_folder_name=sanitize_folder_name(folder_name),
                )

            organization[key].files.append(file_metadata)

        # Return FolderOrganization objects sorted by file count
        return sorted(
            organization.values(), key=lambda x: len(x.files), reverse=True
        )

    def _detect_subcategory(self, file_metadata: FileMetadata) -> Optional[str]:
        """Detect a more specific subcategory for code files.

        Returns one of 'Python', 'SQL', 'Java' when detected, otherwise None.
        """
        # Use file extension first
        ext = (file_metadata.file_type or "").lower()
        name = file_metadata.original_name.lower()
        content = (file_metadata.content_preview or "").lower()

        if ext in [".py", ".pyw"] or "python" in name or "python" in content:
            return "Python"
        if ext in [".sql"] or "sql" in name or "sql" in content:
            return "SQL"
        if ext in [".java"] or "java" in name or "java" in content:
            return "Java"

        # Fallback: no specific subcategory detected
        return None

    def _build_structure(self, organized_folders: List[FolderOrganization]) -> dict:
        """Build suggested folder structure."""
        structure = {}
        for folder in organized_folders:
            structure[folder.suggested_folder_name] = {
                "category": folder.category,
                "file_count": len(folder.files),
                "files": [f.suggested_name for f in folder.files[:5]],  # Top 5
            }
        return structure
