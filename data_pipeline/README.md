# Data Pipeline

A data engineering pipeline that scrapes, cleans, transforms, and loads book catalog data into a normalized relational
database, demonstrating the kind of raw-to-relational workflow a competitive-intelligence or catalog-benchmarking team
would operate.

---

## Overview

This module is the **Data Pipeline** component of the **Zepto Data & AI Platform** capstone project. Its purpose is to
build the data foundation for the platform by collecting, cleaning, transforming, and storing catalog data that can be
consumed by the Analytics and Support Assistant modules.

The pipeline scrapes book catalog data from the public practice website **books.toscrape.com**, converts the raw HTML
into structured records, performs data cleaning and enrichment, and loads the processed data into a normalized SQLite
database. The resulting database serves as the single source of truth for analytical SQL queries in this module and
provides a structured dataset that can be extended for downstream analytics and AI-driven applications.

The entire workflow is implemented in a single Jupyter Notebook (`zepto_catalog_workflow.ipynb`), demonstrating a
complete end-to-end ETL process—from data extraction to validation—in a reproducible and easy-to-understand pipeline.

---

## Problem Statement

Zepto's analysts need a reliable way to benchmark catalog-style pricing and availability data **before** it ever reaches
a dashboard. Raw web data is messy: prices arrive as currency-prefixed strings, ratings are English words, and
availability is buried inside free-text labels. Without a structured pipeline, analysts would spend most of their time
wrangling data instead of analyzing it.

This module solves that problem by delivering a **clean, normalized, query-ready database** from a raw web source in a
single reproducible run.

---

## Features

### Resilient Web Scraping

The scraper uses a dedicated `get_page()` helper that wraps every HTTP request with configurable retry logic (3 attempts
by default) and a 1-second back-off delay between retries. A custom `User-Agent` header is sent with every request to
reduce the chance of being blocked by basic bot-detection. If all retries are exhausted, the function returns `None`
rather than raising an exception, allowing the caller to decide how to handle the failure.

### Pagination-Aware Category Crawling

A separate `get_category_book_urls()` function handles multipage category listings. It follows the "next" pagination
link until no more pages remain, collecting every book URL across all pages of a category. This separation keeps the
scraping logic modular — the page-fetching concern is isolated from the URL-collection concern.

### Structured Data Cleaning

Raw scraped fields are transformed into analysis-ready types through a series of deterministic steps: the `£` currency
symbol is stripped and the price cast to `float`; English-word ratings (`"One"` through `"Five"`) are mapped to integers
`1–5` via a lookup dictionary; and the free-text availability string is reduced to a binary `1`/`0` flag by checking for
the substring `"in stock"`.

### Graceful Handling of Parsing Failures

Numeric fields (`price_gbp`, `rating`) use **median imputation** when parsing fails (`errors='coerce'` produces `NaN`,
which is then filled with the column median). The median was chosen over the mean because it is resistant to outlier
distortion. Rows missing essential text fields (`title` or `category`) are dropped entirely, since those values cannot
be reliably inferred and are required for any meaningful analysis.

### Fixed-Rate Currency Conversion

Book prices are converted from GBP to INR using a project-defined constant (`1 GBP = 105.50 INR`). The converted price
is stored alongside the original, preserving the source value for auditability.

### Normalized Relational Database

The flat DataFrame is decomposed into two tables — `categories` and `books` — linked by a foreign key. This eliminates
category-name duplication across hundreds of book rows and enforces referential integrity at the storage layer.

### SQL and Pandas Cross-Validation

Seven distinct SQL queries exercise the database (filtering, sorting, limiting, distinct selection, set membership,
range filtering, and multi-table joins). The JOIN result is independently reproduced using `pd.merge()`, and the two
outputs are compared with `DataFrame.equals()` to confirm equivalence — a lightweight but effective integration test.

---

## Project Workflow

| Stage                      | Input                | Processing                                                                                     | Output             |
|----------------------------|----------------------|------------------------------------------------------------------------------------------------|--------------------|
| **1. Web Scraping**        | `books.toscrape.com` | Extracts book details from the selected categories using `Requests` and `BeautifulSoup`.       | Raw book data      |
| **2. Data Cleaning**       | Raw book data        | Cleans prices, converts ratings, standardizes stock availability, and handles missing values.  | Clean DataFrame    |
| **3. Data Transformation** | Clean DataFrame      | Converts book prices from GBP to INR using a fixed exchange rate.                              | Enriched dataset   |
| **4. Database Loading**    | Transformed data     | Loads the cleaned data into a normalized SQLite database with `categories` and `books` tables. | `books_catalog.db` |
| **5. SQL Analysis**        | SQLite database      | Executes SQL queries to analyze the stored data.                                               | Query results      |
| **6. Validation**          | SQL query output     | Compares SQL JOIN results with a Pandas merge to verify data consistency.                      | Validated output   |

