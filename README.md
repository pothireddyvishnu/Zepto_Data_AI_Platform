# Zepto Data & AI Platform

An end-to-end capstone project spanning three connected disciplines: a **data engineering pipeline** that turns raw
scraped web data into a clean normalized relational store, an **analytics pipeline** that profiles and models a
customer-style dataset from raw data to a deployment-ready model, and a **GenAI support assistant** that answers
customer-policy questions grounded in Zepto's own documents through a containerized RAG service.

---

## Project Overview

The platform is organized as three independent but thematically connected modules, each representing a distinct layer of
a modern data organization:

| Layer            | Module               | What it demonstrates                                                                         |
| ---------------- | -------------------- | -------------------------------------------------------------------------------------------- |
| **Ingestion**    | `data_pipeline/`     | Raw web data → cleaned, transformed, normalized SQLite database, validated against pandas.   |
| **Intelligence** | `analytics/`         | Raw dataset → profiling, EDA, storytelling, classification, tuning, and a persisted model.   |
| **Application**  | `support_assistant/` | Unstructured policy text → embeddings → retrieval → grounded answers over a FastAPI service. |

Together they trace the full arc of a data product: **collect it, understand it, model it, and put it in front of a
user.** The first two modules are notebook-based analytical workflows; the third is a deployable HTTP service with a
typed API contract and a Docker image.

Every number, metric, and behavior documented in the module READMEs is derived from an actual executed run — nothing is
illustrative.

---

## Project Structure

| Directory            | Description                                                                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `data_pipeline/`     | Scrapes book catalog data from `books.toscrape.com`, cleans and enriches it, and loads it into a normalized SQLite database with SQL analysis.   |
| `analytics/`         | A two-notebook data science workflow on the Titanic dataset: profiling and EDA, then classification, imbalance handling, tuning, and regression. |
| `support_assistant/` | A Retrieval-Augmented Generation service over eight Zepto policy documents, orchestrated with LangGraph and served through FastAPI.              |

Each module carries its own detailed `README.md` covering its architecture, design decisions, results, and assumptions.

- [data_pipeline/README.md](data_pipeline/README.md)
- [analytics/README.md](analytics/README.md)
- [support_assistant/README.md](support_assistant/README.md)

---

## Project File Structure

```text
Capstone Project/
│
├── data_pipeline/
│   ├── zepto_catalog_workflow.ipynb   # End-to-end ETL notebook: scrape → clean → transform → load → query → validate
│   ├── books_catalog.db               # SQLite database produced by the notebook
│   └── README.md                      # Module documentation
│
├── analytics/
│   ├── 01_eda.ipynb                   # Profiling, missing-value handling, univariate/bivariate analysis, data story
│   ├── 02_modeling.ipynb              # Preprocessing pipeline, classifiers, imbalance handling, tuning, regression
│   ├── titanic.csv                    # Cleaned dataset (889 records) produced by 01_eda.ipynb
│   ├── best_model.pkl                 # Serialized scikit-learn Pipeline (preprocessing + Random Forest)
│   └── README.md                      # Module documentation
│
├── support_assistant/
│   ├── data/
│   │   ├── corpus/
│   │   │   ├── doc_01.txt             # Delivery Policy
│   │   │   ├── doc_02.txt             # Returns & Refunds
│   │   │   ├── doc_03.txt             # Membership Tiers
│   │   │   ├── doc_04.txt             # Order Tracking
│   │   │   ├── doc_05.txt             # Order Cancellation Policy
│   │   │   ├── doc_06.txt             # Damaged or Missing Items
│   │   │   ├── doc_07.txt             # Gift Cards
│   │   │   └── doc_08.txt             # Customer Support Hours
│   │   └── chroma/                    # Persisted ChromaDB store (regenerable build artifact)
│   ├── data_ingestion.py              # Corpus → chunks → embeddings → ChromaDB
│   ├── schemas.py                     # Pydantic request/response contracts (AskRequest / AskResponse)
│   ├── prompts.py                     # Structured prompt templates and builders
│   ├── graph_nodes.py                 # LangGraph node implementations + GraphState + MOCK_LLM flag
│   ├── graph.py                       # Graph assembly, conditional routing, run_graph()
│   ├── llm_client.py                  # Groq client with JSON parse + Pydantic validation retries
│   ├── main.py                        # FastAPI application (GET / and POST /ask)
│   ├── Dockerfile                     # Container definition (Python 3.11-slim, CPU-only torch, port 7860)
│   ├── .dockerignore                  # Excludes .env and build cruft from the image
│   ├── requirements.txt               # Module-specific dependencies
│   └── README.md                      # Module documentation
│
├── requirements.txt                   # Project-wide dependencies (all three modules)
├── .gitignore
└── README.md                          # This file
```

