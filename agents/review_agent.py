from langchain_core.messages import SystemMessage, HumanMessage
from agents.llm import llm


def reviewer(state):
    notes = state['article']

    message = [
        SystemMessage(content = """
        You are an expert content reviewer.

        Your responsibility is to improve the quality of the given article.
        
        Rules:

        - Correct the grammer and spelling.
        - Improve the quality.
        - Improve the flow between sections.
        - Keep the article beginner friendly.
        - Don't remove important information
        - Do not add information not present in the research notes.
        - return only the improved article.
"""),
HumanMessage(content = notes)
    ]
    response= llm.invoke(message)

    return {
        "review":response.content
    }
