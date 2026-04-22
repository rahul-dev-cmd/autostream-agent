# AutoStream Agent

An AI agent that converts casual social media chats into qualified leads by figuring out what the user wants and saving their details.

## How to Run

1. Clone the repo
2. Install the requirements `py -3.11 -m pip install -r requirements.txt`
3. Add your `.env` file (you'll need your OpenRouter API key)
4. Run `py -3.11 main.py`

## Architecture

I went with LangGraph over a standard LangChain chain because a simple chain is way too rigid for a real conversation that jumps around. With LangGraph, the agent acts more like a state machine. The state (which holds the chat history, current intent, and extracted lead info) flows from node to node. The app always starts at the intent detection node, and depending on whether the user is just saying hi, asking about pricing, or actually ready to buy, it routes to the right function.

Using MemorySaver was a huge help here. Instead of manually pushing the chat history back into the prompt every single time, MemorySaver ties the state to a `thread_id` (representing the user session). When a new message hits, it automatically pulls up the past turns. Finally, to make sure we don't trigger the backend with half-empty data, the lead capture tool is strictly gated — it only fires after the agent has collected all three fields (Name, Email, and Platform).

## Challenges I Faced

- **Python 3.14 incompatibility:** I originally tried building this on Python 3.14, but LangGraph threw compatibility errors. Had to downgrade to 3.11.
- **OpenRouter model ID issues:** Kept getting API errors because the model ID wasn't mapping correctly. Finally got it working by switching to `langchain_openai` with OpenRouter's base URL and passing the key directly.
- **The classic env bug:** Spent an embarrassing amount of time wondering why my API key was loading as `None` before realizing I forgot to call `load_dotenv()` at the top of the file.
- **Intent routing getting stuck:** Early on the agent kept looping because intent routing wasn't cleanly detecting the shift from inquiry to high intent. Refined the LLM prompt in the detect node to fix transitions.

## WhatsApp Deployment

To get this live on WhatsApp, I would set up a Twilio webhook pointing to a FastAPI backend. When a user sends a message, Twilio sends a POST request to that endpoint. The server extracts the text, passes it into `app.invoke()` using the user's phone number as the `thread_id` so MemorySaver knows who is talking, and gets the agent's reply. Then we fire a request back through Twilio to send the message to the user.

## Tech Stack

- Python 3.11
- LangGraph
- LangChain
- OpenRouter
- MemorySaver