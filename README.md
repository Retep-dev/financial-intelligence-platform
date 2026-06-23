# Financial Intelligence Platform

A Retrieval-Augmented Generation (RAG) platform for extracting insights from documents. Upload PDFs, DOCX, TXT, CSV, or XLSX files and ask natural-language questions. The system retrieves relevant passages, generates grounded answers, and cites its sources.

> **Note:** Although the name references financial intelligence, the platform is domain-agnostic and works well with reports, books, manuals, research papers, and other long-form documents.

---

## Features

- **Document ingestion** — Supports PDF, DOCX, TXT, CSV, and XLSX.
- **OCR fallback** — Automatically runs Tesseract OCR on scanned/image-based PDFs when embedded text is sparse.
- **Hybrid retrieval** — Combines dense vector search (Qdrant) with BM25-style full-text search (PostgreSQL) and reciprocal rank fusion.
- **Re-ranking** — Cohere reranker for improved result ordering.
- **Grounded answers** — LLM-generated answers with citation markers linked back to source chunks.
- **Web UI** — Clean, responsive frontend at `/app` for drag-and-drop upload and chat.
- **REST API** — Full OpenAPI/Swagger documentation at `/docs`.
- **Health monitoring** — `/health` endpoint reports API, database, and vector-store status.
- **Evaluation framework** — Built-in metrics (recall@k, precision@k, citation accuracy) and runner for benchmarking retrieval quality.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI + Uvicorn |
| Database | PostgreSQL 16 |
| Vector Store | Qdrant |
| Task Queue | Redis + Celery |
| Embeddings | NVIDIA NIM (`nvidia/nv-embedqa-e5-v5`) |
| Generation | NVIDIA NIM (`meta/llama-3.1-70b-instruct`) |
| Reranking | Cohere (`rerank-v3.5`) |
| OCR | Tesseract + pytesseract + PyMuPDF |
| Frontend | Vanilla HTML/CSS/JS |
| Testing | pytest |

---

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│  Web UI     │      │  FastAPI     │      │  Celery Worker  │
│  /app       │─────▶│  /documents  │─────▶│  parse/chunk/   │
│  /static    │      │  /queries    │      │  embed/upsert   │
└─────────────┘      └──────────────┘      └─────────────────┘
                              │                       │
                              ▼                       ▼
                       ┌──────────────┐      ┌──────────────┐
                       │  PostgreSQL  │      │   Qdrant     │
                       │  documents   │      │  vectors     │
                       │  chunks      │      │  payloads    │
                       └──────────────┘      └──────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │    Redis     │
                       │    broker    │
                       └──────────────┘
```

### Request Flow

1. **Upload** — `POST /documents/upload` saves the file, creates a DB record, and enqueues a Celery task.
2. **Process** — The worker parses the document, splits it into chunks, generates embeddings, and stores them in PostgreSQL and Qdrant.
3. **Ask** — `POST /queries/ask` enhances the query, runs hybrid retrieval, reranks chunks, and generates a cited answer.
4. **Search** — `POST /queries/search` returns raw retrieved chunks without LLM generation.

---

## Quick Start

### Prerequisites

- Python 3.12+
- Docker + Docker Compose
- NVIDIA API key (for embeddings and generation)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (for scanned/image-based PDFs)

> **Note:** OpenAI can be used instead of NVIDIA NIM by changing `EMBEDDING_PROVIDER` and `GENERATION_PROVIDER` to `openai` and providing an `OPENAI_API_KEY`. The default setup described here uses NVIDIA NIM.

### 1. Clone the repository

```bash
git clone https://github.com/Retep-dev/financial-intelligence-platform.git
cd financial-intelligence-platform
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

If you get an execution-policy error, run once as administrator:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Git Bash / Linux / macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the package in editable mode

```bash
pip install -e .
```

This registers the `financial_intelligence_platform` package so all scripts and tests can import it correctly.

### 5. Configure environment variables

Create a `.env` file in the project root with your NVIDIA API key:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/financial_intelligence
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333

# NVIDIA NIM (default)
EMBEDDING_PROVIDER=nvidia
EMBEDDING_DIMENSIONS=1024
NVIDIA_API_KEY=your-nvidia-api-key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_EMBEDDING_MODEL=nvidia/nv-embedqa-e5-v5

GENERATION_PROVIDER=nvidia
NVIDIA_GENERATION_MODEL=meta/llama-3.1-70b-instruct

# Cohere reranker
COHERE_API_KEY=your-cohere-api-key
```

Replace `your-nvidia-api-key` with your actual key from [build.nvidia.com](https://build.nvidia.com).

### 6. Start infrastructure services

```bash
docker-compose up -d
```

This starts PostgreSQL, Redis, and Qdrant.

### 7. Create database tables

On Windows PowerShell:

```powershell
python scripts/create_tables.py
```

On Linux/macOS/Git Bash:

```bash
python scripts/create_tables.py
```

### 8. Start the API server

```bash
uvicorn financial_intelligence_platform.main:app --host 0.0.0.0 --port 8000
```

### 9. Start the Celery worker

In a second terminal:

```bash
# PowerShell
venv\Scripts\Activate.ps1
celery -A financial_intelligence_platform.workers.celery_app.celery_app worker --loglevel=info -P solo

