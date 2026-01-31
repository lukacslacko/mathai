import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from syntax import (
    NumericVariable, Zero, Equals, Implies, LogicVariable, Node
)
from matcher import Matcher
from storage import SentenceStorage

def test_matches():
    matcher = Matcher()
    
    # Test 1: 0=0 match against x=x
    x = NumericVariable("X")
    ref_eq = Equals(x, x) # x=x
    
    zero = Zero()
    target_eq = Equals(zero, zero) # 0=0
    
    print(f"Test 1: Match {ref_eq} against {target_eq}")
    bindings = matcher.match(ref_eq, target_eq)
    print(f"Bindings: {bindings}")
    if bindings is not None:
        print("Success for 0=0 match!")
    else:
        print("FAIL for 0=0 match!")

    # Test 2: Forward Chain Match
    # Match L2.ant (Pattern) against L1 (Fact)
    # L1: A -> (B -> A)
    # L2: (A -> (B -> C)) -> ((A -> B) -> (A -> C))
    # LHS: A -> (B -> C)
    
    A = LogicVariable("A")
    B = LogicVariable("B")
    C = LogicVariable("C")
    
    L1 = Implies(A, Implies(B, A))
    L2_LHS = Implies(A, Implies(B, C))
    
    print(f"\nTest 2: Match {L2_LHS} against {L1}")
    bindings_2 = matcher.match(L2_LHS, L1)
    print(f"Bindings: {bindings_2}")
    if bindings_2 is not None:
        print("Success for Forward Chain match!")
    else:
        print("FAIL for Forward Chain match!")

if __name__ == "__main__":
    test_matches()
