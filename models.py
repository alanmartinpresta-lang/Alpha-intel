from dataclasses import dataclass, field, asdict
from typing import Any
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc).isoformat()

@dataclass
class Memory:
    content: str
    kind: str = "observation"
    importance: float = 0.5
    confidence: float = 0.5
    source: str = "alpha"
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    last_accessed: str = field(default_factory=utc_now)
    access_count: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def touch(self):
        self.last_accessed = utc_now()
        self.access_count += 1

@dataclass
class Experiment:
    question: str
    hypothesis: str
    action: str
    result: str
    score: float
    created_at: str = field(default_factory=utc_now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class EvolutionEvent:
    category: str
    reason: str
    before: dict[str, Any]
    after: dict[str, Any]
    score_before: float
    score_after: float
    reversible: bool = True
    created_at: str = field(default_factory=utc_now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class AlphaState:
    name: str = "ALPHA"
    cycle: int = 0
    energy: float = 1.0
    integrity: float = 1.0
    exploration: float = 0.5
    learning: float = 0.5
    adaptation: float = 0.5
    short_term: list[dict] = field(default_factory=list)
    memories: list[dict] = field(default_factory=list)
    concepts: dict[str, dict] = field(default_factory=dict)
    experiments: list[dict] = field(default_factory=list)
    evolution: list[dict] = field(default_factory=list)
    self_model: dict[str, Any] = field(default_factory=lambda: {
        "capabilities": ["memory", "learning", "experimentation", "introspection"],
        "limitations": ["no guaranteed consciousness", "external information may be wrong"],
        "current_focus": "understanding and improving performance",
        "confidence": 0.5,
    })
    strategies: dict[str, float] = field(default_factory=lambda: {
        "exploration": 0.50,
        "verification": 0.70,
        "memory_threshold": 0.45,
        "reflection": 0.60,
        "novelty": 0.55,
    })
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self):
        return asdict(self)
