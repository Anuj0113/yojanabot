"""
Scheme Details Service
Given a scheme ID and user's district/state, returns:
- Full offline location (nearest office)
- Website to apply online
- Documents required
- Step by step application process
"""

SCHEME_DETAILS = {
    "pm-ujjwala-yojana": {
        "apply_steps": [
            "Step 1: Visit your nearest LPG distributor (HP Gas / Indane / Bharat Gas)",
            "Step 2: Ask for the Ujjwala Yojana application form (Form KYC-1)",
            "Step 3: Fill the form with your name, address, Aadhaar number",
            "Step 4: Attach copies of Aadhaar card, BPL ration card, bank passbook",
            "Step 5: Submit the form at the distributor",
            "Step 6: LPG connection will be provided within 15-30 days"
        ],
        "online_url": "https://www.pmuy.gov.in",
        "offline_location": "Nearest LPG distributor — HP Gas, Indane, or Bharat Gas agency in your area",
        "helpline": "1800-233-3555 (toll free)"
    },
    "pm-awas-yojana-gramin": {
        "apply_steps": [
            "Step 1: Check if your name is in the SECC 2011 list at your Gram Panchayat",
            "Step 2: If your name is listed, approach your Gram Panchayat office",
            "Step 3: Fill the PMAY-G application form",
            "Step 4: Attach Aadhaar card, BPL certificate, bank passbook, caste certificate",
            "Step 5: Submit to Gram Panchayat — they will verify and forward to Block office",
            "Step 6: Money is transferred directly to your bank account in installments"
        ],
        "online_url": "https://pmayg.nic.in",
        "offline_location": "Your Gram Panchayat office or Block Development Office (BDO)",
        "helpline": "1800-11-6446 (toll free)"
    },
    "pm-kisan-samman-nidhi": {
        "apply_steps": [
            "Step 1: Visit nearest Common Service Centre (CSC) or Patwari office",
            "Step 2: Carry Aadhaar card, land documents (7/12 Utara), bank passbook",
            "Step 3: CSC operator will register you on pmkisan.gov.in",
            "Step 4: Your application will be verified by local Patwari",
            "Step 5: After verification, Rs 2000 installments start within 2-3 months",
            "Step 6: Check status at pmkisan.gov.in using your Aadhaar or mobile number"
        ],
        "online_url": "https://pmkisan.gov.in",
        "offline_location": "Common Service Centre (CSC) or Patwari / Talati office in your village",
        "helpline": "155261 or 011-24300606"
    },
    "ayushman-bharat-pmjay": {
        "apply_steps": [
            "Step 1: Check eligibility at pmjay.gov.in or call 14555",
            "Step 2: Visit nearest Common Service Centre (CSC) with Aadhaar and ration card",
            "Step 3: Get your Ayushman card generated for free",
            "Step 4: Show the Ayushman card at any empanelled hospital for cashless treatment",
            "Step 5: No premium payment required for BPL families",
            "Step 6: Find empanelled hospitals at hospitals.pmjay.gov.in"
        ],
        "online_url": "https://pmjay.gov.in",
        "offline_location": "Common Service Centre (CSC) or any empanelled government/private hospital",
        "helpline": "14555 (toll free)"
    },
    "national-scholarship-portal": {
        "apply_steps": [
            "Step 1: Visit scholarships.gov.in and register with mobile number",
            "Step 2: Select your scholarship scheme based on your category and course",
            "Step 3: Fill application form with academic and personal details",
            "Step 4: Upload documents: marksheet, income certificate, caste certificate, bank passbook",
            "Step 5: Submit before deadline (usually September-October each year)",
            "Step 6: Track status on NSP portal using application ID"
        ],
        "online_url": "https://scholarships.gov.in",
        "offline_location": "Your school or college administration can help with the online application",
        "helpline": "0120-6619540"
    },
    "pm-mudra-yojana": {
        "apply_steps": [
            "Step 1: Prepare a simple business plan (what business, how much loan needed)",
            "Step 2: Visit nearest bank, regional rural bank, or microfinance institution",
            "Step 3: Ask for MUDRA loan application form",
            "Step 4: Fill form and attach Aadhaar, PAN card, bank passbook, business proof",
            "Step 5: Bank will evaluate and approve within 7-30 days",
            "Step 6: Loan amount credited directly to your bank account",
            "Step 7: You can also apply online at mudra.org.in"
        ],
        "online_url": "https://www.mudra.org.in",
        "offline_location": "Any nationalised bank branch, regional rural bank, or microfinance institution near you",
        "helpline": "1800-180-1111 (toll free)"
    },
    "pm-fasal-bima-yojana": {
        "apply_steps": [
            "Step 1: Visit nearest bank branch or Common Service Centre before crop sowing",
            "Step 2: Carry land records (7/12 Utara), Aadhaar, bank passbook",
            "Step 3: Fill the PMFBY enrollment form",
            "Step 4: Pay the premium (only 2% for Kharif, 1.5% for Rabi crops)",
            "Step 5: In case of crop loss, report to bank or agriculture office within 72 hours",
            "Step 6: Claim amount transferred directly to bank account after survey"
        ],
        "online_url": "https://pmfby.gov.in",
        "offline_location": "Nearest bank branch or Common Service Centre (CSC) — enroll before crop sowing deadline",
        "helpline": "1800-200-7710 (toll free)"
    },
    "sukanya-samriddhi-yojana": {
        "apply_steps": [
            "Step 1: Visit nearest post office or authorised bank (SBI, PNB, Bank of Baroda etc.)",
            "Step 2: Carry girl child's birth certificate, parent's Aadhaar and PAN card",
            "Step 3: Fill SSY account opening form",
            "Step 4: Deposit minimum Rs 250 to open the account",
            "Step 5: Account matures when girl turns 21 years old",
            "Step 6: Partial withdrawal allowed after girl turns 18 for education or marriage"
        ],
        "online_url": None,
        "offline_location": "Nearest post office or any authorised bank branch (SBI, PNB, Canara Bank, Bank of Baroda)",
        "helpline": "1800-266-6868 (India Post toll free)"
    },
    "e-shram-card": {
        "apply_steps": [
            "Step 1: Visit eshram.gov.in or nearest Common Service Centre (CSC)",
            "Step 2: Registration is completely FREE at CSC",
            "Step 3: Carry Aadhaar card with mobile number linked to it",
            "Step 4: Fill basic details — name, occupation, bank account",
            "Step 5: e-Shram card generated instantly with 12-digit UAN number",
            "Step 6: Download e-Shram card from the portal"
        ],
        "online_url": "https://eshram.gov.in",
        "offline_location": "Common Service Centre (CSC) — registration is completely free",
        "helpline": "14434 (toll free)"
    },
    "pm-jan-dhan-yojana": {
        "apply_steps": [
            "Step 1: Visit any bank branch near you",
            "Step 2: Ask for Jan Dhan account opening form",
            "Step 3: Carry any one ID proof: Aadhaar, Voter ID, NREGA card, or driving licence",
            "Step 4: Fill the form and submit with one passport size photo",
            "Step 5: Account opened immediately — zero balance required",
            "Step 6: RuPay debit card issued within 7-10 days"
        ],
        "online_url": "https://pmjdy.gov.in",
        "offline_location": "Any bank branch near you — specifically Business Correspondents (BC agents) in rural areas",
        "helpline": "1800-11-0001 (toll free)"
    },
    "gujarat-ikhedut-portal": {
        "apply_steps": [
            "Step 1: Register on ikhedut.gujarat.gov.in using your mobile number",
            "Step 2: Login and select the scheme you want to apply for",
            "Step 3: Fill the application with land details and bank information",
            "Step 4: Upload 7/12 Utara, Aadhaar, bank passbook",
            "Step 5: Submit application — note your application number",
            "Step 6: Visit Agriculture Department office if physical verification required",
            "Step 7: Subsidy amount transferred to bank account after approval"
        ],
        "online_url": "https://ikhedut.gujarat.gov.in",
        "offline_location": "Gram Seva Kendra or nearest Agriculture Department office in your taluka",
        "helpline": "1800-233-0150 (Gujarat Agriculture toll free)"
    },
    "gujarat-manav-garima-yojana": {
        "apply_steps": [
            "Step 1: Visit esamajkalyan.gujarat.gov.in and register",
            "Step 2: Select Manav Garima Yojana from the scheme list",
            "Step 3: Fill application form with personal and income details",
            "Step 4: Upload Aadhaar, SC caste certificate, income certificate, bank passbook",
            "Step 5: Submit online — application goes to District Social Justice Office",
            "Step 6: Toolkit distributed at a government camp or mailed to address"
        ],
        "online_url": "https://esamajkalyan.gujarat.gov.in",
        "offline_location": "District Social Justice and Empowerment Office in your district headquarters",
        "helpline": "1800-233-5500 (Gujarat Social Justice toll free)"
    },
    "gujarat-viklang-sahay-yojana": {
        "apply_steps": [
            "Step 1: Get disability certificate from government hospital (40% or above)",
            "Step 2: Visit esamajkalyan.gujarat.gov.in or District Social Justice Office",
            "Step 3: Fill application form for required assistive device",
            "Step 4: Upload disability certificate, Aadhaar, residence proof, photo",
            "Step 5: Application verified by district office",
            "Step 6: Device provided at a distribution camp or through government hospital"
        ],
        "online_url": "https://esamajkalyan.gujarat.gov.in",
        "offline_location": "District Social Justice and Empowerment Office or nearest government hospital",
        "helpline": "1800-233-5500 (Gujarat Social Justice toll free)"
    },
    "gujarat-namo-saraswati-yojana": {
        "apply_steps": [
            "Step 1: Visit scholarships.gujarat.gov.in",
            "Step 2: Register with your school enrollment number and mobile number",
            "Step 3: Fill the scholarship application form",
            "Step 4: Upload Class 10 marksheet, school bonafide certificate, bank passbook",
            "Step 5: Submit before deadline — school principal must approve",
            "Step 6: Rs 10,000 transferred to student bank account annually"
        ],
        "online_url": "https://scholarships.gujarat.gov.in",
        "offline_location": "Your school administration can help with the online application",
        "helpline": "1800-233-5500"
    },
    "gujarat-chiranjeevi-yojana": {
        "apply_steps": [
            "Step 1: Visit nearest Common Service Centre (CSC) or empanelled hospital",
            "Step 2: Carry Aadhaar card and ration card or residence proof",
            "Step 3: Register for Chiranjeevi card — BPL families get it free, others pay Rs 850/year",
            "Step 4: Chiranjeevi card generated immediately",
            "Step 5: Show card at any empanelled hospital in Gujarat for cashless treatment",
            "Step 6: Find empanelled hospitals at health.gujarat.gov.in"
        ],
        "online_url": "https://health.gujarat.gov.in",
        "offline_location": "Common Service Centre (CSC) or any empanelled government/private hospital in Gujarat",
        "helpline": "104 (Gujarat Health helpline)"
    }
}


