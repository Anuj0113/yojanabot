from typing import Literal
from dataclasses import dataclass, field


@dataclass
class EligibilityResult:
    scheme_id: str
    scheme_name: str
    status: Literal["eligible", "partial", "ineligible"]
    matched_conditions: list
    failed_conditions: list
    missing_info: list
    confidence: float


def check_eligibility(profile: dict, scheme: dict) -> EligibilityResult:
    rules = scheme.get("eligibility", {})
    name  = scheme.get("name_en", scheme.get("id", "Unknown"))
    sid   = scheme.get("id", "")

    matched = []
    failed  = []
    missing = []

    # 1. Gender
    required_gender = rules.get("gender", "any")
    if required_gender != "any":
        if profile.get("gender") is None:
            missing.append("gender")
        elif profile["gender"].lower() != required_gender.lower():
            failed.append(f"Requires {required_gender} applicant")
        else:
            matched.append(f"Gender matches ({required_gender})")

    # 2. Age
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

    # 3. Income
    income_max = rules.get("income_max_annual")
    income = profile.get("income_annual")

    if income_max is not None:
        if income is None:
            missing.append("annual_income")
        elif income > income_max:
            failed.append(f"Income limit is Rs {income_max:,}/year (yours: Rs {income:,})")
        else:
            matched.append(f"Income Rs {income:,} is within the limit")

    # 4. Category
    required_cats = rules.get("category", ["all"])
    if "all" not in required_cats:
        user_cat = profile.get("category")
        if user_cat is None:
            missing.append("caste_category")
        elif user_cat.upper() not in [c.upper() for c in required_cats]:
            failed.append(f"Scheme is for {', '.join(required_cats)} category only")
        else:
            matched.append(f"Category {user_cat} is eligible")

    # 5. State
    required_states = rules.get("state", ["all"])
    if "all" not in required_states:
        user_state = profile.get("state")
        if user_state is None:
            missing.append("state")
        elif user_state.upper() not in [s.upper() for s in required_states]:
            failed.append(f"Scheme only available in: {', '.join(required_states)}")
        else:
            matched.append(f"Available in your state ({user_state})")

    # 6. Occupation
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

    # 7. Bank Account
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

    # 8. Ration Card
    req_ration = rules.get("has_ration_card")
    if req_ration is True:
        if profile.get("has_ration_card") is None:
            missing.append("ration_card_status")
        elif profile["has_ration_card"] is False:
            failed.append("Requires a valid ration card")
        else:
            matched.append("Ration card requirement met")

    # 9. Existing LPG
    req_lpg = rules.get("has_existing_lpg")
    if req_lpg is False:
        if profile.get("has_existing_lpg") is True:
            failed.append("Already has LPG connection — not eligible")
        elif profile.get("has_existing_lpg") is None:
            missing.append("existing_lpg_connection")
        else:
            matched.append("No existing LPG — eligible for new connection")

    # 10. Disability
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

    # Determine status
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