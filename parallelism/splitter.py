from langchain_core.messages import SystemMessage, HumanMessage
from agents.llm import llm

def splitter(state):
    topic = state['topic']
    message = [
        SystemMessage(content = """
        You are an expert in splitting the topic into 3-4 meaningful subparts
        example:
        user: Research about Agentic Ai
        you : "History of Agentic AI","Applications of Agentic AI","Future of Agentic AI".
        

        Rules:
        - Return one task per line.
        - Each task must be independent.
        - Cover different aspects of the topic.
        - Do not explain your choices.
        - Do not number the tasks.
        - Return only the task names.
"""),
HumanMessage(content = topic)
    ]
    response= llm.invoke(message)
    tasks = [task.strip() for task in response.content.split("\n") if task.strip()]

    return {
        "tasks":tasks
    }
    