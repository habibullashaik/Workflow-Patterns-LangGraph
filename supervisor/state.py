# supervisor/state.py
from typing_extensions import TypedDict
class SupervisorState(TypedDict):
    topic: str
    research: str
    article: str
    review: str
    next: str