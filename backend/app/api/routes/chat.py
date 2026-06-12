import os
import sys
import json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.services.eligibility.profile_builder import chat
from app.services.eligibility.rule_engine import check_all_schemes
from app.services.rag.retriever import search, load_schemes_lookup
from app.services.eligibility.scheme_details import get_scheme_details, format_scheme_details_web

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../../../data/schemes")

with open(os.path.join(DATA_DIR, "central_schemes.json"), encoding="utf-8") as f:
    CENTRAL = json.load(f)
with open(os.path.join(DATA_DIR, "gujarat_schemes.json"), encoding="utf-8") as f:
    GUJARAT = json.load(f)

ALL_SCHEMES = CENTRAL + GUJARAT
SCHEME_LOOKUP = {s["id"]: s for s in ALL_SCHEMES}
load_schemes_lookup(ALL_SCHEMES)


class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list = []

class SchemeResult(BaseModel):
    scheme_id: str
    scheme_name: str
    status: str
    matched_conditions: list
    failed_conditions: list
    missing_info: list
    confidence: float
    documents_required: list
    where_to_apply: Optional[str]
    online_url: Optional[str]
    helpline: Optional[str]
    apply_steps: list

class ChatResponse(BaseModel):
    reply: str
    profile_complete: bool
    profile: Optional[dict]
    eligible_schemes: list
    partial_schemes: list
    rag_suggestions: list


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    history = [{"role": m.get("role"), "content": m.get("content")} if isinstance(m, dict) else {"role": m.role, "content": m.content} for m in req.history]
    reply, profile = chat(history, req.message)

    eligible = []
    partial  = []
    rag_suggestions = []

    if profile:
        results = check_all_schemes(profile, ALL_SCHEMES)
        district = profile.get("district")

        def enrich(r):
            scheme = SCHEME_LOOKUP.get(r.scheme_id, {})
            details = get_scheme_details(r.scheme_id, district) or {}
            return SchemeResult(
                scheme_id=r.scheme_id,
                scheme_name=r.scheme_name,
                status=r.status,
                matched_conditions=r.matched_conditions,
                failed_conditions=r.failed_conditions,
                missing_info=r.missing_info,
                confidence=r.confidence,
                documents_required=scheme.get("documents_required", []),
                where_to_apply=details.get("offline_location_personalised"),
                online_url=details.get("online_url"),
                helpline=details.get("helpline"),
                apply_steps=details.get("apply_steps", []),
            )

        eligible = [enrich(r) for r in results["eligible"]]
        partial  = [enrich(r) for r in results["partial"]]

        rag_raw = search(req.message, top_k=3)
        rag_suggestions = [
            {"scheme_id": r["scheme_id"], "scheme_name": r["scheme_name"], "similarity": r["similarity"]}
            for r in rag_raw
        ]

    return ChatResponse(
        reply=reply,
        profile_complete=profile is not None,
        profile=profile,
        eligible_schemes=eligible,
        partial_schemes=partial,
        rag_suggestions=rag_suggestions,
    )


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/search")
async def search_endpoint(req: SearchRequest):
    results = search(req.query, req.top_k)
    return {
        "query": req.query,
        "results": [
            {"scheme_id": r["scheme_id"], "scheme_name": r["scheme_name"], "similarity": r["similarity"]}
            for r in results
        ]
    }