---

## Folder Structure

```text
data_pipeline/
│
├── zepto_catalog_workflow.ipynb   # End-to-end pipeline notebook (47 cells)
├── books_catalog.db               # SQLite database produced by the notebook
└── README.md                      # This documentation
```

| File                           | Purpose                                                                                                                                                                                                |
|--------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `zepto_catalog_workflow.ipynb` | The complete pipeline implementation — scraping, cleaning, transformation, database creation, data loading, SQL querying, and pandas validation. Designed to be run top-to-bottom in a single session. |
| `books_catalog.db`             | The SQLite database generated by the notebook. Contains two tables (`categories`, `books`) holding 4 categories and 304 book records. Can be queried independently with any SQLite client.             |
| `README.md`                    | Technical documentation for this module.                                                                                                                                                               |

---

## Technology Stack

| Technology         | Purpose                                                                                                                                                                     |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Python**         | Core runtime for all pipeline logic.                                                                                                                                        |
| **Requests**       | Sends HTTP GET requests to the target website. Chosen for its simple API and built-in status-code handling (`raise_for_status()`).                                          |
| **BeautifulSoup4** | Parses HTML responses into a navigable tree. Used with the `html.parser` backend (no external C dependency required).                                                       |
| **pandas**         | Structures scraped data into DataFrames for vectorised cleaning, transformation, and cross-validation against SQL query results via `pd.read_sql()` and `pd.merge()`.       |
| **SQLite3**        | Embedded relational database. Part of Python's standard library — no server setup, no credentials, zero-config. Ideal for a self-contained pipeline that must run anywhere. |
| **time**           | Provides `time.sleep()` for the retry back-off delay between failed HTTP requests.                                                                                          |
| **urllib.parse**   | `urljoin()` resolves relative URLs (pagination links, book detail paths) against the base URL to produce absolute URLs.                                                     |

> **Note:** `NumPy` is listed in the project-level `requirements.txt` but is **not directly imported** in this notebook.
> It is an indirect dependency of pandas.

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

```bash
pip3 install -r requirements.txt
```

The `requirements.txt` at the project root includes `requests`, `beautifulsoup4`, `pandas`, and other project-wide
dependencies.

### 4. Install Jupyter (if not already present)

```bash
pip3 install jupyter
```

---

## Running the Project

1. Navigate to the `data_pipeline/` directory:

   ```bash
   cd data_pipeline
   ```

2. Launch Jupyter Notebook:

   ```bash
   jupyter notebook
   ```

3. Open `zepto_catalog_workflow.ipynb` in your browser.

4. Run all cells sequentially (**Cell → Run All**).

**What the notebook produces:**

- Scrapes **304 books** across 4 selected categories from `books.toscrape.com`.
- Cleans, transforms, and enriches the dataset with INR pricing.
- Creates (or overwrites) `books_catalog.db` with two normalized tables.
- Executes 7 SQL queries and prints their row counts.
- Cross-validates the SQL JOIN output against a pandas merge, confirming `Equivalent Output: True`.
- Closes the SQLite connection cleanly.

---

## Data Pipeline Architecture

### 1. Web Scraping

**What the code does**

