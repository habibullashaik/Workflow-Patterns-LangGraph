from langgraph.graph import START,END,StateGraph
from agents.article_agent import writer
from agents.llm import llm
from agents.parallel_research import research
from agents.review_agent import reviewer
from agents.state import AgentState


graph = StateGraph(AgentState)

#adding nodes
graph.add_node("researcher",research)
graph.add_node("writer",writer)
graph.add_node("reviewer",reviewer)

#connecting those nodes
graph.add_edge(START,"researcher")
graph.add_edge("researcher","writer")
graph.add_edge("writer","reviewer")
graph.add_edge("reviewer",END)

#Compiling
sequential_graph = graph.compile()


from IPython.display import Image, display

display(
    Image(
        sequential_graph.get_graph().draw_mermaid_png()
    )
)
png = sequential_graph.get_graph().draw_mermaid_png()

with open("Sequential_graph.png", "wb") as f:
    f.write(png)
