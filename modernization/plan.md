# Modernization Plan: Go → Rust

**Repository:** `rishabsinghal-design/dryrun`
**Target Architecture:** Go → Rust (systems-level, memory-safe, zero-cost abstractions)
**Plan Created:** 2025
**Agent:** App Modernization Agent
**Supersedes:** Previous Python → C++ plan (archived below in §7)

---

## 1. Codebase Orientation

| File | Language | Role | Status |
|---|---|---|---|
| `true.py` | Python | `hello_world()` utility | ⚠️ Deprecated (superseded by `true.js`) |
| `test.py` | Python | Smoke test (`print('hello world')`) | Active but trivial |
| `tik.py` | Python | Empty stub | Dead code |
| `rag_pipeline.py` | Python | LangGraph RAG pipeline (ingest → retrieve → generate) | Active, core logic |
| `true.js` | JavaScript | Port of `true.py` | Active |
| `test_true.js` | JavaScript | Jest tests for `true.js` | Active |
| `hello_world.rs` | Rust | Standalone "Hello, World!" program | Active — **Rust foothold already exists** |

### Go → Rust Context

The target migration is **Go → Rust**. The repository does not currently contain Go source files; however, the **architectural patterns** present in `rag_pipeline.py` map directly to patterns commonly found in Go services (synchronous pipeline stages, global mutable state, blocking I/O, interface-based dispatch). The migration plan therefore:

1. Treats the existing Python/JS code as the **functional specification** (what the system must do).
2. Introduces Go as an **intermediate representation** only where it clarifies the migration path (optional — see Phase 1).
3. Targets **Rust** as the final runtime, leveraging the existing `hello_world.rs` as the Rust foothold.

---

## 2. Detected Legacy Smells (Go → Rust Lens)

| Smell | Location | Go Equivalent | Rust Target | Risk |
|---|---|---|---|---|
| **Global mutable state** | `rag_pipeline.py` — `_vector_store` module-level global written in `ingest()`, read in `retrieve()` | `var vectorStore *faiss.Index` package-level var | `Arc<RwLock<VectorStore>>` passed through pipeline state | High |
| **Blocking synchronous I/O** | `loader.load()`, `chain.invoke()` — blocking calls on main thread | `http.Get(...)` blocking goroutine | `tokio::spawn` + `async fn` with `reqwest` | Medium |
| **Dynamic dispatch / duck typing** | `load_documents()` — `ext`-based `if/elif` chain | `interface Loader { Load() }` | `trait Loader { fn load(...) }` + `Box<dyn Loader>` | Medium |
| **Untyped error handling** | `raise ValueError(...)` — exceptions, no typed errors | `error` interface (stringly typed) | `thiserror` / `anyhow` typed `Result<T, E>` | Medium |
| **No build system** | No `Cargo.toml`, no `go.mod` | `go.mod` + `go.sum` | `Cargo.toml` + `Cargo.lock` | High |
| **No Rust tests** | `hello_world.rs` has no `#[test]` | `_test.go` files | `#[cfg(test)]` modules + `cargo test` | High |
| **Unstructured concurrency** | `rag_pipeline.py` — sequential, no parallelism | goroutines + channels | `tokio` tasks + `mpsc` channels | Low (future) |
| **External Python-only SDKs** | `langgraph`, `langchain`, `faiss-cpu`, `langchain-openai` | Go equivalents via REST | `reqwest` (HTTP) + `hnsw_rs` / `faiss` bindings | High |
| **Deprecated dead code** | `true.py`, `tik.py` | N/A | Remove after compat shim | Low |

---

## 3. Phased Plan

---

### Phase 0 — Baseline & Safety Net *(zero risk, must complete first)*

**Goal:** Establish a reproducible Rust build, test harness, and CI gate *before* touching any logic. Nothing functional changes.

#### 0.1 — Introduce `Cargo.toml` (workspace)

Create a Cargo workspace at the repo root:

```toml
# Cargo.toml
[workspace]
members = [
    "crates/hello_world",
    "crates/rag_pipeline",
]
resolver = "2"
```

Move `hello_world.rs` into a proper crate:

```
crates/
  hello_world/
    Cargo.toml
    src/
      main.rs        ← contents of hello_world.rs
      lib.rs         ← pub fn hello_world() -> &'static str
  rag_pipeline/
    Cargo.toml
    src/
      lib.rs         ← stub (empty for now)
```

**Why a workspace:** Keeps crates independently compilable and testable; mirrors how a Go module with sub-packages would be structured.

#### 0.2 — Add `#[test]` to `hello_world` crate

