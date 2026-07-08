from langgraph.graph import START,END,StateGraph
from agents.article_agent import writer
from agents.llm import llm
from agents.research_agent import research
from agents.review_agent import reviewer
from supervisor.state import SupervisorState
from supervisor.supervisor import supervisor


graph = StateGraph(SupervisorState)

graph.add_node("supervisor",supervisor)
graph.add_node("researcher",research)
graph.add_node("writer",writer)
graph.add_node("reviewer",reviewer)

graph.add_edge(START,"supervisor")


def routing_edge(state):
    return state['next']

graph.add_conditional_edges(
    "supervisor",
    routing_edge,
    {
        "researcher":"researcher",
        "writer":"writer",
        "reviewer":"reviewer",
        "FINISH":END
    },
)

graph.add_edge("researcher","supervisor")
graph.add_edge("writer","supervisor")
graph.add_edge("reviewer","supervisor")

super_graph = graph.compile()

# from IPython.display import Image, display

# display(
#     Image(
#         super_graph.get_graph().draw_mermaid_png()
#     )
# )
# png = super_graph.get_graph().draw_mermaid_png()

# with open("super_graph.png", "wb") as f:
#     f.write(png)
