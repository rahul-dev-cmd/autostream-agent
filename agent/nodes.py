
import json
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from .tools import mock_lead_capture

load_dotenv()

llm = ChatOpenAI(
    model="openrouter/free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "AutoStream"
    }
)

def load_kb():
    # Loads the local knowledge base
    kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Knowledge", "autostream_kb.json")
    with open(kb_path, "r") as f:
        return json.load(f)

def detect_intent(state):
    last_msg = state["messages"][-1]["content"]
    
    # LLM-based intent routing
    prompt = f"""Classify this message into one of three intents:
- casual: greeting or small talk
- inquiry: asking about product, features, pricing, or how something works
- high_intent: ready to buy, sign up, or try the product

Message: "{last_msg}"
Reply with only one word: casual, inquiry, or high_intent"""

    response = llm.invoke(prompt)
    intent = response.content.strip().lower()
    
    # Fallback to casual if the LLM goes off script
    if intent not in ["casual", "inquiry", "high_intent"]:
        intent = "casual"
    
    return {"intent": intent}

def handle_greeting(state):
    return {"messages": [{"role": "assistant", "content": "Hi there! Welcome to AutoStream. How can I help you with your video editing needs today?"}]}

def rag_retrieval(state):
    kb = load_kb()
    kb_string = json.dumps(kb)
    user_query = state["messages"][-1]["content"]
    
    prompt = f"You are an assistant for AutoStream. Answer the user's query based ONLY on this knowledge base: {kb_string}. \nUser Query: {user_query}"
    
    response = llm.invoke(prompt)
    return {"messages": [{"role": "assistant", "content": response.content}]}

def lead_collection(state):
    lead_info = state.get("lead_info", {})
    last_msg = state["messages"][-1]["content"]

    # We use the LLM to extract data from the user's latest reply
    extraction_prompt = f"""Extract the user's name, email, and creator platform from this message.
    Return ONLY a valid JSON object with keys "name", "email", and "platform". 
    If a value is not present or you cannot confidently extract it, set its value to null.
    Message: "{last_msg}"
    """
    try:
        extraction_response = llm.invoke(extraction_prompt)
        # Strip potential markdown formatting from the LLM output before parsing
        cleaned_response = extraction_response.content.replace('```json', '').replace('```', '').strip()
        extracted_data = json.loads(cleaned_response)
        
        # Update the lead_info dictionary with any newly found data
        if extracted_data.get("name"): lead_info["name"] = extracted_data["name"]
        if extracted_data.get("email"): lead_info["email"] = extracted_data["email"]
        if extracted_data.get("platform"): lead_info["platform"] = extracted_data["platform"]
    except Exception as e:
        # If parsing fails, we just continue and ask again
        pass

    missing = []
    if not lead_info.get("name"): missing.append("Name")
    if not lead_info.get("email"): missing.append("Email")
    if not lead_info.get("platform"): missing.append("Creator Platform (YouTube, Instagram, etc.)")
    
    # If anything is missing, ask for it and update the state
    if missing:
        ask_msg = f"Awesome! To get you set up, I just need your: {', '.join(missing)}."
        return {"lead_info": lead_info, "messages": [{"role": "assistant", "content": ask_msg}]}
    
    # Only execute the tool if all 3 values are collected and it hasn't been captured yet
    if not state.get("lead_captured"):
        mock_lead_capture(lead_info["name"], lead_info["email"], lead_info["platform"])
        return {"lead_info": lead_info, "lead_captured": True, "messages": [{"role": "assistant", "content": "Thanks! You're all set up. Our team will reach out shortly."}]}
    
    return {}