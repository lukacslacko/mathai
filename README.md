# MathAI: Formal Logic Proof System for Peano Arithmetic

MathAI is a Python-based formal system for First Order Logic (FOL) with Peano Arithmetic. It strictly handles syntax, axioms, schemas, and inference rules to enable automated theorem proving.

## 🚀 Quick Start: Proving Theorems

To attempt to prove a new theorem, use the `prove.py` script. You can specify your goal using the supported string syntax.

**Syntax Guide:**
-   **Variables**: `x`, `y`, `z`, `a`, `b`...
-   **Connectives**:
    -   Implication: `->` (e.g., `A->B`)
    -   Negation: `~` (e.g., `~A`)
    -   And: `&` (e.g., `A&B`)
    -   Or: `|` (e.g., `A|B`)
-   **Quantifiers**:
    -   Forall: `!x(...)` (e.g., `!x(x=x)`)
    -   Exists: `?x(...)` (e.g., `?x(x=0)`)
-   **Arithmetic**: `0`, `S(x)`, `+`, `*`, `=`

**Example:**
Try to prove that "Zero equals Zero":
```bash
python scripts/prove.py "0=0"
```

Try to prove "Reflexivity of Equality":
```bash
python scripts/prove.py "!x(x=x)"
```

**Persistence:**
Every time you run the prover, any new theorems derived or axioms instantiated are **saved** to the database. The system "learns" and grows its knowledge base with every run.

### Explaining Proofs
To understand *why* a theorem is true, use the `explain.py` script. It traces the dependencies backwards and prints a step-by-step derivation.

```bash
python scripts/explain.py "!x(x=x)"
```

## 🔍 Inspecting the Knowledge Base

The entire state of the system (all known axioms, proven theorems, and interned expressions) is stored in `data/mathai.db`.

To view everything the system currently knows to be true:
```bash
python scripts/inspect_db.py
```
This will print all proven sentences along with their **Provenance** (why they are true, e.g., "Peano Axiom", "Modus Ponens(A, A->B)").

---

## 📚 System Reference

### 1. Logic Axioms
Standard axiom schemas for propositional logic:
1.  **L1**: `A -> (B -> A)`
2.  **L2**: `(A -> (B -> C)) -> ((A -> B) -> (A -> C))`
3.  **L3**: `(~A -> ~B) -> (B -> A)`

### 2. Peano Axioms
Foundational axioms for arithmetic:
1.  **Zero is not a Successor**: `~0=S(x)`
2.  **Injectivity of Successor**: `S(x)=S(y) -> x=y`
3.  **Identity of Addition**: `x+0 = x`
4.  **Recursive Addition**: `x+S(y) = S(x+y)`
5.  **Zero Property of Multiplication**: `x*0 = 0`
6.  **Recursive Multiplication**: `x*S(y) = (x*y)+x`
7.  **Reflexivity of Equality**: `x=x`

### 3. Axiom Schemas
Rules that generate axioms for specific expressions:
1.  **Induction**: `P[0] -> (!x(P -> P[S(x)])) -> !x(P)`
2.  **Instantiation**: `!x(P) -> P[x/e]` (where `e` is any numeric term)
3.  **Vacuous Generalization**: `P -> !x(P)` (if `x` is not free in `P`)
4.  **Distribution**: `!x(P->Q) -> (!x(P) -> !x(Q))`
5.  **Indiscernability of Equals**: `x=y -> P -> P[x/y]`

### 4. Inference Rules
Mechanisms to derive new truths from existing ones:
1.  **Modus Ponens**: If `P` and `P->Q` are proven, then `Q` is proven.
2.  **Universal Generalization**: If `P` is proven, then `!x(P)` is proven.

---

## 🏗️ Architecture

-   **`src/syntax.py`**: Defines the strictly typed DAG nodes (`Zero`, `Successor`, `Implies`, `Forall`, etc.).
-   **`src/storage.py`**: Handles **Hash Consing** (deduplication) and persistence. Ensures `Node(A) is Node(A)` via interning.
-   **`src/parser.py`**: Recursive descent parser converting string queries to `Node` DAGs.
-   **`src/schemas.py`**: implementation of axiom generating schemas.
-   **`src/inference.py`**: Implementation of inference rules (`apply(proven_node)`).
-   **`src/prover.py`**: The automated proof search engine using backward chaining and unification.
-   **`src/matcher.py`**: Structural pattern matching (`match(pattern, target) -> bindings`).

## Initialization
If you need to reset the system to its base state:
```bash
# Deletes old DB and re-initializes
python scripts/init_axioms.py
python scripts/init_peano.py
```