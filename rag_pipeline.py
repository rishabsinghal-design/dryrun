# pip install langgraph langchain langchain-openai langchain-community faiss-cpu pypdf python-docx

import os
import sys
from typing import List

from typing_extensions import TypedDict

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import StateGraph, END


# ---------------------------------------------------------------------------
# Typed state shared across all graph nodes
# ---------------------------------------------------------------------------

class RAGState(TypedDict):
    file_path: str
    question: str
    documents: List[Document]
    context: str
    answer: str


# ---------------------------------------------------------------------------
# Loaders — pick the right one based on file extension
# ---------------------------------------------------------------------------

def load_documents(file_path: str) -> List[Document]:
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        from langchain_community.document_loaders import Docx2txtLoader
        loader = Docx2txtLoader(file_path)
    elif ext in (".md", ".txt"):
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return loader.load()


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------

def ingest(state: RAGState) -> RAGState:
    """Load file → split into chunks → build FAISS index stored in state."""
    raw_docs = load_documents(state["file_path"])

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(raw_docs)

    # Attach the vector store to state via a side-channel (module-level var)
    # because TypedDict values must be serialisable; the store is used in retrieve().
    global _vector_store
    _vector_store = FAISS.from_documents(chunks, OpenAIEmbeddings())

    print(f"[ingest] Indexed {len(chunks)} chunks from '{state['file_path']}'.")
    return {**state, "documents": chunks}


def retrieve(state: RAGState) -> RAGState:
    """Retrieve the top-k most relevant chunks for the question."""
    retriever = _vector_store.as_retriever(search_kwargs={"k": 4})
    relevant_docs = retriever.invoke(state["question"])
    context = "\n\n".join(doc.page_content for doc in relevant_docs)
    return {**state, "context": context}


def generate(state: RAGState) -> RAGState:
    """Feed retrieved context + question to the LLM and produce an answer."""
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a helpful assistant. Answer the question using only the "
            "context provided below. If the answer is not in the context, say "
            "'I don't know'.\n\nContext:\n{context}",
        ),
        ("human", "{question}"),
    ])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt | llm

    response = chain.invoke({"context": state["context"], "question": state["question"]})
    return {**state, "answer": response.content}


# ---------------------------------------------------------------------------
# Build the LangGraph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    graph = StateGraph(RAGState)

    graph.add_node("ingest", ingest)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rag_pipeline.py <path/to/file>")
        sys.exit(1)

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"Error: File not found — {file_path}")
        sys.exit(1)

    question = input("Ask a question about the document: ").strip()
    if not question:
        print("No question provided. Exiting.")
        sys.exit(1)

    # Module-level placeholder; populated inside the ingest node
    _vector_store = None

    pipeline = build_graph()
    initial_state: RAGState = {
        "file_path": file_path,
        "question": question,
        "documents": [],
        "context": "",
        "answer": "",
    }

    final_state = pipeline.invoke(initial_state)
    print("\nAnswer:", final_state["answer"])
