import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from storage import SentenceStorage

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

def inspect_storage():
    storage = SentenceStorage.load(DB_PATH)
    print("--- Proven Sentences ---")
    for sentence, provenance in storage.proven.items():
        print(f"[{provenance}] {sentence}")

if __name__ == "__main__":
    inspect_storage()
