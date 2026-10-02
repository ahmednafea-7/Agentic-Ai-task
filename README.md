# Product RAG Agent

A small Python Retrieval-Augmented Generation (RAG) assistant for product data.
It can scrape product listings, index them in ChromaDB, and answer product questions with Gemini.

## What the agent does

The agent workflow is:
1. Load product records from `products.json`
2. Build/search a local ChromaDB vector store
3. Retrieve relevant product chunks for a user question
4. Ask Gemini to answer using only retrieved product context

## Prerequisites

- Python 3.10+
- `pip`
- A Gemini API key (`GEMINI_API_KEY`)

Optional (only if scraping):
- Playwright browser dependencies (`python -m playwright install`)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set your Gemini key in your shell:

```bash
export GEMINI_API_KEY="your-gemini-key"
```

Or create a `.env` file in the repository root:

```env
GEMINI_API_KEY=your-gemini-key
```

## How to use

### 1) (Optional) Scrape products

Update `BASE_URL` and `SELECTORS` in `scraper.py`, then run:

```bash
python scraper.py
```

This writes product data to `products.json`.

### 2) Build the vector store

```bash
python vector_store.py --build
```

Optional quick search test:

```bash
python vector_store.py --query "waterproof electronics under $50"
```

### 3) Run the agent (CLI)

```bash
python agent.py
```

Ask questions interactively and type `quit` to exit.

### 4) Run the API (FastAPI)

```bash
uvicorn app:app --reload
```

Endpoints:
- `GET /` health check
- `POST /ask` → LLM answer
- `POST /search` → raw vector-search results

Example request:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"any waterproof electronics under $50?","k":5}'
```

## Expected workflow

For normal usage:
1. Prepare/update `products.json` (scrape or edit manually)
2. Rebuild the vector store
3. Run CLI or API and ask questions

Rebuild the vector store whenever `products.json` changes.

## Project structure

- `scraper.py` — scrapes products into `products.json`
- `vector_store.py` — builds/searches local ChromaDB store
- `agent.py` — retrieval + Gemini answer generation
- `app.py` — FastAPI wrapper around the agent
- `products.json` — source product dataset

## Troubleshooting

- **`GEMINI_API_KEY is not configured`**: set `GEMINI_API_KEY` in environment or `.env`.
- **No/poor results**: rebuild the store with `python vector_store.py --build` after updating data.
- **Scraper browser errors**: install Playwright browsers with `python -m playwright install`.
- **Scraper launch path errors**: `scraper.py` currently sets a Windows Chrome `executable_path`; update it for your OS/browser or remove it to use Playwright's default browser.
