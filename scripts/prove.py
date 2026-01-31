import sys
import os

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from storage import SentenceStorage
from prover import AutoProver

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        goal = sys.argv[1]
        steps = 20
        enable_forward = True
        
        if len(sys.argv) > 2:
            try:
                steps = int(sys.argv[2])
            except:
                pass
        
        if len(sys.argv) > 3:
            # Third argument controls forward reasoning: "false", "0", "no" disable it
            enable_forward = sys.argv[3].lower() not in ['false', '0', 'no', 'backward']
        
        storage = SentenceStorage.load(DB_PATH)
        prover = AutoProver(storage)
        prover.prove(goal, max_rounds=steps, enable_forward=enable_forward)
        
        storage.save(DB_PATH)
    else:
        print("Usage: python scripts/prove.py '<goal>' [steps] [enable_forward]")
        print("  enable_forward: 'true' (default) or 'false' for backward-only mode")
