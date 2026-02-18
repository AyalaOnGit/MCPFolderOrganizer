"""Main MCP Server for File Organization."""
from typing import Any

from mcp.server.fastmcp import FastMCP

from models import OperationResult
from services import FileAnalysisService, FileOrganizationService


# Initialize services
analysis_service = FileAnalysisService()
organization_service = FileOrganizationService()

# Create FastMCP server
mcp = FastMCP("File Organizer", json_response=True)


@mcp.tool()
def analyze_folder(folder_path: str) -> dict[str, Any]:
    """
    Analyze a folder to understand its contents and suggest file organization by topics.
    
    Args:
        folder_path: Absolute path to the folder to analyze
        
    Returns:
        Dictionary with analysis results including suggested categories and file organization
    """
    result = analysis_service.analyze_folder(folder_path)

    response = {
        "success": True,
        "source_folder": str(result.source_folder),
        "total_files": result.total_files,
        "categories": [
            {
                "name": org.category,
                "suggested_folder": org.suggested_folder_name,
                "file_count": len(org.files),
                "files": [
                    {
                        "original_name": f.original_name,
                        "suggested_name": f.suggested_name,
                        "size": f.file_size,
                        "type": f.file_type,
                        "confidence": f.confidence_score,
                        "tags": f.tags,
                    }
                    for f in org.files[:10]  # Top 10 files per category
                ],
            }
            for org in result.organized_folders
        ],
        "uncategorized_count": len(result.unorganized_files),
        "suggested_structure": result.suggested_structure,
    }

    return response


@mcp.tool()
def organize_files(
    folder_path: str,
    create_folders: bool = False,
    move_files: bool = False,
    apply_naming: bool = False,
) -> dict[str, Any]:
    """
    Organize files into topic-based folders with suggested names.
    
    Args:
        folder_path: Absolute path to the folder to organize
        create_folders: Whether to create the folder structure
        move_files: Whether to actually move files to new folders
        apply_naming: Whether to rename files with suggested names
        
    Returns:
        Dictionary with organization results including created folders and moved files
    """
    # First analyze the folder
    analysis_result = analysis_service.analyze_folder(folder_path)

    # Then organize based on analysis
    org_result = organization_service.organize_files(
        analysis_result, create_folders=create_folders, move_files=move_files
    )

    response = {
        "success": True,
        "action": "analyze" if not create_folders else "organize",
        "source_folder": str(analysis_result.source_folder),
        "created_folders": org_result.get("created_folders", []),
        "moved_files": org_result.get("moved_files", []),
        "errors": org_result.get("errors", []),
        "summary": {
            "total_files": analysis_result.total_files,
            "folders_created": len(org_result.get("created_folders", [])),
            "files_moved": len(org_result.get("moved_files", [])),
            "errors_count": len(org_result.get("errors", [])),
        },
    }

    return response


@mcp.tool()
def get_structure(folder_path: str) -> dict[str, Any]:
    """
    Get the suggested folder structure for an analyzed folder.
    
    Args:
        folder_path: Absolute path to the folder
        
    Returns:
        Dictionary with suggested folder structure
    """
    result = analysis_service.analyze_folder(folder_path)

    response = {
        "success": True,
        "folder": str(result.source_folder),
        "suggested_structure": result.suggested_structure,
        "total_files": result.total_files,
        "categories_count": len(result.organized_folders),
    }

    return response


if __name__ == "__main__":
    mcp.run()