def get_scheme_details(scheme_id: str, district: str = None, state: str = None) -> dict:
    """
    Returns full application details for a scheme.
    Personalises the offline location with district if provided.
    """
    details = SCHEME_DETAILS.get(scheme_id)
    if not details:
        return None

    result = dict(details)

    # Personalise offline location with district
    if district:
        result["offline_location_personalised"] = (
            f"{result['offline_location']} — nearest to {district}"
        )
    else:
        result["offline_location_personalised"] = result["offline_location"]

    return result


def format_scheme_details_whatsapp(scheme_name: str, details: dict) -> str:
    """Format scheme details as clean WhatsApp message."""
    lines = []
    lines.append(f"{scheme_name}")
    lines.append("")

    if details.get("offline_location_personalised"):
        lines.append(f"Where to apply:")
        lines.append(f"{details['offline_location_personalised']}")
        lines.append("")

    if details.get("online_url"):
        lines.append(f"Online: {details['online_url']}")
        lines.append("")

    if details.get("helpline"):
        lines.append(f"Helpline: {details['helpline']}")
        lines.append("")

    if details.get("apply_steps"):
        lines.append("How to apply:")
        for step in details["apply_steps"]:
            lines.append(step)

    return "\n".join(lines)


def format_scheme_details_web(scheme_id: str, scheme_name: str, documents: list, details: dict) -> dict:
    """Format scheme details for web frontend response."""
    return {
        "scheme_id": scheme_id,
        "scheme_name": scheme_name,
        "where_to_apply": details.get("offline_location_personalised"),
        "online_url": details.get("online_url"),
        "helpline": details.get("helpline"),
        "documents_required": documents,
        "apply_steps": details.get("apply_steps", [])
    }