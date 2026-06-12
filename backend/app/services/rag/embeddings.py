"""
Embeddings using Google Gemini API - free, zero memory, excellent multilingual.
Uses text-embedding-004 model - great for Hindi and Gujarati.
"""
import os
import numpy as np
import httpx
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


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


def get_embedding(text: str) -> np.ndarray:
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
        "taskType": "RETRIEVAL_DOCUMENT"
    }
    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={GEMINI_API_KEY}",
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    return np.array(data["embedding"]["values"], dtype=np.float32)


def embed_text(text: str) -> np.ndarray:
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
        "taskType": "RETRIEVAL_QUERY"
    }
    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={GEMINI_API_KEY}",
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    return np.array(data["embedding"]["values"], dtype=np.float32)


def embed_schemes(schemes: list):
    texts = [scheme_to_text(s) for s in schemes]
    embeddings = []
    for i, text in enumerate(texts):
        print(f"Embedding scheme {i+1}/{len(schemes)}: {schemes[i]['id']}")
        emb = get_embedding(text)
        embeddings.append(emb)
    return texts, np.array(embeddings, dtype=np.float32)