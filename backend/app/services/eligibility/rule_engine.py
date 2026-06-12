from typing import Literal
from dataclasses import dataclass


@dataclass
class EligibilityResult:
    scheme_id: str
    scheme_name: str
    status: Literal["eligible", "partial", "ineligible"]
    matched_conditions: list
    failed_conditions: list
    missing_info: list
    confidence: float


# Accurate income limits and exclusion rules per scheme based on official data
SCHEME_INCOME_RULES = {
    # PM Kisan: No income limit BUT excludes income tax payers, govt employees, professionals
    "pm-kisan-samman-nidhi": {
        "income_max": None,
        "excludes_income_tax_payer": True,
        "excludes_govt_employee": True,
        "excludes_professional": True,  # doctors, lawyers, engineers, CAs
        "income_tax_threshold": 250000,  # if income > 2.5L likely files taxes
    },
    # Ayushman Bharat: Rs 10,000/month = Rs 1.2 lakh/year max
    "ayushman-bharat-pmjay": {
        "income_max": 120000,
        "excludes_four_wheeler": True,
        "excludes_govt_employee": True,
    },
    # NSP: Rs 2.5 lakh for most pre-matric, Rs 3.5-4.5 lakh for higher education
    "national-scholarship-portal": {
        "income_max": 350000,
    },
    # MUDRA: No income limit
    "pm-mudra-yojana": {
        "income_max": None,
        "excludes_income_tax_defaulter": True,
    },
    # PMAY-G: Based on SECC 2011, no strict income limit but must be BPL/homeless
    "pm-awas-yojana-gramin": {
        "income_max": None,
        "must_be_homeless_or_kutcha": True,
    },
    # Ujjwala: BPL household, state-defined income limit (~Rs 1 lakh/year)
    "pm-ujjwala-yojana": {
        "income_max": 100000,
    },
    # Fasal Bima: No income limit for farmers
    "pm-fasal-bima-yojana": {
        "income_max": None,
    },
    # SSY: No income limit
    "sukanya-samriddhi-yojana": {
        "income_max": None,
    },
    # e-Shram: Must not be income tax payer
    "e-shram-card": {
        "income_max": None,
        "excludes_income_tax_payer": True,
        "income_tax_threshold": 250000,
    },
    # Jan Dhan: No income limit
    "pm-jan-dhan-yojana": {
        "income_max": None,
    },
    # iKhedut: No income limit for farmers
    "gujarat-ikhedut-portal": {
        "income_max": None,
    },
    # Manav Garima: Rs 47,000/year rural, Rs 60,000/year urban
    "gujarat-manav-garima-yojana": {
        "income_max": 47000,
    },
    # Viklang Sahay: No income limit
    "gujarat-viklang-sahay-yojana": {
        "income_max": None,
    },
    # Namo Saraswati: No income limit
    "gujarat-namo-saraswati-yojana": {
        "income_max": None,
    },
    # Chiranjeevi: No income limit (BPL free, others pay Rs 850/year)
    "gujarat-chiranjeevi-yojana": {
        "income_max": None,
    },
}


