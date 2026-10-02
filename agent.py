"""
agent.py
--------
The "agent" piece: user question -> vector search -> LLM answers using the
retrieved product chunks as context (classic RAG).

Needs a Google Gemini API key:
    $env:GEMINI_API_KEY="your-key-here"

Run:
    python agent.py
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from vector_store import search

load_dotenv()

MODEL = "gemini-3.6-flash"


def build_context(hits: list[dict]) -> str:
    lines = []
    for h in hits:
        m = h["metadata"]
        lines.append(f"- {m['name']} ({m.get('price', 'N/A')}, {m.get('category', 'N/A')}): {h['text']}")
    return "\n".join(lines)


def answer(question: str, k: int = 5) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to .env or set it in PowerShell."
        )

    hits = search(question, k=k)
    if not hits:
        return "I couldn't find any matching products."

    context = build_context(hits)

    system_prompt = (
        "You are a helpful product assistant. Answer the user's question ONLY "
        "using the product information given below. If the answer isn't in "
        "there, say you don't have that product. Keep answers short and "
        "mention product names and prices where relevant.\n\n"
        f"PRODUCT CONTEXT:\n{context}"
    )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=500,
        ),
    )
    return response.text


if __name__ == "__main__":
    print("Product agent ready. Type a question (or 'quit').")
    while True:
        q = input("\nYou: ").strip()
        if q.lower() in {"quit", "exit"}:
            break
        print("Agent:", answer(q))
