# File Organizer

A Python utility to analyze folders and suggest organized file structures using AI classification. The classifier can use OpenAI, a custom LLM endpoint, or interactive prompts.

## Features

- Analyze a folder and suggest categories for files using AI.
- Subcategorize files with AI-determined categories (e.g., Python, Flask, PostgreSQL, etc.).
- Produce a suggested folder structure and AI-suggested filenames.
- Support for OpenAI, custom LLM endpoints, or interactive manual classification.
- Graceful fallback: when AI unavailable, optionally ask user for input via CLI/Inspector.

## Quick start

Prerequisites: Python 3.9+ and pip.

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run tests:

```powershell
python -m pytest -q
```

## Using the classifier

### Option 1: OpenAI (recommended)

1. Get an OpenAI API key from [platform.openai.com](https://platform.openai.com).
2. Run with AI:

```powershell
$env:OPENAI_API_KEY = 'sk-your-key-here'
python main.py /path/to/folder
```

### Option 2: Custom LLM endpoint

If you have a custom LLM service, configure it:

```powershell
$env:EXTERNAL_LLM_URL = 'https://your-llm-api.example.com/classify'
$env:EXTERNAL_LLM_API_KEY = 'your-api-key'
python main.py /path/to/folder
```

Your endpoint should accept JSON:
```json
{
  "filename": "example.py",
  "file_type": ".py",
  "content_preview": "def hello(): ..."
}
```

And return JSON:
```json
{
  "category": "Code",
  "confidence": 0.95,
  "subcategory": "Python",
  "suggested_name": "hello_world.py"
}
```

### Option 3: Interactive mode (manual classification)

For testing or when you prefer to classify files manually:

```powershell
$env:INTERACTIVE_MODE = 'true'
python main.py /path/to/folder
```

The system will prompt you for each file's category, confidence, subcategory, and suggested name.

### Option 4: No AI (auto-categorizes as "Uncategorized")

```powershell
python main.py /path/to/folder
```

All files will be categorized as "Uncategorized" without any AI or interactive prompts.

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
