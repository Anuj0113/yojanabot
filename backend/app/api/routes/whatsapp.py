import os
import sys
import json
from fastapi import APIRouter, Form
from fastapi.responses import Response

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.services.eligibility.profile_builder import chat
from app.services.eligibility.rule_engine import check_all_schemes
from app.services.rag.retriever import search, load_schemes_lookup
from app.services.eligibility.scheme_details import get_scheme_details, format_scheme_details_whatsapp

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../../../data/schemes")

with open(os.path.join(DATA_DIR, "central_schemes.json"), encoding="utf-8") as f:
    CENTRAL = json.load(f)
with open(os.path.join(DATA_DIR, "gujarat_schemes.json"), encoding="utf-8") as f:
    GUJARAT = json.load(f)

ALL_SCHEMES = CENTRAL + GUJARAT
load_schemes_lookup(ALL_SCHEMES)

SESSIONS = {}
SCHEME_LOOKUP = {s["id"]: s for s in ALL_SCHEMES}


def twiml_response(message: str) -> Response:
    safe = message.replace("&", "and").replace("<", "").replace(">", "")
    xml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe}</Message></Response>'
    return Response(content=xml, media_type="text/xml")


def format_results_whatsapp(eligible, partial, district=None) -> str:
    lines = []

    if eligible:
        lines.append(f"{len(eligible)} Schemes You Qualify For:")
        lines.append("")
        for i, r in enumerate(eligible[:5], 1):
            scheme = SCHEME_LOOKUP.get(r.scheme_id, {})
            details = get_scheme_details(r.scheme_id, district)
            lines.append(f"{i}. {r.scheme_name}")

            # Documents
            docs = scheme.get("documents_required", [])
            if docs:
                lines.append(f"   Documents: {', '.join(docs[:3])}")

            # Where to apply
            if details:
                lines.append(f"   Where: {details.get('offline_location_personalised', '')}")
                if details.get("online_url"):
                    lines.append(f"   Online: {details['online_url']}")
                if details.get("helpline"):
                    lines.append(f"   Helpline: {details['helpline']}")
            lines.append("")

    if partial:
        lines.append(f"{len(partial)} More Schemes (need more info):")
        lines.append("")
        for i, r in enumerate(partial[:3], 1):
            lines.append(f"{i}. {r.scheme_name}")
            if r.missing_info:
                lines.append(f"   Need: {', '.join(r.missing_info[:2])}")
        lines.append("")

    if not eligible and not partial:
        lines.append("No matching schemes found.")
        lines.append("")

    lines.append("Reply the scheme number (1, 2, 3...) to get full step-by-step application guide.")
    lines.append("Reply reset to start over.")
    return "\n".join(lines)


@router.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
):
    user_number = From
    user_message = Body.strip()

    if user_message.lower() in ("reset", "start", "hi", "hello", "namaste"):
        SESSIONS[user_number] = {"history": [], "profile_done": False, "profile": None, "eligible": []}
        return twiml_response(
            "Namaste! I am YojanaBot.\n\n"
            "I help you find government schemes you qualify for.\n\n"
            "Tell me about yourself — your job, location, and family.\n\n"
            "You can type in Hindi, Gujarati, or English.\n\n"
            "Example: I am a farmer in Gujarat"
        )

    if user_number not in SESSIONS:
        SESSIONS[user_number] = {"history": [], "profile_done": False, "profile": None, "eligible": []}

    session = SESSIONS[user_number]

    # Handle scheme detail request (user replies with a number)
    if session["profile_done"] and user_message.strip().isdigit():
        idx = int(user_message.strip()) - 1
        eligible = session.get("eligible", [])
        if 0 <= idx < len(eligible):
            r = eligible[idx]
            scheme = SCHEME_LOOKUP.get(r.scheme_id, {})
            district = session.get("profile", {}).get("district")
            details = get_scheme_details(r.scheme_id, district)
            if details:
                msg = format_scheme_details_whatsapp(r.scheme_name, details)
                docs = scheme.get("documents_required", [])
                if docs:
                    msg += f"\n\nDocuments needed:\n" + "\n".join(f"- {d}" for d in docs)
                return twiml_response(msg)
        return twiml_response("Invalid number. Reply reset to start over.")

    if session["profile_done"]:
        return twiml_response("Your schemes have been found. Reply a scheme number for full details, or reply reset to start a new search.")

    try:
        reply, profile = chat(session["history"], user_message)
        session["history"].append({"role": "user", "content": user_message})
        session["history"].append({"role": "assistant", "content": reply})

        if profile:
            session["profile_done"] = True
            session["profile"] = profile
            results = check_all_schemes(profile, ALL_SCHEMES)
            eligible = results["eligible"]
            partial  = results["partial"]
            session["eligible"] = eligible

            district = profile.get("district")
            scheme_text = format_results_whatsapp(eligible, partial, district)

            msg = (
                f"Profile complete!\n\n"
                f"State: {profile.get('state', 'N/A')}\n"
                f"District: {profile.get('district', 'N/A')}\n"
                f"Occupation: {profile.get('occupation', 'N/A')}\n\n"
                f"{scheme_text}"
            )
            return twiml_response(msg)
        else:
            return twiml_response(reply)

    except Exception as e:
        return twiml_response("Something went wrong. Reply reset to try again.")