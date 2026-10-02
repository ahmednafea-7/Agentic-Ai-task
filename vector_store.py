"""
vector_store.py
----------------
Turns products.json into chunks, embeds them, and stores them in a local
persistent ChromaDB collection. Also exposes a `search()` function used by
the agent.

Chunking rule:
- Each product is usually short, so most products become ONE chunk
  (name + category + price + description combined into one text blob).
- If a description is long (> MAX_WORDS), it's split into overlapping
  word-chunks so no single embedding has to represent too much text.
  Each chunk keeps the parent product's metadata (id, name, price, url)
  so we can always trace a result back to its product.

Run directly to (re)build the store:
    python vector_store.py --build
"""

import json
import argparse
import chromadb

DB_DIR = "chroma_db"
COLLECTION_NAME = "products"
MAX_WORDS = 120     # chunk size (words) before we split a description
OVERLAP = 20        # word overlap between consecutive chunks


def load_products(path="products.json") -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def product_to_text(p: dict) -> str:
    """Combine a product's fields into one text blob for embedding."""
    parts = [p.get("name", ""), p.get("category", ""), p.get("price", ""), p.get("description", "")]
    return " | ".join(x for x in parts if x)


def chunk_text(text: str, max_words=MAX_WORDS, overlap=OVERLAP) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        end = start + max_words
        chunks.append(" ".join(words[start:end]))
        start = end - overlap  # step forward, keeping some overlap
    return chunks


def get_collection():
    client = chromadb.PersistentClient(path=DB_DIR)
    # chromadb's default embedding function (all-MiniLM-L6-v2, downloaded
    # automatically on first use) is used when none is passed explicitly.
    return client.get_or_create_collection(name=COLLECTION_NAME)


def build_store(json_path="products.json"):
    products = load_products(json_path)
    collection = get_collection()

    ids, documents, metadatas = [], [], []
    for p in products:
        full_text = product_to_text(p)
        for i, chunk in enumerate(chunk_text(full_text)):
            ids.append(f"{p['id']}-{i}")
            documents.append(chunk)
            metadatas.append({
                "product_id": p.get("id", ""),
                "name": p.get("name", ""),
                "price": p.get("price", ""),
                "category": p.get("category", ""),
                "url": p.get("url", ""),
                "chunk_index": i,
            })

    # upsert = safe to re-run without creating duplicates
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Indexed {len(products)} products as {len(ids)} chunks into '{DB_DIR}'.")


def search(query: str, k: int = 5) -> list[dict]:
    """User query -> embedding (done internally by Chroma) -> vector search -> results."""
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=k)

    hits = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        hits.append({"text": doc, "metadata": meta, "distance": dist})
    return hits


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="(re)build the vector store from products.json")
    parser.add_argument("--query", type=str, help="run a quick test search")
    args = parser.parse_args()

    if args.build:
        build_store()
    if args.query:
        for r in search(args.query):
            print(f"[{r['distance']:.3f}] {r['metadata']['name']} — {r['text'][:80]}...")
