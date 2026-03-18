from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from .errors import ErrorDetail


@dataclass
class ResponseMeta:
    model: str
    latency_ms: int
    session_id: Optional[str] = None


@dataclass
class ResponseEnvelope:
    schema_version: str
    ok: bool
    command: str
    result: Dict[str, Any]
    meta: ResponseMeta
    error: Optional[ErrorDetail] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        return payload
