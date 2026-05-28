# dryrun

A sandbox repository for experimenting with basic functionality, language modernization, and AI-powered RAG (Retrieval-Augmented Generation) pipelines.

---

## Repository Structure

```
dryrun/
├── calculator.py          # ✨ NEW: Scientific calculator module (Python)
├── tests/
│   └── test_calculator.py # ✨ NEW: Unit tests for calculator.py
├── requirements-dev.txt   # ✨ NEW: Dev/test dependencies (pytest, pytest-cov)
├── pytest.ini             # ✨ NEW: pytest configuration
├── calculator/
│   ├── index.html         # Calculator – markup (browser UI)
│   ├── style.css          # Calculator – iOS-inspired dark theme
│   └── script.js          # Calculator – logic & keyboard support
├── true.py                # (Deprecated) Python hello-world utility
├── true.js                # JavaScript hello-world utility (replaces true.py)
├── test.py                # Minimal Python smoke test
├── test_true.js           # Jest unit tests for true.js
├── rag_pipeline.py        # LangGraph-based RAG pipeline (PDF / DOCX / Markdown)
├── hello_world.rs         # Rust hello-world program
├── hello_world.go         # Go hello-world program
└── modernization/         # Assets and notes related to the Python → JS migration
```

---

## ✨ Scientific Calculator (`calculator.py`)

A stateless, pure-function scientific calculator module written in Python.
Uses only the standard library `math` module — no third-party runtime
dependencies.

### Operations

| Function | Description | Raises |
|---|---|---|
| `add(a, b)` | `a + b` | `TypeError` |
| `subtract(a, b)` | `a − b` | `TypeError` |
| `multiply(a, b)` | `a × b` | `TypeError` |
| `divide(a, b)` | `a / b` | `DivisionByZeroError` if `b=0`, `TypeError` |
| `sqrt(a)` | √a (principal root) | `DomainError` if `a < 0`, `TypeError` |
| `power(base, exp)` | `base ** exp` | `TypeError` |
| `log(a)` | Natural log ln(a) | `DomainError` if `a ≤ 0`, `TypeError` |
| `sin(a)` | sin(a) — radians | `TypeError` |
| `cos(a)` | cos(a) — radians | `TypeError` |
| `tan(a)` | tan(a) — radians | `DomainError` at odd multiples of π/2, `TypeError` |

### Custom Exceptions

| Exception | Base class | When raised |
|---|---|---|
| `DivisionByZeroError` | `ArithmeticError` | `divide(a, 0)` |
| `DomainError` | `ValueError` | `sqrt(a<0)`, `log(a≤0)`, `tan` at π/2 multiples |

### Usage

```python
import calculator

# Basic arithmetic
calculator.add(3.5, 2.0)        # → 5.5
calculator.subtract(3.5, 2.0)   # → 1.5
calculator.multiply(3.5, 2.0)   # → 7.0
calculator.divide(10.0, 4.0)    # → 2.5

# Scientific operations
calculator.sqrt(9.0)            # → 3.0
calculator.power(2.0, 10.0)     # → 1024.0
calculator.log(1.0)             # → 0.0  (natural log)

import math
calculator.sin(0.0)             # → 0.0
calculator.cos(0.0)             # → 1.0
calculator.tan(math.pi / 4)     # → 1.0

# Error handling
try:
    calculator.divide(10.0, 0)
except calculator.DivisionByZeroError as e:
    print(e)  # Cannot divide by zero

try:
    calculator.sqrt(-1.0)
except calculator.DomainError as e:
    print(e)  # sqrt requires a non-negative argument, got -1.0
```

### Running Tests

```bash
# Install dev dependencies (one-time)
pip install -r requirements-dev.txt

# Run all tests (verbose)
pytest tests/ -v

# Run with coverage report (must be ≥ 90%)
pytest tests/ --cov=calculator --cov-report=term-missing --cov-fail-under=90

# Run with per-test timing
pytest tests/ --durations=0

# Or simply (pytest.ini configures all of the above by default):
pytest
```

---

## Files

### `calculator/` — HTML / CSS / JS Calculator (Browser UI)

A fully-featured, zero-dependency browser calculator with an iOS-inspired dark theme.

**Features**
- Basic arithmetic: `+`, `−`, `×`, `÷`
- Percentage (`%`) and sign-toggle (`+/−`)
- Decimal point input
- Chained operations (e.g. `3 + 4 × 2`)
- Division-by-zero error handling
- Floating-point noise suppression (`toPrecision(12)`)
- Responsive layout (works on mobile)
- Full **keyboard support**

| Key(s)          | Action              |
|-----------------|---------------------|
| `0`–`9`         | Digit input         |
| `.` or `,`      | Decimal point       |
| `+` `-` `*` `/` | Operators           |
| `Enter` or `=`  | Evaluate            |
| `Backspace`     | Delete last digit   |
| `Escape`        | Clear (AC)          |
| `%`             | Percent             |

**Usage** — open directly in any browser, no build step needed:

```bash
open calculator/index.html
# or
xdg-open calculator/index.html   # Linux
start calculator/index.html      # Windows
```

---

### `true.js`
A simple JavaScript module that exports a `helloWorld()` function returning "Hello, World!".

```js
const helloWorld = require('./true');
console.log(helloWorld()); // Hello, World!
```

### `true.py` ⚠️ Deprecated
The original Python implementation of `hello_world()`. Superseded by `true.js` and scheduled for removal in Phase 3.

```python
from true import hello_world
print(hello_world())  # Hello, World!
```

### `hello_world.rs`
A simple Rust program that prints "Hello, World!".

```rust
fn main() {
    println!("Hello, World!");
}
```

### `hello_world.go`
A simple Go program that prints "Hello, World!".

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```

```bash
go run hello_world.go
```

### `test_true.js`
Jest unit tests for `true.js`.

```bash
npm test
```

### `test.py`
Minimal Python smoke test that prints `hello world`.

```bash
python test.py
```

### `rag_pipeline.py`
A [LangGraph](https://github.com/langchain-ai/langgraph) pipeline that answers questions about a local document (PDF, DOCX, or Markdown/TXT) using OpenAI embeddings and GPT-4o-mini.

**Pipeline stages:** `ingest → retrieve → generate`

#### Prerequisites

```bash
pip install langgraph langchain langchain-openai langchain-community faiss-cpu pypdf python-docx
export OPENAI_API_KEY="sk-..."
```

#### Usage

```bash
python rag_pipeline.py path/to/your/document.pdf
# You will be prompted to enter a question about the document.
```

---

## Getting Started

### Scientific Calculator (Python)

```bash
pip install -r requirements-dev.txt
pytest
```

### Calculator (Browser UI)

```bash
# Just open the file in your browser — no server or build step required
open calculator/index.html
```

### Go

```bash
go run hello_world.go
# Hello, World!
```

### JavaScript

```bash
# Run tests
npm test
```

### Python

```bash
# Install RAG dependencies
pip install langgraph langchain langchain-openai langchain-community faiss-cpu pypdf python-docx

# Run the RAG pipeline
python rag_pipeline.py <path/to/file>
```

---

## Modernization

The `modernization/` directory tracks the ongoing effort to migrate Python utilities to JavaScript. `true.py` has already been ported to `true.js`; further phases are in progress.

---

## License

This project is for dry-run / experimental purposes.
