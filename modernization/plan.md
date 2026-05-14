# Modernization Plan: Python → C++

**Repository:** `rishabsinghal-design/dryrun`
**Target Architecture:** Python → C++ (native, compiled)
**Plan Created:** 2025
**Agent:** App Modernization Agent

---

## 1. Codebase Orientation

| File | Language | Role | Status |
|---|---|---|---|
| `true.py` | Python | `hello_world()` utility | ⚠️ Deprecated (superseded by `true.js`) |
| `test.py` | Python | Smoke test (`print('hello world')`) | Active but trivial |
| `rag_pipeline.py` | Python | LangGraph RAG pipeline (ingest → retrieve → generate) | Active, core logic |
| `true.js` | JavaScript | Port of `true.py` | Active |
| `test_true.js` | JavaScript | Jest tests for `true.js` | Active |

### Detected Legacy Smells (Python → C++ lens)

| Smell | Location | Risk |
|---|---|---|
| **Global mutable state** | `rag_pipeline.py` — `_vector_store` module-level global, written inside `ingest()` node and read inside `retrieve()` | High — not thread-safe, invisible to callers |
| **Dynamic typing / duck typing** | All `.py` files — no static types enforced at runtime | Medium — must be replaced with explicit C++ types |
| **Runtime type dispatch** | `load_documents()` — `ext`-based `if/elif` chain with lazy imports | Medium — maps cleanly to a C++ factory pattern |
| **Interpreter-managed memory** | All Python objects — GC-managed heap | High — must be replaced with RAII / smart pointers |
| **Blocking synchronous I/O** | `loader.load()`, `chain.invoke()` — blocking calls on the main thread | Medium — C++ port should use `std::future` / async I/O |
| **External Python-only SDKs** | `langgraph`, `langchain`, `faiss-cpu`, `langchain-openai` | High — no direct C++ equivalents; requires REST/gRPC boundary or C++ native libs |
| **No build system** | No `CMakeLists.txt`, `Makefile`, or `conanfile.txt` | High — must be introduced before any C++ code lands |
| **No C++ tests** | No `catch2`, `gtest`, or `doctest` harness | High — must be introduced in Phase 0 |
| **Deprecated dead code** | `true.py` — already marked deprecated | Low — safe to remove after compat shim confirmed |

---

## 2. Phased Plan

---

### Phase 0 — Baseline & Safety Net *(lowest risk, do first)*

**Goal:** Establish a reproducible build, test harness, and CI gate *before* touching any logic. Nothing functional changes.

#### 0.1 — Introduce a C++ build system
- Add `CMakeLists.txt` (CMake ≥ 3.25) at the repo root.
- Add `conanfile.txt` (or `vcpkg.json`) for dependency management.
- Initial targets: compile a single `main.cpp` that prints `"Hello, World!"` — proves the toolchain works.

#### 0.2 — Add a C++ test harness
- Integrate **GoogleTest** (via CMake `FetchContent` or Conan).
- Add `tests/CMakeLists.txt`.
- Add a trivial passing test (`EXPECT_EQ(1, 1)`) to prove the harness compiles and runs.

#### 0.3 — Add CI workflow
- Add `.github/workflows/ci.yml`:
  - Job 1: `cmake --build` + `ctest` (C++ gate).
  - Job 2: `python -m pytest` on existing Python files (regression gate — must stay green throughout all phases).
- **Rule:** CI must be green on `main` before any Phase 1 PR merges.

#### 0.4 — Snapshot Python behaviour as contract tests
- Add `tests/python/test_rag_contract.py` using `pytest` + `unittest.mock` to pin the public surface of `rag_pipeline.py`:
  - `load_documents()` returns a `List[Document]`.
  - `build_graph()` returns a compiled `StateGraph`.
  - `ingest / retrieve / generate` nodes each accept and return a valid `RAGState`.
- These tests become the acceptance criteria for the C++ port.

**Exit criteria:** CI green, all Python contract tests passing, C++ "Hello World" binary produced.

---

### Phase 1 — Low-Risk Wins: Boundaries, Dead Code, Pure Utilities *(~1–2 PRs)*

**Goal:** Extract clean module boundaries in Python, remove dead code, and port the simplest pure-logic units to C++.

#### 1.1 — Remove deprecated `true.py`
- **Pre-condition:** Confirm no live import of `true.py` anywhere (grep confirms only `test.py` and `true.py` itself reference it).
- Add a compat shim `true_compat.py` that re-exports `hello_world` with a `DeprecationWarning` for any external consumers.
- Delete `true.py` in the same PR.
- **Rollback:** Revert the PR; the shim ensures no breakage.

#### 1.2 — Port `hello_world` to C++
- Add `src/hello_world.hpp` + `src/hello_world.cpp`:
  ```cpp
  // src/hello_world.hpp
  #pragma once
  #include <string>
  std::string hello_world();

  // src/hello_world.cpp
  #include "hello_world.hpp"
  std::string hello_world() { return "Hello, World!"; }
  ```