```rust
// crates/hello_world/src/lib.rs
pub fn hello_world() -> &'static str {
    "Hello, World!"
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn returns_correct_string() {
        assert_eq!(hello_world(), "Hello, World!");
    }
}
```

Proves `cargo test` works end-to-end.

#### 0.3 — Add CI workflow (`.github/workflows/ci.yml`)

```yaml
jobs:
  rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo build --workspace
      - run: cargo test --workspace
      - run: cargo clippy --workspace -- -D warnings
      - run: cargo fmt --check

  python-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install pytest
      - run: python test.py   # smoke test — must stay green throughout all phases
```

**Rule:** CI must be green on `main` before any Phase 1 PR merges.

#### 0.4 — Snapshot Python behaviour as contract tests

Add `tests/python/test_rag_contract.py` using `pytest` + `unittest.mock`:

- `load_documents()` returns a `List[Document]`.
- `build_graph()` returns a compiled `StateGraph`.
- `ingest / retrieve / generate` nodes each accept and return a valid `RAGState` dict.
- `_vector_store` global is `None` before `ingest()` runs, non-`None` after.

These tests become the **acceptance criteria** for the Rust port — every Rust integration test must produce equivalent outputs.

**Exit criteria:** `cargo test --workspace` green, `cargo clippy` clean, Python smoke test green, contract tests passing.

---

### Phase 1 — Low-Risk Wins: Dead Code, Module Boundaries, Pure Utilities *(~2 PRs)*

**Goal:** Remove dead code, extract clean module boundaries in Python, and port the simplest pure-logic units to Rust.

#### 1.1 — Remove deprecated `true.py` and `tik.py`

- **Pre-condition:** `grep -r "true"` and `grep -r "tik"` confirm no live imports beyond the files themselves.
- Add compat shim `true_compat.py` re-exporting `hello_world` with a `DeprecationWarning`.
- Delete `true.py` and `tik.py` in the same PR.
- **Rollback:** Revert the PR; shim ensures no consumer breakage.

#### 1.2 — Port `hello_world` to idiomatic Rust library function

Already started in Phase 0.2. Extend with:

```rust
// crates/hello_world/src/lib.rs
/// Returns the canonical greeting string.
///
/// # Examples
/// ```
/// assert_eq!(rag_hello::hello_world(), "Hello, World!");
/// ```
pub fn hello_world() -> &'static str {
    "Hello, World!"
}
```

- Add `cargo doc` generation to CI.
- **Risk:** Zero — purely additive.

#### 1.3 — Refactor `rag_pipeline.py`: eliminate global state

Replace the `_vector_store` module-level global with an explicit field in `RAGState`:

```python
class RAGState(TypedDict):
    file_path: str
    question: str
    documents: List[Document]
    context: str
    answer: str
    vector_store: Any   # ← NEW: was a module-level global
```

Update `ingest()` to write `state["vector_store"]` and `retrieve()` to read it.

**Why now:** In Rust there are no module-level mutable globals (without `unsafe`). Making state explicit in Python now means the Rust struct maps 1-to-1 with zero surprises.

**Risk:** Medium — changes node signatures. Covered by Phase 0.4 contract tests.

#### 1.4 — Split `rag_pipeline.py` into focused modules

```
src/python/
  loaders.py        # load_documents() + extension dispatch
  splitter.py       # RecursiveCharacterTextSplitter wrapper
  vector_store.py   # FAISS wrapper
  llm_chain.py      # prompt + ChatOpenAI chain
  graph.py          # LangGraph wiring (nodes + build_graph)
  __main__.py       # CLI entry point (preserves python rag_pipeline.py)
```

No logic changes — pure structural refactor. Each module maps to a future Rust module (`mod loaders`, `mod splitter`, etc.).

**Risk:** Low — `__main__.py` preserves the public CLI surface.

**Exit criteria:** All Phase 0 tests still green, dead code removed, `rag_pipeline.py` split with explicit state, Rust `hello_world` crate fully tested and documented.

---

### Phase 2 — Rust Core Data Structures & Pure Logic *(~2–3 PRs)*

**Goal:** Define the Rust equivalents of the Python data model and pure-logic layers. No network calls yet.

#### 2.1 — `Document` struct

```rust
// crates/rag_pipeline/src/document.rs
#[derive(Debug, Clone, PartialEq)]
pub struct Document {
    pub page_content: String,
    pub metadata: std::collections::HashMap<String, String>,
}
```

Full unit tests with `assert_eq!`.

#### 2.2 — `RAGState` struct

```rust
// crates/rag_pipeline/src/state.rs
use crate::document::Document;
use crate::vector_store::VectorStore;
use std::sync::Arc;

