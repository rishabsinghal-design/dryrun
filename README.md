# DRYRUN

A sandbox repository for testing and prototyping basic functionality, including a LangGraph-based RAG pipeline and a simple Hello World module migrated from Python to JavaScript.

---

## Repository Structure

```
.
├── rag_pipeline.py      # LangGraph RAG pipeline (PDF / DOCX / Markdown / TXT)
├── true.js              # Hello World module (JavaScript — current)
├── true.py              # Hello World function (Python — deprecated, see true.js)
├── test_true.js         # Jest tests for true.js
├── test.py              # Python smoke test
└── modernization/       # Modernization spike work
```

---

## Modules

### `rag_pipeline.py` — RAG Pipeline

A [LangGraph](https://github.com/langchain-ai/langgraph) pipeline that answers questions about a local document using Retrieval-Augmented Generation (RAG).

**Supported file types:** `.pdf`, `.docx`, `.md`, `.txt`

**Pipeline stages:**

| Stage | Description |
|-------|-------------|
| `ingest` | Loads the file, splits it into chunks, and builds a FAISS vector index |
| `retrieve` | Retrieves the top-4 most relevant chunks for the user's question |
| `generate` | Sends the retrieved context + question to `gpt-4o-mini` and returns an answer |

**Prerequisites:**

```bash
pip install langgraph langchain langchain-openai langchain-community faiss-cpu pypdf python-docx
export OPENAI_API_KEY="sk-..."
```

**Usage:**

```bash
python rag_pipeline.py path/to/your/document.pdf
# You will be prompted to enter a question about the document.
```

---

### `true.js` — Hello World (JavaScript)

The current Hello World module, written in JavaScript.

```js
const helloWorld = require('./true');
console.log(helloWorld()); // "Hello, World!"
```

**Tests:**

```bash
npx jest test_true.js
```

---

### `true.py` — Hello World (Python, Deprecated)

> ⚠️ **Deprecated.** This file will be removed in Phase 3.  
> The equivalent functionality has been rewritten in [`true.js`](./true.js).

---

## Development

### Running Python tests

```bash
python test.py
```

### Running JavaScript tests

```bash
npx jest
```

---

## Modernization

The `modernization/` directory contains spike work for migrating Python utilities to JavaScript. See the `modernize/phase1-true-py-to-js` branch for the completed Phase 1 migration.
