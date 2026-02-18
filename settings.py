"""Settings and configuration for the MCP server."""
import os

# ============================================================================
# AI Configuration
# ============================================================================
# To use AI-powered classification, configure one of the following:

# Option 1: OpenAI API
# Set via environment variable: OPENAI_API_KEY='sk-...'
# This will use GPT-3.5-turbo for classification
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Option 2: Custom external LLM endpoint
# Set via environment variables: EXTERNAL_LLM_URL and EXTERNAL_LLM_API_KEY
# The endpoint should accept JSON: {"filename", "file_type", "content_preview"}
# And return JSON: {"category", "confidence", "subcategory", "suggested_name"}
EXTERNAL_LLM_URL = os.environ.get("EXTERNAL_LLM_URL")
EXTERNAL_LLM_API_KEY = os.environ.get("EXTERNAL_LLM_API_KEY")

# Option 3: Interactive mode (for MCP Inspector)
# When INTERACTIVE_MODE is True and AI is unavailable, the system will
# prompt the user via stdin for classification decisions.
INTERACTIVE_MODE = os.environ.get("INTERACTIVE_MODE", "false").lower() == "true"

# ============================================================================
# File Processing Settings
# ============================================================================
MAX_FILE_SIZE_MB = 10

# Maximum number of files to analyze per folder
MAX_FILES_TO_ANALYZE = 1000

# File extensions to consider as text
TEXT_FILE_EXTENSIONS = {
    ".txt",
    ".md",
    ".py",
    ".js",
    ".ts",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".html",
    ".css",
    ".sql",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".sh",
    ".bash",
    ".log",
    ".csv",
    ".ini",
    ".conf",
    ".config",
    ".toml",
    ".properties",
    ".vue",
    ".jsx",
    ".tsx",
    ".scala",
    ".rb",
    ".php",
    ".go",
    ".rs",
}

# Category detection keywords
CATEGORY_KEYWORDS = {
    "Documents": [
        "document",
        "doc",
        "pdf",
        "word",
        "text",
        "report",
        "essay",
        "article",
        "paper",
        "memo",
        "letter",
        "contract",
        "agreement",
    ],
    "Images": [
        "image",
        "photo",
        "picture",
        "img",
        "graphic",
        "design",
        "icon",
        "screenshot",
    ],
    "Videos": ["video", "movie", "film", "clip", "recording"],
    "Audio": ["audio", "music", "sound", "song", "podcast"],
    "Code": [
        "code",
        "script",
        "program",
        "source",
        "python",
        "java",
        "javascript",
    ],
    "Data": ["data", "dataset", "database", "csv", "sql", "excel", "sheet"],
    "Configuration": [
        "config",
        "settings",
        "setup",
        "configuration",
    ],
}

# Maximum folder name length
MAX_FOLDER_NAME_LENGTH = 200

# Enable detailed logging
DEBUG = False

# ============================================================================
# Configuration Setup Guide
# ============================================================================
# 
# To get started with AI classification:
#
# 1. Using OpenAI (recommended for quick start):
#    powershell> $env:OPENAI_API_KEY = 'sk-your-key-here'
#    powershell> python main.py /path/to/folder
#
# 2. Using custom external LLM:
#    powershell> $env:EXTERNAL_LLM_URL = 'https://your-api.example.com/classify'
#    powershell> $env:EXTERNAL_LLM_API_KEY = 'your-api-key'
#    powershell> python main.py /path/to/folder
#
# 3. Interactive mode (ask user for classification):
#    powershell> $env:INTERACTIVE_MODE = 'true'
#    powershell> python main.py /path/to/folder
#
# Without any AI configuration, files will be categorized as 'Uncategorized'.
