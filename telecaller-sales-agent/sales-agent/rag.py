"""Tiny FAISS-backed retrieval over the company policy document.

Splits knowledge/company_policy.md into one chunk per "## " section, embeds
each chunk with a Google embedding model, and serves nearest-neighbour lookups
so the agent can quote policy/ToS accurately instead of guessing.

Deliberately minimal: a flat in-memory FAISS index rebuilt on startup. The doc
is small, so there's no need to persist the index to disk.
"""

import re
from pathlib import Path

import faiss
import numpy as np
from google import genai

POLICY_PATH = Path(__file__).parent / "knowledge" / "company_policy.md"
EMBED_MODEL = "gemini-embedding-001"  # Google embedding model; change if needed

# Module-level cache so we build the index only once per process.
_index: faiss.Index | None = None
_chunks: list[str] = []


def _split_sections(markdown: str) -> list[str]:
    """Split the doc into chunks, one per top-level "## " section.

    The leading title/intro (before the first "## ") is kept as its own chunk.
    """
    parts = re.split(r"\n(?=## )", markdown.strip())
    return [p.strip() for p in parts if p.strip()]


def _embed(texts: list[str]) -> np.ndarray:
    """Embed a list of texts and return L2-normalised float32 vectors.

    Normalising lets us use inner-product search as cosine similarity.
    """
    client = genai.Client()  # reads GOOGLE_API_KEY from the environment
    resp = client.models.embed_content(model=EMBED_MODEL, contents=texts)
    vecs = np.array([e.values for e in resp.embeddings], dtype="float32")
    faiss.normalize_L2(vecs)
    return vecs


def build_index() -> None:
    """Read the policy doc, embed its sections, and build the FAISS index.

    Idempotent and cheap to call once at startup. Safe to call again to rebuild
    (e.g. after editing the policy doc).
    """
    global _index, _chunks
    text = POLICY_PATH.read_text()
    _chunks = _split_sections(text)
    vecs = _embed(_chunks)
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    _index = index


def search(query: str, k: int = 3) -> list[str]:
    """Return the top-k most relevant policy sections for a query.

    Builds the index lazily on first use if it wasn't built at startup.
    """
    if _index is None:
        build_index()
    qvec = _embed([query])
    k = min(k, len(_chunks))
    _, idxs = _index.search(qvec, k)
    return [_chunks[i] for i in idxs[0] if i >= 0]


if __name__ == "__main__":
    # Quick manual check: python -m rag "do you offer refunds?"
    import sys

    build_index()
    print(f"Indexed {len(_chunks)} sections from {POLICY_PATH.name}\n")
    q = " ".join(sys.argv[1:]) or "what is the refund policy?"
    print(f"Query: {q}\n")
    for i, chunk in enumerate(search(q), 1):
        title = chunk.splitlines()[0]
        print(f"{i}. {title}")