def check_eligibility(profile: dict, scheme: dict) -> EligibilityResult:
    rules = scheme.get("eligibility", {})
    name  = scheme.get("name_en", scheme.get("id", "Unknown"))
    sid   = scheme.get("id", "")

    matched = []
    failed  = []
    missing = []

    income = profile.get("income_annual")
    occupation = profile.get("occupation", "")

    # ── 1. Gender ────────────────────────────────────────────
    required_gender = rules.get("gender", "any")
    if required_gender != "any":
        if profile.get("gender") is None:
            missing.append("gender")
        elif profile["gender"].lower() != required_gender.lower():
            failed.append(f"Requires {required_gender} applicant")
        else:
            matched.append(f"Gender matches ({required_gender})")

    # ── 2. Age ───────────────────────────────────────────────
    age_min = rules.get("age_min")
    age_max = rules.get("age_max")
    age = profile.get("age")

    if age_min is not None or age_max is not None:
        if age is None:
            missing.append("age")
        else:
            age = int(age)
            if age_min is not None and age < age_min:
                failed.append(f"Minimum age required: {age_min} (yours: {age})")
            elif age_max is not None and age > age_max:
                failed.append(f"Maximum age allowed: {age_max} (yours: {age})")
            else:
                matched.append(f"Age {age} is within eligible range")

    # ── 3. Accurate income check ─────────────────────────────
    scheme_income_rules = SCHEME_INCOME_RULES.get(sid, {})
    income_max = scheme_income_rules.get("income_max")

    if income_max is not None:
        if income is None:
            missing.append("annual_income")
        elif income > income_max:
            failed.append(f"Income Rs {income:,}/year exceeds limit of Rs {income_max:,}/year for this scheme")
        else:
            matched.append(f"Income Rs {income:,} is within the limit")

    # ── 3b. Income tax payer exclusion ───────────────────────
    if scheme_income_rules.get("excludes_income_tax_payer"):
        tax_threshold = scheme_income_rules.get("income_tax_threshold", 250000)
        if income and income > tax_threshold:
            failed.append(f"Income tax payers (income > Rs {tax_threshold:,}) are not eligible")
        elif income and income <= tax_threshold:
            matched.append("Not an income tax payer — eligible")

    # ── 3c. Govt employee exclusion ──────────────────────────
    if scheme_income_rules.get("excludes_govt_employee"):
        if occupation and "government" in occupation.lower():
            failed.append("Government employees are not eligible for this scheme")

    # ── 3d. Professional exclusion (PM Kisan) ────────────────
    if scheme_income_rules.get("excludes_professional"):
        professional_keywords = ["doctor", "lawyer", "engineer", "ca", "chartered", "architect"]
        if occupation and any(k in occupation.lower() for k in professional_keywords):
            failed.append("Professionals (doctors, lawyers, engineers, CAs) are not eligible")

    # ── 4. Category ──────────────────────────────────────────
    required_cats = rules.get("category", ["all"])
    if "all" not in required_cats:
        user_cat = profile.get("category")
        if user_cat is None:
            missing.append("caste_category")
        elif user_cat.upper() not in [c.upper() for c in required_cats]:
            failed.append(f"Scheme is for {', '.join(required_cats)} category only")
        else:
            matched.append(f"Category {user_cat} is eligible")

    # ── 5. State ─────────────────────────────────────────────
    required_states = rules.get("state", ["all"])
    if "all" not in required_states:
        user_state = profile.get("state")
        if user_state is None:
            missing.append("state")
        elif user_state.upper() not in [s.upper() for s in required_states]:
            failed.append(f"Scheme only available in: {', '.join(required_states)}")
        else:
            matched.append(f"Available in your state ({user_state})")

    # ── 6. Occupation ────────────────────────────────────────
    required_occupations = rules.get("occupation", ["any"])
    if "any" not in required_occupations:
        user_occ = profile.get("occupation")
        if user_occ is None:
            missing.append("occupation")
        else:
            occ_match = any(
                req.lower() in user_occ.lower() or user_occ.lower() in req.lower()
                for req in required_occupations
            )
            if not occ_match:
                failed.append(f"Scheme is for: {', '.join(required_occupations)}")
            else:
                matched.append(f"Occupation '{user_occ}' is eligible")

    # ── 7. Bank Account ──────────────────────────────────────
    req_bank = rules.get("has_bank_account")
    if req_bank is True:
        if profile.get("has_bank_account") is None:
            missing.append("bank_account_status")
        elif profile["has_bank_account"] is False:
            failed.append("Requires a bank account")
        else:
            matched.append("Bank account requirement met")
    elif req_bank is False:
        if profile.get("has_bank_account") is True:
            failed.append("Scheme is for those without existing bank accounts")

    # ── 8. Ration Card ───────────────────────────────────────
    req_ration = rules.get("has_ration_card")
    if req_ration is True:
        if profile.get("has_ration_card") is None:
            missing.append("ration_card_status")
        elif profile["has_ration_card"] is False:
            failed.append("Requires a valid ration card")
        else:
            matched.append("Ration card requirement met")

    # ── 9. Existing LPG ─────────────────────────────────────
    req_lpg = rules.get("has_existing_lpg")
    if req_lpg is False:
        if profile.get("has_existing_lpg") is True:
            failed.append("Already has LPG connection — not eligible")
        elif profile.get("has_existing_lpg") is None:
            missing.append("existing_lpg_connection")
        else:
            matched.append("No existing LPG — eligible for new connection")

    # ── 10. Disability ───────────────────────────────────────
    custom = rules.get("custom_conditions", [])
    needs_disability = any("disability" in c.lower() for c in custom)
    if needs_disability:
        disability = profile.get("disability_percent")
        if disability is None:
            missing.append("disability_percent")
        elif disability < 40:
            failed.append("Requires minimum 40% disability certificate")
        else:
            matched.append(f"Disability {disability}% meets requirement")

    # ── Determine status ─────────────────────────────────────
    total_checks = len(matched) + len(failed) + len(missing)

    if len(failed) > 0:
        status = "ineligible"
        confidence = 0.95 if len(missing) == 0 else 0.75
    elif len(missing) > 0:
        status = "partial"
        confidence = len(matched) / max(total_checks, 1)
    else:
        status = "eligible"
        confidence = 0.95

    return EligibilityResult(
        scheme_id=sid,
        scheme_name=name,
        status=status,
        matched_conditions=matched,
        failed_conditions=failed,
        missing_info=missing,
        confidence=round(confidence, 2),
    )


def check_all_schemes(profile: dict, schemes: list) -> dict:
    results = {"eligible": [], "partial": [], "ineligible": []}

    for scheme in schemes:
        if not scheme.get("active", True):
            continue
        result = check_eligibility(profile, scheme)
        results[result.status].append(result)

    for bucket in results.values():
        bucket.sort(key=lambda r: r.confidence, reverse=True)

    return results