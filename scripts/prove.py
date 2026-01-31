import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from storage import SentenceStorage
from prover import AutoProver

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

def main():
    if len(sys.argv) > 1:
        goal = sys.argv[1]
    else:
        print("Usage: python scripts/prove.py '<goal_string>'")
        return # Exit if no arg? Or simple default test
        
    storage = SentenceStorage.load(DB_PATH)
    prover = AutoProver(storage)
    
    prover.prove(goal)
    
    storage.save(DB_PATH)

if __name__ == "__main__":
    main()
