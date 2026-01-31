import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from syntax import (
    Forall, Not, Equals, Implies, NumericVariable, LogicVariable
)
from storage import SentenceStorage
from parser import Parser

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

def test_parser():
    storage = SentenceStorage.load(DB_PATH)
    parser = Parser(storage)
    
    # 1. Simple Logic Variable
    print("Test 1: P")
    p = parser.parse("P")
    print(f"Parsed: {p} ({type(p)})")
    assert isinstance(p, LogicVariable)
    assert str(p) == "P"
    
    # 2. Negation
    print("\nTest 2: ~P")
    not_p = parser.parse("~P")
    print(f"Parsed: {not_p}")
    assert str(not_p) == "¬P"
    
    # 3. Forall
    print("\nTest 3: !x(x=0)")
    forall = parser.parse("!x(x=0)")
    print(f"Parsed: {forall}")
    assert str(forall) == "∀x(x=0)"
    
    # 4. Exists (Desguised forall)
    print("\nTest 4: ?x(x=x)")
    exists = parser.parse("?x(x=x)")
    print(f"Parsed: {exists}")
    # ?x(P) -> ~!x(~P)
    # P is x=x
    # ~!x(~(x=x))
    print(f"Structure: {exists}")
    
    # 5. Sugars
    print("\nTest 5: P|Q ( (~P)->Q )")
    or_expr = parser.parse("P|Q")
    print(f"Parsed: {or_expr}")
    assert isinstance(or_expr, Implies)
    assert isinstance(or_expr.left, Not)
    
    print("\nTest 6: P&Q ( ~(P->~Q) )")
    and_expr = parser.parse("P&Q")
    print(f"Parsed: {and_expr}")
    assert isinstance(and_expr, Not)
    assert isinstance(and_expr.operand, Implies)
    
    # 7. Complex
    print("\nTest 7: !x( ~!y( ~x=y ) )") # effectively forall x, exists y, x=y
    uniq = parser.parse("!x(~!y(~x=y))")
    print(f"Parsed: {uniq}")
    
    # 8. Math
    print("\nTest 8: S(x)+y = 0")
    math = parser.parse("S(x)+y=0")
    print(f"Parsed: {math}")
    assert str(math) == "(S(x)+y)=0"

if __name__ == "__main__":
    test_parser()