- Add `tests/test_hello_world.cpp` (GoogleTest):
  ```cpp
  TEST(HelloWorldTest, ReturnsCorrectString) {
      EXPECT_EQ(hello_world(), "Hello, World!");
  }
  ```
- Wire into `CMakeLists.txt`.
- **Risk:** Zero — purely additive.

#### 1.3 — Refactor `rag_pipeline.py`: eliminate global state
- Replace the `_vector_store` module-level global with an explicit parameter passed between nodes via `RAGState`.
- Extend `RAGState` TypedDict with a `vector_store_handle: Any` field (or use a wrapper object).
- **Why now:** This is a prerequisite for the C++ port — C++ has no equivalent of Python module-level mutable globals; the state must be explicit.
- **Risk:** Medium — changes node signatures. Covered by contract tests from Phase 0.4.

#### 1.4 — Split `rag_pipeline.py` into focused modules
Split the single 160-line file into:
```
src/python/
  loaders.py        # load_documents() + extension dispatch
  splitter.py       # chunking logic
  vector_store.py   # FAISS wrapper
  llm_chain.py      # prompt + ChatOpenAI chain
  graph.py          # LangGraph wiring (ingest/retrieve/generate nodes + build_graph)
  __main__.py       # CLI entry point
```
- No logic changes — pure structural refactor.
- Each module gets its own unit test file.
- **Risk:** Low — import paths change internally; public CLI (`python rag_pipeline.py`) preserved via `__main__.py`.

**Exit criteria:** All Phase 0 tests still green, `true.py` removed, C++ `hello_world` test passing, `rag_pipeline.py` split with no global state.

---

### Phase 2 — C++ Core Data Structures & Document Model *(~2–3 PRs)*

**Goal:** Define the C++ equivalents of the Python data model and pure-logic layers. No LLM calls yet.

#### 2.1 — C++ `Document` struct
```cpp
// src/document.hpp
struct Document {
    std::string page_content;
    std::map<std::string, std::string> metadata;
};
```
- Add GoogleTest coverage.

#### 2.2 — C++ `TextSplitter`
- Port `RecursiveCharacterTextSplitter` logic to `src/text_splitter.hpp/.cpp`.
- Parameters: `chunk_size`, `chunk_overlap`, separator list.
- Pure function: `std::vector<Document> split(const std::vector<Document>& docs)`.
- Full unit-test coverage with known inputs/outputs (derived from Python contract tests).

#### 2.3 — C++ file loaders (plain text / Markdown)
- Port `load_documents()` for `.txt` / `.md` to `src/loaders/text_loader.hpp/.cpp`.
- Use `std::ifstream` — no external dependencies.
- Factory function: `std::unique_ptr<BaseLoader> make_loader(const std::string& path)`.
- PDF/DOCX loaders deferred to Phase 3 (require third-party libs: `libpoppler`, `libzip`).

#### 2.4 — C++ `RAGState` struct
```cpp
struct RAGState {
    std::string file_path;
    std::string question;
    std::vector<Document> documents;
    std::string context;
    std::string answer;
    // vector_store owned here, not as a global
    std::shared_ptr<VectorStore> vector_store;
};
```

**Exit criteria:** C++ data model compiles, all unit tests pass, Python tests still green.

---

### Phase 3 — C++ Vector Store & Retrieval *(~2–3 PRs)*

**Goal:** Replace the Python FAISS wrapper with a C++ native vector store.

#### 3.1 — Integrate FAISS C++ library
- FAISS ships a native C++ API (`faiss/Index.h`).
- Add `faiss` as a Conan/vcpkg dependency.
- Implement `src/vector_store.hpp/.cpp`:
  - `void add(const std::vector<Document>& docs, const std::vector<std::vector<float>>& embeddings)`.
  - `std::vector<Document> search(const std::vector<float>& query_embedding, int k)`.

#### 3.2 — Embedding interface (C++ abstraction)
- Define `src/embeddings/base_embedder.hpp` (pure virtual interface).
- Implement `src/embeddings/openai_embedder.hpp/.cpp` — calls OpenAI Embeddings REST API via `libcurl` or `cpp-httplib`.
- **Compat note:** Python `OpenAIEmbeddings` is deprecated in favour of this C++ implementation once Phase 3 is complete.

#### 3.3 — C++ `ingest` node
- Wire loader → splitter → embedder → vector store.
- Covered by integration test using a small fixture `.txt` file (no live API call — embeddings mocked).

#### 3.4 — C++ `retrieve` node
- Accept `RAGState`, call `vector_store->search(query_embedding, 4)`, populate `context`.

