import uuid
from agent.graph import app

def run_chat():
    print("Starting AutoStream Agent... (Type 'quit' to exit)")
    
    # Generate a unique thread ID for this specific session.
    # In a real WhatsApp deployment, this would be the user's phone number.
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    while True:
        user_input = input("User: ")
        if user_input.lower() == 'quit':
            break
            
        # We ONLY pass the new user message. 
        # LangGraph + MemorySaver automatically fetches the history and updates the state dict.
        input_state = {"messages": [{"role": "user", "content": user_input}]}
        
        # Invoke the graph with the session config
        result = app.invoke(input_state, config=config)
        
        # Extract and print the agent's latest response from the returned state
        latest_response = result["messages"][-1]["content"]
        print(f"Agent: {latest_response}")

if __name__ == "__main__":
    run_chat()