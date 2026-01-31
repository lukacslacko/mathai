import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from syntax import NumericVariable, LogicVariable, Implies
from storage import SentenceStorage, Provenance
from inference import ModusPonens, UniversalGeneralization

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

def test_inference():
    storage = SentenceStorage.load(DB_PATH)
    mp = ModusPonens(storage)
    ug = UniversalGeneralization(storage)
    
    # Setup a manual scenario locally for testing if we don't have handy proven axioms that fit perfectly
    # or rely on existing ones.
    
    # Let's prove: A -> A (using MP and axioms)
    # Actually Axiom 1 is A -> (B -> A).
    # This is hard to automate "proof searching" right now.
    # Let's just manually inject some "proven" sentences to test the RULES mechanics.
    # In a real run, these would come from axioms.
    
    P = storage.intern(LogicVariable("P"))
    Q = storage.intern(LogicVariable("Q"))
    
    # Fake prove P->Q and P
    imp = storage.intern(Implies(P, Q))
    
    # Hack: Inject into storage for testing mechanics (marked as "Test Axiom")
    test_prov = Provenance("Test Setup")
    storage.mark_proven(imp, test_prov)
    storage.mark_proven(P, test_prov)
    
    print("Testing Modus Ponens...")
    # Derive Q
    result_q = mp.apply(imp, P)
    print(f"Derived: {result_q}")
    assert result_q == Q
    assert storage.is_proven(Q)
    
    print("Testing Universal Generalization...")
    x = storage.intern(NumericVariable("x"))
    # Derive forall x (Q)
    result_ug = ug.apply(Q, x)
    print(f"Derived: {result_ug}")
    assert str(result_ug) == "∀x(Q)"
    assert storage.is_proven(result_ug)
    
    # Don't save this test data to main DB to keep it clean? 
    # Or save to a temp test DB.
    # User didn't specify, but I'll avoid polluting the main DB with "Test Setup" axioms.
    print("Test passed. Not saving to DB to avoid pollution.")

if __name__ == "__main__":
    test_inference()