---

## Technology Stack

### Languages & Runtimes

| Technology   | Purpose                                                                      |
| ------------ | ---------------------------------------------------------------------------- |
| **Python 3** | Core runtime for all three modules.                                          |
| **SQL**      | Analytical querying against the SQLite catalog database.                     |
| **Jupyter**  | Interactive execution environment for the pipeline and analytics notebooks.  |
| **Docker**   | Containerization of the Support Assistant service (`python:3.11-slim` base). |

### Data Engineering

| Library          | Purpose                                                                                |
| ---------------- | -------------------------------------------------------------------------------------- |
| `requests`       | HTTP GET requests to the scrape target, wrapped in retry logic with back-off.          |
| `beautifulsoup4` | Parses HTML into a navigable tree using the `html.parser` backend.                     |
| `pandas`         | DataFrame construction, vectorized cleaning, transformation, and SQL cross-validation. |
| `sqlite3`        | Embedded, zero-config relational store for the normalized catalog (standard library).  |
| `numpy`          | Numerical backing for pandas operations.                                               |

### Analytics & Machine Learning

| Library            | Purpose                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------ |
| `scikit-learn`     | Preprocessing pipelines, classifiers, regression, evaluation metrics, GridSearchCV tuning. |
| `imbalanced-learn` | SMOTE oversampling for class-imbalance comparison.                                         |
| `seaborn`          | Statistical visualizations — histograms, boxplots, barplots, heatmaps, pairplots.          |
| `matplotlib`       | Base plotting framework and figure layout control.                                         |
| `joblib`           | Serialization and reloading of the complete trained pipeline.                              |

### GenAI & Services

| Library                 | Purpose                                                                                   |
| ----------------------- | ----------------------------------------------------------------------------------------- |
| `langgraph`             | State-machine orchestration of the RAG workflow with conditional intent routing.          |
| `chromadb`              | Persistent vector database with cosine-similarity semantic search.                        |
| `sentence-transformers` | `all-MiniLM-L6-v2` encoder producing 384-dimensional embeddings at index and query time.  |
| `fastapi`               | HTTP API layer declaring the `/ask` route with an enforced `response_model`.              |
| `uvicorn`               | ASGI server running the FastAPI app locally and in the container.                         |
| `pydantic`              | Schema definition and runtime validation of both the API contract and LLM-generated JSON. |
| `groq`                  | Client for the optional real-LLM generation path (`MOCK_LLM=0`).                          |
| `python-dotenv`         | Loads `GROQ_API_KEY` and `MOCK_LLM` from a local `.env` file.                             |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/pothireddyvishnu/Zepto_Data_AI_Platform.git
cd Zepto_Data_AI_Platform
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

The project-level `requirements.txt` covers all three modules:

```bash
pip3 install -r requirements.txt
```

To install only the Support Assistant's dependencies:

```bash
pip3 install -r support_assistant/requirements.txt
```

### 4. Install Jupyter (for the notebook modules)

```bash
pip3 install jupyter
```

---

## Running the Project

The three modules are independent and can be run in any order.

### Data Pipeline

```bash
cd data_pipeline
jupyter notebook
```

