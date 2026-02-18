# File Organizer

A small Python utility to analyze a folder and suggest an organized folder structure based on file types and simple content/filename heuristics.

## Features

- Analyze a folder and suggest categories for files (Documents, Images, Code, Data, Configuration, etc.).
- Subcategorize code files into `Code/Python`, `Code/SQL`, and `Code/Java` when detected.
- Produce a suggested folder structure and file renaming hints.

## Quick start

Prerequisites: Python 3.9+ and pip. Node.js is optional if you use the MCP Inspector.

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run tests:

```powershell
python -m pytest -q
```

Run the main script (example):

```powershell
python main.py /path/to/your/folder
```

Notes about MCP Inspector (optional):
- The project is independent of the MCP Inspector. If you use the Inspector, ensure its proxy is running on `localhost:6277` before connecting.

## Project layout

- `services/` — core services (`FileAnalysisService`, `FileOrganizationService`).
- `models/` — dataclasses for `FileMetadata`, `FolderOrganization`, `OrganizationResult`.
- `tests/` — unit tests (run with `pytest`).
- `utils/` — helpers and validators.

## Contributing

1. Fork the repo and create a branch for your feature/bugfix.
2. Run tests and add new tests for your changes.
3. Open a pull request describing the change.

## License

This repository does not include a license file. Add one if you intend to publish or share the project publicly (e.g. `MIT`).
# File Organizer MCP

An intelligent MCP (Model Context Protocol) server that analyzes folders, automatically categorizes files, suggests meaningful names, and organizes them into topic-based folder structures.

## Features

- **Folder Analysis**: Scan a folder and analyze its contents
- **Intelligent Categorization**: Automatically categorize files by type (Documents, Images, Code, Data, etc.)
- **Smart Naming**: Suggest improved, meaningful filenames based on content and context
- **Folder Organization**: Create organized folder structures by topics
- **File Organization**: Option to move and rename files according to suggested structure
- **Metadata Extraction**: Extract tags and metadata from files for better organization
- **Confidence Scoring**: Get confidence scores for suggested categorizations

## Installation

```bash
pip install -e .
```

## Configuration

Edit `settings.py` to customize:
- Maximum file size to analyze
- File extensions to consider as text
- Category detection keywords
- Maximum folder name length

## Usage

### As an MCP Server

Start the server:

```bash
python main.py
```

### Available Tools

#### 1. `analyze_folder`

Analyze a folder to understand its contents and suggest organization.

**Parameters:**
- `folder_path` (string, required): Absolute path to the folder to analyze

**Returns:**
- Suggested folder structure
- File categorization
- Renamed suggestions for each file
- Confidence scores

**Example:**
```json
{
  "folder_path": "/path/to/folder"
}
```

#### 2. `organize_files`

Organize files into topic-based folders with suggested names.

**Parameters:**
- `folder_path` (string, required): Absolute path to the folder to organize
- `create_folders` (boolean, optional): Whether to create the folder structure (default: false)
- `move_files` (boolean, optional): Whether to actually move files to new folders (default: false)
- `apply_naming` (boolean, optional): Whether to rename files with suggested names (default: false)

**Returns:**
- Created folders list
- Moved files list
- Any errors encountered
- Summary statistics

#### 3. `get_structure`

Get the suggested folder structure for an analyzed folder.

**Parameters:**
- `folder_path` (string, required): Absolute path to the folder

**Returns:**
- Suggested structure with categories and file counts

## Project Structure

```
file-organizer-mcp/
├── main.py                    # MCP server entry point
├── settings.py                # Configuration settings
├── pyproject.toml            # Project metadata
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── models/
│   ├── __init__.py
│   ├── result.py            # OperationResult model
│   └── file_models.py       # File and organization models
├── services/
│   ├── __init__.py
│   ├── file_analysis_service.py      # File analysis logic
│   └── file_organization_service.py  # File organization logic
├── utils/
│   ├── __init__.py
│   ├── errors.py            # Custom exceptions
│   ├── paths.py             # Path utilities
│   └── validate.py          # Validation utilities
└── tests/
    ├── __init__.py
    ├── test_file_analysis_service.py
    ├── test_file_organization_service.py
    └── test_integration.py
```

## Categories

The server automatically recognizes and organizes into these categories:

- **Documents**: PDFs, Word docs, text files, reports
- **Images**: Photos, graphics, icons, screenshots
- **Videos**: Video files and recordings
- **Audio**: Music files, podcasts, audio recordings
- **Code**: Source code files in various languages
- **Data**: Datasets, databases, CSV, SQL files
- **Configuration**: Config files, settings, environment files
- **Archives**: Compressed files (zip, rar, etc.)
- **Backup**: Backup and old version files
- **README**: Documentation and guide files

## Example Workflow

1. Analyze a folder:
   ```python
   result = analyze_folder("/path/to/messy/folder")
   ```

2. Review the suggested structure

3. Organize with folders created but files not moved (safe preview):
   ```python
   organize_files("/path/to/messy/folder", create_folders=True, move_files=False)
   ```

4. If satisfied, actually move files:
   ```python
   organize_files("/path/to/messy/folder", create_folders=True, move_files=True)
   ```

## Testing

Run tests:

```bash
pytest tests/
```

## Error Handling

The server provides detailed error handling:
- `InvalidPathError`: When folder path is invalid
- `FileAccessError`: When files cannot be accessed
- `AnalysisError`: When file analysis fails
- `OrganizationError`: When organization fails

## Limitations

- Maximum file size for analysis: 10 MB (configurable)
- Maximum files per folder: 1000 (configurable)
- Text file preview: First 500 characters only
- Folder name length: Maximum 200 characters

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License
