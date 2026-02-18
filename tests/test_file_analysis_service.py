"""Tests for file analysis service."""
import tempfile
from pathlib import Path
import pytest

from services.file_analysis_service import FileAnalysisService


@pytest.fixture
def analysis_service():
    """Create analysis service instance."""
    return FileAnalysisService()


@pytest.fixture
def temp_folder():
    """Create temporary folder with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        # Create test files
        (base_path / "document.txt").write_text("This is a document file")
        (base_path / "report.md").write_text("# Report\nThis is a report document")
        (base_path / "script.py").write_text("print('hello')")
        (base_path / "data.json").write_text('{"key": "value"}')
        (base_path / "config.yaml").write_text("setting: value")

        yield base_path


def test_analyze_folder(analysis_service, temp_folder):
    """Test folder analysis."""
    result = analysis_service.analyze_folder(str(temp_folder))

    assert result.total_files == 5
    assert len(result.organized_folders) > 0


def test_analyze_empty_folder(analysis_service):
    """Test analyzing empty folder."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = analysis_service.analyze_folder(tmpdir)
        assert result.total_files == 0


def test_file_categorization(analysis_service, temp_folder):
    """Test file categorization."""
    result = analysis_service.analyze_folder(str(temp_folder))

    categories = {org.category for org in result.organized_folders}

    assert "Code" in categories or "Configuration" in categories


def test_invalid_path(analysis_service):
    """Test with invalid path."""
    with pytest.raises(Exception):
        analysis_service.analyze_folder("/nonexistent/path")
