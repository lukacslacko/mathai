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
        # If pattern is a variable, check binding consistency
        if isinstance(p, (NumericVariable, LogicVariable)):
            name = p.name
            if name in bindings:
                # Must match previous binding
                return bindings[name] == t # Relies on __eq__ (structural equality)
            else:
                # New binding
                # Constraint: NumericVariable pattern can only match NumericExpression target
                if isinstance(p, NumericVariable) and not isinstance(t, NumericExpression):
                    return False
                if isinstance(p, LogicVariable) and not isinstance(t, LogicExpression):
                    # But LogicVariable might match a LogicExpression? 
                    # Yes, "P" template matches "A=B".
                    if not isinstance(t, LogicExpression):
                         return False
                
                bindings[name] = t
                return True

        # If types differ (and not a variable pattern), fail
        if type(p) != type(t):
            return False

        # Structural recursion
        if isinstance(p, Zero):
            return True # t is Zero (checked by type)

        if isinstance(p, Successor):
            return self._recursive_match(p.operand, t.operand, bindings)

        if isinstance(p, (Add, Multiply, Equals, Implies)):
            return (self._recursive_match(p.left, t.left, bindings) and
                    self._recursive_match(p.right, t.right, bindings))

        if isinstance(p, Not):
            return self._recursive_match(p.operand, t.operand, bindings)

        if isinstance(p, Forall):
            # !x(P) matching !y(Q)
            # This is tricky: Bound variables.
            # If pattern is !x(P[x]) and target is !y(Q[y]).
            # We match x to y? Or do we treat x as a placeholder?
            
            # Simple approach: Pattern variable `x` must essentially map to `y`.
            # But `x` is a NumericVariable in the pattern.
            # If we simply bind "x" -> "y" (NumericVariable), then recurse...
            
            # check the var match 
            if not self._recursive_match(p.var, t.var, bindings):
                return False
                
            # Then body
            return self._recursive_match(p.sentence, t.sentence, bindings)
            
        return False
