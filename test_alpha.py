import tempfile, os, json, threading, time
from pathlib import Path
from alpha_core.agent import AlphaAgent

def main():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.json"
        a=AlphaAgent(str(p), internet=False)
        r=a.answer("Qui es-tu ?")
        assert r["source"]=="alpha"
        assert p.exists()
        assert len(a.state.memories)>=2
        a.learn_from_text("La thermodynamique étudie les transformations d'énergie.", "test", .8)
        assert a.store.recall("thermodynamique")
        before=len(a.state.evolution)
        a.evolve()
        assert len(a.state.evolution)==before+1
    print("ALPHA V2 TESTS: PASS")

if __name__=="__main__":
    main()
