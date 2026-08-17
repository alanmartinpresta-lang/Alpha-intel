from .models import Memory, Experiment
from .memory.store import MemoryStore
from .evolution.engine import EvolutionEngine
from .tools.internet import fetch_url

class AlphaAgent:
    def __init__(self, state_path="alpha_core/storage/alpha_state.json", internet=False):
        self.store=MemoryStore(state_path)
        self.evolver=EvolutionEngine(self.store)
        self.internet_enabled=internet

    @property
    def state(self):
        return self.store.state

    def observe(self, content, source="human", importance=0.55, confidence=0.7, tags=None):
        m=Memory(content=content, source=source, importance=importance, confidence=confidence, tags=tags or [])
        self.store.add_memory(m)
        self.state.short_term.append({"content":content,"source":source})
        self.state.short_term=self.state.short_term[-30:]
        self.state.cycle += 1
        self.state.learning=min(1.0,self.state.learning+0.002)
        self.store.save()
        return m

    def answer(self, question):
        memories=self.store.recall(question)
        q=question.lower()
        if any(x in q for x in ("qui es-tu","qui es tu","état","etat","comment vas-tu")):
            raw=f"Je suis {self.state.name}. Mon cycle courant est {self.state.cycle}. Mon modèle interne indique que je travaille sur : {self.state.self_model['current_focus']}."
        elif memories:
            raw="J'ai retrouvé des informations pertinentes dans ma mémoire : " + " | ".join(m["content"] for m in memories[:4])
        else:
            raw="Je n'ai pas encore de connaissance pertinente dans ma mémoire pour cette question. Je peux l'enregistrer comme question à explorer."
        self.observe(f"Question reçue: {question}", source="human", importance=0.45, confidence=1.0, tags=["dialogue"])
        self.observe(f"Réponse produite: {raw}", source="alpha", importance=0.35, confidence=0.65, tags=["dialogue"])
        return {"source":"alpha","response":raw,"memories_used":len(memories)}

    def learn_from_text(self, text, source="internet", confidence=0.5):
        if not text.strip(): return {"learned":False}
        self.observe(text[:4000], source=source, importance=0.55, confidence=confidence, tags=["knowledge"])
        self.state.learning=min(1.0,self.state.learning+0.01)
        self.store.save()
        return {"learned":True,"chars":len(text[:4000])}

    def research(self, url):
        if not self.internet_enabled:
            return {"ok":False,"error":"Internet disabled. Start Alpha with --internet."}
        data=fetch_url(url)
        result=self.learn_from_text(data["text"], source="internet", confidence=0.45)
        return {"ok":True,"url":url,"preview":data["text"][:2000],"learned":result}

    def experiment(self, question, hypothesis):
        before=self.evolver.evaluate()
        action=f"Compare hypothesis against current memory for: {question}"
        result="No external experiment runner was required; the hypothesis was recorded for future evaluation."
        exp=Experiment(question,hypothesis,action,result,before)
        self.state.experiments.append(exp.__dict__)
        self.state.cycle += 1
        self.state.self_model["confidence"]=min(1.0,self.state.self_model["confidence"]+0.005)
        self.store.save()
        return exp.__dict__

    def evolve(self):
        proposal=self.evolver.propose()
        event=self.evolver.apply(proposal)
        return event.__dict__

    def introspect(self):
        return {
            "cycle":self.state.cycle,
            "energy":self.state.energy,
            "integrity":self.state.integrity,
            "exploration":self.state.exploration,
            "learning":self.state.learning,
            "adaptation":self.state.adaptation,
            "memory_count":len(self.state.memories),
            "concept_count":len(self.state.concepts),
            "experiment_count":len(self.state.experiments),
            "evolution_count":len(self.state.evolution),
            "strategies":self.state.strategies,
            "self_model":self.state.self_model,
        }