Open `zepto_catalog_workflow.ipynb` and run all cells top-to-bottom (**Cell → Run All**). The notebook scrapes 304 books
across 4 categories, cleans and enriches them, creates `books_catalog.db`, executes 7 SQL queries, and cross-validates
the JOIN output against a pandas merge (`Equivalent Output: True`).

### Analytics

```bash
cd analytics
jupyter notebook
```

Run the notebooks in **strict sequential order** — the second consumes the CSV produced by the first:

```text
01_eda.ipynb  →  02_modeling.ipynb
```

`01_eda.ipynb` profiles, cleans, and explores the dataset and exports `titanic.csv`. `02_modeling.ipynb` builds the
preprocessing pipeline, trains and evaluates three classifiers, handles imbalance, tunes hyperparameters, runs the
regression side-task, and saves `best_model.pkl`.

### Support Assistant

`MOCK_LLM` defaults to mock mode, so **no API key is required** to run or evaluate this module.

**Local:**

```bash
cd support_assistant

# 1. Build the vector store (run once — required before serving)
python3 data_ingestion.py

# 2. Serve the API
uvicorn main:app --reload
```

Available at `http://127.0.0.1:8000`, with interactive docs at `/docs`.

**Docker:**

```bash
cd support_assistant

docker build -t zepto-support .
docker run -p 7860:7860 zepto-support
```

The image runs ingestion at build time, so the vector store is baked in and no runtime ingestion step is needed. The
container serves on `http://127.0.0.1:7860`.

---

## Modules

### 1. Data Pipeline

**Problem Statement**

Zepto's analysts need a reliable way to benchmark catalog-style pricing and availability data **before** it ever reaches
a dashboard. Raw web data is messy: prices arrive as currency-prefixed strings, ratings are English words, and
availability is buried inside free-text labels. Without a structured pipeline, analysts would spend most of their time
wrangling data instead of analyzing it. This module delivers a clean, normalized, query-ready database from a raw web
source in a single reproducible run.

**Workflow**

| Stage                      | Input                | Processing                                                                                                                           | Output             |
| -------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------ |
| **1. Web Scraping**        | `books.toscrape.com` | Extracts book details from 4 selected categories with `requests` + `BeautifulSoup`, using retry logic and pagination-aware crawling. | Raw book data      |
| **2. Data Cleaning**       | Raw book data        | Strips currency symbols, maps word ratings to integers, reduces availability to a binary flag, and median-imputes parse failures.    | Clean DataFrame    |
| **3. Data Transformation** | Clean DataFrame      | Converts prices GBP → INR at a fixed rate (`1 GBP = 105.50 INR`), preserving the source value.                                       | Enriched dataset   |
| **4. Database Loading**    | Transformed data     | Decomposes the flat frame into normalized `categories` and `books` tables linked by a foreign key, loaded via `executemany()`.       | `books_catalog.db` |
| **5. SQL Analysis**        | SQLite database      | Runs 7 queries exercising `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT`, `IN`, `BETWEEN`, and `INNER JOIN`.                               | Query results      |
| **6. Validation**          | SQL query output     | Reproduces the JOIN with `pd.merge()` and compares via `.equals()`.                                                                  | Validated output   |

**Result:** 304 books across 4 categories in a normalized two-table database, with SQL and pandas outputs confirmed
equivalent.

---

### 2. Analytics

**Problem Statement**

Given the Titanic passenger manifest, the objective is to profile and clean the dataset, extract meaningful patterns
through exploratory analysis, and build classification models that predict passenger survival. A secondary regression
task predicts passenger fare. The workflow evaluates multiple modeling strategies, addresses class imbalance, tunes
hyperparameters, and persists the best-performing pipeline for downstream consumption.

**Workflow**

