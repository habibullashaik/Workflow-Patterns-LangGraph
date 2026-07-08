from sequential.graph import sequential_graph
from router.graph import router_graph
user = input("Enter any Research topic: ")

message = {
    "topic":user,
    "research":"",
    "article":"",
    "review":"",
    "next":""
}

response = router_graph.invoke(message)

output_map = {
    "researcher": "research",
    "writer": "article",
    "reviewer": "review",
}

print("=" * 80)
print(f"Selected Agent : {response['next']}")
print("=" * 80)

print(response[output_map[response["next"]]])