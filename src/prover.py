import random
from typing import List, Set, Dict, Optional
from syntax import (
    Node, Implies, Forall, NumericVariable, LogicVariable
)
from storage import SentenceStorage
from matcher import Matcher
from inference import ModusPonens, UniversalGeneralization
from parser import Parser

class AutoProver:
    def __init__(self, storage: SentenceStorage):
        self.storage = storage
        self.matcher = Matcher()
        self.mp = ModusPonens(storage)
        self.ug = UniversalGeneralization(storage)
        self.parser = Parser(storage)
        self.guesses: List[Node] = []
        self.history: Set[Node] = set()

    def prove(self, goal_str: str, max_rounds: int = 10):
        try:
            initial_goal = self.parser.parse(goal_str)
        except Exception as e:
            print(f"Parse Error: {e}")
            return False
            
        print(f"Goal: {initial_goal}")
        self.guesses = [initial_goal]
        self.history.add(initial_goal)
        
        for round_num in range(max_rounds):
            print(f"\n--- Round {round_num + 1} ({len(self.guesses)} guesses) ---")
            
            # 1. Check if any guess is proven
            for g in self.guesses:
                if self.storage.is_proven(g):
                    print(f"Success! Proven: {g}")
                    print(f"Provenance: {self.storage.get_provenance(g)}")
                    return True

            next_guesses: List[Node] = []
            
            # 2. Process guesses
            for g in self.guesses:
                # A. Direct Inference Rules Check
                if self._check_inference_rules(g):
                    print(f"Success (Inference)! Proven: {g}")
                    return True
                
                # B. Backward Chaining (Implications)
                # Look for Proven P->Q where unify(Q, g) -> bindings
                # Then we need to prove P[bindings]
                for proven in self.storage.proven.keys():
                    if isinstance(proven, Implies):
                        consequent = proven.right
                        bindings = self.matcher.match(consequent, g)
                        if bindings is not None:
                            # We found A->B and B matches Goal.
                            # We need to prove A (substituted).
                            antecedent = proven.left
                            try:
                                # Apply substitutions to antecedent
                                # Bindings maps "names" to Nodes.
                                needed = antecedent
                                for var_name, replacement in bindings.items():
                                    if hasattr(replacement, 'kind') and replacement.kind == 'numeric':
                                         needed = needed.substitute(var_name, replacement)
                                    # Logic variable substitution? 
                                    # My syntax.substitute only handles numeric vars for now.
                                    # Logic variables need structural replacement?
                                    # Limitation in current `substitute`: logic vars not replaced.
                                    # But match returns logic vars bindings too.
                                    # We need a proper Logic substitution.
                                    pass
                                
                                # Hack: If antecedent was a LogicVariable "A", and we bound "A": "x=0".
                                # Then needed IS "x=0".
                                if isinstance(needed, LogicVariable):
                                    if needed.name in bindings:
                                        needed = bindings[needed.name]
                                
                                needed = self.storage.intern(needed)
                                
                                if needed not in self.history:
                                    print(f"  Guessing {needed} (from {proven})")
                                    next_guesses.append(needed)
                                    self.history.add(needed)
                            except Exception as e:
                                # Substitution failed or unsupported
                                pass
                
                # C. Instantiation Heuristic
                # If goal is P, and P has free vars, try proving !x(P)
                free_vars = g.free_variables
                for v_name in free_vars:
                    # Construct !v(P)
                    # We need the actual variable object.
                    # This is tricky if we don't have it.
                    # We can create a new one with same name?
                    # Or find it in the expression?
                    # Let's recreate
                    v = NumericVariable(v_name) 
                    try:
                        new_goal = self.storage.intern(Forall(v, g))
                        if new_goal not in self.history:
                            print(f"  Guessing {new_goal} (Generalization)")
                            next_guesses.append(new_goal)
                            self.history.add(new_goal)
                    except:
                        pass

            # Pruning / Sampling
            if len(next_guesses) > 1000:
                next_guesses = random.sample(next_guesses, 1000)
                
            # Keep original guesses? User said: "remove it from guesses... if not proven... add next guesses"
            # Basically replacing old batch with new batch?
            # "append them, and do the thing again" -> Accumulate?
            # "iterate over all current guesses... create a list of next... append them".
            # So growing list.
            self.guesses.extend(next_guesses)
            
            # Prune total
            if len(self.guesses) > 2000:
                 self.guesses = self.guesses[:2000]

        print("Max rounds reached. Failed to prove.")
        return False

    def _check_inference_rules(self, goal: Node) -> bool:
        # Modus Ponens Check:
        # Do we have P->Goal proven?
        # This requires searching all proven implications for one ending in Goal.
        for proven in self.storage.proven.keys():
            if isinstance(proven, Implies):
                if proven.right == goal:
                    # Found P->Goal. Is P proven?
                    antecedent = proven.left
                    if self.storage.is_proven(antecedent):
                        # Yes!
                        self.mp.apply(proven, antecedent)
                        return True
        
        # Universal Gen Check:
        # Is goal !x(P)? Is P proven?
        if isinstance(goal, Forall):
             if self.storage.is_proven(goal.sentence):
                 self.ug.apply(goal.sentence, goal.var)
                 return True
                 
        return False
