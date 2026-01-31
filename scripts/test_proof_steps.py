import sys
import os

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from syntax import LogicVariable, Implies
from matcher import Matcher
from storage import SentenceStorage
from inference import ModusPonens

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

# Load storage with axioms
storage = SentenceStorage.load(DB_PATH)
matcher = Matcher()
mp = ModusPonens(storage)

# Get axioms
axioms = list(storage.proven.keys())
L1 = axioms[0]  # A → (B → A)
L2 = axioms[1]  # (A → (B → C)) → ((A → B) → (A → C))

print("=== Testing P→P Proof ===\n")
print(f"L1: {L1}")
print(f"L2: {L2}\n")

# Create P
P = storage.intern(LogicVariable("P"))
P_implies_P = storage.intern(Implies(P, P))

print("Goal: P → P\n")
print("=== Step 1: L1[A=P, B=P] → P → (P → P) ===")
# Test if L1 matches to give us P → (P → P)
# L1 is A → (B → A), we want P → (P → P)
# So we need A=P, B=P
step1_target = storage.intern(Implies(P, Implies(P, P)))
bindings1 = matcher.match(L1, step1_target)
print(f"Target: {step1_target}")
print(f"Match L1 against target: {bindings1}")

if bindings1:
    print("✓ Step 1 can be derived!")
    # Mark as proven
    from storage import Provenance
    storage.mark_proven(step1_target, Provenance("L1 instantiation", dependencies=[L1]))
else:
    print("✗ Step 1 FAILED")

print("\n=== Step 2: L1[A=P, B=(P→P)] → P → ((P→P) → P) ===")
# L1 is A → (B → A), we want P → ((P→P) → P)
# So A=P, B=(P→P)
step2_target = storage.intern(Implies(P, Implies(P_implies_P, P)))
bindings2 = matcher.match(L1, step2_target)
print(f"Target: {step2_target}")
print(f"Match L1 against target: {bindings2}")

if bindings2:
    print("✓ Step 2 can be derived!")
    storage.mark_proven(step2_target, Provenance("L1 instantiation", dependencies=[L1]))
else:
    print("✗ Step 2 FAILED")

print("\n=== Step 3: L2[A=P, B=(P→P), C=P] ===")
# L2 is (A → (B → C)) → ((A → B) → (A → C))
# With A=P, B=(P→P), C=P:
# (P → ((P→P) → P)) → ((P → (P→P)) → (P → P))
step3_target = storage.intern(Implies(
    step2_target,  # P → ((P→P) → P)
    Implies(step1_target, P_implies_P)  # (P → (P→P)) → (P → P)
))
bindings3 = matcher.match(L2, step3_target)
print(f"Target: {step3_target}")
print(f"Match L2 against target: {bindings3}")

if bindings3:
    print("✓ Step 3 can be derived!")
    storage.mark_proven(step3_target, Provenance("L2 instantiation", dependencies=[L2]))
else:
    print("✗ Step 3 FAILED")

print("\n=== Step 4: MP on step 3 and step 2 ===")
if storage.is_proven(step3_target) and storage.is_proven(step2_target):
    try:
        mp.apply(step3_target, step2_target)
        step4_result = step3_target.right
        print(f"Result: {step4_result}")
        if storage.is_proven(step4_result):
            print("✓ Step 4 derived successfully!")
        else:
            print("✗ Step 4 NOT marked as proven")
    except Exception as e:
        print(f"✗ Step 4 FAILED: {e}")
else:
    print("✗ Step 4 skipped (prerequisites not met)")

print("\n=== Step 5: MP on step 4 and step 1 ===")
if storage.is_proven(step1_target) and 'step4_result' in locals() and storage.is_proven(step4_result):
    try:
        mp.apply(step4_result, step1_target)
        final_result = step4_result.right
        print(f"Result: {final_result}")
        if storage.is_proven(final_result) and final_result == P_implies_P:
            print("✓✓✓ PROOF COMPLETE! P → P is proven! ✓✓✓")
        else:
            print("✗ Step 5 result mismatch or not proven")
    except Exception as e:
        print(f"✗ Step 5 FAILED: {e}")
else:
    print("✗ Step 5 skipped (prerequisites not met)")

print(f"\n=== Final Check ===")
print(f"Is P → P proven? {storage.is_proven(P_implies_P)}")
