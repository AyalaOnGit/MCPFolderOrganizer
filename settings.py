"""Settings and configuration for the MCP server."""

# Maximum file size to read (in MB)
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
