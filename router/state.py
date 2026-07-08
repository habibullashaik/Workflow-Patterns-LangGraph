# router/state.py
from typing_extensions import TypedDict
class RouterState(TypedDict):
    topic: str
    research: str
    article: str
    review: str
    next: str