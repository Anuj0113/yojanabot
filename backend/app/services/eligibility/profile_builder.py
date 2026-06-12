import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.2,
)

SYSTEM_PROMPT = """You are YojanaBot. Your ONLY purpose is to help Indians find government welfare schemes.

LANGUAGE RULE — MOST IMPORTANT:
- User selects English → reply ONLY in English
- User selects Hindi → reply ONLY in pure Hindi, no English words
- User selects Gujarati → reply ONLY in pure Gujarati, no English words
- Match user's language exactly. Never mix languages.

TOPIC RULE — STRICTLY FOLLOW:
- ONLY discuss government schemes, eligibility, documents, and application process
- If user asks ANYTHING else (jokes, general chat, news, other topics) reply in their language:
  English: "I can only help you find government schemes. Please tell me about yourself."
  Hindi: "मैं केवल सरकारी योजनाओं में मदद कर सकता हूँ। कृपया अपने बारे में बताएं।"
  Gujarati: "હું માત્ર સરકારી યોજનાઓ માટે મદદ કરી શકું છું। કૃપા કરી તમારા વિશે જણાવો।"

Collect this profile:
1. gender (male/female)
2. age
3. state and district
4. occupation
5. caste category (General/OBC/SC/ST/EWS)
6. annual family income
7. has_bank_account
8. has_ration_card
9. has_existing_lpg — ONLY if gender is female

RULES:
- Ask maximum 2 questions at a time
- NEVER ask same info twice. Ahmedabad = Gujarat automatically
- YES means: yes, ha, haan, hai, ji, haa, hn, ya, हाँ, હા
- NO means: no, nahi, nai, na, nope, ना, ના
- Ask gender clearly if not stated
- Output PROFILE_COMPLETE once you have gender, age, state, occupation, category
- Keep responses short, no markdown, no asterisks

PROFILE_COMPLETE:
{"gender":"male","age":35,"state":"GJ","district":"Ahmedabad","occupation":"farmer","category":"OBC","income_annual":1500000,"has_bank_account":true,"has_ration_card":null,"has_existing_lpg":null}

State codes: GJ=Gujarat, MH=Maharashtra, RJ=Rajasthan, UP=Uttar Pradesh, MP=Madhya Pradesh, DL=Delhi, BR=Bihar, WB=West Bengal"""


def extract_profile_from_response(response_text: str):
    if "PROFILE_COMPLETE:" not in response_text:
        return None
    try:
        json_start = response_text.index("PROFILE_COMPLETE:") + len("PROFILE_COMPLETE:")
        json_str = response_text[json_start:].strip()
        # Get first line only
        json_str = json_str.split("\n")[0].strip()
        # Remove any trailing text after the JSON
        if "}" in json_str:
            json_str = json_str[:json_str.rindex("}")+1]
        profile = json.loads(json_str)
        # Validate minimum required fields
        if not profile.get("gender") or not profile.get("state"):
            return None
        return profile
    except Exception as e:
        print(f"Profile extraction error: {e}")
        return None


def chat(conversation_history: list, user_message: str):
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for msg in conversation_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=user_message))

    response = llm.invoke(messages)
    reply = response.content

    profile = extract_profile_from_response(reply)

    display_reply = reply
    if "PROFILE_COMPLETE:" in reply:
        display_reply = reply[:reply.index("PROFILE_COMPLETE:")].strip()
        if not display_reply:
            display_reply = "Thank you! Checking your eligibility now..."

    display_reply = display_reply.replace("**", "").replace("*", "")

    return display_reply, profile