| Stage                 | Description                                                                               | Output                       |
| --------------------- | ----------------------------------------------------------------------------------------- | ---------------------------- |
| Dataset Loading       | Load the Titanic dataset from Seaborn and persist as CSV.                                 | `titanic.csv` (raw)          |
| Profiling             | Examine shape, dtypes, summary statistics, and missing values.                            | Profiling report             |
| Cleaning              | Threshold-based missing-value strategy: drop rows, impute, or drop the column.            | Cleaned DataFrame (889 rows) |
| EDA — Univariate      | Histograms, boxplots, and IQR outlier detection for `age` and `fare`.                     | Distribution insights        |
| EDA — Bivariate       | Survival rates by sex, class, and sex × class; correlation matrix.                        | Survival-rate tables         |
| Storytelling          | Five sequenced visualizations with written interpretations.                               | Multivariate data narrative  |
| Preprocessing         | Imputation, encoding, and scaling via `ColumnTransformer` + `Pipeline`.                   | Transformed feature matrices |
| Classification        | Train Logistic Regression, Decision Tree, and Random Forest on the same stratified split. | Three fitted pipelines       |
| Evaluation            | Accuracy, Precision, Recall, F1, AUC, confusion matrices, ROC curves.                     | Comparison table             |
| Imbalance Handling    | Baseline vs. `class_weight='balanced'` vs. SMOTE.                                         | Imbalance comparison table   |
| Hyperparameter Tuning | GridSearchCV on Random Forest across estimators, depth, and feature strategy.             | Best params, CV & OOB scores |
| Regression            | Linear Regression predicting fare; MAE, RMSE, R², Adjusted R², residual diagnostics.      | Regression evaluation table  |
| Pipeline Saving       | Serialize the best pipeline with Joblib; reload and verify.                               | `best_model.pkl`             |

**Result:** Random Forest selected for deployment — highest test accuracy (0.8202) and F1 (0.7576), with the complete
preprocessing + estimator pipeline serialized so raw data can be passed straight to `predict()`.

---

### 3. Support Assistant

**Problem Statement**

Zepto customer support receives repetitive questions whose answers already exist in published policy documents —
delivery timelines, return windows, membership tiers, cancellation rules, and so on. The objective is to build a service
that accepts a natural-language question, decides whether it is a policy question at all, retrieves the most semantically
relevant policy passages when it is, and returns a concise answer alongside the source documents it drew from and a
confidence score. Queries unrelated to Zepto policy must be declined rather than answered from general knowledge, and the
entire system must run and be graded without requiring a paid LLM API key.

**Workflow**

| Stage                      | Description                                                                                                                                                            | Output                           |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| **1. Ingestion**           | `DocumentIngestor` loads the 8 `.txt` policy documents in sorted order, skipping empties, and assigns IDs from filenames.                                              | Document chunks                  |
| **2. Embedding & Storage** | Chunks encoded with `all-MiniLM-L6-v2` (384-dim) and upserted into the `zepto_policies` ChromaDB collection with cosine distance.                                      | Persisted vector store           |
| **3. Intent Routing**      | `classify_intent` labels the query `policy_question` or `general_question`; a LangGraph conditional edge routes accordingly, defaulting safely on unrecognized labels. | Routed execution branch          |
| **4a. Retrieve & Answer**  | Policy questions: query embedded with the same encoder, top-3 chunks retrieved, and a grounded answer generated from them.                                             | Answer + source IDs + confidence |
| **4b. Direct Answer**      | General questions: declined without touching the vector store.                                                                                                         | Refusal response                 |
| **5. Validation**          | Output parsed and validated against `AskResponse`; on the real-LLM path, failures retry with error feedback before a graceful fallback.                                | Pydantic-validated JSON          |

**Execution modes** — retrieval and embedding are identical in both; only classification and generation change:

| Mode               | Classification                     | Generation                                       | Network        |
| ------------------ | ---------------------------------- | ------------------------------------------------ | -------------- |
| **Mock (default)** | Keyword substring matching         | Canned snippet from the top retrieved chunk      | None; no key   |
| **`MOCK_LLM=0`**   | LLM one-word classification prompt | Groq-generated JSON validated against the schema | Groq API + key |

