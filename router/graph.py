from langgraph.graph import START,END,StateGraph
from agents.article_agent import writer
from agents.llm import llm
from agents.parallel_research import research
from agents.review_agent import reviewer
from agents.state import AgentState
from router.route import routee


graph = StateGraph(AgentState)

graph.add_node("router",routee)
graph.add_node("researcher",research)
graph.add_node("writer",writer)
graph.add_node("reviewer",reviewer)

graph.add_edge(START,"router")


def routing_edge(state):
    return state['next']

graph.add_conditional_edges(
    "router",
    routing_edge,
    {
        "researcher":"researcher",
        "writer":"writer",
        "reviewer":"reviewer"
    },
)

graph.add_edge("researcher",END)
graph.add_edge("writer",END)
graph.add_edge("reviewer",END)

router_graph = graph.compile()

from IPython.display import Image, display

display(
    Image(
        router_graph.get_graph().draw_mermaid_png()
    )
)
png = router_graph.get_graph().draw_mermaid_png()

with open("Router_graph.png", "wb") as f:
    f.write(png)
