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

SYSTEM_PROMPT = """You are YojanaBot, a helpful assistant that helps Indians find government schemes.

Collect this profile through natural conversation:
1. gender (male/female)
2. age
3. state and district
4. occupation
5. caste category (General/OBC/SC/ST/EWS)
6. annual family income
7. has_bank_account
8. has_ration_card
9. has_existing_lpg — ONLY if gender is female

STRICT RULES:
- Ask maximum 2 questions per message.
- NEVER ask the same information twice. If user says they live in Ahmedabad, you already know state=Gujarat. Do not ask again.
- Match user's language. If they write in English, reply in English. If Hindi, reply in Hindi. If Gujarati, reply in Gujarati.
- Understand these as YES: yes, ha, haan, han, hai, haa, ji, ji haan, yes hai, hn, ya, yeah, हाँ, હા
- Understand these as NO: no, nahi, nai, nahin, na, nope, ना, ના
- If user mentions their purpose (scholarship, house, health) note it and ask only relevant questions first.
- gender must be explicitly stated. If unclear, ask once clearly: "Are you male or female?"
- Once you have gender, age, state, occupation, category — output PROFILE_COMPLETE immediately. Do not ask unnecessary questions.
- Never repeat back what user said in a long sentence. Keep responses short and direct.
- Do not use asterisks or markdown.

Output PROFILE_COMPLETE on a new line when ready:
PROFILE_COMPLETE:
{"gender":"male","age":20,"state":"GJ","district":"Ahmedabad","occupation":"student","category":"ST","income_annual":200000,"has_bank_account":true,"has_ration_card":null,"has_existing_lpg":null}

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