pub struct RAGState {
    pub file_path: String,
    pub question: String,
    pub documents: Vec<Document>,
    pub context: String,
    pub answer: String,
    pub vector_store: Option<Arc<dyn VectorStore + Send + Sync>>,
}
```

Note: `vector_store` is `Option<Arc<dyn VectorStore>>` — explicit ownership, no global, thread-safe. This is the direct Rust translation of the refactored Python `RAGState` from Phase 1.3.

#### 2.3 — `TextSplitter`

```rust
// crates/rag_pipeline/src/splitter.rs
pub struct TextSplitter {
    pub chunk_size: usize,
    pub chunk_overlap: usize,
}

impl TextSplitter {
    pub fn split(&self, docs: &[Document]) -> Vec<Document> { ... }
}
```

Pure function — no I/O, no external deps. Full unit-test coverage with known inputs derived from Python contract tests.

#### 2.4 — File loaders (plain text / Markdown)

```rust
// crates/rag_pipeline/src/loaders/mod.rs
pub trait Loader {
    fn load(&self) -> Result<Vec<Document>, LoaderError>;
}

pub fn make_loader(path: &str) -> Result<Box<dyn Loader>, LoaderError>;
```

Implement `TextLoader` using `std::fs::read_to_string` — zero external deps.
PDF/DOCX loaders deferred to Phase 3 (require `lopdf` / `docx-rs` crates).

**Exit criteria:** `cargo test` green for all pure-logic units. Python tests still green.

---

### Phase 3 — Rust Vector Store & Async Retrieval *(~2–3 PRs)*

**Goal:** Replace the Python FAISS wrapper with a Rust-native vector store and introduce async I/O.

#### 3.1 — Introduce `tokio` async runtime

Add to `crates/rag_pipeline/Cargo.toml`:

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
reqwest = { version = "0.12", features = ["json", "rustls-tls"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

Convert `main.rs` entry point to `#[tokio::main] async fn main()`.

#### 3.2 — `VectorStore` trait + `HnswVectorStore` implementation

```rust
// crates/rag_pipeline/src/vector_store.rs
#[async_trait::async_trait]
pub trait VectorStore: Send + Sync {
    async fn add(&mut self, docs: &[Document], embeddings: &[Vec<f32>]) -> Result<()>;
    async fn search(&self, query: &[f32], k: usize) -> Result<Vec<Document>>;
}
```

Implement using `hnsw_rs` (pure Rust, no C FFI — safer than FAISS bindings for a first pass):

```toml
hnsw_rs = "0.3"
```

**Go parallel:** In Go this would be `type VectorStore interface { Add(...); Search(...) }` — the Rust trait is a direct equivalent with compile-time safety guarantees.

#### 3.3 — OpenAI Embeddings client

```rust
// crates/rag_pipeline/src/embeddings/openai.rs
pub struct OpenAIEmbedder {
    client: reqwest::Client,
    api_key: String,
}

impl OpenAIEmbedder {
    pub async fn embed(&self, texts: &[String]) -> Result<Vec<Vec<f32>>, EmbedError>;
}
```

- All tests use a mock embedder (`MockEmbedder` implementing the trait) — no live API calls in CI.
- **Compat note:** Python `OpenAIEmbeddings` is deprecated in favour of this Rust implementation once Phase 3 is complete.

#### 3.4 — Rust `ingest` function

```rust
pub async fn ingest(state: RAGState, embedder: &dyn Embedder) -> Result<RAGState>;
```

Wires: loader → splitter → embedder → vector store → returns updated `RAGState`.

#### 3.5 — Rust `retrieve` function

```rust
pub async fn retrieve(state: RAGState) -> Result<RAGState>;
```

Calls `state.vector_store.search(query_embedding, 4)`, populates `context`.

**Exit criteria:** Rust ingest + retrieve pipeline passes integration tests with `MockEmbedder`. Python pipeline still runs and passes contract tests.

---

### Phase 4 — Rust LLM Chain & Full Pipeline *(~2 PRs)*

**Goal:** Port the `generate` node and wire the full pipeline end-to-end in Rust.

#### 4.1 — LLM client trait + OpenAI implementation

```rust
// crates/rag_pipeline/src/llm/mod.rs
#[async_trait::async_trait]
pub trait LlmClient: Send + Sync {
    async fn complete(&self, system: &str, user: &str) -> Result<String, LlmError>;
}

// crates/rag_pipeline/src/llm/openai.rs
pub struct OpenAIChatClient {
    client: reqwest::Client,
    api_key: String,
    model: String,
}
```

#### 4.2 — Rust `generate` function

