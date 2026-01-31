import sys
import os

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mathai.db')

def reset_database():
    """Reset the database by deleting it and reinitializing with axioms."""
    print("=== Resetting MathAI Database ===\n")
    
    # Delete existing database
    if os.path.exists(DB_PATH):
        print(f"Deleting existing database: {DB_PATH}")
        os.remove(DB_PATH)
        print("✓ Database deleted\n")
    else:
        print("No existing database found\n")
    
    # Reinitialize with axioms
    print("Initializing Logic Axioms...")
    os.system(f'{sys.executable} {os.path.join(os.path.dirname(__file__), "init_axioms.py")}')
    
    print("\nInitializing Peano Axioms...")
    os.system(f'{sys.executable} {os.path.join(os.path.dirname(__file__), "init_peano.py")}')
    
    print("\n✓ Database reset complete!")
    print(f"Database location: {DB_PATH}")

if __name__ == "__main__":
    reset_database()