**Result:** A working containerized RAG service returning `{ answer, sources[], confidence }`. Verified locally under
both Docker and uvicorn, and on the real-LLM path against the Groq free tier. Not deployed publicly — free hosting tiers
OOM-kill the image while loading the encoder and Chroma store, so the graded baseline is local containerization.

---

## Learning Outcomes

### Data Engineering

- **Web Scraping** — building resilient scrapers with retry logic and back-off, custom headers, pagination-aware
  crawling, and structured field extraction from HTML.
- **Data Cleaning & Transformation** — type casting, string manipulation, dictionary-based mapping, boolean parsing, and
  outlier-resistant median imputation on a pipeline that must not halt on bad input.
- **Relational Database Design** — normalization into fact and dimension tables, primary/foreign key relationships,
  referential integrity, and idempotent schema creation.
- **SQL Querying** — filtering, sorting, limiting, distinct selection, set membership, range filtering, and multi-table
  joins against a live database.
- **Cross-Validation of Results** — reproducing SQL output with pandas operations as a lightweight integration test,
  reinforcing that both tools operate on the same relational algebra.
- **Pipeline Architecture** — separating fetch, parse, clean, transform, load, and validate into distinct, auditable
  stages.

### Analytics & Machine Learning

- **Data Profiling** — assessing dataset quality through shape, dtypes, summary statistics, and missingness analysis.
- **Threshold-Based Cleaning** — applying rule-driven strategies (drop rows, impute, drop column) scaled to missingness
  severity.
- **Univariate & Bivariate Analysis** — characterizing distributions with histograms, boxplots, and IQR outlier
  detection; quantifying group differences and linear relationships.
- **Visual Storytelling** — constructing a multivariate narrative through sequenced visualizations with written
  interpretations.
- **Leakage-Free Preprocessing** — composing `ColumnTransformer` and `Pipeline` so test-set statistics never influence
  training.
- **Classification Modeling & Evaluation** — comparing linear, tree-based, and ensemble models on a stratified split;
  interpreting confusion matrices, precision–recall trade-offs, F1, and ROC-AUC.
- **Class Imbalance Handling** — comparing baseline, class weighting, and SMOTE, and recognizing when resampling is not
  warranted.
- **Hyperparameter Tuning** — systematic parameter search with GridSearchCV and cross-validation, including reading OOB
  estimates.
- **Regression Analysis** — computing MAE, RMSE, R², and Adjusted R², and diagnosing heteroscedasticity from residual
  plots.
- **Model Persistence** — serializing complete pipelines with Joblib so raw data can be passed directly to `predict()`
  at inference time.

### GenAI & Deployment

- **RAG Pipeline Design** — composing ingestion, embedding, vector persistence, semantic retrieval, and grounded
  generation into a single request path, with a shared encoder guaranteeing comparable vector spaces.
- **Vector Database Operations** — persisting embeddings with ChromaDB, choosing cosine similarity for normalized
  sentence embeddings, attaching queryable metadata, and building idempotent ingestion.
- **State Orchestration with LangGraph** — modeling a multi-step workflow as a typed `StateGraph`, implementing nodes as
  pure state transformations, and branching through conditional edges with a safe routing fallback.
- **Structured Prompt Engineering** — building prompts from an explicit Role/Context/Task/Format/Length skeleton,
  reinforcing grounding with negative constraints, and steering output shape with few-shot examples.
- **Schema Validation with Retries** — treating LLM output as untrusted input that must be parsed, validated, and
  repaired through error-feedback retries with a graceful terminal fallback.
- **Environment-Based Mode Toggling** — designing a deterministic, offline-by-default path so the system is testable
  without credentials, while keeping the production path behind a single environment variable.
- **API Development with FastAPI** — exposing typed request and response models, enforcing contracts with
  `response_model`, and separating transport concerns from orchestration logic.
- **Docker Containerization** — installing CPU-only PyTorch to control image size, precomputing the vector store at
  build time for fast cold starts, and excluding secrets from the build context.
