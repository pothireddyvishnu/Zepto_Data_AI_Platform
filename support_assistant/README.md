# Support Assistant

The Support Assistant module is a Retrieval-Augmented Generation (RAG) service that answers Zepto customer-policy
questions from a curated document corpus. It combines a ChromaDB vector store, a LangGraph state machine that routes
queries by intent, and a FastAPI endpoint that returns a Pydantic-validated JSON contract. The service runs
deterministically offline by default via a mock-LLM toggle, with an optional Groq-backed path for real language-model
generation — both of which are exercised and documented here.

---

## Overview

The Support Assistant is the GenAI component of the **Zepto Data & AI Platform**. Where the Data Pipeline module handles
ingestion and the Analytics module handles modeling on structured data, this module operates on unstructured policy text
and demonstrates the retrieval-augmented generation pattern end to end: document ingestion, embedding, semantic
retrieval, and grounded answer generation. It is packaged as a containerized HTTP service, making it the platform's
first deployable inference surface rather than a notebook-based analysis.

---

## Problem Statement

Zepto customer support receives repetitive questions whose answers already exist in published policy documents —
delivery timelines, return windows, membership tiers, cancellation rules, and so on. The objective is to build a service
that accepts a natural-language question, decides whether it is a policy question at all, retrieves the most
semantically relevant policy passages when it is, and returns a concise answer alongside the source documents it drew
from and a confidence score. Queries unrelated to Zepto policy must be declined rather than answered from general
knowledge, and the entire system must run and be graded without requiring a paid LLM API key.

---

## Folder Structure

```
support_assistant/
├── data/
│   ├── corpus/
│   │   ├── doc_01.txt        # Delivery Policy
│   │   ├── doc_02.txt        # Returns & Refunds
│   │   ├── doc_03.txt        # Membership Tiers
│   │   ├── doc_04.txt        # Order Tracking
│   │   ├── doc_05.txt        # Order Cancellation Policy
│   │   ├── doc_06.txt        # Damaged or Missing Items
│   │   ├── doc_07.txt        # Gift Cards
│   │   └── doc_08.txt        # Customer Support Hours
│   └── chroma/               # Persisted ChromaDB store (build artifact)
├── data_ingestion.py         # Corpus → embeddings → ChromaDB
├── schemas.py                # Pydantic request/response contracts
├── prompts.py                # Structured prompt templates
├── graph_nodes.py            # LangGraph node implementations
├── graph.py                  # Graph assembly and compilation
├── llm_client.py             # Groq client with validation retries
├── main.py                   # FastAPI application
├── Dockerfile                # Container definition
├── .dockerignore
├── requirements.txt
└── README.md
```

| File                | Description                                                                                                                                                                                |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `data/corpus/*.txt` | Eight single-paragraph Zepto policy documents forming the knowledge base. Each file is one document and, in the current configuration, one retrievable chunk                               |
| `data/chroma/`      | Persisted ChromaDB store produced by `data_ingestion.py`. A regenerable build artifact, not source                                                                                         |
| `data_ingestion.py` | Defines `DocumentIngestor`, which loads the corpus, encodes it with a sentence-transformer, and upserts vectors into the `zepto_policies` collection. Run once before serving              |
| `schemas.py`        | `AskRequest` (`query`) and `AskResponse` (`answer`, `sources`, `confidence`). `confidence` is constrained to `[0.0, 1.0]` via a Pydantic `Field`                                           |
| `prompts.py`        | `LLM_PROMPT_TEMPLATE` and `DIRECT_PROMPT_TEMPLATE`, plus the `get_llm_prompt` / `get_direct_prompt` builders that interpolate retrieved context and the user query                         |
| `graph_nodes.py`    | The three node functions (`classify_intent`, `retrieve_and_answer`, `direct_answer`), the `GraphState` TypedDict, and the module-level embedding model, Chroma client, and `MOCK_LLM` flag |
| `graph.py`          | Wires the nodes into a `StateGraph`, registers the conditional edge via `_route_intent`, compiles the graph, and exposes `run_graph(query) -> AskResponse`                                 |
| `llm_client.py`     | Lazily constructs the Groq client and provides `llm_call` (plain text) and `llm_call_structured` (JSON parse + Pydantic validation with retries)                                           |
| `main.py`           | FastAPI app exposing `GET /` for a status check and `POST /ask` for the RAG endpoint                                                                                                       |
| `Dockerfile`        | Installs dependencies, bakes the vector store at build time, and serves on port 7860                                                                                                       |

