import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from syntax import (
    NumericVariable, Zero, Successor, 
    Equals, Not, Implies, Add, Multiply, Forall
)

def test_free_variables():
    x = NumericVariable("x")
    y = NumericVariable("y")
    
    # x + y
    expr = Add(x, y)
    assert expr.free_variables == {'x', 'y'}, f"Got {expr.free_variables}"
    
    # forall x (x + y)  <- nonsense as term, but let's assume eq
    f = Forall(x, Equals(x, y))
    assert f.free_variables == {'y'}, f"Got {f.free_variables}"
    
    print("test_free_variables passed")

def test_substitution():
    x = NumericVariable("x")
    y = NumericVariable("y")
    z = Zero()
    
    # x + y replace x/0 -> 0 + y
    expr = Add(x, y)
    subbed = expr.substitute("x", z)
    assert str(subbed) == "(0+y)", f"Got {subbed}"
    
    # Shadowing: forall x (x=y) replace x/0 -> unchanged
    f = Forall(x, Equals(x, y))
    subbed_f = f.substitute("x", z)
    assert str(subbed_f) == str(f), f"Got {subbed_f}"
    
    # Nested: forall x (x=y) replace y/S(0) -> forall x (x=S(0))
    subbed_f2 = f.substitute("y", Successor(z))
    assert str(subbed_f2) == "∀x(x=S(0))", f"Got {subbed_f2}"
    
    print("test_substitution passed")

if __name__ == "__main__":
    test_free_variables()
    test_substitution()