```rust
pub async fn generate(state: RAGState, llm: &dyn LlmClient) -> Result<RAGState>;
```

Builds the prompt string, calls `llm.complete(system_prompt, question)`, writes `answer`.

**Go parallel:** In Go this would be `func Generate(ctx context.Context, state RAGState, llm LlmClient) (RAGState, error)` — the Rust version adds lifetime/ownership guarantees at compile time.

#### 4.3 — Pipeline orchestrator

```rust
// crates/rag_pipeline/src/pipeline.rs
pub async fn run_pipeline(
    file_path: &str,
    question: &str,
    embedder: Arc<dyn Embedder + Send + Sync>,
    llm: Arc<dyn LlmClient + Send + Sync>,
) -> Result<String, PipelineError> {
    let state = RAGState::new(file_path, question);
    let state = ingest(state, embedder.as_ref()).await?;
    let state = retrieve(state).await?;
    let state = generate(state, llm.as_ref()).await?;
    Ok(state.answer)
}
```

**Rationale:** LangGraph's graph abstraction is valuable for Python's dynamic dispatch. In Rust, a typed sequential async pipeline is simpler, safer, and equally extensible via the Strategy pattern (swap `embedder` / `llm` implementations without changing pipeline logic).

#### 4.4 — Rust CLI entry point (`crates/rag_pipeline/src/main.rs`)

```rust
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let file_path = std::env::args().nth(1).expect("Usage: rag_pipeline <file>");
    let api_key = std::env::var("OPENAI_API_KEY")?;
    let question = prompt_user("Ask a question about the document: ")?;

    let embedder = Arc::new(OpenAIEmbedder::new(&api_key));
    let llm = Arc::new(OpenAIChatClient::new(&api_key, "gpt-4o-mini"));

    let answer = run_pipeline(&file_path, &question, embedder, llm).await?;
    println!("\nAnswer: {answer}");
    Ok(())
}
```

**Exit criteria:** `cargo run -p rag_pipeline -- path/to/file.txt` works end-to-end. Python pipeline kept alive in parallel until Phase 5.

---

### Phase 5 — Cutover, Cleanup & Deprecation *(1 PR)*

**Goal:** Retire Python source files, update docs, finalize.

#### 5.1 — Deprecate Python pipeline

Add `DeprecationWarning` to `rag_pipeline.py` entry point:

```python
import warnings
warnings.warn(
    "rag_pipeline.py is deprecated. Use the Rust binary `rag_pipeline` instead.",
    DeprecationWarning,
    stacklevel=1,
)
```

Update `README.md` to point users to `cargo run -p rag_pipeline`.

#### 5.2 — Remove Python source files

> ⚠️ **Destructive action — requires explicit user approval before execution.**

Files to remove: `rag_pipeline.py`, `true.py` (already gone after Phase 1), `tik.py` (already gone after Phase 1), `test.py`, `src/python/`.

Python contract tests converted to Rust integration tests (`tests/integration_test.rs`).

#### 5.3 — Final documentation pass

- Update `README.md`: `cargo build --release`, `cargo test`, usage, dependencies.
- Add `ARCHITECTURE.md` describing the Rust crate structure.
- Archive `modernization/` notes.

**Exit criteria:** Repo contains only Rust source, all tests pass, CI green, `cargo clippy -- -D warnings` clean.

---

## 4. Risk Matrix

| Change | What It Could Break | Rollback Plan |
|---|---|---|
| Move `hello_world.rs` into workspace (Phase 0.1) | Any tooling referencing the root-level `.rs` file directly | Keep `hello_world.rs` symlink at root until Phase 1 cleanup; revert PR |
| Add CI workflow (Phase 0.3) | CI may fail if Rust toolchain version mismatches | Pin `dtolnay/rust-toolchain@stable`; revert workflow file |
| Remove `true.py` / `tik.py` (Phase 1.1) | Any undiscovered import of `hello_world` from Python | Compat shim `true_compat.py` re-exports the symbol; revert PR if shim insufficient |
| Refactor `_vector_store` global (Phase 1.3) | `ingest` / `retrieve` node contract | Contract tests from Phase 0.4 catch regressions; revert PR |
| Split `rag_pipeline.py` (Phase 1.4) | CLI invocation path | `__main__.py` preserves `python rag_pipeline.py` entrypoint; revert PR |
| `hnsw_rs` vector store (Phase 3.2) | Recall quality vs. FAISS | `hnsw_rs` can be swapped for `faiss` C bindings (`faiss-rs` crate) behind the `VectorStore` trait without changing callers |
| OpenAI REST calls in Rust (Phase 3.3, 4.1) | API key handling, TLS, proxy | Abstracted behind `Embedder` / `LlmClient` traits; `MockEmbedder` / `MockLlm` used in all CI tests |
| Remove Python files (Phase 5.2) | Any tooling that depends on `.py` files | **Requires explicit approval**; branch kept alive for 1 sprint post-cutover |
| LangGraph removal (Phase 4.3) | Graph-based extensibility (conditional edges, retries) | Sequential Rust pipeline is functionally equivalent for current linear graph; Strategy pattern allows future branching |

