from langgraph.graph import START, END, StateGraph
from langgraph.types import Send

from agents.article_agent import writer
from agents.parallel_research import research
from agents.review_agent import reviewer
from parallelism.state import AgentState
from parallelism.splitter import splitter

graph = StateGraph(AgentState)

graph.add_node("splitter", splitter)
graph.add_node("researcher", research)
graph.add_node("writer", writer)
graph.add_node("reviewer", reviewer)

graph.add_edge(START, "splitter")


def parallel_routing(state):
    return [
        Send("researcher", {"task": task})
        for task in state["tasks"]
    ]


graph.add_conditional_edges("splitter", parallel_routing, ["researcher"])

graph.add_edge("researcher", "writer")
graph.add_edge("writer", "reviewer")
graph.add_edge("reviewer", END)

parallel_graph = graph.compile()

from IPython.display import Image, display

display(
    Image(
        parallel_graph.get_graph().draw_mermaid_png()
    )
)
png = parallel_graph.get_graph().draw_mermaid_png()

with open("Parallel_agent.png", "wb") as f:
    f.write(png)
