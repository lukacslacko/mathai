from abc import ABC, abstractmethod
from typing import Union, List, Set

class Node(ABC):
    """Base class for all sentences in the system."""
    @abstractmethod
    def __str__(self):
        pass

    @property
    @abstractmethod
    def kind(self):
        """Returns 'numeric' or 'logic'."""
        pass
    
    @abstractmethod
    def _key(self):
        """Returns a tuple characterizing the node for equality and hashing."""
        pass
    
    @property
    @abstractmethod
    def free_variables(self) -> Set[str]:
        """Returns a set of variable names that are free in this expression."""
        pass

    @abstractmethod
    def substitute(self, var_name: str, replacement: 'NumericExpression') -> 'Node':
        """
        Returns a new Node with free occurrences of var_name replaced by replacement.
        Must be implemented by subclasses.
        """
        pass

    def __hash__(self):
        return hash((self.__class__, self._key()))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._key() == other._key()

# --- Kinds ---

class NumericExpression(Node):
    @property
    def kind(self):
        return 'numeric'

class LogicExpression(Node):
    @property
    def kind(self):
        return 'logic'

# --- Leaves ---

class Zero(NumericExpression):
    def __init__(self):
        pass
    
    def __str__(self):
        return "0"

    def _key(self):
        return ()

    @property
    def free_variables(self) -> Set[str]:
        return set()

    def substitute(self, var_name: str, replacement: NumericExpression) -> Node:
        return self

class Variable(Node):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name
    
    def _key(self):
        return (self.name,)

    @property
    def free_variables(self) -> Set[str]:
        return {self.name}

class NumericVariable(Variable, NumericExpression):
    def substitute(self, var_name: str, replacement: NumericExpression) -> Node:
        if self.name == var_name:
            return replacement
        return self

class LogicVariable(Variable, LogicExpression):
    def substitute(self, var_name: str, replacement: Node) -> Node:
        if self.name == var_name:
            return replacement
        return self

# --- Combinations: Numeric -> Logic ---

class Equals(LogicExpression):
    def __init__(self, left: NumericExpression, right: NumericExpression):
        if not isinstance(left, NumericExpression) or not isinstance(right, NumericExpression):
            raise TypeError("Equals takes two numeric expressions.")
        self.left = left
        self.right = right

    def __str__(self):
        return f"{self.left}={self.right}"

    def _key(self):
        return (self.left, self.right)

    @property
    def free_variables(self) -> Set[str]:
        return self.left.free_variables.union(self.right.free_variables)

    def substitute(self, var_name: str, replacement: NumericExpression) -> Node:
        return Equals(
            self.left.substitute(var_name, replacement), 
            self.right.substitute(var_name, replacement)
        )

# --- Combinations: Logic -> Logic ---

class Not(LogicExpression):
    def __init__(self, operand: LogicExpression):
        if not isinstance(operand, LogicExpression):
            raise TypeError("Not takes a logic expression.")
        self.operand = operand

    def __str__(self):
        return f"¬{self.operand}"

    def _key(self):
        return (self.operand,)

    @property
    def free_variables(self) -> Set[str]:
        return self.operand.free_variables

    def substitute(self, var_name: str, replacement: NumericExpression) -> Node:
        return Not(self.operand.substitute(var_name, replacement))

class Implies(LogicExpression):
    def __init__(self, left: LogicExpression, right: LogicExpression):
        if not isinstance(left, LogicExpression) or not isinstance(right, LogicExpression):
            raise TypeError("Implies takes two logic expressions.")
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left}→{self.right})"

    def _key(self):
        return (self.left, self.right)
    
    @property
    def free_variables(self) -> Set[str]:
        return self.left.free_variables.union(self.right.free_variables)

    def substitute(self, var_name: str, replacement: NumericExpression) -> Node:
        return Implies(
            self.left.substitute(var_name, replacement),
            self.right.substitute(var_name, replacement)
        )

class Forall(LogicExpression):
    def __init__(self, var: NumericVariable, sentence: LogicExpression):
        if not isinstance(var, NumericVariable):
            raise TypeError("Forall expects a numeric variable.")
        if not isinstance(sentence, LogicExpression):
            raise TypeError("Forall expects a logic sentence body.")
        self.var = var
        self.sentence = sentence

    def __str__(self):
        return f"∀{self.var}({self.sentence})"

    def _key(self):
        return (self.var, self.sentence)
    
    @property
    def free_variables(self) -> Set[str]:
        return self.sentence.free_variables - {self.var.name}

    def substitute(self, var_name: str, replacement: NumericExpression) -> Node:
        if self.var.name == var_name:
            # Variable is shadowed/bound here, don't substitute inside
            return self
        return Forall(
            self.var,
            self.sentence.substitute(var_name, replacement)
        )

# --- Combinations: Numeric -> Numeric ---

class Successor(NumericExpression):
    def __init__(self, operand: NumericExpression):
        if not isinstance(operand, NumericExpression):
            raise TypeError("Successor takes a numeric expression.")
        self.operand = operand

    def __str__(self):
        return f"S({self.operand})"

    def _key(self):
        return (self.operand,)

    @property
    def free_variables(self) -> Set[str]:
        return self.operand.free_variables

    def substitute(self, var_name: str, replacement: NumericExpression) -> Node:
        return Successor(self.operand.substitute(var_name, replacement))

class Add(NumericExpression):
    def __init__(self, left: NumericExpression, right: NumericExpression):
        if not isinstance(left, NumericExpression) or not isinstance(right, NumericExpression):
            raise TypeError("Add takes two numeric expressions.")
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left}+{self.right})"

    def _key(self):
        return (self.left, self.right)

    @property
    def free_variables(self) -> Set[str]:
        return self.left.free_variables.union(self.right.free_variables)

    def substitute(self, var_name: str, replacement: NumericExpression) -> Node:
        return Add(
            self.left.substitute(var_name, replacement),
            self.right.substitute(var_name, replacement)
        )

class Multiply(NumericExpression):
    def __init__(self, left: NumericExpression, right: NumericExpression):
        if not isinstance(left, NumericExpression) or not isinstance(right, NumericExpression):
            raise TypeError("Multiply takes two numeric expressions.")
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left}*{self.right})"

    def _key(self):
        return (self.left, self.right)

    @property
    def free_variables(self) -> Set[str]:
        return self.left.free_variables.union(self.right.free_variables)

    def substitute(self, var_name: str, replacement: NumericExpression) -> Node:
        return Multiply(
            self.left.substitute(var_name, replacement),
            self.right.substitute(var_name, replacement)
        )
