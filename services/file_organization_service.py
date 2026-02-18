"""File organization service."""
import shutil
from pathlib import Path
from typing import List, Optional

from models import OrganizationResult
from utils import sanitize_folder_name, FileAccessError, OrganizationError


class FileOrganizationService:
    """Service for organizing files into folders."""

    def organize_files(
        self,
        organization_result: OrganizationResult,
        create_folders: bool = False,
        move_files: bool = False,
    ) -> dict:
        """
        Organize files based on analysis result.

        Args:
            organization_result: Result from file analysis
            create_folders: Whether to create the folder structure
            move_files: Whether to actually move files

        Returns:
            Dictionary with organization details
        """
        source_folder = organization_result.source_folder

        if not source_folder.exists():
            raise FileAccessError(f"Source folder no longer exists: {source_folder}")

        try:
            results = {"created_folders": [], "moved_files": [], "errors": []}

            for folder_org in organization_result.organized_folders:
                folder_name = folder_org.suggested_folder_name
                folder_path = source_folder / folder_name

                if create_folders:
                    try:
                        folder_path.mkdir(exist_ok=True)
                        results["created_folders"].append(str(folder_path))
                    except Exception as e:
                        results["errors"].append(
                            f"Failed to create {folder_name}: {str(e)}"
                        )
                        continue

                if move_files and create_folders:
                    for file_metadata in folder_org.files:
                        try:
                            self._move_file(
                                file_metadata.file_path, folder_path, file_metadata.suggested_name
                            )
                            results["moved_files"].append(
                                {
                                    "from": str(file_metadata.file_path),
                                    "to": str(
                                        folder_path / file_metadata.suggested_name
                                    ),
                                }
                            )
                        except Exception as e:
                            results["errors"].append(
                                f"Failed to move {file_metadata.original_name}: {str(e)}"
                            )

            return results

        except Exception as e:
            raise OrganizationError(f"Failed to organize files: {str(e)}")

    def _move_file(self, source: Path, dest_folder: Path, new_name: str) -> None:
        """Move file to destination folder with new name."""
        dest_path = dest_folder / new_name

        # If destination already exists, append number
        if dest_path.exists():
            stem = Path(new_name).stem
            suffix = Path(new_name).suffix
            counter = 1
            while dest_path.exists():
                new_name = f"{stem}_{counter}{suffix}"
                dest_path = dest_folder / new_name
                counter += 1

        shutil.move(str(source), str(dest_path))
