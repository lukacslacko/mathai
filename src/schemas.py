from syntax import (
    NumericVariable, LogicExpression, NumericExpression,
    Implies, Forall, Successor, Zero, Equals,
)
from storage import SentenceStorage, Provenance
import copy

class InductionSchema:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage

    def apply(self, var: NumericVariable, predicate: LogicExpression):
        """
        Generates the induction axiom for a given variable and predicate P.
        P[x/0] -> (forall x (P -> P[x/S(x)])) -> forall x P
        """
        # Ensure inputs are interned/valid
        # Note: predicate should structurally be a valid LogicExpression
        
        # P[x/0]
        base_case_expr = predicate.substitute(var.name, Zero())
        base_case = self.storage.intern(base_case_expr)
        
        # P[x/S(x)]
        succ_x = Successor(var)
        inductive_step_expr = predicate.substitute(var.name, succ_x)
        
        # P -> P[x/S(x)]
        inductive_implication = self.storage.intern(Implies(predicate, inductive_step_expr))
        
        # forall x (P -> P[x/S(x)])
        quantified_step = self.storage.intern(Forall(var, inductive_implication))
        
        # forall x P
        conclusion = self.storage.intern(Forall(var, predicate))
        
        # (forall x (P -> ...)) -> forall x P
        step_to_conclusion = self.storage.intern(Implies(quantified_step, conclusion))
        
        # Final Axiom
        axiom = self.storage.intern(Implies(base_case, step_to_conclusion))
        
        # Register Provenance
        provenance = Provenance("Induction Schema", dependencies=[], metadata={
            "var": var,
            "predicate": predicate
        })
        
        self.storage.mark_proven(axiom, provenance)
        return axiom

class InstantiationSchema:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage

    def apply(self, var: NumericVariable, predicate: LogicExpression, replacement: NumericExpression):
        """
        forall x (P) -> P[x/e]
        """
        if not isinstance(replacement, NumericExpression):
             raise TypeError(f"Replacement must be numeric, got {replacement}")
             
        # forall x (P)
        quantified = self.storage.intern(Forall(var, predicate))
        
        # P[x/e]
        substituted_expr = predicate.substitute(var.name, replacement)
        substituted = self.storage.intern(substituted_expr)
        
        # Axiom
        axiom = self.storage.intern(Implies(quantified, substituted))
        
        provenance = Provenance("Instantiation Schema", dependencies=[], metadata={
            "var": var,
            "predicate": predicate,
            "replacement": replacement
        })
        self.storage.mark_proven(axiom, provenance)
        return axiom

class VacuousGeneralizationSchema:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage

    def apply(self, var: NumericVariable, predicate: LogicExpression):
        """
        P -> forall x (P), if x is not free in P.
        """
        if var.name in predicate.free_variables:
            raise ValueError(f"Variable {var.name} is free in P, cannot apply Vacuous Generalization.")
        
        # forall x (P)
        quantified = self.storage.intern(Forall(var, predicate))
        
        # P -> forall x (P)
        axiom = self.storage.intern(Implies(predicate, quantified))
        
        provenance = Provenance("Vacuous Generalization Schema", dependencies=[], metadata={
            "var": var,
            "predicate": predicate
        })
        self.storage.mark_proven(axiom, provenance)
        return axiom

class DistributionSchema:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage

    def apply(self, var: NumericVariable, P: LogicExpression, Q: LogicExpression):
        """
        forall x(P->Q) -> (forall x(P) -> forall x(Q))
        """
        # forall x(P->Q)
        p_implies_q = self.storage.intern(Implies(P, Q))
        quantified_implication = self.storage.intern(Forall(var, p_implies_q))
        
        # forall x(P) -> forall x(Q)
        forall_p = self.storage.intern(Forall(var, P))
        forall_q = self.storage.intern(Forall(var, Q))
        conclusion = self.storage.intern(Implies(forall_p, forall_q))
        
        # Axiom
        axiom = self.storage.intern(Implies(quantified_implication, conclusion))
        
        provenance = Provenance("Distribution Schema", dependencies=[], metadata={
            "var": var,
            "P": P,
            "Q": Q
        })
        self.storage.mark_proven(axiom, provenance)
        return axiom

