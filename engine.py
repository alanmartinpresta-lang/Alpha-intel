import random
from ..models import EvolutionEvent

class EvolutionEngine:
    def __init__(self, store):
        self.store = store

    def evaluate(self):
        s=self.store.state
        return round(
            0.25*s.learning + 0.25*s.adaptation +
            0.20*s.integrity + 0.15*s.exploration +
            0.15*min(1.0, len(s.memories)/100.0), 4)

    def propose(self):
        s=self.store.state
        before=dict(s.strategies)
        target=random.choice(list(before))
        delta=random.choice([-0.05,-0.03,0.03,0.05])
        after=dict(before)
        after[target]=min(1.0,max(0.05,after[target]+delta))
        return {"target":target,"delta":delta,"before":before,"after":after}

    def apply(self, proposal):
        s=self.store.state
        score_before=self.evaluate()
        self.store.snapshot()
        s.strategies=proposal["after"]
        # strategy changes produce a small measurable adaptation update
        s.adaptation=min(1.0,max(0.0,s.adaptation + abs(proposal["delta"])*0.25))
        score_after=self.evaluate()
        event=EvolutionEvent(
            category="strategy",
            reason=f"bounded strategy adjustment: {proposal['target']} {proposal['delta']:+.2f}",
            before=proposal["before"], after=proposal["after"],
            score_before=score_before, score_after=score_after
        )
        s.evolution.append(event.__dict__)
        self.store.save()
        return event