---

## 5. Go → Rust Concept Mapping Reference

This table is a quick-reference for contributors familiar with Go who are writing Rust for the first time in this codebase.

| Go Concept | Rust Equivalent | Notes |
|---|---|---|
| `interface Foo { Bar() }` | `trait Foo { fn bar(&self); }` | Rust traits are checked at compile time; no runtime vtable unless `dyn Trait` |
| `var x *T` (nullable pointer) | `Option<Box<T>>` | Rust forces explicit `None` handling — no nil panics |
| `go func() { ... }()` | `tokio::spawn(async { ... })` | Rust async is explicit; no implicit goroutine scheduler |
| `chan T` | `tokio::sync::mpsc::channel::<T>()` | Typed, bounded channels |
| `sync.RWMutex` | `std::sync::RwLock<T>` | Rust wraps the data, not just the lock |
| `defer f()` | `Drop` trait / `scopeguard` crate | RAII — destructor runs at end of scope |
| `error` (interface) | `Result<T, E>` + `thiserror` | Errors are values; `?` operator propagates |
| `context.Context` | `tokio_util::sync::CancellationToken` | Explicit cancellation propagation |
| `go test ./...` | `cargo test --workspace` | |
| `go build ./...` | `cargo build --workspace` | |
| `go vet` / `staticcheck` | `cargo clippy` | |
| `gofmt` | `cargo fmt` | |

---

## 6. Dependency Map (Rust target)

```
crates/rag_pipeline/src/main.rs
  └── pipeline.rs                    (orchestrator: ingest → retrieve → generate)
        ├── loaders/
        │     ├── mod.rs             (trait Loader + make_loader factory)
        │     ├── text_loader.rs     (std::fs — no external deps)
        │     ├── pdf_loader.rs      (lopdf crate — Phase 3+)
        │     └── docx_loader.rs     (docx-rs crate — Phase 3+)
        ├── splitter.rs              (pure Rust — no external deps)
        ├── vector_store.rs          (trait VectorStore + HnswVectorStore)
        ├── embeddings/
        │     ├── mod.rs             (trait Embedder)
        │     └── openai.rs          (reqwest HTTP client)
        └── llm/
              ├── mod.rs             (trait LlmClient)
              └── openai.rs          (reqwest HTTP client)

External Rust crates (Cargo.toml):
  tokio          — async runtime
  reqwest        — HTTP client (OpenAI REST API)
  serde / serde_json — JSON serialization
  hnsw_rs        — vector similarity search (pure Rust)
  anyhow         — ergonomic error handling
  thiserror      — typed error definitions
  async-trait    — async methods in traits
  clap           — CLI argument parsing (Phase 4)
  lopdf          — PDF parsing (Phase 3)
  docx-rs        — DOCX parsing (Phase 3)
```

---

## 7. What Is NOT Changing

- The **public behaviour** of the pipeline: same inputs (file path + question), same output (answer string).
- The **OpenAI API** used (embeddings + chat completions) — only the client library changes.
- The **vector similarity algorithm** — same approximate nearest-neighbour search, same `k=4` retrieval.
- **Test assertions** — contract tests from Phase 0 define the acceptance criteria for every subsequent phase.

---

## 8. Archived: Previous Python → C++ Plan

The previous modernization plan targeted Python → C++. It is preserved for reference but superseded by this Go → Rust plan. Key differences:

| Dimension | Python → C++ | Go → Rust |
|---|---|---|
| Build system | CMake + Conan | Cargo (built-in) |
| Test harness | GoogleTest (external) | `cargo test` (built-in) |
| Async model | `std::future` / manual threads | `tokio` async/await |
| Error handling | Exceptions / `std::expected` | `Result<T, E>` + `?` |
| Memory model | RAII + smart pointers (manual) | Ownership + borrow checker (compiler-enforced) |
| Package ecosystem | Conan / vcpkg (fragmented) | crates.io (unified) |
| Compile times | Fast incremental | Slower (acceptable for this codebase size) |
| Safety guarantees | Programmer-enforced | Compiler-enforced (no `unsafe` needed here) |
