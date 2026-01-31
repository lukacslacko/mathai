import sys
import os

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from syntax import (
    NumericVariable, Zero, Successor, 
    Equals, Not, Implies, Add, Multiply
)
from storage import SentenceStorage, Provenance

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

def init_peano():
    storage = SentenceStorage.load(DB_PATH)
    
    # Variables
    X = storage.intern(NumericVariable("X"))
    Y = storage.intern(NumericVariable("Y"))
    Z = storage.intern(Zero())
    
    peano_provenance = Provenance("Peano Axiom")
    
    # 1. ¬0=S(X)
    # Note syntax: Not(Equals(Zero, S(X)))
    s_x = storage.intern(Successor(X))
    ax1 = storage.intern(Not(storage.intern(Equals(Z, s_x))))
    
    # 2. S(X)=S(Y) -> X=Y
    s_y = storage.intern(Successor(Y))
    sx_eq_sy = storage.intern(Equals(s_x, s_y))
    x_eq_y = storage.intern(Equals(X, Y))
    ax2 = storage.intern(Implies(sx_eq_sy, x_eq_y))
    
    # 3. X+0=X
    x_plus_0 = storage.intern(Add(X, Z))
    ax3 = storage.intern(Equals(x_plus_0, X))
    
    # 4. X+S(Y)=S(X+Y)
    x_plus_sy = storage.intern(Add(X, s_y))
    x_plus_y = storage.intern(Add(X, Y))
    s_x_plus_y = storage.intern(Successor(x_plus_y))
    ax4 = storage.intern(Equals(x_plus_sy, s_x_plus_y))
    
    # 5. X*0=0
    x_mul_0 = storage.intern(Multiply(X, Z))
    ax5 = storage.intern(Equals(x_mul_0, Z))
    
    # 6. X*S(Y)=(X*Y)+X
    x_mul_sy = storage.intern(Multiply(X, s_y))
    x_mul_y = storage.intern(Multiply(X, Y))
    rhs = storage.intern(Add(x_mul_y, X))
    ax6 = storage.intern(Equals(x_mul_sy, rhs))
    
    # 7. X=X (Reflexivity)
    ax7 = storage.intern(Equals(X, X))
    
    axioms = [ax1, ax2, ax3, ax4, ax5, ax6, ax7]
    
    print("Marking Peano axioms as proven...")
    for i, ax in enumerate(axioms, 1):
        print(f"{i}. {ax}")
        storage.mark_proven(ax, peano_provenance)
        
    storage.save(DB_PATH)

if __name__ == "__main__":
    init_peano()
