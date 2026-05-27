# dryrun

A sandbox repository for experimenting with basic functionality, language modernization, and AI-powered RAG (Retrieval-Augmented Generation) pipelines.

---

## Repository Structure

```
dryrun/
├── calculator/
│   ├── index.html     # Calculator – markup
│   ├── style.css      # Calculator – iOS-inspired dark theme
│   └── script.js      # Calculator – logic & keyboard support
├── true.py            # (Deprecated) Python hello-world utility
├── true.js            # JavaScript hello-world utility (replaces true.py)
├── test.py            # Minimal Python smoke test
├── test_true.js       # Jest unit tests for true.js
├── rag_pipeline.py    # LangGraph-based RAG pipeline (PDF / DOCX / Markdown)
├── hello_world.rs     # Rust hello-world program
├── hello_world.go     # Go hello-world program
└── modernization/     # Assets and notes related to the Python → JS migration
```

---

## Files

### `calculator/` — HTML / CSS / JS Calculator

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

### Calculator

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