class IndiscernabilitySchema:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage

    def apply(self, x: NumericVariable, y: NumericVariable, P: LogicExpression):
        """
        x=y -> P -> P[x/y]
        """
        # x=y
        eq = self.storage.intern(Equals(x, y))
        
        # P[x/y]
        substituted_expr = P.substitute(x.name, y)
        substituted = self.storage.intern(substituted_expr)
        
        # P -> P[x/y]
        implication = self.storage.intern(Implies(P, substituted))
        
        # Axiom
        axiom = self.storage.intern(Implies(eq, implication))
        
        provenance = Provenance("Indiscernability Schema", dependencies=[], metadata={
            "x": x,
            "y": y,
            "P": P
        })
        self.storage.mark_proven(axiom, provenance)
        return axiom

class InstantiationSchema:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage

    def apply(self, var: NumericVariable, predicate: LogicExpression, replacement: NumericExpression):
        """
        forall x (P) -> P[x/e]
        """
        if not isinstance(replacement, NumericExpression):
             raise TypeError(f"Replacement must be numeric, got {replacement}")
             
        # forall x (P)
        quantified = self.storage.intern(Forall(var, predicate))
        
        # P[x/e]
        substituted_expr = predicate.substitute(var.name, replacement)
        substituted = self.storage.intern(substituted_expr)
        
        # Axiom
        axiom = self.storage.intern(Implies(quantified, substituted))
        
        provenance = Provenance("Instantiation Schema", dependencies=[], metadata={
            "var": str(var),
            "predicate": str(predicate),
            "replacement": str(replacement)
        })
        self.storage.mark_proven(axiom, provenance)
        return axiom

class VacuousGeneralizationSchema:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage

    def apply(self, var: NumericVariable, predicate: LogicExpression):
        """
        P -> forall x (P), if x is not free in P.
        """
        if var.name in predicate.free_variables:
            raise ValueError(f"Variable {var.name} is free in P, cannot apply Vacuous Generalization.")
        
        # forall x (P)
        quantified = self.storage.intern(Forall(var, predicate))
        
        # P -> forall x (P)
        axiom = self.storage.intern(Implies(predicate, quantified))
        
        provenance = Provenance("Vacuous Generalization Schema", dependencies=[], metadata={
            "var": str(var),
            "predicate": str(predicate)
        })
        self.storage.mark_proven(axiom, provenance)
        return axiom

class DistributionSchema:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage

    def apply(self, var: NumericVariable, P: LogicExpression, Q: LogicExpression):
        """
        forall x(P->Q) -> (forall x(P) -> forall x(Q))
        """
        # forall x(P->Q)
        p_implies_q = self.storage.intern(Implies(P, Q))
        quantified_implication = self.storage.intern(Forall(var, p_implies_q))
        
        # forall x(P) -> forall x(Q)
        forall_p = self.storage.intern(Forall(var, P))
        forall_q = self.storage.intern(Forall(var, Q))
        conclusion = self.storage.intern(Implies(forall_p, forall_q))
        
        # Axiom
        axiom = self.storage.intern(Implies(quantified_implication, conclusion))
        
        provenance = Provenance("Distribution Schema", dependencies=[], metadata={
            "var": str(var),
            "P": str(P),
            "Q": str(Q)
        })
        self.storage.mark_proven(axiom, provenance)
        return axiom

class IndiscernabilitySchema:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage

    def apply(self, x: NumericVariable, y: NumericVariable, P: LogicExpression):
        """
        x=y -> P -> P[x/y]
        """
        # x=y
        eq = self.storage.intern(Equals(x, y))
        
        # P[x/y]
        substituted_expr = P.substitute(x.name, y)
        substituted = self.storage.intern(substituted_expr)
        
        # P -> P[x/y]
        implication = self.storage.intern(Implies(P, substituted))
        
        # Axiom
        axiom = self.storage.intern(Implies(eq, implication))
        
        provenance = Provenance("Indiscernability Schema", dependencies=[], metadata={
            "x": str(x),
            "y": str(y),
            "P": str(P)
        })
        self.storage.mark_proven(axiom, provenance)
        return axiom
