import random
import traceback
import time
from typing import List, Set, Dict, Optional
from syntax import (
    Node, Implies, Forall, NumericVariable, LogicVariable
)
from storage import SentenceStorage, Provenance
from matcher import Matcher
from inference import ModusPonens, UniversalGeneralization, Substitution
from parser import Parser

class AutoProver:
    # Limits to prevent infinite loops - VERY STRICT for P->P proof
    MAX_NEW_GUESSES_PER_ROUND = 20  # Down from 100
    MAX_TOTAL_GUESSES = 50  # Down from 500
    MAX_GUESSES_PER_IMPLICATION = 3  # Down from 10 - limit guesses per proven implication
    
    def __init__(self, storage: SentenceStorage):
        self.storage = storage
        self.matcher = Matcher()
        self.mp = ModusPonens(storage)
        self.ug = UniversalGeneralization(storage)
        self.subst = Substitution(storage)
        self.parser = Parser(storage)
        self.guesses: List[Node] = []
        self.history: Set[Node] = set()


    def prove(self, goal_str: str, max_rounds: int = 20, timeout: float = 10.0, enable_forward: bool = True, verbose: bool = False):
        """
        Attempt to prove the goal with a timeout failsafe.
        
        Args:
            goal_str: The goal to prove
            max_rounds: Maximum number of proof rounds
            timeout: Maximum time in seconds before stopping (default 10)
            enable_forward: Enable forward reasoning (default True). Set to False for backward-only mode.
            verbose: Print detailed progress information (default False)
        """
        start_time = time.time()
        
        try:
            initial_goal = self.parser.parse(goal_str)
        except Exception as e:
            print(f"Parse Error: {e}")
            return False
            
        print(f"Goal: {initial_goal}")
        if verbose:
            print(f"Timeout: {timeout} seconds")
            print(f"Forward reasoning: {'enabled' if enable_forward else 'disabled (backward-only mode)'}")
        self.guesses = [initial_goal]
        self.history.add(initial_goal)
        
        for round_num in range(max_rounds):
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"\n⏱️  TIMEOUT after {elapsed:.2f} seconds!")
                if verbose:
                    print(f"Stopped at round {round_num + 1} with {len(self.guesses)} guesses")
                return False
                
            if verbose:
                print(f"\n--- Round {round_num + 1} ({len(self.guesses)} guesses) ---")
                print(f"Elapsed: {elapsed:.2f}s")
                print(f"Guesses: {[str(g) for g in self.guesses]}")

            # 1. Check if GOAL is proven
            if self.storage.is_proven(initial_goal):
                print(f"Success! Goal Proven: {initial_goal}")
                if verbose:
                    print(f"Provenance: {self.storage.get_provenance(initial_goal)}")
                return True

            guesses_to_process = list(self.guesses)
            self.guesses = [] 
            
            next_guesses: List[Node] = []
            
            for g in guesses_to_process:
                if self.storage.is_proven(g):
                    continue 

                self.guesses.append(g) # Keep unproven guess
                
                # A. Direct Inference Check for g
                if self._check_inference_rules(g):
                    if verbose:
                        print(f"  Proven (Inference): {g}")
                    if g == initial_goal:
                         print(f"Success! Goal Proven: {initial_goal}")
                         return True
                    continue 

                # A2. Match against Proven Facts (Atomic or Implications) directly
                # If we have proven 'x=x', and goal is '0=0'.
                candidates = list(self.storage.proven.keys())
                # print(f" DEBUG: Checking {len(candidates)} proven facts against {g}")
                for proven in candidates:
                    # print(f"  matching vs {proven}")
                    bindings = self.matcher.match(proven, g)
                    if bindings is not None:
                        # Proven fact matches Goal!
                        # Instantiate it.
                        try:
                            instantiated = self._instantiate(proven, bindings)
                            # Mark proven
                            # Provenance?
                            parent_prov = self.storage.get_provenance(proven)
                            new_prov = Provenance(f"Instance of {parent_prov.method}", dependencies=[proven])
                            self.storage.mark_proven(instantiated, new_prov)
                            if verbose:
                                print(f"  Proven (Match): {instantiated}")
                            if instantiated == initial_goal:
                                print(f"Success! Goal Proven: {initial_goal}")
                                return True
                        except Exception as e:
                            print(f"Error in atom match: {e}")
                            traceback.print_exc()
                            pass

                # B. Backward Strategy: Goal matching Consequent
                candidates = list(self.storage.proven.keys())
                guesses_per_implication: Dict[Node, int] = {}
                
                for proven in candidates:
                    if isinstance(proven, Implies):
                        # Limit guesses per implication to prevent explosion
                        if proven not in guesses_per_implication:
                            guesses_per_implication[proven] = 0
                        if guesses_per_implication[proven] >= self.MAX_GUESSES_PER_IMPLICATION:
                            continue
                            
                        consequent = proven.right
                        bindings = self.matcher.match(consequent, g)
                        if bindings:
                            try:
                                instantiated_imp = self._instantiate(proven, bindings)
                                self.storage.intern(instantiated_imp)
                                # Mark as proven (Schema instance)
                                parent_prov = self.storage.get_provenance(proven)
                                if "Axiom" in parent_prov.method or "Schema" in parent_prov.method:
                                    # Create new provenance
                                    # Note: If proven is L1, prov is "Logic Axiom".
                                    new_prov = Provenance(f"Instance of {parent_prov.method}", dependencies=[proven])
                                    self.storage.mark_proven(instantiated_imp, new_prov)
                                    
                                    antecedent = instantiated_imp.left
                                    if antecedent not in self.history:
                                        if verbose:
                                            print(f"  Guessing {antecedent} (Backward fromImplies {proven})")
                                        next_guesses.append(antecedent)
                                        self.history.add(antecedent)
                                        guesses_per_implication[proven] += 1
                                        
                                elif self.storage.is_proven(proven): 
                                    if not bindings: # This condition seems incorrect, bindings should be used for instantiation
                                        antecedent = proven.left
                                        if antecedent not in self.history:
                                            if verbose:
                                                print(f"  Guessing {antecedent} (Backward fromImplies {proven})")
                                            next_guesses.append(antecedent)
                                            self.history.add(antecedent)
                                            guesses_per_implication[proven] += 1
                            except Exception as e:
                                pass



            # C. Forward Strategy: Pattern matching and substitution (skip if backward-only mode)
            if enable_forward:
                proven_facts = list(self.storage.proven.keys())
                proven_implications = [p for p in proven_facts if isinstance(p, Implies)]
                
                iteration_count = 0
                for imp in proven_implications:
                    for fact in proven_facts:
                        # Periodic timeout check (every 100 iterations to reduce overhead)
                        iteration_count += 1
                        if iteration_count % 100 == 0:
                            elapsed = time.time() - start_time
                            if elapsed > timeout:
                                print(f"\n⏱️  TIMEOUT after {elapsed:.2f} seconds during forward reasoning!")
                                print(f"Stopped after {iteration_count} forward reasoning iterations")
                                return False
                        
                        # Try to match the implication's antecedent against the fact
                        # If imp is P->Q and fact is R, check if there's a substitution S such that P[S] = R
                        bindings = self.matcher.match(imp.left, fact)
                        if bindings is not None:
                            try:
                                # Apply substitution to the entire implication to get P[S]->Q[S]
                                substituted_imp = self.subst.apply(imp, bindings)
                                
                                # Now apply modus ponens: we have P[S]->Q[S] and P[S] (which is fact)
                                # The antecedent should match exactly
                                if substituted_imp.left == fact:
                                    consequent = self.mp.apply(substituted_imp, fact)
                                    if verbose:
                                        print(f"  Forward Derived: {consequent} (from {imp} + {fact})")
                                    if consequent == initial_goal:
                                        print(f"Success! Goal Proven: {initial_goal}")
                                        return True
                                
                            except Exception as e:
                                # Substitution or MP might fail, just continue
                                pass

            # Sample next_guesses with bias towards simpler expressions
            if len(next_guesses) > self.MAX_NEW_GUESSES_PER_ROUND:
                next_guesses = self._sample_by_complexity(next_guesses, self.MAX_NEW_GUESSES_PER_ROUND)
            self.guesses.extend(next_guesses)
            
            # Limit total guesses with bias towards simpler expressions
            if len(self.guesses) > self.MAX_TOTAL_GUESSES:
                self.guesses = self._sample_by_complexity(self.guesses, self.MAX_TOTAL_GUESSES)

        print("Max rounds reached. Failed to prove.")
        return False

    def _expression_complexity(self, node: Node) -> int:
        """Calculate complexity score for an expression (lower is better)"""
        if isinstance(node, (NumericVariable, LogicVariable)):
            return 1
        elif isinstance(node, Implies):
            return 1 + self._expression_complexity(node.left) + self._expression_complexity(node.right)
        elif isinstance(node, Forall):
            return 1 + self._expression_complexity(node.sentence)
        else:
            # For other node types, count recursively if possible
            complexity = 1
            # Try to get children if the node has them
            if hasattr(node, 'left') and hasattr(node, 'right'):
                complexity += self._expression_complexity(node.left)
                complexity += self._expression_complexity(node.right)
            elif hasattr(node, 'sentence'):
                complexity += self._expression_complexity(node.sentence)
            return complexity
    
    def _sample_by_complexity(self, guesses: List[Node], max_count: int) -> List[Node]:
        """Sample guesses, biasing towards simpler expressions"""
        if len(guesses) <= max_count:
            return guesses
        
        # Score all guesses
        scored = [(g, self._expression_complexity(g)) for g in guesses]
        # Sort by complexity (lower is better)
        scored.sort(key=lambda x: x[1])
        
        # Take the simplest ones
        return [g for g, _ in scored[:max_count]]
    
    def _instantiate(self, node: Node, bindings: Dict[str, Node]) -> Node:
        # Helper to perform potentially multiple substitutions
        # This is simple sequential substitution.
        # Ideally simultaneous?
        # For our L1-L3 schemas, vars are distinct.
        current = node
        for name, repl in bindings.items():
            current = current.substitute(name, repl)
        return self.storage.intern(current)
            
    def _check_inference_rules(self, goal: Node) -> bool:
        # Modus Ponens Check:
        # Do we have P->Goal proven?
        for proven in self.storage.proven.keys():
            if isinstance(proven, Implies):
                if proven.right == goal:
                    antecedent = proven.left
                    if self.storage.is_proven(antecedent):
                        self.mp.apply(proven, antecedent)
                        return True
        
        # Universal Gen Check:
        if isinstance(goal, Forall):
             if self.storage.is_proven(goal.sentence):
                 self.ug.apply(goal.sentence, goal.var)
                 return True
                 
        return False
