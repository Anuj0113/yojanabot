import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.services.rag.embeddings import embed_text
from app.services.rag.vector_store import load_index

_embeddings = None
_meta = None
_schemes_by_id = {}

# Comprehensive keyword boost covering every possible way a user might ask
# English + Hindi + Gujarati + Hinglish + common misspellings
KEYWORD_BOOST = {

    # ── Housing ──────────────────────────────────────────────
    "ghar": ["pm-awas-yojana-gramin"],
    "makaan": ["pm-awas-yojana-gramin"],
    "makan": ["pm-awas-yojana-gramin"],
    "awas": ["pm-awas-yojana-gramin"],
    "house": ["pm-awas-yojana-gramin"],
    "home": ["pm-awas-yojana-gramin"],
    "housing": ["pm-awas-yojana-gramin"],
    "rehna": ["pm-awas-yojana-gramin"],
    "naya ghar": ["pm-awas-yojana-gramin"],
    "pucca": ["pm-awas-yojana-gramin"],
    "pakka": ["pm-awas-yojana-gramin"],
    "construction": ["pm-awas-yojana-gramin"],
    "banane": ["pm-awas-yojana-gramin"],
    "banana": ["pm-awas-yojana-gramin"],
    "muje ghar": ["pm-awas-yojana-gramin"],
    "ghar chahiye": ["pm-awas-yojana-gramin"],
    "pmay": ["pm-awas-yojana-gramin"],
    "avas": ["pm-awas-yojana-gramin"],
    "ઘર": ["pm-awas-yojana-gramin"],
    "મકાન": ["pm-awas-yojana-gramin"],
    "આવાસ": ["pm-awas-yojana-gramin"],

    # ── LPG / Gas ────────────────────────────────────────────
    "gas": ["pm-ujjwala-yojana"],
    "lpg": ["pm-ujjwala-yojana"],
    "cylinder": ["pm-ujjwala-yojana"],
    "chulha": ["pm-ujjwala-yojana"],
    "rasoi": ["pm-ujjwala-yojana"],
    "cooking": ["pm-ujjwala-yojana"],
    "ujjwala": ["pm-ujjwala-yojana"],
    "gas connection": ["pm-ujjwala-yojana"],
    "free gas": ["pm-ujjwala-yojana"],
    "mahila gas": ["pm-ujjwala-yojana"],
    "gass": ["pm-ujjwala-yojana"],
    "ગૅસ": ["pm-ujjwala-yojana"],
    "ગેસ": ["pm-ujjwala-yojana"],
    "ચૂલો": ["pm-ujjwala-yojana"],
    "रसोई": ["pm-ujjwala-yojana"],
    "गैस": ["pm-ujjwala-yojana"],

    # ── Farmer / Agriculture ─────────────────────────────────
    "kisan": ["pm-kisan-samman-nidhi", "pm-fasal-bima-yojana"],
    "farmer": ["pm-kisan-samman-nidhi", "pm-fasal-bima-yojana", "gujarat-ikhedut-portal"],
    "kheti": ["pm-kisan-samman-nidhi", "gujarat-ikhedut-portal"],
    "khedut": ["pm-kisan-samman-nidhi", "gujarat-ikhedut-portal"],
    "krishi": ["pm-kisan-samman-nidhi", "gujarat-ikhedut-portal"],
    "agriculture": ["pm-kisan-samman-nidhi", "gujarat-ikhedut-portal"],
    "farming": ["pm-kisan-samman-nidhi", "gujarat-ikhedut-portal"],
    "annadata": ["pm-kisan-samman-nidhi"],
    "pm kisan": ["pm-kisan-samman-nidhi"],
    "pmkisan": ["pm-kisan-samman-nidhi"],
    "kisaan": ["pm-kisan-samman-nidhi"],
    "खेती": ["pm-kisan-samman-nidhi", "gujarat-ikhedut-portal"],
    "किसान": ["pm-kisan-samman-nidhi"],
    "ખેડૂત": ["pm-kisan-samman-nidhi", "gujarat-ikhedut-portal"],
    "ખેતી": ["pm-kisan-samman-nidhi", "gujarat-ikhedut-portal"],
    "ikhedut": ["gujarat-ikhedut-portal"],
    "subsidy": ["gujarat-ikhedut-portal"],
    "equipment": ["gujarat-ikhedut-portal"],
    "tractor": ["gujarat-ikhedut-portal"],
    "drip": ["gujarat-ikhedut-portal"],
    "irrigation": ["gujarat-ikhedut-portal"],
    "sinchai": ["gujarat-ikhedut-portal"],

    # ── Crop Insurance ───────────────────────────────────────
    "fasal": ["pm-fasal-bima-yojana"],
    "crop": ["pm-fasal-bima-yojana"],
    "bima": ["pm-fasal-bima-yojana"],
    "insurance": ["pm-fasal-bima-yojana", "ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "nuksan": ["pm-fasal-bima-yojana"],
    "flood": ["pm-fasal-bima-yojana"],
    "drought": ["pm-fasal-bima-yojana"],
    "sukhaa": ["pm-fasal-bima-yojana"],
    "baadh": ["pm-fasal-bima-yojana"],
    "pmfby": ["pm-fasal-bima-yojana"],
    "फसल": ["pm-fasal-bima-yojana"],
    "ફસલ": ["pm-fasal-bima-yojana"],
    "પાક": ["pm-fasal-bima-yojana"],

    # ── Health ───────────────────────────────────────────────
    "health": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "hospital": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "ilaaj": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "dawai": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "bimari": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "sehat": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "swasthya": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "treatment": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "doctor": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "operation": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "ayushman": ["ayushman-bharat-pmjay"],
    "pmjay": ["ayushman-bharat-pmjay"],
    "cashless": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "free treatment": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "chiranjeevi": ["gujarat-chiranjeevi-yojana"],
    "gujarat health": ["gujarat-chiranjeevi-yojana"],
    "સારવાર": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "આરોગ્ય": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "दवाई": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],
    "इलाज": ["ayushman-bharat-pmjay", "gujarat-chiranjeevi-yojana"],

    # ── Girl Child / Savings ─────────────────────────────────
    "beti": ["sukanya-samriddhi-yojana"],
    "ladki": ["sukanya-samriddhi-yojana"],
    "daughter": ["sukanya-samriddhi-yojana"],
    "dikri": ["sukanya-samriddhi-yojana"],
    "girl": ["sukanya-samriddhi-yojana", "gujarat-namo-saraswati-yojana"],
    "savings": ["sukanya-samriddhi-yojana"],
    "bachat": ["sukanya-samriddhi-yojana"],
    "sukanya": ["sukanya-samriddhi-yojana"],
    "ssy": ["sukanya-samriddhi-yojana"],
    "beti bachao": ["sukanya-samriddhi-yojana"],
    "girl child": ["sukanya-samriddhi-yojana"],
    "future": ["sukanya-samriddhi-yojana"],
    "shaadi": ["sukanya-samriddhi-yojana"],
    "vivah": ["sukanya-samriddhi-yojana"],
    "interest": ["sukanya-samriddhi-yojana"],
    "दीकरी": ["sukanya-samriddhi-yojana"],
    "बेटी": ["sukanya-samriddhi-yojana"],
    "દીકરી": ["sukanya-samriddhi-yojana"],

    # ── Business / Loan ──────────────────────────────────────
    "loan": ["pm-mudra-yojana"],
    "business": ["pm-mudra-yojana"],
    "dhanda": ["pm-mudra-yojana"],
    "vyapaar": ["pm-mudra-yojana"],
    "mudra": ["pm-mudra-yojana"],
    "udhyog": ["pm-mudra-yojana"],
    "startup": ["pm-mudra-yojana"],
    "self employed": ["pm-mudra-yojana"],
    "khud ka kaam": ["pm-mudra-yojana"],
    "rin": ["pm-mudra-yojana"],
    "paisa chahiye": ["pm-mudra-yojana"],
    "no guarantee": ["pm-mudra-yojana"],
    "collateral": ["pm-mudra-yojana"],
    "shishu": ["pm-mudra-yojana"],
    "kishore": ["pm-mudra-yojana"],
    "tarun": ["pm-mudra-yojana"],
    "ધંધો": ["pm-mudra-yojana"],
    "લોન": ["pm-mudra-yojana"],
    "व्यापार": ["pm-mudra-yojana"],

    # ── Labour / Worker ──────────────────────────────────────
    "majdoor": ["e-shram-card"],
    "mazdoor": ["e-shram-card"],
    "labour": ["e-shram-card"],
    "worker": ["e-shram-card"],
    "shramik": ["e-shram-card"],
    "dihadi": ["e-shram-card"],
    "daily wage": ["e-shram-card"],
    "construction worker": ["e-shram-card"],
    "e shram": ["e-shram-card"],
    "eshram": ["e-shram-card"],
    "unorganised": ["e-shram-card"],
    "असंगठित": ["e-shram-card"],
    "મજૂર": ["e-shram-card"],
    "श्रमिक": ["e-shram-card"],

    # ── Banking ──────────────────────────────────────────────
    "bank account": ["pm-jan-dhan-yojana"],
    "khata": ["pm-jan-dhan-yojana"],
    "zero balance": ["pm-jan-dhan-yojana"],
    "jan dhan": ["pm-jan-dhan-yojana"],
    "jandhan": ["pm-jan-dhan-yojana"],
    "rupay": ["pm-jan-dhan-yojana"],
    "no account": ["pm-jan-dhan-yojana"],
    "open account": ["pm-jan-dhan-yojana"],
    "बैंक खाता": ["pm-jan-dhan-yojana"],
    "ખાતું": ["pm-jan-dhan-yojana"],

    # ── Education / Scholarship ──────────────────────────────
    "scholarship": ["national-scholarship-portal", "gujarat-namo-saraswati-yojana"],
    "padhai": ["national-scholarship-portal"],
    "student": ["national-scholarship-portal", "gujarat-namo-saraswati-yojana"],
    "school": ["national-scholarship-portal", "gujarat-namo-saraswati-yojana"],
    "college": ["national-scholarship-portal"],
    "fees": ["national-scholarship-portal"],
    "education": ["national-scholarship-portal", "gujarat-namo-saraswati-yojana"],
    "vidyarthi": ["national-scholarship-portal"],
    "chhatravritti": ["national-scholarship-portal"],
    "shishyavritti": ["national-scholarship-portal", "gujarat-namo-saraswati-yojana"],
    "nsp": ["national-scholarship-portal"],
    "study": ["national-scholarship-portal"],
    "padhna": ["national-scholarship-portal"],
    "छात्रवृत्ति": ["national-scholarship-portal"],
    "શિષ્યવૃત્તિ": ["national-scholarship-portal", "gujarat-namo-saraswati-yojana"],
    "saraswati": ["gujarat-namo-saraswati-yojana"],
    "science": ["gujarat-namo-saraswati-yojana"],
    "vigyan": ["gujarat-namo-saraswati-yojana"],
    "class 11": ["gujarat-namo-saraswati-yojana"],
    "class 12": ["gujarat-namo-saraswati-yojana"],

    # ── Disability ───────────────────────────────────────────
    "disability": ["gujarat-viklang-sahay-yojana"],
    "viklang": ["gujarat-viklang-sahay-yojana"],
    "divyang": ["gujarat-viklang-sahay-yojana"],
    "apang": ["gujarat-viklang-sahay-yojana"],
    "wheelchair": ["gujarat-viklang-sahay-yojana"],
    "handicap": ["gujarat-viklang-sahay-yojana"],
    "hearing aid": ["gujarat-viklang-sahay-yojana"],
    "crutch": ["gujarat-viklang-sahay-yojana"],
    "disabled": ["gujarat-viklang-sahay-yojana"],
    "અપંગ": ["gujarat-viklang-sahay-yojana"],
    "विकलांग": ["gujarat-viklang-sahay-yojana"],

    # ── SC Artisan ───────────────────────────────────────────
    "manav garima": ["gujarat-manav-garima-yojana"],
    "toolkit": ["gujarat-manav-garima-yojana"],
    "artisan": ["gujarat-manav-garima-yojana"],
    "naai": ["gujarat-manav-garima-yojana"],
    "barber": ["gujarat-manav-garima-yojana"],
    "darzi": ["gujarat-manav-garima-yojana"],
    "tailor": ["gujarat-manav-garima-yojana"],
    "mochi": ["gujarat-manav-garima-yojana"],
    "cobbler": ["gujarat-manav-garima-yojana"],
    "sc tools": ["gujarat-manav-garima-yojana"],
    "free tools": ["gujarat-manav-garima-yojana"],
}


def _load():
    global _embeddings, _meta
    if _embeddings is None:
        _embeddings, _meta = load_index()


def load_schemes_lookup(schemes: list):
    global _schemes_by_id
    _schemes_by_id = {s["id"]: s for s in schemes}


def search(query: str, top_k: int = 5) -> list:
    _load()

    query_vec = embed_text(query).reshape(1, -1).astype(np.float32)
    scores = (_embeddings @ query_vec.T).flatten()

    results = []
    query_lower = query.lower()

    for idx, score in enumerate(scores):
        meta = _meta[idx]
        scheme = _schemes_by_id.get(meta["id"], {})
        boost = 0.0

        # Check all keyword matches — take highest boost
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
    search_and_explain("khedut sahay gujarat")
    search_and_explain("dikri mate bachat")
    search_and_explain("majdoor card")
    search_and_explain("viklang sahay")