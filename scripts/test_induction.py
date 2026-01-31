import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from syntax import NumericVariable, Zero, Add, Equals
from storage import SentenceStorage
from schemas import InductionSchema

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

def test_induction():
    storage = SentenceStorage.load(DB_PATH)
    schema = InductionSchema(storage)
    
    X = storage.intern(NumericVariable("X"))
    Z = storage.intern(Zero())
    
    # Predicate: X+0 = X (This is actually an axiom, but let's generate induction for it as test)
    # P(X) := X+0=X
    P = storage.intern(Equals(storage.intern(Add(X, Z)), X))
    
    axiom = schema.apply(X, P)
    print(f"Generated Induction Axiom:\n{axiom}")
    
    storage.save(DB_PATH)

if __name__ == "__main__":
    test_induction()
