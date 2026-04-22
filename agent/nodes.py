import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from .tools import mock_lead_capture

# Initialize Gemini 1.5 Flash as required by the assignment stack [cite: 86]
# Ensure to have GOOGLE_API_KEY set in your environment variables.
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

def load_kb():
    # Loads the local knowledge base [cite: 25]
    with open("knowledge_base/autostream_kb.json", "r") as f:
        return json.load(f)

def detect_intent(state):
    last_msg = state["messages"][-1]["content"].lower()
    
    # Keeping the hacky detection for now, but you should upgrade this to an LLM call later.
    intent = "casual"
    if "price" in last_msg or "cost" in last_msg or "plan" in last_msg:
        intent = "inquiry"
    if "buy" in last_msg or "sign up" in last_msg or "ready" in last_msg or "try" in last_msg:
        intent = "high_intent"
        
   
    return {"intent": intent} 

def handle_greeting(state):
    
    return {"messages": [{"role": "assistant", "content": "Hi there! Welcome to AutoStream. How can I help you with your video editing needs today?"}]}

def rag_retrieval(state):
    kb = load_kb()
    kb_string = json.dumps(kb)
    user_query = state["messages"][-1]["content"]
    
    # Actual RAG LLM call using Gemini [cite: 86] 
    prompt = f"You are an assistant for AutoStream. Answer the user's query based ONLY on this knowledge base: {kb_string}. \nUser Query: {user_query}"
    
    response = llm.invoke(prompt)
    return {"messages": [{"role": "assistant", "content": response.content}]}

def lead_collection(state):
    
    lead_info = state.get("lead_info", {})
    missing = []
    
    if not lead_info.get("name"): missing.append("Name")
    if not lead_info.get("email"): missing.append("Email")
    if not lead_info.get("platform"): missing.append("Creator Platform (YouTube, Instagram, etc.)")
    
    if missing:
        ask_msg = f"Awesome! To get you set up, I just need your: {', '.join(missing)}."
        return {"messages": [{"role": "assistant", "content": ask_msg}]}
    
    # Trigger tool if we have everything and haven't captured yet
    if not state.get("lead_captured"):
        mock_lead_capture(lead_info["name"], lead_info["email"], lead_info["platform"])
        return {"lead_captured": True, "messages": [{"role": "assistant", "content": "Thanks! You're all set up. Our team will reach out."}]}
    
    return {}