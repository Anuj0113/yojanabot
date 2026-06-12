"""
Embeddings using Groq API - free, zero memory, better accuracy.
Uses nomic-embed-text model via Groq.
"""
import os
import numpy as np
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMBED_MODEL = "nomic-embed-text-v1_5"
GROQ_EMBED_URL = "https://api.groq.com/openai/v1/embeddings"


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
    """Get embedding from Groq API."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": EMBED_MODEL,
        "input": text
    }
    response = httpx.post(GROQ_EMBED_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return np.array(data["data"][0]["embedding"], dtype=np.float32)


def embed_text(text: str) -> np.ndarray:
    return get_embedding(text)


def embed_schemes(schemes: list):
    """Embed all schemes using Groq API."""
    texts = [scheme_to_text(s) for s in schemes]
    embeddings = []
    for i, text in enumerate(texts):
        print(f"Embedding scheme {i+1}/{len(texts)}: {schemes[i]['id']}")
        emb = get_embedding(text)
        embeddings.append(emb)
    return texts, np.array(embeddings, dtype=np.float32)