from src.feeder.graph import compile_feeder_graph

# Visualize graph
graph = compile_feeder_graph()
with open("./images/feeder_graph.png", "wb") as f:
    f.write(graph.get_graph(xray=True).draw_mermaid_png())
