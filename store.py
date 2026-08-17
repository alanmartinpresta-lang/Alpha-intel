from pathlib import Path
import json, copy
from ..models import AlphaState, Memory, utc_now

class MemoryStore:
    def __init__(self, path="alpha_core/storage/alpha_state.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load()

    def _load(self):
        if not self.path.exists():
            return AlphaState()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return AlphaState(**data)
        except Exception:
            return AlphaState()

    def save(self):
        self.state.updated_at = utc_now()
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def snapshot(self):
        snap = self.path.with_name(f"alpha_state_cycle_{self.state.cycle}.json")
        snap.write_text(json.dumps(self.state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return str(snap)

    def add_memory(self, memory: Memory):
        self.state.memories.append(memory.__dict__)
        # bounded but persistent: retain important/recent memories
        if len(self.state.memories) > 5000:
            self.state.memories.sort(key=lambda x: (x.get("importance",0), x.get("last_accessed","")))
            self.state.memories = self.state.memories[-4500:]
        self.save()

    def recall(self, query, limit=8):
        q = set(query.lower().split())
        scored = []
        for m in self.state.memories:
            words = set(m.get("content","").lower().split())
            overlap = len(q & words)
            score = overlap + 0.2*m.get("importance",0) + 0.1*m.get("confidence",0)
            if score > 0:
                scored.append((score, m))
        scored.sort(key=lambda x: x[0], reverse=True)
        result = []
        for _, m in scored[:limit]:
            m["access_count"] = m.get("access_count",0)+1
            result.append(m)
        return result

    def add_concept(self, name, description, confidence=0.5):
        c = self.state.concepts.setdefault(name, {"description": description, "confidence": confidence, "uses": 0})
        c["description"] = description
        c["confidence"] = max(c["confidence"], confidence)
        c["uses"] += 1
        self.save()
