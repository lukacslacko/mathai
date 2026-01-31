import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from syntax import NumericVariable, Zero, Add, Equals, Successor, Implies
from storage import SentenceStorage
from schemas import (
    InstantiationSchema, VacuousGeneralizationSchema, 
    DistributionSchema, IndiscernabilitySchema
)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

def test_new_schemas():
    storage = SentenceStorage.load(DB_PATH)
    
    # Vars
    x = storage.intern(NumericVariable("x"))
    y = storage.intern(NumericVariable("y"))
    z = storage.intern(Zero())
    P = storage.intern(Equals(x, z)) # x=0
    Q = storage.intern(Equals(x, x)) # x=x
    
    print("Testing Instantiation...")
    inst = InstantiationSchema(storage)
    # forall x (x=0) -> 0=0
    ax1 = inst.apply(x, P, z) 
    print(f"Instantiation: {ax1}")
    
    print("\nTesting Vacuous...")
    vacuous = VacuousGeneralizationSchema(storage)
    # y=0 -> forall x (y=0)  (x not in y=0)
    P_vacuous = storage.intern(Equals(y, z))
    ax2 = vacuous.apply(x, P_vacuous)
    print(f"Vacuous: {ax2}")
    
    # Expected Failure
    try:
        vacuous.apply(x, P) # x is free in x=0
        print("ERROR: Should have failed vacuous check")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    print("\nTesting Distribution...")
    dist = DistributionSchema(storage)
    # forall x(x=0 -> x=x) -> (forall x(x=0) -> forall x(x=x))
    ax3 = dist.apply(x, P, Q)
    print(f"Distribution: {ax3}")
    
    print("\nTesting Indiscernability...")
    indisc = IndiscernabilitySchema(storage)
    # x=y -> (x=0 -> y=0)
    ax4 = indisc.apply(x, y, P)
    print(f"Indiscernability: {ax4}")
    
    storage.save(DB_PATH)

if __name__ == "__main__":
    test_new_schemas()
