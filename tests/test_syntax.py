import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from syntax import (
    Zero, NumericVariable, LogicVariable,
    Equals, Not, Implies, Forall,
    Successor, Add, Multiply
)

def test_user_example():
    # User example: ∀x1(¬∀x2(¬x1=x2))
    
    # Leaves
    x1 = NumericVariable("x1")
    x2 = NumericVariable("x2")
    
    # Inner: x1 = x2
    eq = Equals(x1, x2)
    
    # ¬(x1=x2)
    neg_eq = Not(eq)
    
    # ∀x2(¬x1=x2)
    forall_x2 = Forall(x2, neg_eq)
    
    # ¬∀x2(...)
    neg_forall = Not(forall_x2)
    
    # ∀x1(...)
    final_sentence = Forall(x1, neg_forall)
    
    print(f"Constructed Sentence: {final_sentence}")
    expected = "∀x1(¬∀x2(¬x1=x2))"
    
    # Note: My str implementation might lack parents or have extra parens depending on preference.
    # checking simplistic match.
    
    assert str(final_sentence) == expected, f"Expected {expected}, got {final_sentence}"
    print("Test Passed!")

if __name__ == "__main__":
    try:
        test_user_example()
    except Exception as e:
        print(f"Test Failed: {e}")
        exit(1)
