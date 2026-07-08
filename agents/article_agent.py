from langchain_core.messages import SystemMessage, HumanMessage
from agents.llm import llm


def writer(state):
    notes = "\n\n".join(state["research"])

    message = [
        SystemMessage(content = """
        You are an expert article writer.

        Your responsibility is to convert research notes into a clear article.
        You know how to add best logical headings and subheadings and many more.
        your job is so simple.
        Rules:

        - Write a well-structured article.
        - Use headings and subheadings.
        - Use bullet points when appropriate.
        - Use simple English.
        - Do not add information not present in the research notes.
        - Keep the flow logical.
"""),
HumanMessage(content = notes)
    ]
    response= llm.invoke(message)

    return {
        "article":response.content
    }
