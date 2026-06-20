# Financial Intelligence Platform

A Retrieval-Augmented Generation (RAG) platform for extracting insights from documents. Upload PDFs, DOCX, TXT, CSV, or XLSX files and ask natural-language questions. The system retrieves relevant passages, generates grounded answers, and cites its sources.

> **Note:** Although the name references financial intelligence, the platform is domain-agnostic and works well with reports, books, manuals, research papers, and other long-form documents.

---

## Features

- **Document ingestion** — Supports PDF, DOCX, TXT, CSV, and XLSX.
- **OCR fallback** — Automatically runs Tesseract OCR on scanned/image-based PDFs when embedded text is sparse.
- **Hybrid retrieval** — Combines dense vector search (Qdrant) with BM25-style full-text search (PostgreSQL) and reciprocal rank fusion.
- **Re-ranking** — Optional Cohere reranker for improved result ordering.
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
| Embeddings | OpenAI or NVIDIA NIM |
| Generation | OpenAI or NVIDIA NIM |
| Reranking | Cohere (optional) |
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
- (Optional but recommended for scanned PDFs) [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

### 1. Clone and create the virtual environment

```bash
cd financial-intelligence-platform
python -m venv venv
```

On Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

On Linux/macOS/Git Bash:

```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/financial_intelligence
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333

# Embedding provider: openai or nvidia
EMBEDDING_PROVIDER=nvidia
EMBEDDING_DIMENSIONS=1024

OPENAI_API_KEY=your-openai-key
NVIDIA_API_KEY=your-nvidia-key

# Generation provider: openai or nvidia
GENERATION_PROVIDER=nvidia

# Optional reranker
COHERE_API_KEY=your-cohere-key
```

### 4. Start infrastructure services

```bash
docker-compose up -d
```

This starts PostgreSQL, Redis, and Qdrant.

### 5. Create database tables

On Windows PowerShell:

```powershell
python scripts/create_tables.py
```

On Linux/macOS/Git Bash:

```bash
python scripts/create_tables.py
```

### 6. Start the API server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 7. Start the Celery worker

In a second terminal:

```bash
# PowerShell
venv\Scripts\Activate.ps1
celery -A workers.celery_app.celery_app worker --loglevel=info -P solo

# Git Bash
source venv/Scripts/activate
celery -A workers.celery_app.celery_app worker --loglevel=info -P solo
```

### 8. Open the app

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
├── api/                    # FastAPI routers, schemas, dependencies
│   ├── dependencies/
│   ├── routes/
│   └── schemas/
├── core/                   # Configuration and logging
│   └── config/
├── db/                     # Database clients and models
│   ├── postgres/
│   └── qdrant/
├── docker/                 # Docker-related files
├── docs/                   # Documentation
├── frontend/               # Web UI (HTML/CSS/JS)
│   ├── css/
│   ├── js/
│   └── index.html
├── scripts/                # Utility scripts
│   ├── create_tables.py
│   └── ...
├── services/               # Business logic
│   ├── chunking/
│   ├── citations/
│   ├── embeddings/
│   ├── evaluation/
│   ├── generation/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── reranking/
│   └── retrieval/
├── storage/uploads/        # Uploaded files
├── tests/                  # Test suite
│   ├── evaluation/
│   ├── integration/
│   └── unit/
├── workers/                # Celery workers
│   ├── celery_app.py
│   └── tasks/
├── docker-compose.yml
├── main.py                 # FastAPI application entry point
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
| `COHERE_API_KEY` | Optional Cohere reranker key | — |
| `COHERE_RERANK_MODEL` | Cohere rerank model | `rerank-v3.5` |

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'db'` when running scripts

The script path is added to `sys.path` instead of the project root. Run as a module:

```bash
python -m scripts.create_tables
```

or use the updated `scripts/create_tables.py` which adds the project root automatically.

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
