import sys
import os
from typing import Set, List, Dict

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from storage import SentenceStorage, Provenance
from parser import Parser
from syntax import Node

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

def topological_sort(target: Node, storage: SentenceStorage) -> List[Node]:
    """
    Returns a list of nodes in topological order (dependencies first)
    that are required to prove the target node.
    """
    visited: Set[Node] = set()
    sorted_nodes: List[Node] = []

    def visit(node: Node):
        if node in visited:
            return
        visited.add(node)
        
        # Provenance dependencies must be visited first
        prov = storage.get_provenance(node)
        if prov:
            for dep in prov.dependencies:
                visit(dep)
        
        sorted_nodes.append(node)

    if not storage.is_proven(target):
        return []

    visit(target)
    return sorted_nodes

def explain(target_str: str):
    storage = SentenceStorage.load(DB_PATH)
    parser = Parser(storage)
    
    try:
        target = parser.parse(target_str)
    except Exception as e:
        print(f"Error parsing goal: {e}")
        return

    target = storage.intern(target) # Ensure we have the canonical object
    
    if not storage.is_proven(target):
        print(f"Sentence '{target}' is NOT proven in the current database.")
        print("Try running 'python scripts/prove.py' first.")
        return

    print(f"Proof Explanation for: {target}\n")
    
    # Get relevant subset in order
    steps = topological_sort(target, storage)
    
    # Print logic
    # We want to number them similar to a latex proof
    # 1. P (Reason)
    
    # Map node to step number for referencing
    step_map: Dict[Node, int] = {}
    
    for i, node in enumerate(steps):
        step_num = i + 1
        step_map[node] = step_num
        
        prov = storage.get_provenance(node)
        if not prov:
            # Should not happen if topological sort checked is_proven, 
            # unless it's a premise added manually without provenance? 
            # Or maybe an unproven leaf if we traversed unproven things (we shouldn't have).
            reason = "Unknown Origin"
        else:
            # Format dependencies as step numbers
            dep_refs = []
            for dep in prov.dependencies:
                if dep in step_map:
                    dep_refs.append(f"#{step_map[dep]}")
                else:
                    dep_refs.append(str(dep)) # Fallback
            
            # Format metadata
            meta_str = ""
            if prov.metadata:
                # Format clearly: {x=0}
                # If values are Nodes, they might be long strings.
                formatted_meta = []
                for k, v in prov.metadata.items():
                    # If v is a node, maybe just print it? 
                    formatted_meta.append(f"{k}: {v}")
                meta_str = f" [{', '.join(formatted_meta)}]"

            reason = f"{prov.method}"
            if dep_refs:
                reason += f" using {', '.join(dep_refs)}"
            if meta_str:
                reason += meta_str
        
        print(f"{step_num}. {node}")
        print(f"   Reason: {reason}")
        print()

def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
        explain(target)
    else:
        print("Usage: python scripts/explain.py '<theorem_string>'")

if __name__ == "__main__":
    main()
