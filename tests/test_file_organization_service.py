"""Tests for file organization service."""
import tempfile
from pathlib import Path
import pytest

from services import FileAnalysisService, FileOrganizationService


@pytest.fixture
def analysis_service():
    """Create analysis service instance."""
    return FileAnalysisService()


@pytest.fixture
def organization_service():
    """Create organization service instance."""
    return FileOrganizationService()


@pytest.fixture
def temp_folder_with_files():
    """Create temporary folder with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        (base_path / "document.txt").write_text("This is a document")
        (base_path / "script.py").write_text("print('hello')")
        (base_path / "data.json").write_text('{"test": true}')

        yield base_path


def test_organize_files_preview(
    analysis_service, organization_service, temp_folder_with_files
):
    """Test organizing files in preview mode (no actual changes)."""
    analysis_result = analysis_service.analyze_folder(
        str(temp_folder_with_files)
    )

    org_result = organization_service.organize_files(
        analysis_result, create_folders=False, move_files=False
    )

    assert "created_folders" in org_result
    assert "moved_files" in org_result
    assert "errors" in org_result


def test_create_folders(analysis_service, organization_service, temp_folder_with_files):
    """Test creating folder structure."""
    analysis_result = analysis_service.analyze_folder(
        str(temp_folder_with_files)
    )

    org_result = organization_service.organize_files(
        analysis_result, create_folders=True, move_files=False
    )

    # Check that folders were created
    assert len(org_result.get("created_folders", [])) > 0

    # Verify folders exist
    for folder in org_result.get("created_folders", []):
        assert Path(folder).exists()
