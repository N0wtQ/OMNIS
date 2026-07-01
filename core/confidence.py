from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ConfidenceLevel(Enum):
    HIGH = "Alto"
    MEDIUM = "Medio"
    LOW = "Bajo"


@dataclass
class Finding:
    discipline: str
    description: str
    sources: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    timestamp: str = ""
    raw_data: dict = field(default_factory=dict)

    @property
    def confidence(self) -> ConfidenceLevel:
        n = len(self.sources)
        if n >= 3:
            return ConfidenceLevel.HIGH
        if n >= 2:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    def to_dict(self) -> dict:
        return {
            "discipline": self.discipline,
            "description": self.description,
            "confidence": self.confidence.value,
            "sources": self.sources,
            "tools_used": self.tools_used,
            "timestamp": self.timestamp,
        }


def aggregate_confidence(findings: List[Finding]) -> ConfidenceLevel:
    if not findings:
        return ConfidenceLevel.LOW
    high = sum(1 for f in findings if f.confidence == ConfidenceLevel.HIGH)
    medium = sum(1 for f in findings if f.confidence == ConfidenceLevel.MEDIUM)
    total = len(findings)
    if high / total >= 0.5:
        return ConfidenceLevel.HIGH
    if (high + medium) / total >= 0.5:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW
