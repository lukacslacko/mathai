from syntax import Implies, Forall, NumericVariable, LogicExpression
from storage import SentenceStorage, Provenance

class ModusPonens:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage

    def apply(self, implication: Implies, antecedent: LogicExpression):
        """
        If (P->Q) is proven and P is proven, then Q is proven.
        """
        # Checks
        if not isinstance(implication, Implies):
            raise TypeError(f"First argument must be an Implies expression, got {type(implication)}")
        
        # Intern them to be safe/canonical
        implication = self.storage.intern(implication)
        antecedent = self.storage.intern(antecedent)
        
        if implication.left != antecedent:
            raise ValueError(f"Antecedent {antecedent} does not match LHS of implication {implication}")
            
        if not self.storage.is_proven(implication):
             raise ValueError(f"Implication {implication} is not proven.")
             
        if not self.storage.is_proven(antecedent):
             raise ValueError(f"Antecedent {antecedent} is not proven.")
             
        consequent = implication.right
        
        # Mark Proven
        provenance = Provenance("Modus Ponens", dependencies=[implication, antecedent])
        self.storage.mark_proven(consequent, provenance)
        return consequent

class UniversalGeneralization:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage

    def apply(self, sentence: LogicExpression, var: NumericVariable):
        """
        If P is proven, then forall x (P) is proven.
        """
        sentence = self.storage.intern(sentence)
        
        if not self.storage.is_proven(sentence):
            raise ValueError(f"Sentence {sentence} is not proven.")
            
        quantified = self.storage.intern(Forall(var, sentence))
        
        provenance = Provenance("Universal Generalization", dependencies=[sentence], metadata={
            "var": var
        })
        self.storage.mark_proven(quantified, provenance)
        return quantified

class Substitution:
    """
    Substitution inference rule: If expression E is proven, then E[S] is also proven
    for any substitution S (mapping of variables to expressions).
    """
    def __init__(self, storage: SentenceStorage):
        self.storage = storage
    
    def _substitute(self, node, bindings):
        """Recursively apply substitutions to a node."""
        from syntax import (
            Node, NumericVariable, LogicVariable, Zero, Successor,
            Add, Multiply, Equals, Not, Implies, Forall
        )
        
        # If node is a variable, replace it if there's a binding
        if isinstance(node, (NumericVariable, LogicVariable)):
            if node.name in bindings:
                return bindings[node.name]
            return node
        
        # Recursively substitute in compound expressions
        if isinstance(node, Zero):
            return node
        elif isinstance(node, Successor):
            return self.storage.intern(Successor(self._substitute(node.operand, bindings)))
        elif isinstance(node, Add):
            return self.storage.intern(Add(
                self._substitute(node.left, bindings),
                self._substitute(node.right, bindings)
            ))
        elif isinstance(node, Multiply):
            return self.storage.intern(Multiply(
                self._substitute(node.left, bindings),
                self._substitute(node.right, bindings)
            ))
        elif isinstance(node, Equals):
            return self.storage.intern(Equals(
                self._substitute(node.left, bindings),
                self._substitute(node.right, bindings)
            ))
        elif isinstance(node, Not):
            return self.storage.intern(Not(self._substitute(node.operand, bindings)))
        elif isinstance(node, Implies):
            return self.storage.intern(Implies(
                self._substitute(node.left, bindings),
                self._substitute(node.right, bindings)
            ))
        elif isinstance(node, Forall):
            # Don't substitute the bound variable
            return self.storage.intern(Forall(
                node.var,
                self._substitute(node.sentence, bindings)
            ))
        else:
            return node
    
    def apply(self, expression, bindings):
        """
        If expression is proven, return expression with bindings applied.
        bindings: dict mapping variable names (str) to Node objects
        """
        expression = self.storage.intern(expression)
        
        if not self.storage.is_proven(expression):
            raise ValueError(f"Expression {expression} is not proven.")
        
        # Apply substitution
        substituted = self._substitute(expression, bindings)
        
        # Mark as proven
        provenance = Provenance("Substitution", dependencies=[expression], metadata={
            "bindings": {k: str(v) for k, v in bindings.items()}
        })
        self.storage.mark_proven(substituted, provenance)
        return substituted