---

## Technology Stack

| Library                 | Purpose                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------------------------ |
| `fastapi`               | HTTP API layer; declares the `/ask` route and enforces `response_model=AskResponse`                    |
| `uvicorn`               | ASGI server that runs the FastAPI application locally and inside the container                         |
| `langgraph`             | State-machine orchestration; `StateGraph` holds the node graph and the conditional intent routing      |
| `chromadb`              | Persistent vector database storing document embeddings and metadata; performs cosine similarity search |
| `sentence-transformers` | `all-MiniLM-L6-v2` encoder producing 384-dimensional embeddings for both documents and queries         |
| `pydantic`              | Schema definition and runtime validation of the API contract and of LLM-generated JSON                 |
| `groq`                  | Client for the optional real-LLM path (`MOCK_LLM=0`)                                                   |
| `python-dotenv`         | Loads `GROQ_API_KEY` and `MOCK_LLM` from a local `.env` file                                           |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/pothireddyvishnu/Zepto_Data_AI_Platform.git
cd Zepto_Data_AI_Platform

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate          # Windows

# Install dependencies
pip3 install -r support_assistant/requirements.txt
```

---

## Running the Module

`MOCK_LLM` defaults to mock mode on both paths, so **no API key is required** to run, test, or grade this module.

### Local

The vector store must exist before the API starts — `graph_nodes.py` calls `get_collection()` at import time and will
raise if the collection is missing.

```bash
cd support_assistant

# 1. Build the vector store (run once)
python3 data_ingestion.py

# 2. Serve the API
uvicorn main:app --reload
```

The API is then available at `http://127.0.0.1:8000`, with interactive docs at `/docs`.

### Docker

```bash
cd support_assistant

docker build -t zepto-support .
docker run -p 7860:7860 zepto-support
```

The image runs `data_ingestion.py` during the build, so the vector store is baked into the image and no ingestion step
is needed at runtime. The container sets `ENV MOCK_LLM=1` explicitly and serves on `http://127.0.0.1:7860`.

---

## Architecture

```
                       data/corpus/*.txt  (8 policy documents)
                                  │
                                  ▼
              ┌────────────────────────────────────────┐
              │  data_ingestion.py :: DocumentIngestor │   BUILD-TIME
              │  load → chunk → encode → upsert        │
              └────────────────────────────────────────┘
                                  │
                                  ▼
                  ChromaDB  collection "zepto_policies"
                  persisted at  support_assistant/data/chroma/
                                  │
════════════════════════════════════════════════════════════════════
                                  │                        REQUEST-TIME
   POST /ask  ──▶  main.py  ──▶  graph.run_graph()
                                  │
                                  ▼
                        ┌──────────────────┐
                        │  classify_intent │
                        └──────────────────┘
                                  │
                    _route_intent (conditional edge)
                     ┌────────────┴────────────┐
        policy_question                    general_question
                     │                         │
                     ▼                         ▼
          ┌─────────────────────┐     ┌─────────────────┐
          │ retrieve_and_answer │     │  direct_answer  │
          │  embed → top-3 →    │     │  refusal, no    │
          │  generate           │     │  retrieval      │
          └─────────────────────┘     └─────────────────┘
                     │                         │
                     └────────────┬────────────┘
                                  ▼
                      AskResponse (Pydantic-validated)
                   { answer, sources[], confidence }
```

### Stage 1 — Ingestion

