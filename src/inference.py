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
