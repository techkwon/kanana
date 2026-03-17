from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class ErrorDetail:
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KananaError(Exception):
    exit_code = 5
    error_code = "internal_error"

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_error_detail(self) -> ErrorDetail:
        return ErrorDetail(code=self.error_code, message=self.message, details=self.details or None)


class InputValidationError(KananaError):
    exit_code = 3
    error_code = "invalid_input"


class SafetyViolationError(KananaError):
    exit_code = 2
    error_code = "safety_blocked"


class RuntimeDependencyError(KananaError):
    exit_code = 4
    error_code = "runtime_unavailable"
