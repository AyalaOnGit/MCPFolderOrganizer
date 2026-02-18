from dataclasses import dataclass
from typing import Optional


@dataclass
class OperationResult:
    """Standard result object for operations."""
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None
