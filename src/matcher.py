from typing import Dict, Optional, Any
from syntax import (
    Node, NumericVariable, LogicVariable,
    NumericExpression, LogicExpression,
    Equals, Not, Implies, Forall,
    Zero, Successor, Add, Multiply
)

class Matcher:
    def __init__(self):
        pass

    def match(self, pattern: Node, target: Node) -> Optional[Dict[str, Node]]:
        """
        Attempts to match 'target' against 'pattern'.
        Pattern may contain Variables that act as placeholders.
        Returns a dictionary mapping pattern variable names to target sub-expressions.
        Returns None if match fails.
        """
        bindings: Dict[str, Node] = {}
        if self._recursive_match(pattern, target, bindings):
            return bindings
        return None

    def _recursive_match(self, p: Node, t: Node, bindings: Dict[str, Node]) -> bool:
        # print(f"DEBUG Match: {p} ({type(p).__name__}) vs {t} ({type(t).__name__})")
        # If pattern is a variable, check binding consistency
        if isinstance(p, (NumericVariable, LogicVariable)):
            name = p.name
            if name in bindings:
                # Must match previous binding
                if bindings[name] != t:
                    # print(f"  Fail: Binding mismatch {name} -> {bindings[name]} vs {t}")
                    return False
                return True
            else:
                # New binding
                # Constraint: NumericVariable pattern can only match NumericExpression target
                if isinstance(p, NumericVariable) and not isinstance(t, NumericExpression):
                    # print(f"  Fail: Type mismatch NumVar vs {type(t)}")
                    return False
                # LogicVariable can match ANY LogicExpression (including compound formulas)
                # This enables axiom schema instantiation: A, B, C can be replaced with any formula
                if isinstance(p, LogicVariable) and not isinstance(t, LogicExpression):
                    # print(f"  Fail: Type mismatch LogicVar vs {type(t)}")
                    return False
                
                bindings[name] = t
                return True

        # If types differ (and not a variable pattern), fail
        if type(p) != type(t):
            # print(f"  Fail: Type mismatch {type(p)} != {type(t)}")
            return False

        # Structural recursion
        if isinstance(p, Zero):
            return True # t is Zero (checked by type)

        if isinstance(p, Successor):
            return self._recursive_match(p.operand, t.operand, bindings)

        if isinstance(p, (Add, Multiply, Equals, Implies)):
            if not self._recursive_match(p.left, t.left, bindings): return False
            return self._recursive_match(p.right, t.right, bindings)

        if isinstance(p, Not):
            return self._recursive_match(p.operand, t.operand, bindings)

        if isinstance(p, Forall):
            if not self._recursive_match(p.var, t.var, bindings): return False
            return self._recursive_match(p.sentence, t.sentence, bindings)
            
        return False
