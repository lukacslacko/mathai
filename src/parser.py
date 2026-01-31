import re
from typing import List, Optional
from syntax import (
    Node, NumericVariable, LogicVariable, Zero, Successor,
    Add, Multiply, Equals, Not, Implies, Forall,
    NumericExpression, LogicExpression
)
from storage import SentenceStorage

class Tokenizer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if self.text else None
        
    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
            
    def peek(self):
        if self.pos + 1 < len(self.text):
            return self.text[self.pos + 1]
        return None

class Parser:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage
        self.tokenizer = None
        
    def parse(self, text: str) -> Node:
        self.tokenizer = Tokenizer(text)
        node = self.parse_logic()
        return self.storage.intern(node)

    # Precedence levels (Logic):
    # 1. Implication (->), OR (|), AND (&)   (Lowest)  NOTE: User defined sugars for | and &
    # 2. Negation (~), Quantifiers (!, ?)
    # 3. Equality (=)
    # 4. Numeric Terms (Add, Mul)
    
    # Actually, & and | bind tighter than -> usually.
    # Level 1: ->
    # Level 2: |
    # Level 3: &
    # Level 4: ~ ! ?
    # Level 5: =
    # Level 6: +
    # Level 7: *
    # Level 8: S, 0, ( ), var
    
    def parse_logic(self) -> Node:
        # Handles Implication
        left = self.parse_or()
        
        self.tokenizer.skip_whitespace()
        # Check for ->
        if self.tokenizer.current_char == '-' and self.tokenizer.peek() == '>':
            self.tokenizer.advance() # -
            self.tokenizer.advance() # >
            right = self.parse_logic() # Right associative? A->B->C is A->(B->C)
            return Implies(left, right)
            
        return left

    def parse_or(self) -> Node:
        left = self.parse_and()
        
        while self.tokenizer.current_char == '|':
            self.tokenizer.advance()
            right = self.parse_and()
            # P|Q is (~P)->Q
            left = Implies(Not(left), right)
            
        return left

    def parse_and(self) -> Node:
        left = self.parse_unary_logic()
        
        while self.tokenizer.current_char == '&':
            self.tokenizer.advance()
            right = self.parse_unary_logic()
            # P&Q is ~(P->~Q)
            left = Not(Implies(left, Not(right)))
            
        return left

    def parse_unary_logic(self) -> Node:
        self.tokenizer.skip_whitespace()
        char = self.tokenizer.current_char
        
        if char == '~':
            self.tokenizer.advance()
            # No parens required after ~, so recurse immediately
            operand = self.parse_unary_logic()
            return Not(operand)
            
        if char == '!': # Forall
            self.tokenizer.advance()
            var_name = self.parse_var_name()
            # Expect ( maybe? Or just logic expr?
            # User said !x(P). usually parens surround P
            if self.tokenizer.current_char == '(':
                # We usually expect parens for the body or just a body
                # Let's try to parse logic
                pass
            
            # The body follows.
            body = self.parse_unary_logic() # Tighter binding? or parse_logic?
            # !x(P) -> P is usually in parens.
            # If user writes !x~P -> P, it's (!x(~P)) -> P.
            # Let's assume ! binds tight to the immediate next unit.
            
            var = NumericVariable(var_name) # Assuming numeric quantification mostly
            return Forall(var, body)
            
        if char == '?': # Exists
            self.tokenizer.advance()
            var_name = self.parse_var_name()
            # ?x(P) is ~!x(~P)
            body = self.parse_unary_logic()
            
            var = NumericVariable(var_name)
            # ~!x(~body)
            return Not(Forall(var, Not(body)))
            
        # Try numeric equality or parens logic
        return self.parse_equality()

    def parse_equality(self) -> Node:
        left = self.parse_numeric()
        
        self.tokenizer.skip_whitespace()
        if self.tokenizer.current_char == '=':
            self.tokenizer.advance()
            right = self.parse_numeric()
            return Equals(left, right)
            
        # If no =, then 'left' must have been a Logic Expression disguised?
        # Or maybe it's a Logic Variable?
        # But parse_numeric parses numeric terms.
        # This assumes strictly typed context.
        # If 'left' turned out to be a Variable, it could be LogicVariable or NumericVariable.
        # But we constructed it via parse_numeric which yields NumericExpressions.
        # Wait, if we have logic variables (P, Q), they are leaves logic.
        
        # Issue: Logic Variables vs Numeric Variables.
        # Simple heuristic: Uppercase = Logic, Lowercase = Numeric?
        # Or mixed. "P" is logic var. "x" is numeric.
        # My parse_numeric assumes it returns NumericExpression.
        # If I want to support Logic Variables like 'P', I need to check here.
        
        if isinstance(left, NumericVariable) and left.name[0].isupper():
            # Treat Uppercase vars as Logic Variables for now?
            # User example P, Q.
            # Convert
            return LogicVariable(left.name)
            
        if isinstance(left, NumericExpression) and not isinstance(left, (NumericVariable, Zero, Successor, Add, Multiply)):
             pass
        
        # If we just parsed a logic variable 'P' inside parse_numeric (thinking it was numeric var),
        # we cast it. But if it was "P->Q", parse_logic called parse_or -> parse_and -> parse_unary -> parse_equality -> parse_numeric.
        # parse_numeric reads 'P'.
        # Returns NumericVariable('P').
        # Then we see ->.
        # So 'P' implies ...
        # Correct approach: try to reinterpret 'left' if valid.
        
        if isinstance(left, NumericVariable):
             # Heuristic: if it's acting as logic sentence, upgrade it.
             # User examples: P, Q.
             return LogicVariable(left.name)

        return left 

    def parse_numeric(self) -> NumericExpression:
        left = self.parse_add()
        return left

    def parse_add(self) -> NumericExpression:
        left = self.parse_mul()
        
        while self.tokenizer.current_char == '+':
            self.tokenizer.advance()
            right = self.parse_mul()
            left = Add(left, right)
        return left
        
    def parse_mul(self) -> NumericExpression:
        left = self.parse_term()
        
        while self.tokenizer.current_char == '*':
            self.tokenizer.advance()
            right = self.parse_term()
            left = Multiply(left, right)
        return left

    def parse_term(self) -> NumericExpression:
        self.tokenizer.skip_whitespace()
        c = self.tokenizer.current_char
        
        if c == '0':
            self.tokenizer.advance()
            return Zero()
            
        if c == 'S':
            # S(x)
            self.tokenizer.advance()
            if self.tokenizer.current_char == '(':
                self.tokenizer.advance()
                inner = self.parse_numeric()
                if self.tokenizer.current_char == ')':
                    self.tokenizer.advance()
                    return Successor(inner)
            raise ValueError("Expected ( after S")
            
        if c == '(':
            self.tokenizer.advance()
            # This could be (Numeric) or (Logic)?
            # Context matters. We are in parse_term (Numeric).
            # But what if it's (P->Q)?
            # This parser is simple LL(1).
            # Let's try parsing as Logic first? No, logic includes numeric.
            # Try numeric.
            
            expr = self.parse_logic() # Top level
            
            if self.tokenizer.current_char == ')':
                self.tokenizer.advance()
                return expr
            raise ValueError("Expected )")
            
        if c is not None and c.isalnum():
            name = self.parse_var_name()
            return NumericVariable(name)
            
        raise ValueError(f"Unexpected char in numeric: {c}")

    def parse_var_name(self) -> str:
        res = []
        while self.tokenizer.current_char is not None and self.tokenizer.current_char.isalnum():
            res.append(self.tokenizer.current_char)
            self.tokenizer.advance()
        return "".join(res)