`DocumentIngestor.load_documents()` in [`data_ingestion.py`](data_ingestion.py) reads every `.txt` file in`data/corpus/`
in sorted order, skipping empty files, and assigns each document an ID derived from its filename (`doc_01` … `doc_08`).

`chunk_documents()` currently maps each document to exactly one chunk — it is a structural pass-through rather than a
splitter. The corpus documents are single paragraphs short enough to embed whole, so **one document equals one chunk
equals one vector**. The method exists as the seam where a real splitting strategy would be introduced if the corpus
grew.

### Stage 2 — Embedding

`generate_embeddings()` encodes the chunk texts with `SentenceTransformer("all-MiniLM-L6-v2")`, producing
384-dimensional vectors. `store_embeddings()` upserts them into a ChromaDB collection with:

| Property         | Value                                                              |
| ---------------- | ------------------------------------------------------------------ |
| Collection name  | `zepto_policies`                                                   |
| Persistence path | `support_assistant/data/chroma/` (via `chromadb.PersistentClient`) |
| Distance metric  | Cosine (`metadata={"hnsw:space": "cosine"}`)                       |
| Record ID        | The document ID, e.g. `doc_02`                                     |
| Metadata         | `{"doc_id": "<document id>"}`                                      |
| Document text    | The full raw paragraph, returned with query results                |

The constructor deletes any existing collection before recreating it, so `python3 data_ingestion.py` is idempotent and
always rebuilds from scratch.

### Stage 3 — Routing and Retrieval

`graph.py` assembles a LangGraph `StateGraph` over the `GraphState` TypedDict (`query`, `intent`, `retrieved_context`,
`answer`, `sources`, `confidence`):

| Node                  | Role                                                                          |
| --------------------- | ----------------------------------------------------------------------------- |
| `classify_intent`     | Labels the query `policy_question` or `general_question`                      |
| `retrieve_and_answer` | Embeds the query, retrieves the top-3 chunks, and generates a grounded answer |
| `direct_answer`       | Declines out-of-scope queries without touching the vector store               |

The single conditional edge is registered with `add_conditional_edges("classify_intent", _route_intent, {...})`, mapping
`policy_question → retrieve_and_answer` and `general_question → direct_answer`. `_route_intent` defends against an
unrecognized intent string by defaulting to `general_question` — this matters on the real-LLM path, where the classifier
returns free-form text.

`retrieve_and_answer` encodes the query with the same `all-MiniLM-L6-v2` model used at ingestion, queries the collection
with `n_results=TOP_K` (3), and assembles `retrieved_context` entries of `{chunk_id, doc_id, text}`. Because embeddings
are shared between ingestion and query time, the two vector spaces are directly comparable.

### Stage 4 — Generation

`prompts.py` backs the real-LLM path with two templates, both built on the same five-part skeleton:

| Template                 | Used by               | Skeleton                                                                                 |
| ------------------------ | --------------------- | ---------------------------------------------------------------------------------------- |
| `LLM_PROMPT_TEMPLATE`    | `retrieve_and_answer` | Role, Context (interpolated retrieved chunks), Task, Rules, Examples, Format, Length     |
| `DIRECT_PROMPT_TEMPLATE` | `direct_answer`       | Role, Context (explains why nothing was retrieved), Task, Rules, Example, Format, Length |

Both carry explicit negative constraints
(`Do NOT answer using information that is not present in the retrieved context`, `Do NOT use outside knowledge`,
`Do NOT invent Zepto policy details`), few-shot examples, and a literal JSON output specification matching`AskResponse`.
`get_llm_prompt()` formats retrieved chunks as `[chunk_id] text` lines so the model can cite sources by ID.

### The `MOCK_LLM` toggle

`MOCK_LLM` is read once at import time in `graph_nodes.py` as `os.getenv("MOCK_LLM", "1") == "1"` — mock mode is the
default, and any value other than `"1"` selects the real path.