**Exit criteria:** C++ ingest + retrieve pipeline passes integration tests with mocked embeddings. Python pipeline still runs and passes contract tests.

---

### Phase 4 — C++ LLM Chain & Full Pipeline *(~2 PRs)*

**Goal:** Port the `generate` node and wire the full pipeline end-to-end in C++.

#### 4.1 — C++ LLM client
- Define `src/llm/base_llm.hpp` (pure virtual).
- Implement `src/llm/openai_chat.hpp/.cpp` — calls OpenAI Chat Completions REST API.
- Prompt templating: simple `std::string` interpolation (no external template engine needed at this scale).

#### 4.2 — C++ `generate` node
- Accept `RAGState` with populated `context`, call LLM, write `answer`.

#### 4.3 — C++ pipeline orchestrator
- Replace LangGraph with a simple sequential C++ function:
  ```cpp
  RAGState run_pipeline(const std::string& file_path, const std::string& question);
  ```
- Internally calls `ingest → retrieve → generate` in order.
- **Rationale:** LangGraph's graph abstraction is valuable for Python's dynamic dispatch; in C++ a typed sequential call is simpler, safer, and equally extensible via the Strategy pattern.

#### 4.4 — C++ CLI entry point (`main.cpp`)
- Replaces `rag_pipeline.py __main__` block.
- Reads `OPENAI_API_KEY` from environment.
- Accepts `argv[1]` as file path, prompts for question via `std::cin`.

**Exit criteria:** `./rag_pipeline path/to/file.txt` works end-to-end in C++. Python pipeline kept alive in parallel until Phase 5.

---

### Phase 5 — Cutover, Cleanup & Deprecation *(1 PR)*

**Goal:** Retire Python source files, update docs, finalize.

#### 5.1 — Deprecate Python pipeline
- Add `DeprecationWarning` to `rag_pipeline.py` entry point.
- Update `README.md` to point users to the C++ binary.

#### 5.2 — Remove Python source files
> ⚠️ **Destructive action — requires explicit user approval before execution.**
- Files to remove: `rag_pipeline.py`, `true.py` (already gone after Phase 1), `test.py`, `src/python/`.
- Python contract tests converted to C++ integration tests.

#### 5.3 — Final documentation pass
- Update `README.md`: build instructions (`cmake`, `ctest`), usage, dependencies.
- Archive `modernization/` notes.

**Exit criteria:** Repo contains only C++ source, all tests pass, CI green.

---

## 3. Risk Matrix

| Change | What It Could Break | Rollback Plan |
|---|---|---|
| Remove `true.py` (Phase 1.1) | Any undiscovered import of `hello_world` from Python | Compat shim `true_compat.py` re-exports the symbol; revert PR if shim insufficient |
| Refactor `_vector_store` global (Phase 1.3) | `ingest` / `retrieve` node contract | Contract tests from Phase 0.4 catch regressions; revert PR |
| Split `rag_pipeline.py` (Phase 1.4) | CLI invocation path | `__main__.py` preserves `python rag_pipeline.py` entrypoint; revert PR |
| FAISS C++ integration (Phase 3.1) | Build portability (Linux/macOS/Windows) | Conan profile per platform; FAISS can be swapped for `hnswlib` (header-only) |
| OpenAI REST calls in C++ (Phase 3.2, 4.1) | API key handling, TLS, proxy | Abstracted behind interface; mock implementation used in all tests |
| Remove Python files (Phase 5.2) | Any tooling that depends on `.py` files | **Requires explicit approval**; branch kept alive for 1 sprint post-cutover |
| LangGraph removal (Phase 4.3) | Graph-based extensibility (conditional edges, retries) | Sequential C++ pipeline is functionally equivalent for current linear graph; Strategy pattern allows future branching |

---

## 4. Dependency Map (C++ target)

```
main.cpp
  └── pipeline.hpp/cpp          (orchestrator)
        ├── loaders/             (text_loader, pdf_loader, docx_loader)
        ├── text_splitter.hpp    (chunking)
        ├── vector_store.hpp     (FAISS C++ API)
        ├── embeddings/          (openai_embedder)
        └── llm/                 (openai_chat)

External C++ deps (via Conan/vcpkg):
  faiss          — vector similarity search
  cpp-httplib    — HTTP client (OpenAI REST)
  nlohmann/json  — JSON parsing (API responses)
  googletest     — unit/integration testing
  libcurl        — TLS-capable HTTP (alternative to cpp-httplib)
```

---

## 5. What Is NOT Changing

- The **public behaviour** of the pipeline: same inputs (file path + question), same output (answer string).
- The **OpenAI API** used (embeddings + chat completions) — only the client library changes.
- The **FAISS index algorithm** — same cosine/L2 similarity, same `k=4` retrieval.
- **Test assertions** — contract tests from Phase 0 define the acceptance criteria for every subsequent phase.
