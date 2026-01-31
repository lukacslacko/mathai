import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from syntax import LogicVariable, Implies, Not
from storage import SentenceStorage, Provenance

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

def init_axioms():
    storage = SentenceStorage.load(DB_PATH)
    
    # Define variables
    # Note: Variable uniqueness depends on name equality.
    A = storage.intern(LogicVariable("A"))
    B = storage.intern(LogicVariable("B"))
    C = storage.intern(LogicVariable("C"))
    
    # Axiom 1: A -> (B -> A)
    # Construction should ideally use interned children
    ax1 = storage.intern(Implies(A, storage.intern(Implies(B, A))))
    
    # Axiom 2: (A -> (B -> C)) -> ((A -> B) -> (A -> C))
    # Parts
    A_implies_B = storage.intern(Implies(A, B))
    A_implies_C = storage.intern(Implies(A, C))
    B_implies_C = storage.intern(Implies(B, C))
    A_implies_BtC = storage.intern(Implies(A, B_implies_C))
    
    left = A_implies_BtC
    right = storage.intern(Implies(A_implies_B, A_implies_C))
    
    ax2 = storage.intern(Implies(left, right))
    
    # Axiom 3: (~A -> ~B) -> (B -> A)
    # Parts
    not_A = storage.intern(Not(A))
    not_B = storage.intern(Not(B))
    notA_implies_notB = storage.intern(Implies(not_A, not_B))
    B_implies_A = storage.intern(Implies(B, A))
    
    ax3 = storage.intern(Implies(notA_implies_notB, B_implies_A))
    
    # Mark as proven
    print("Marking axioms as proven...")
    axiom_provenance = Provenance("Logic Axiom")
    
    print(f"1. {ax1}")
    storage.mark_proven(ax1, axiom_provenance)
    
    print(f"2. {ax2}")
    storage.mark_proven(ax2, axiom_provenance)
    
    print(f"3. {ax3}")
    storage.mark_proven(ax3, axiom_provenance)
    
    # Save
    storage.save(DB_PATH)

if __name__ == "__main__":
    init_axioms()
