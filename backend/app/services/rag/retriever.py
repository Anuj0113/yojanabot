import os
import sys
import json
import numpy as np
import faiss
import pickle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.services.rag.embeddings import embed_text
from app.services.rag.vector_store import load_index

_index = None
_meta  = None
_schemes_by_id = {}

KEYWORD_BOOST = {
    "ghar": ["pm-awas-yojana-gramin"],
    "makaan": ["pm-awas-yojana-gramin"],
    "awas": ["pm-awas-yojana-gramin"],
    "house": ["pm-awas-yojana-gramin"],
    "home": ["pm-awas-yojana-gramin"],
    "beti": ["sukanya-samriddhi-yojana"],
    "ladki": ["sukanya-samriddhi-yojana"],
    "daughter": ["sukanya-samriddhi-yojana"],
    "dikri": ["sukanya-samriddhi-yojana"],
    "savings": ["sukanya-samriddhi-yojana"],
    "bachat": ["sukanya-samriddhi-yojana"],
    "gas": ["pm-ujjwala-yojana"],
    "lpg": ["pm-ujjwala-yojana"],
    "cylinder": ["pm-ujjwala-yojana"],
    "kisan": ["pm-kisan-samman-nidhi"],
    "farmer": ["pm-kisan-samman-nidhi", "pm-fasal-bima-yojana"],
    "kheti": ["pm-kisan-samman-nidhi", "gujarat-ikhedut-portal"],
    "loan": ["pm-mudra-yojana"],
    "business": ["pm-mudra-yojana"],
    "health": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "ilaaj": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "hospital": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "majdoor": ["e-shram-card"],
    "labour": ["e-shram-card"],
    "worker": ["e-shram-card"],
    "scholarship": ["national-scholarship-portal"],
    "padhai": ["national-scholarship-portal"],
    "disability": ["gujarat-viklang-sahay-yojana"],
    "viklang": ["gujarat-viklang-sahay-yojana"],
}


def _load():
    global _index, _meta
    if _index is None:
        _index, _meta = load_index()


def load_schemes_lookup(schemes: list):
    global _schemes_by_id
    _schemes_by_id = {s["id"]: s for s in schemes}


def search(query: str, top_k: int = 5) -> list:
    _load()
    query_vec = embed_text(query).reshape(1, -1).astype(np.float32)
    faiss.normalize_L2(query_vec)
    scores, indices = _index.search(query_vec, top_k * 2)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        meta = _meta[idx]
        scheme = _schemes_by_id.get(meta["id"], {})
        boost = 0.0
        query_lower = query.lower()
        for keyword, scheme_ids in KEYWORD_BOOST.items():
            if keyword in query_lower and meta["id"] in scheme_ids:
                boost = 0.3
                break
        results.append({
            "scheme_id":   meta["id"],
            "scheme_name": meta["name"],
            "similarity":  round(float(score) + boost, 3),
            "scheme":      scheme,
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


def search_and_explain(query: str, top_k: int = 5) -> None:
    results = search(query, top_k)
    print(f"\nQuery: '{query}'")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['scheme_name']} (similarity: {r['similarity']})")


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "../../../../data/schemes")
    with open(os.path.join(data_dir, "central_schemes.json"), encoding="utf-8") as f:
        central = json.load(f)
    with open(os.path.join(data_dir, "gujarat_schemes.json"), encoding="utf-8") as f:
        gujarat = json.load(f)
    load_schemes_lookup(central + gujarat)
    search_and_explain("muje ghar chahiye madad")
    search_and_explain("farmer income support")
    search_and_explain("beti ke liye savings")
    search_and_explain("health insurance poor family")
    search_and_explain("business loan no guarantee")