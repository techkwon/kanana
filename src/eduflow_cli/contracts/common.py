from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class LearnerLevel(str, Enum):
    ELEMENTARY = "elementary"
    MIDDLE = "middle"
    HIGH = "high"
    ADULT = "adult"


class SafetyMode(str, Enum):
    STRICT = "strict"
    STANDARD = "standard"


class OutputVerbosity(str, Enum):
    BRIEF = "brief"
    STANDARD = "standard"
    DETAILED = "detailed"


@dataclass
class Audience:
    role: str = "educator"
    learner_level: str = LearnerLevel.ELEMENTARY.value


@dataclass
class SafetyOptions:
    mode: str = SafetyMode.STRICT.value
    block_on_unsafe: bool = True


@dataclass
class SessionOptions:
    id: Optional[str] = None
    save: bool = True


@dataclass
class OutputOptions:
    format: str = "json"
    verbosity: str = OutputVerbosity.STANDARD.value


@dataclass
class RequestEnvelope:
    input: Dict[str, Any] = field(default_factory=dict)
    audience: Audience = field(default_factory=Audience)
    safety: SafetyOptions = field(default_factory=SafetyOptions)
    session: SessionOptions = field(default_factory=SessionOptions)
    output: OutputOptions = field(default_factory=OutputOptions)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
