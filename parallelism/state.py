from typing import Annotated
from typing_extensions import TypedDict
import operator


class AgentState(TypedDict):
    topic:str
    tasks: list[str]
    task:str
    research: Annotated[list[str], operator.add]
    article: str
    review: str
    