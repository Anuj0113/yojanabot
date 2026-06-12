"""
Lightweight embeddings using TF-IDF instead of sentence-transformers.
Saves ~470MB RAM — fits within Render free tier 512MB limit.
"""
import numpy as np
import re


def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return text


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
    return preprocess(" ".join(p for p in parts if p).strip())


class TFIDFEmbedder:
    def __init__(self):
        self.vocab = {}
        self.idf = {}
        self.fitted = False

    def fit(self, texts):
        from collections import Counter
        import math
        N = len(texts)
        df = Counter()
        tokenized = []
        for text in texts:
            tokens = set(text.split())
            df.update(tokens)
            tokenized.append(text.split())
        self.vocab = {w: i for i, w in enumerate(df.keys())}
        self.idf = {w: math.log(N / (df[w] + 1)) for w in df}
        self.fitted = True

    def transform(self, texts):
        from collections import Counter
        vecs = []
        for text in texts:
            tokens = text.split()
            tf = Counter(tokens)
            vec = np.zeros(len(self.vocab))
            for word, count in tf.items():
                if word in self.vocab:
                    vec[self.vocab[word]] = (count / len(tokens)) * self.idf.get(word, 0)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vecs.append(vec)
        return np.array(vecs, dtype=np.float32)

    def transform_one(self, text: str) -> np.ndarray:
        return self.transform([preprocess(text)])[0]


_embedder = None


def get_embedder() -> TFIDFEmbedder:
    global _embedder
    if _embedder is None:
        _embedder = TFIDFEmbedder()
    return _embedder


def embed_text(text: str) -> np.ndarray:
    embedder = get_embedder()
    if not embedder.fitted:
        raise RuntimeError("Embedder not fitted. Run build_index first.")
    return embedder.transform_one(text)


def embed_schemes(schemes: list):
    texts = [scheme_to_text(s) for s in schemes]
    embedder = get_embedder()
    embedder.fit(texts)
    embeddings = embedder.transform(texts)
    return texts, embeddings