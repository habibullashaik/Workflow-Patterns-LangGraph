from supervisor.graph import super_graph
topic = input("Enter topic: ")

state = {
    "topic": topic,
    "tasks": [],
    "task": "",
    "research": [],
    "article": "",
    "review": ""
}

result = super_graph.invoke(state)

print("=" * 80)
print("FINAL OUTPUT")
print("=" * 80)

print(result['review'])
