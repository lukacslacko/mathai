import sys
import os

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from storage import SentenceStorage

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

# Test the 5-step P->P proof
# Each step should work with max_rounds=1

print("=== Testing 5-Step P->P Proof ===\n")

# Reset and initialize
print("Step 0: Resetting database...")
os.system(f'{sys.executable} {os.path.join(os.path.dirname(__file__), "reset.py")}')

print("\n" + "="*60)
print("Step 1: Proving P->(P->P) using L1")
print("="*60)
os.system(f'{sys.executable} {os.path.join(os.path.dirname(__file__), "prove.py")} "P->(P->P)" 1')

storage = SentenceStorage.load(DB_PATH)
from parser import Parser
parser = Parser(storage)
step1 = parser.parse("P->(P->P)")
if storage.is_proven(step1):
    print("✓ Step 1 SUCCESS\n")
else:
    print("✗ Step 1 FAILED\n")
    sys.exit(1)

print("\n" + "="*60)
print("Step 2: Proving P->((P->P)->P) using L1")
print("="*60)
os.system(f'{sys.executable} {os.path.join(os.path.dirname(__file__), "prove.py")} "P->((P->P)->P)" 1')

storage = SentenceStorage.load(DB_PATH)
step2 = parser.parse("P->((P->P)->P)")
if storage.is_proven(step2):
    print("✓ Step 2 SUCCESS\n")
else:
    print("✗ Step 2 FAILED\n")
    sys.exit(1)

print("\n" + "="*60)
print("Step 3: Proving (P->((P->P)->P))->((P->(P->P))->(P->P)) using L2")
print("="*60)
os.system(f'{sys.executable} {os.path.join(os.path.dirname(__file__), "prove.py")} "(P->((P->P)->P))->((P->(P->P))->(P->P))" 1')

storage = SentenceStorage.load(DB_PATH)
step3 = parser.parse("(P->((P->P)->P))->((P->(P->P))->(P->P))")
if storage.is_proven(step3):
    print("✓ Step 3 SUCCESS\n")
else:
    print("✗ Step 3 FAILED\n")
    sys.exit(1)

print("\n" + "="*60)
print("Step 4: Proving (P->(P->P))->(P->P) using Modus Ponens")
print("="*60)
os.system(f'{sys.executable} {os.path.join(os.path.dirname(__file__), "prove.py")} "(P->(P->P))->(P->P)" 1')

storage = SentenceStorage.load(DB_PATH)
step4 = parser.parse("(P->(P->P))->(P->P)")
if storage.is_proven(step4):
    print("✓ Step 4 SUCCESS\n")
else:
    print("✗ Step 4 FAILED\n")
    sys.exit(1)

print("\n" + "="*60)
print("Step 5: Proving P->P using Modus Ponens")
print("="*60)
os.system(f'{sys.executable} {os.path.join(os.path.dirname(__file__), "prove.py")} "P->P" 1')

storage = SentenceStorage.load(DB_PATH)
step5 = parser.parse("P->P")
if storage.is_proven(step5):
    print("✓ Step 5 SUCCESS\n")
else:
    print("✗ Step 5 FAILED\n")
    sys.exit(1)

print("\n" + "="*60)
print("✓✓✓ ALL 5 STEPS SUCCESSFUL! P->P IS PROVEN! ✓✓✓")
print("="*60)
