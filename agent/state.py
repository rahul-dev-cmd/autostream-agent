from typing import TypedDict, Annotated, List, Optional
import operator

# State dictionary to keep track of the convo and extracted details
class AgentState(TypedDict):
    messages: Annotated[List[dict], operator.add] # stores history
    intent: str # casual, inquiry, or high_intent
    lead_info: dict # collected lead details (name, email, platform)
    lead_captured: bool