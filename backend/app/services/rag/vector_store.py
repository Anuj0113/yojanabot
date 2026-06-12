import os
import sys
import json
import pickle
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.services.rag.embeddings import embed_schemes

VECTOR_DIR = os.path.join(os.path.dirname(__file__), "../../../../data/vectors")
INDEX_PATH = os.path.join(VECTOR_DIR, "schemes_vectors.npy")
META_PATH  = os.path.join(VECTOR_DIR, "schemes_meta.pkl")


def build_index(schemes: list):
    os.makedirs(VECTOR_DIR, exist_ok=True)
    print(f"Embedding {len(schemes)} schemes...")
    texts, embeddings = embed_schemes(schemes)
    embeddings = embeddings.astype(np.float32)
    # Normalize for cosine similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / np.maximum(norms, 1e-9)
    np.save(INDEX_PATH, embeddings)
    meta = [{"id": s["id"], "name": s["name_en"], "text": t}
            for s, t in zip(schemes, texts)]
    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)
    print(f"Index saved: {len(schemes)} schemes")
    return embeddings, meta


def load_index():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError("Index not found. Run: python app/services/rag/vector_store.py")
    embeddings = np.load(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        meta = pickle.load(f)
    return embeddings, meta


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "../../../../data/schemes")
    with open(os.path.join(data_dir, "central_schemes.json"), encoding="utf-8") as f:
        central = json.load(f)
    with open(os.path.join(data_dir, "gujarat_schemes.json"), encoding="utf-8") as f:
        gujarat = json.load(f)
    build_index(central + gujarat)
    print("Done!")