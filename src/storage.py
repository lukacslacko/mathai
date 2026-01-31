import pickle
import os
from typing import Optional
from syntax import Node

class Provenance:
    def __init__(self, method: str, dependencies: list[Node] = None, metadata: dict = None):
        self.method = method
        self.dependencies = dependencies if dependencies is not None else []
        self.metadata = metadata if metadata is not None else {}
    
    def __str__(self):
        deps = ", ".join(str(d) for d in self.dependencies)
        meta = ", ".join(f"{k}={v}" for k, v in self.metadata.items())
        parts = []
        if deps: parts.append(deps)
        if meta: parts.append(meta)
        content = ", ".join(parts)
        return f"{self.method}({content})" if content else self.method

class SentenceStorage:
    def __init__(self):
        self.nodes: dict[Node, Node] = {} # Map object to canonical object (hash consing)
        self.proven: dict[Node, Provenance] = {}

    def intern(self, node: Node) -> Node:
        """
        Returns the canonical version of the node. 
        """
        if node in self.nodes:
            return self.nodes[node]
        self.nodes[node] = node
        return node
    
    def mark_proven(self, node: Node, provenance: Provenance):
        """Marks a node as proven with a specific reason. Ensure node is canonical first."""
        canonical = self.intern(node)
        if canonical in self.proven:
            # Already proven. In future we might want to store multiple proofs?
            # For now, first proof wins or we ignore.
            return
        self.proven[canonical] = provenance
    
    def get_provenance(self, node: Node) -> Optional[Provenance]:
        return self.proven.get(node)

    def is_proven(self, node: Node) -> bool:
        return node in self.proven

    def save(self, filepath: str):
        """Saves the entire storage to a file."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'nodes': self.nodes,
                'proven': self.proven
            }, f)
        print(f"Storage saved to {filepath} with {len(self.nodes)} expressions ({len(self.proven)} proven).")

    @classmethod
    def load(cls, filepath: str) -> 'SentenceStorage':
        """Loads storage from a file."""
        if not os.path.exists(filepath):
            return cls()
        
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        storage = cls()
        storage.nodes = data.get('nodes', {})
        
        # Backward compatibility or migrate if structure changed drastically
        # Assuming we just wiped DB or compatible since we control it.
        # But let's handle the set->dict migration if user kept old DB file
        loaded_proven = data.get('proven', {})
        if isinstance(loaded_proven, set):
            print("Migrating legacy 'proven' set to dict...")
            storage.proven = {node: Provenance("Legacy Axiom") for node in loaded_proven}
        else:
            storage.proven = loaded_proven
            
        print(f"Storage loaded from {filepath} with {len(storage.nodes)} expressions ({len(storage.proven)} proven).")
        return storage
