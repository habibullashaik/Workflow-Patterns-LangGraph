from langchain_core.messages import SystemMessage, HumanMessage
from agents.llm import llm


def research(state):
    topic = state["topic"]

    messages = [
        SystemMessage(content = 
                    """
    You are a Experienced Research assistant.
    Who have 30+ years of experience in researching in and out about the given topic.
    
    Your job is to Generate the best research notes not need to be in order or any structured ,
    a simple and direct researched notes.

    Rules:
    - Only gather useful information
    - Mainly focus on most important concepts and gradually moves to other topics.
    - Use bullet points
    - Do not write an article
    - Do not explain your reasons.
"""),
HumanMessage(content =f"Research the topic:\n\n{topic}")
    ]

    response = llm.invoke(messages)
    return {
        "research":response.content
    }
