"""
Accuracy test for the rule engine.
Run with: cd backend && python -m pytest tests/test_rule_engine.py -v
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.eligibility.rule_engine import check_eligibility, check_all_schemes

# ── Load schemes ─────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data/schemes")

with open(os.path.join(DATA_DIR, "central_schemes.json"), encoding="utf-8") as f:
    central = json.load(f)
with open(os.path.join(DATA_DIR, "gujarat_schemes.json"), encoding="utf-8") as f:
    gujarat = json.load(f)

ALL_SCHEMES = central + gujarat

def get_scheme(scheme_id):
    return next(s for s in ALL_SCHEMES if s["id"] == scheme_id)


# ── 20 labelled test cases (ground truth) ────────────────────────────────────
# Format: (profile, scheme_id, expected_status, description)
TEST_CASES = [

    # ✅ Clear ELIGIBLE cases
    (
        {"gender": "female", "age": 28, "category": "BPL", "has_bank_account": True,
         "has_ration_card": True, "has_existing_lpg": False, "occupation": "any", "state": "GJ"},
        "pm-ujjwala-yojana", "eligible",
        "BPL woman, no LPG, has bank account + ration card → Ujjwala eligible"
    ),
    (
        {"gender": "any", "age": 40, "occupation": "farmer", "has_bank_account": True,
         "category": "OBC", "state": "GJ"},
        "pm-kisan-samman-nidhi", "eligible",
        "Farmer with bank account → PM Kisan eligible"
    ),
    (
        {"gender": "any", "age": 25, "category": "BPL", "has_ration_card": True, "state": "GJ"},
        "ayushman-bharat-pmjay", "eligible",
        "BPL with ration card → Ayushman Bharat eligible"
    ),
    (
        {"gender": "any", "age": 30, "has_bank_account": False, "state": "GJ"},
        "pm-jan-dhan-yojana", "eligible",
        "Person without bank account → Jan Dhan eligible"
    ),
    (
        {"gender": "female", "age": 8, "category": "general", "state": "GJ"},
        "sukanya-samriddhi-yojana", "eligible",
        "Girl child age 8 → SSY eligible"
    ),
    (
        {"gender": "any", "age": 35, "occupation": "farmer", "has_bank_account": True, "state": "GJ"},
        "pm-fasal-bima-yojana", "eligible",
        "Gujarat farmer → PMFBY eligible"
    ),
    (
        {"gender": "any", "age": 30, "occupation": "daily_wage", "has_bank_account": True,
         "state": "GJ", "category": "general"},
        "e-shram-card", "eligible",
        "Daily wage unorganised worker → e-Shram eligible"
    ),
    (
        {"gender": "any", "age": 25, "has_bank_account": True, "occupation": "small_business",
         "state": "GJ", "category": "general"},
        "pm-mudra-yojana", "eligible",
        "Person with small business plan → MUDRA eligible"
    ),
    (
        {"gender": "any", "age": 35, "occupation": "farmer", "has_bank_account": True, "state": "GJ"},
        "gujarat-ikhedut-portal", "eligible",
        "Gujarat farmer → iKhedut eligible"
    ),
    (
        {"gender": "any", "age": 40, "category": "SC", "occupation": "artisan",
         "income_annual": 40000, "has_bank_account": True, "state": "GJ"},
        "gujarat-manav-garima-yojana", "eligible",
        "SC artisan in Gujarat, income under 47k → Manav Garima eligible"
    ),

    # ❌ Clear INELIGIBLE cases
    (
        {"gender": "male", "age": 35, "category": "BPL", "has_bank_account": True,
         "has_ration_card": True, "has_existing_lpg": False},
        "pm-ujjwala-yojana", "ineligible",
        "Male applicant → Ujjwala ineligible (women only)"
    ),
    (
        {"gender": "female", "age": 28, "category": "BPL", "has_bank_account": True,
         "has_ration_card": True, "has_existing_lpg": True},
        "pm-ujjwala-yojana", "ineligible",
        "Already has LPG → Ujjwala ineligible"
    ),
    (
        {"gender": "any", "age": 40, "occupation": "government_employee",
         "has_bank_account": True, "state": "GJ"},
        "pm-kisan-samman-nidhi", "ineligible",
        "Government employee (non-farmer) → PM Kisan ineligible"
    ),
    (
        {"gender": "female", "age": 12, "category": "general", "state": "GJ"},
        "sukanya-samriddhi-yojana", "ineligible",
        "Girl child over 10 → SSY ineligible"
    ),
    (
        {"gender": "any", "age": 30, "has_bank_account": True, "state": "MH"},
        "gujarat-chiranjeevi-yojana", "ineligible",
        "Maharashtra resident → Gujarat Chiranjeevi ineligible"
    ),
    (
        {"gender": "male", "age": 30, "category": "general", "income_annual": 350000,
         "occupation": "student", "state": "GJ"},
        "national-scholarship-portal", "ineligible",
        "General category + income over 2.5L → NSP ineligible"
    ),

    # 🟡 PARTIAL cases — missing info
    (
        {"gender": "female", "age": 28},
        "pm-ujjwala-yojana", "partial",
        "Female but missing BPL/bank/LPG info → partial"
    ),
    (
        {"occupation": "farmer", "state": "GJ"},
        "pm-kisan-samman-nidhi", "partial",
        "Farmer in Gujarat but age/bank unknown → partial"
    ),
    (
        {"gender": "any", "age": 25, "state": "GJ"},
        "ayushman-bharat-pmjay", "partial",
        "Gujarat resident but category/ration unknown → partial"
    ),
    (
        {"gender": "any", "age": 30, "category": "SC", "state": "GJ"},
        "gujarat-manav-garima-yojana", "partial",
        "SC in Gujarat but income unknown → partial"
    ),
]


# ── Run tests ────────────────────────────────────────────────────────────────
def test_accuracy():
    correct = 0
    total = len(TEST_CASES)
    failures = []

    for profile, scheme_id, expected, description in TEST_CASES:
        scheme = get_scheme(scheme_id)
        result = check_eligibility(profile, scheme)
        passed = result.status == expected
        if passed:
            correct += 1
        else:
            failures.append({
                "description": description,
                "expected": expected,
                "got": result.status,
                "failed_conditions": result.failed_conditions,
                "missing_info": result.missing_info,
            })

    accuracy = correct / total * 100
    print(f"\n{'='*60}")
    print(f"  RULE ENGINE ACCURACY TEST")
    print(f"{'='*60}")
    print(f"  Passed : {correct}/{total}")
    print(f"  Accuracy: {accuracy:.1f}%")

    if failures:
        print(f"\n  Failed cases:")
        for f in failures:
            print(f"  ✗ {f['description']}")
            print(f"    Expected: {f['expected']} | Got: {f['got']}")
            if f["failed_conditions"]:
                print(f"    Failed: {f['failed_conditions']}")

    print(f"{'='*60}\n")
    assert accuracy >= 85.0, f"Accuracy {accuracy:.1f}% below 85% threshold"
    return accuracy


if __name__ == "__main__":
    test_accuracy()