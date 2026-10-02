"""
app.py
------
Exposes the product agent over HTTP.

Run:
    uvicorn app:app --reload

Then POST to http://127.0.0.1:8000/ask
    { "question": "any waterproof electronics under $50?" }
"""

from fastapi import FastAPI
from pydantic import BaseModel
from agent import answer
from vector_store import search

app = FastAPI(title="Product RAG Agent")


class Question(BaseModel):
    question: str
    k: int = 5


@app.post("/ask")
def ask(q: Question):
    return {"answer": answer(q.question, k=q.k)}


@app.post("/search")
def raw_search(q: Question):
    """Bypasses the LLM — just the raw vector search results (useful for debugging)."""
    return {"results": search(q.question, k=q.k)}


@app.get("/")
def health():
    return {"status": "ok"}