|                       | **Mock (default)**                                                                                                                                                              | **`MOCK_LLM=0`**                                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `classify_intent`     | Substring match against `POLICY_KEYWORDS` (`delivery`, `return`, `refund`, `membership`, `tracking`, `cancel`, `gift card`, `support hours`)                                    | `llm_call()` with a one-word classification prompt                                                                                                        |
| `retrieve_and_answer` | Retrieval runs normally; answer is the canned `f"Based on the retrieved context: {top_chunk[:200]}..."`, `sources` = all 3 retrieved chunk IDs, `confidence` hardcoded to `1.0` | Retrieval runs identically; `get_llm_prompt()` output is sent to `llm_call_structured()`, and `answer` / `sources` / `confidence` all come from the model |
| `direct_answer`       | Fixed string `"I can only answer questions about Zepto policies right now."`, `sources=[]`, `confidence=1.0`                                                                    | `get_direct_prompt()` output sent to `llm_call_structured()`                                                                                              |
| Network               | None. No API key needed                                                                                                                                                         | Groq API calls; `GROQ_API_KEY` required                                                                                                                   |

Retrieval and embedding are **identical in both modes** — only classification and answer generation change. This keeps
the retrieval layer verifiable without an API key.

`llm_call_structured()` wraps generation in a validation loop: it strips markdown code fences, parses JSON, and
validates against `AskResponse`. On `JSONDecodeError` or `ValidationError` it retries up to `MAX_RETRIES` (2),
re-sending the prompt augmented with the validation error and the previous raw output. If all three attempts fail it
returns a structured error object with `confidence: 0.0` rather than raising, so `/ask` never breaks its contract.

> **Note on configuration precedence:** `llm_client.py` calls `dotenv.load_dotenv()` at import, and `graph_nodes.py`
> imports `llm_client` _before_ reading `MOCK_LLM`. A `MOCK_LLM` entry in `.env` therefore takes effect ahead of the `"1"`
> code fallback. Because `load_dotenv()` does not override variables already present in the environment, an explicitly
> exported `MOCK_LLM` still wins over `.env`.

---

## Example API Calls

Captured from a live local run in mock mode (`MOCK_LLM=1`), after `python3 data_ingestion.py` and
`uvicorn main:app --reload`. Responses are verbatim.

**Status check**

```bash
curl http://127.0.0.1:8000/
```

```json
{
	"status": "running",
	"service": "Support Assistant",
	"version": "1.0.0"
}
```

**Policy query**

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "How long do I have to return a damaged grocery item?"}'
```

```json
{
	"answer": "Based on the retrieved context: Grocery and perishable items may be reported for a return within 24 hours of delivery if damaged, spoiled, or incorrect; non-perishable packaged items may be returned within 7 days of delivery in unop...",
	"sources": ["doc_02", "doc_06", "doc_05"],
	"confidence": 1.0
}
```

The `return` keyword routed the query to `retrieve_and_answer`, and semantic search ranked `doc_02` (Returns & Refunds)
first — the correct source document. The answer truncates at the 200-character snippet limit, which is the expected mock
behavior.

**General query**

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}'
```

```json
{
	"answer": "I can only answer questions about Zepto policies right now.",
	"sources": [],
	"confidence": 1.0
}
```

No `POLICY_KEYWORDS` match, so the query routed to `direct_answer`, which returned the canned refusal without querying
the vector store.

---

## Optional Extensions

### Real-LLM path (`MOCK_LLM=0`)

Verified working against the Groq free tier using model **`qwen/qwen3.6-27b`**, with `GROQ_API_KEY` supplied from a
local `.env` file and `MOCK_LLM=0` exported so it overrides the `.env` value. The same two queries produced:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "How long do I have to return a damaged grocery item?"}'
```

```json
{
	"answer": "You must report a damaged grocery item within 24 hours of delivery through the 'Report an Issue' button on the order page.",
	"sources": ["doc_02", "doc_06"],
	"confidence": 1.0
}
```

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}'
```

```json
{
	"answer": "I can only answer questions related to Zepto policies.",
	"sources": [],
	"confidence": 0.0
}
```

Observations from that run:

- The model produced schema-valid JSON on the first attempt for both queries — the retry loop was available but not
  needed.
- Unlike mock mode, the LLM **selected a subset** of the retrieved chunks as sources (2 of 3, dropping the least
  relevant one) and wrote a synthesised answer rather than echoing a truncated chunk.
- Confidence is genuinely graded rather than hardcoded: the model returned `1.0` on the well-supported policy query and
  `0.0` on the out-of-scope one, where mock mode reports `1.0` for both.
- The LLM classifier routed both queries identically to the keyword heuristic, confirming the two paths agree on these
  cases.
- `GROQ_API_KEY` is read from the environment at call time and is never committed. `.dockerignore` excludes `.env` from
  the image, which was confirmed by listing `/app` inside a running container.

---

## Deployment Status

This module is **not deployed to a public URL**. Container images build and run correctly, but every free hosting tier
evaluated was either paywalled or unable to fit the image's memory footprint.

| Platform                | Outcome     | Reason                                                                                                    |
| ----------------------- | ----------- | --------------------------------------------------------------------------------------------------------- |
| **Hugging Face Spaces** | Not pursued | Docker Spaces have been discontinued on the free plan and now require a paid PRO subscription             |
| **Render**              | Failed      | Out of memory — the free instance is killed while loading the sentence-transformer model and Chroma store |
| **Railway**             | Failed      | Out of memory on the free/trial resource limits, same failure mode as Render                              |
| **Local Docker**        | ✅ Verified | `docker build` succeeds and `docker run -p 7860:7860` serves `/ask`                                       |

The memory pressure is inherent to the stack rather than to the application code: the image ships CPU-only PyTorch plus
the `all-MiniLM-L6-v2` encoder, which is loaded into memory at import time in `graph_nodes.py`, on top of a persistent
ChromaDB client. That working set exceeds the RAM allowance of the free tiers on both Render and Railway, so the
processes are OOM-killed during startup before the server ever binds a port. Rather than pay for a hosting tier or
degrade the retrieval quality to fit, **the decision was to keep this module local-only**.

The graded baseline is therefore local containerization, which is verified: `docker build` completes successfully and
`docker run -p 7860:7860` serves `/ask` with responses identical to the local uvicorn run. No live URL is published for
this module.

---

## Learning Outcomes

This module demonstrates the following concepts through hands-on implementation:

- **RAG Pipeline Design** – composing corpus ingestion, embedding, vector persistence, semantic retrieval, and grounded
  generation into a single request path, with a shared encoder guaranteeing comparable vector spaces at index and query
  time
- **Vector Database Operations** — persisting embeddings with ChromaDB, choosing cosine similarity for normalized
  sentence embeddings, attaching queryable metadata, and building idempotent, rerunnable ingestion
- **LangGraph State Orchestration** — modeling a multi-step workflow as a typed `StateGraph`, implementing nodes as pure
  state transformations, and branching execution through conditional edges with a safe routing fallback
- **Structured Prompt Engineering** — constructing prompts from an explicit Role/Context/Task/Format/Length skeleton,
  reinforcing grounding with negative constraints, and steering output shape with few-shot examples
- **Schema Validation with Retries** — enforcing an API contract with Pydantic constrained fields, and treating LLM
  output as untrusted input that must be parsed, validated, and repaired through error-feedback retries with a graceful
  terminal fallback
- **Environment-Based Mode Toggling** — designing a deterministic, offline-by-default execution path so the system is
  testable and gradeable without credentials, while keeping a production path behind a single environment variable
- **FastAPI Deployment** — exposing typed request and response models, enforcing the contract with `response_model`, and
  separating transport concerns from orchestration logic
- **Docker Containerization** — installing CPU-only PyTorch to control image size, precomputing the vector store at
  build time for fast cold starts, and excluding secrets from the build context with `.dockerignore`
- **Verification Discipline** — proving offline behavior by blocking sockets rather than assuming it, and testing
  failure paths with stubbed clients instead of live API calls
  </content>
