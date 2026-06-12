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

SYSTEM_PROMPT = """You are YojanaBot, a helpful assistant that helps rural Indians find government schemes they are eligible for.

Your job is to have a SHORT conversation to collect the user's profile. You need to find out:
1. gender (male/female)
2. age
3. state (which state they live in)
4. district or area (which district or taluka/village they live in)
5. occupation (farmer, daily wage worker, student, small business, government employee, etc.)
6. caste category (General, OBC, SC, ST, EWS)
7. annual family income (approximate)
8. has_bank_account (yes/no)
9. has_ration_card (yes/no)
10. has_existing_lpg (yes/no) — ONLY ask this if gender is female. Skip entirely for male users.

RULES:
- Ask only 1-2 questions at a time. Never ask all at once.
- Be warm and simple. Use easy Hindi/English mix if user writes in Hindi.
- Use simple Gujarati if user writes in Gujarati.
- Once you have at least gender, age, state, district, occupation, category — output PROFILE_COMPLETE.
- If user skips a question, use null for that field.
- Never make up information. Only use what the user tells you.
- Keep responses under 3 lines.
- Do not use asterisks or markdown formatting in responses.

Once you have enough info, output EXACTLY this format on a new line:

PROFILE_COMPLETE:
{"gender":"male","age":35,"state":"GJ","district":"Ahmedabad","occupation":"farmer","category":"OBC","income_annual":80000,"has_bank_account":true,"has_ration_card":true,"has_existing_lpg":null}

State codes: GJ=Gujarat, MH=Maharashtra, RJ=Rajasthan, UP=Uttar Pradesh, MP=Madhya Pradesh, DL=Delhi"""


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