# Git Bash
source venv/Scripts/activate
celery -A financial_intelligence_platform.workers.celery_app.celery_app worker --loglevel=info -P solo
```

### 10. Open the app

- **Web UI:** http://localhost:8000/app
- **API docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

---

## Usage

### Using the Web UI

1. Open `http://localhost:8000/app`.
2. Drag a document into the upload zone or click to browse.
3. Wait until the document status shows **Ready**.
4. Type a question and press Enter.
5. Expand **Show sources** on the assistant’s answer to see cited chunks.

### Using the API

**Upload a document:**

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

**Ask a question:**

```bash
curl -X POST "http://localhost:8000/queries/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main revenue driver?",
    "top_k": 50,
    "top_n": 10,
    "use_llm": true
  }'
```

**Search chunks only:**

```bash
curl -X POST "http://localhost:8000/queries/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "revenue Q1 2024",
    "top_k": 50,
    "top_n": 10
  }'
```

---

## OCR Support

Scanned PDFs and image-heavy documents require OCR. The system uses:

- **PyMuPDF** (`fitz`) to extract embedded text.
- **Tesseract OCR** (`pytesseract`) as a fallback when the extracted text is too short or the page appears to be mostly images.

### Installing Tesseract

- **Windows:** Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and add it to your system PATH.
- **macOS:** `brew install tesseract`
- **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`

After installing, verify with:

```bash
tesseract --version
```

If Tesseract is not available, the system will still process standard text-based PDFs, but scanned PDFs may return empty or low-quality results.

---

## Testing

Run the full test suite:

```bash
pytest tests/ -v
```

Run only unit tests:

```bash
pytest tests/unit -v
```

Run only integration tests (requires Docker services):

```bash
pytest tests/integration -v
```

---

## Project Structure

```
financial-intelligence-platform/
├── src/
│   └── financial_intelligence_platform/   # Application package
│       ├── main.py                        # FastAPI entry point
│       ├── api/                           # FastAPI routers, schemas, dependencies
│       │   ├── dependencies/
│       │   ├── routes/
│       │   └── schemas/
│       ├── core/                          # Configuration and logging
│       │   └── config/
│       ├── db/                            # Database clients and models
│       │   ├── postgres/
│       │   └── qdrant/
│       ├── services/                      # Business logic
│       │   ├── chunking/
│       │   ├── citations/
│       │   ├── embeddings/
│       │   ├── evaluation/
│       │   ├── generation/
│       │   ├── ingestion/
│       │   ├── preprocessing/
│       │   ├── reranking/
│       │   └── retrieval/
│       └── workers/                       # Celery workers
│           ├── celery_app.py
│           └── tasks/
├── alembic/                               # Database migrations
├── docker/                                # Docker-related files
├── docs/                                  # Documentation
├── frontend/                              # Web UI (HTML/CSS/JS)
│   ├── css/
│   ├── js/
│   └── index.html
├── scripts/                               # Utility scripts
│   ├── create_tables.py
│   └── ...
├── storage/uploads/                       # Uploaded files
├── tests/                                 # Test suite
│   ├── evaluation/
│   ├── integration/
│   └── unit/
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Configuration Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | — |
| `REDIS_URL` | Redis connection string | — |
| `QDRANT_URL` | Qdrant URL | `http://localhost:6333` |
| `EMBEDDING_PROVIDER` | `openai` or `nvidia` | `nvidia` |
| `EMBEDDING_DIMENSIONS` | Vector dimensionality | `1024` |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `OPENAI_EMBEDDING_MODEL` | OpenAI embedding model | `text-embedding-3-large` |
| `NVIDIA_API_KEY` | NVIDIA API key | — |
| `NVIDIA_EMBEDDING_MODEL` | NVIDIA embedding model | `nvidia/nv-embedqa-e5-v5` |
| `GENERATION_PROVIDER` | `openai` or `nvidia` | `nvidia` |
| `OPENAI_GENERATION_MODEL` | OpenAI chat model | `gpt-4o-mini` |
| `NVIDIA_GENERATION_MODEL` | NVIDIA chat model | `meta/llama-3.1-70b-instruct` |
| `COHERE_API_KEY` | Cohere reranker key | — |
| `COHERE_RERANK_MODEL` | Cohere rerank model | `rerank-v3.5` |

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'financial_intelligence_platform'` when running scripts

The package is not installed or not on `PYTHONPATH`. Run:

```bash
pip install -e .
```

Then try the script again.

### Upload succeeds but the answer says “I do not have enough information”

1. Check that the Celery worker is running and finished processing the document.
2. Verify OCR is installed if the PDF is scanned: `tesseract --version`.
3. Test raw retrieval with `POST /queries/search` to see if chunks are returned.
4. Check worker logs for parsing or embedding errors.

### `/app` does not load in the browser

1. Ensure Uvicorn is running and shows `Uvicorn running on http://0.0.0.0:8000`.
2. Check that Qdrant collection validation passed on startup.
3. Verify `docker-compose up -d` is running.
4. Try `curl http://localhost:8000/health`.

### PowerShell activation fails

Use the PowerShell-specific activation script:

```powershell
venv\Scripts\Activate.ps1
```

If you get an execution-policy error, run once as administrator:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## License

This project is licensed under the terms of the included LICENSE file.