The pipeline targets [books.toscrape.com](https://books.toscrape.com/), a public scraping-practice site that hosts 1,000
books across 50 categories.

Three distinct functions handle scraping:

| Function                               | Responsibility                                                                                                                                                                                                                                                                                                                      |
|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `get_page(url, retries=3, delay=1)`    | Sends a GET request with a spoofed `User-Agent` header. On failure, retries up to 3 times with a 1-second sleep between attempts. Returns the `Response` object on success or `None` after exhausting retries.                                                                                                                      |
| `get_category_book_urls(category_url)` | Given a category landing page, collects all `<article class="product_pod">` book links. Follows the `<li class="next">` pagination link recursively until no more pages exist, accumulating absolute URLs via `urljoin()`.                                                                                                          |
| `get_book_details(book_url)`           | Visits a single book's detail page and extracts five fields: `title` (from `<h1>`), `price` (from `<p class="price_color">`), `star_rating` (from the CSS class on `<p class="star-rating">`), `availability` (from `<p class="instock availability">`), and `category` (from the breadcrumb trail, specifically the third `<li>`). |

**Why this implementation**

- **`requests` over Selenium**: The target site is static HTML with no JavaScript rendering. Using a headless browser
  would add unnecessary overhead and complexity. `requests` + `BeautifulSoup` is the lightest-weight option that gets
  the job done.
- **Custom User-Agent**: Basic bot-detection often rejects the default `python-requests` user-agent string. Spoofing a
  Chrome-like header avoids that without resorting to a full browser stack.
- **Retry with back-off**: Network requests are inherently unreliable. The retry wrapper prevents transient failures
  (DNS timeouts, server 503s) from killing a long-running scrape. The 1-second delay prevents hammering the server on
  consecutive failures.
- **Separation of concerns**: Pagination logic lives in `get_category_book_urls()`, not inside the detail scraper. This
  means the detail scraper can be reused independently, and pagination behavior can be modified without touching the
  field-extraction code.

**Category selection**

The notebook does not scrape all 50 categories. It explicitly selects four:

```python
selected_categories = ['Sequential Art', 'Fiction', 'Nonfiction', 'Young Adult']
```

This produces **304 books** — a dataset large enough to demonstrate every pipeline stage without requiring a 20-minute
scrape of the full site.

---

### 2. Data Cleaning

**What the code does**

The raw list of dictionaries is loaded into a pandas DataFrame (`books_df`), then a working copy (`books_df_clean`) is
created to preserve the original data.

| Transformation | Raw Value                   | Cleaned Value   | Method                                                                        |
|----------------|-----------------------------|-----------------|-------------------------------------------------------------------------------|
| Price          | `"£52.29"`                  | `52.29` (float) | `str.replace('£', '')` → `astype(float)` via `pd.to_numeric(errors='coerce')` |
| Star rating    | `"Five"`                    | `5` (int)       | Lowercase → dictionary lookup `{"one": 1, ..., "five": 5}` via `.map()`       |
| Availability   | `"In stock (19 available)"` | `1` (int)       | `.str.contains('in stock')` → `.astype(int)`                                  |

After transformation, the original columns (`price`, `star_rating`, `availability`) are dropped, leaving a clean schema:
`title`, `category`, `price_gbp`, `rating`, `in_stock`.

**Handling parsing failures**

```python
books_df_clean['price_gbp'] = books_df_clean['price_gbp'].fillna(books_df_clean['price_gbp'].median())
books_df_clean['rating'] = books_df_clean['rating'].fillna(books_df_clean['rating'].median())
```

- **Numeric columns**: `NaN` values (produced by `errors='coerce'` when parsing fails) are filled with the **column
  median**. The median is preferred over the mean because it is robust to outliers — a single extreme price would skew a
  mean-imputed value but leave the median unaffected.
- **Text columns**: Rows missing `title` or `category` would be dropped (the notebook's Markdown states this policy,
  though the current dataset does not contain such rows).

**Why these transformations**

The raw data is entirely string-typed and unsuitable for aggregation, filtering, or database storage. Converting prices
to floats enables arithmetic (currency conversion, range queries). Integer ratings enable sorting and aggregation. A
binary stock flag simplifies inventory filtering without forcing downstream consumers to parse free-text strings.

---

### 3. Currency Conversion

**What the code does**

A single constant defines the exchange rate:

```python
GBP_TO_INR_RATE = 105.50
```

The INR price is computed as a vectorized multiplication, rounded to two decimal places:

```python
books_df_clean['price_inr'] = (books_df_clean['price_gbp'] * GBP_TO_INR_RATE).round(2)
```

**Why a fixed rate**

- **Reproducibility**: A fixed rate guarantees that every run of the notebook produces identical INR prices. A live API
  call would introduce non-determinism, making it impossible to compare results across runs.
- **Simplicity**: Calling an external currency API adds a network dependency, requires error handling, and may require
  an API key. For a pipeline whose primary purpose is demonstrating data engineering patterns, a hardcoded constant is
  the appropriate trade-off.
- **Auditability**: Both `price_gbp` and `price_inr` are stored side-by-side. Anyone reviewing the data can verify the
  conversion by dividing any INR value by 105.50.

**Limitations**

The fixed rate does not reflect real-time market fluctuations. In a production system, this constant would be replaced
with a rate fetched from a currency API at pipeline execution time, cached for the duration of the run.

---

### 4. Database Design

**What the code does**

The pipeline stores the processed data in a normalized SQLite database named **`books_catalog.db`**. The database
contains two related tables.

#### Categories Table

| Column          | Data Type | Description                      |
|-----------------|-----------|----------------------------------|
| `category_id`   | INTEGER   | Primary Key (Auto Increment)     |
| `category_name` | TEXT      | Category name (Unique, Not Null) |

#### Books Table

| Column        | Data Type | Description                                         |
|---------------|-----------|-----------------------------------------------------|
| `book_id`     | INTEGER   | Primary Key (Auto Increment)                        |
| `title`       | TEXT      | Book title                                          |
| `price_gbp`   | REAL      | Original price in GBP                               |
| `price_inr`   | REAL      | Converted price in INR                              |
| `rating`      | INTEGER   | Book rating (1–5)                                   |
| `in_stock`    | INTEGER   | Stock availability (1 = In Stock, 0 = Out of Stock) |
| `category_id` | INTEGER   | Foreign Key referencing `categories.category_id`    |

The database follows a normalized relational structure where each book references its category through a foreign key.
This minimizes duplicate category information while maintaining a clear relationship between books and their categories.

---

**Why SQLite**

- Included with Python's standard library.
- Requires no server installation or configuration.
- Stores the database in a single portable `.db` file.
- Suitable for lightweight analytical projects and educational pipelines.

---

**Why Normalization**

- Eliminates repeated category names.
- Reduces data redundancy.
- Maintains data consistency using foreign keys.
- Makes JOIN operations straightforward for SQL analysis.

---

**Why Auto-Increment Primary Keys**

Auto-incremented integer keys provide a unique identifier for every record without depending on business data such as
book titles or category names.

---

### 5. Data Loading

**What the code does**

1. **Categories first**: Unique category names are extracted from the DataFrame, sorted, and inserted into the
   `categories` table using `cursor.executemany()`.
2. **Build a mapping**: A `SELECT category_id, category_name FROM categories` query builds a Python dictionary
   (`category_map`) that maps each category name to its auto-generated integer ID.
3. **Books second**: Each book row is assembled into a tuple
   `(title, price_gbp, price_inr, rating, in_stock, category_id)` — the `category_id` is resolved via
   `category_map[row['category']]`. All 304 tuples are inserted in a single `executemany()` call.
4. **Commit after each stage**: `conn.commit()` is called after category insertion and again after book insertion,
   ensuring partial progress is persisted.

**Why categories are inserted first**

The `books` table has a foreign key referencing `categories(category_id)`. Inserting books before categories would
violate this constraint. By inserting categories first and building the ID mapping in memory, the pipeline resolves the
relationship without requiring a sub-query or a second pass.

**Why `executemany()`**

Inserting 304 rows one at a time with individual `execute()` calls would issue 304 separate SQL statements.
`executemany()` batches them into a single call, reducing round-trip overhead against the database engine.

---

### 6. SQL Queries

The notebook executes seven SQL queries against the loaded database. Each query demonstrates a different SQL capability
and serves a specific analytical purpose.

| # | SQL Concept                    | Query Summary                                                     | Business Value                                                                           | Rows Returned |
|---|--------------------------------|-------------------------------------------------------------------|------------------------------------------------------------------------------------------|---------------|
| 1 | `WHERE`                        | Books with `rating >= 4`                                          | Identify the highest-rated titles for merchandising or recommendation.                   | 124           |
| 2 | `ORDER BY` + `LIMIT`           | Top 20 books by `price_inr DESC`                                  | Spot the most expensive items in the catalog — useful for premium-tier segmentation.     | 20            |
| 3 | `WHERE` + `ORDER BY` + `LIMIT` | Top 20 books priced above ₹2,000                                  | Combines price filtering with ranking to isolate high-value, high-price products.        | 20            |
| 4 | `DISTINCT`                     | Unique category names                                             | Confirms the dimension table content and verifies deduplication.                         | 4             |
| 5 | `IN`                           | Books with rating in `(1, 3, 5)`                                  | Selects odd-numbered ratings — demonstrates set-based filtering for ad-hoc analysis.     | 191           |
| 6 | `BETWEEN`                      | Books priced ₹1,000–₹2,000                                        | Identifies the mid-range price segment for targeted promotions.                          | 53            |
| 7 | `INNER JOIN`                   | Books joined with categories, sorted by category → rating → title | Produces the full denormalized view — the canonical output for any downstream dashboard. | 304           |

**Cross-validation**

The Query 7 JOIN result is read into a pandas DataFrame via `pd.read_sql()`. Independently, the raw `books` and
`categories` tables are loaded and merged with `pd.merge(on="category_id", how="inner")`. Both DataFrames are sorted
identically and compared with `.equals()`, which returns `True` — confirming that the SQL engine and pandas produce the
same result.

---

## Design Decisions

| Decision                              | Reasoning                                                                                                                                                                                      |
|---------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Helper functions for HTTP**         | `get_page()` encapsulates retry logic, header injection, and error handling in one place. Every caller benefits from resilience without duplicating code.                                      |
| **Retry with sleep**                  | Network errors are transient by nature. Retrying 3 times with a 1-second delay handles the vast majority of intermittent failures without overwhelming the target server.                      |
| **Pagination in a separate function** | `get_category_book_urls()` handles the "crawl" concern (following `next` links) independently of the "extract" concern (`get_book_details()`). This makes each function testable in isolation. |
| **BeautifulSoup over Selenium**       | The target site is fully server-rendered HTML. A headless browser would add a heavy dependency (ChromeDriver, Selenium) for zero benefit.                                                      |
| **SQLite over PostgreSQL**            | No external server to install or configure. The `.db` file is portable and version-controllable. For a single-user analytical pipeline, SQLite is sufficient.                                  |
| **Normalization over flat table**     | Eliminates redundant category strings, prevents update anomalies, and enforces referential integrity.                                                                                          |
| **Fixed exchange rate**               | Ensures reproducibility across runs. A live API call would make outputs non-deterministic and add a network dependency to the transformation stage.                                            |
| **Integer ratings**                   | Enables arithmetic operations (mean, median, range queries) that are impossible on string values like `"Five"`.                                                                                |
| **Binary stock flag**                 | Reduces a verbose free-text string to a single bit of information. Downstream filters can check `WHERE in_stock = 1` instead of parsing text.                                                  |
| **Median imputation**                 | Outlier-resistant. A single £59.99 book would not distort the imputed value the way it would distort a mean.                                                                                   |
| **Working copy of DataFrame**         | `books_df_clean = books_df.copy()` preserves the original scraped data. If any cleaning step needs to be revised, the raw data is still available in memory without re-running the scrape.     |
| **`conn.close()` at the end**         | Explicitly closing the SQLite connection releases the file lock and flushes any buffered writes. The notebook prints a confirmation message to make this visible in the output.                |

---

## Assumptions

- The target website (`books.toscrape.com`) is available and returns a `200` status code during execution.
- The HTML structure of the site (CSS classes, breadcrumb layout, pagination markup) has not changed since the notebook
  was last run.
- The four selected categories (`Sequential Art`, `Fiction`, `Nonfiction`, `Young Adult`) exist on the site and contain
  the expected number of books.
- A fixed exchange rate of `1 GBP = 105.50 INR` is acceptable for the project's analytical purposes.
- The notebook is executed top-to-bottom in a single session. Re-running individual cells out of order (especially the
  insert cells) may cause duplicate-key errors.
- The Python environment has `requests`, `beautifulsoup4`, and `pandas` installed.

---

## Learning Outcomes

This project demonstrates the following data engineering concepts through hands-on implementation:

- **Web scraping** with `requests` and `BeautifulSoup`, including retry logic, pagination handling, and structured field
  extraction.
- **Data cleaning and transformation** using pandas — type casting, string manipulation, dictionary-based mapping, and
  boolean parsing.
- **Imputation strategies** for handling missing or malformed data in a pipeline that must not halt on bad input.
- **Relational database design** — normalization, primary/foreign key relationships, and schema idempotency with
  `IF NOT EXISTS`.
- **SQL querying** across a range of clause types (`WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT`, `IN`, `BETWEEN`, `JOIN`).
- **Cross-validation** of SQL results against pandas operations, reinforcing that both tools operate on the same
  relational algebra.
- **Pipeline architecture** — separating concerns (fetch, parse, clean, transform, load, validate) into distinct,
  auditable stages.
