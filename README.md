# MathAI: Formal Logic Proof System

This project implements a formal system for First Order Logic (FOL) in Peano Arithmetic, written in Python. It is designed to be a foundation for an automated theorem prover using machine learning.

## Features

### 1. Syntax (`src/syntax.py`)
Provides a strictly typed DAG representation of mathematical statements:
-   **Numeric Expressions**: `Zero`, `Successor`, `Add`, `Multiply`, `NumericVariable`.
-   **Logic Expressions**: `Equals`, `Not`, `Implies`, `Forall`, `LogicVariable`.
-   **Operations**:
    -   `free_variables`: Recursively identifies free variables.
    -   `substitute(var, expr)`: Performs capture-avoiding substitution.

### 2. Global Storage (`src/storage.py`)
A persistence layer that ensures canonical representation (hash consing) of all expressions.
-   **Deduplication**: Identical expressions share the same memory object.
-   **Persistence**: Saves/loads state to `data/mathai.db`.
-   **Provenance Tracking**: Records *how* and *why* a sentence is proven (e.g., "Peano Axiom", "Modus Ponens(Parent1, Parent2)"). Metadata includes actual `Node` objects for future embedding.

### 3. Axioms & Schemas (`src/schemas.py`, `scripts/init_*.py`)
The system is initialized with a robust set of logical foundation:
-   **Logic Axioms**: Standard implications (e.g., A→B→A).
-   **Peano Axioms**: The 7 standard arithmetic axioms (including `X=X`).
-   **Axiom Schemas**:
    -   Induction
    -   Instantiation
    -   Vacuous Generalization
    -   Distribution of Quantification
    -   Indiscernability of Equals

### 4. Inference Rules (`src/inference.py`)
Mechanisms to derive new proven sentences from existing ones:
-   **Modus Ponens**
-   **Universal Generalization**

## Usage

### Initialization
Run the initialization scripts to populate the database with axioms:
```bash
python scripts/init_axioms.py
python scripts/init_peano.py
```

### Inspection
View the currently proven sentences and their provenance:
```bash
python scripts/inspect_db.py
```

### Testing schemas
```bash
python scripts/test_new_schemas.py
python scripts/test_induction.py
```