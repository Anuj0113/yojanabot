import os
import sys
import json
from fastapi import APIRouter, HTTPException

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../../../data/schemes")

with open(os.path.join(DATA_DIR, "central_schemes.json"), encoding="utf-8") as f:
    CENTRAL = json.load(f)
with open(os.path.join(DATA_DIR, "gujarat_schemes.json"), encoding="utf-8") as f:
    GUJARAT = json.load(f)

ALL_SCHEMES = CENTRAL + GUJARAT


@router.get("/")
async def get_all_schemes():
    return {"total": len(ALL_SCHEMES), "schemes": ALL_SCHEMES}


@router.get("/{scheme_id}")
async def get_scheme(scheme_id: str):
    scheme = next((s for s in ALL_SCHEMES if s["id"] == scheme_id), None)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme


@router.get("/tag/{tag}")
async def get_schemes_by_tag(tag: str):
    matched = [s for s in ALL_SCHEMES if tag.lower() in [t.lower() for t in s.get("tags", [])]]
    return {"tag": tag, "total": len(matched), "schemes": matched}