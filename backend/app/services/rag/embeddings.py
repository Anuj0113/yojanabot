import os
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def scheme_to_text(scheme: dict) -> str:
    parts = [
        scheme.get("name_en", ""),
        scheme.get("name_hi", ""),
        scheme.get("name_gu", ""),
        scheme.get("benefit_en", ""),
        scheme.get("keywords", ""),
        " ".join(scheme.get("tags", [])),
        " ".join(scheme.get("eligibility", {}).get("custom_conditions", [])),
    ]
    occupation = scheme.get("eligibility", {}).get("occupation", [])
    if occupation and "any" not in occupation:
        parts.append("for " + " ".join(occupation))
    return " ".join(p for p in parts if p).strip()

def embed_text(text: str):
    return get_model().encode(text, convert_to_numpy=True)

def embed_schemes(schemes: list):
    texts = [scheme_to_text(s) for s in schemes]
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return texts, embeddings