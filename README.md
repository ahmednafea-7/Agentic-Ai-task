# Product RAG Agent — Quick Start

Pipeline: **scrape → JSON → chunk → embed → ChromaDB → query → LLM answer**

## 1. Install
```bash
pip install -r requirements.txt
```

## 2. Get product data
- **Option A (fastest for your deadline):** use the included `products.json` sample to get everything else working first.
- **Option B (real data):** open `scraper.py`, edit `BASE_URL` and `SELECTORS` to match your target site (inspect the page's HTML to find the right CSS classes), then:
```bash
python scraper.py
```

## 3. Build the vector store
```bash
python vector_store.py --build
```
This chunks each product, embeds the chunks (ChromaDB auto-downloads a small local embedding model the first time — needs internet, ~80MB, one-time), and stores everything in `./chroma_db/`.

Quick test without the LLM:
```bash
python vector_store.py --query "waterproof electronics under $50"
```

## 4. Set your API key
Create a free Gemini API key at https://aistudio.google.com/app/apikey, then set it in PowerShell:
```powershell
$env:GEMINI_API_KEY="your-gemini-key"
```
For a persistent project configuration, put this in a `.env` file in this folder:
```env
GEMINI_API_KEY=your-gemini-key
```

## 5. Run the agent
CLI:
```bash
python agent.py
```
Or as an API:
```bash
uvicorn app:app --reload
```
Then POST JSON to `http://127.0.0.1:8000/ask`:
```json
{ "question": "any waterproof electronics under $50?" }
```

## How it fits together
- `scraper.py` — pulls products off a site into `products.json`
- `vector_store.py` — chunks + embeds + stores in ChromaDB, and has the `search()` function
- `agent.py` — the RAG loop: your question → `search()` → stuff results into an LLM prompt → answer
- `app.py` — FastAPI wrapper around `agent.py` so it's callable over HTTP

## If you're short on time tomorrow
Skip step 2/Option B — demo with the sample `products.json`, since the grader almost certainly cares about the **pipeline working end-to-end**, not the specific site scraped. Swap in real scraped data after if there's time.
