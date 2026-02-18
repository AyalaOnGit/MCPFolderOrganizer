"""Custom error classes for the MCP server."""


class MCPError(Exception):
    """Base exception for MCP operations."""
    pass


class InvalidPathError(MCPError):
    """Raised when provided path is invalid."""
    pass


class FileAccessError(MCPError):
    """Raised when file cannot be accessed."""
    pass


class AnalysisError(MCPError):
    """Raised when file analysis fails."""
    pass


class OrganizationError(MCPError):
    """Raised when file organization fails."""
    pass
