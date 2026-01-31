import sys
import os

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from syntax import LogicVariable, Implies
from matcher import Matcher
from storage import SentenceStorage

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

# Load storage with axioms
storage = SentenceStorage.load(DB_PATH)
matcher = Matcher()

# Get the actual L2 axiom from storage
axioms = list(storage.proven.keys())
print("Axioms in database:")
for i, ax in enumerate(axioms):
    print(f"{i+1}. {ax}")

# L2 should be: ((A → (B → C)) → ((A → B) → (A → C)))
L2 = axioms[1]  # Should be L2
print(f"\nL2: {L2}")
print(f"L2 type: {type(L2)}")
print(f"L2.right: {L2.right}")

# Goal: P → P
P = storage.intern(LogicVariable("P"))
goal = storage.intern(Implies(P, P))
print(f"\nGoal: {goal}")

# Try to match L2's RHS against goal
print(f"\nMatching {L2.right} against {goal}")
bindings = matcher.match(L2.right, goal)
print(f"Bindings: {bindings}")

if bindings:
    print("\n✓ Match succeeded!")
    for var, val in bindings.items():
        print(f"  {var} → {val}")
else:
    print("\n✗ Match failed!")
