# sequential/state.py
from typing_extensions import TypedDict
class SequentialState(TypedDict):
    topic: str
    research: str
    article: str
    review: str