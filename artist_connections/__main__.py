from artist_connections.datatypes.datatypes import Edge, EdgesJSON, Graph, GraphNetworkX, NodesJSON
from artist_connections.helpers.helpers import load_edges_json
import polars as pl
import networkx as nx
import matplotlib.pyplot as plt
from difflib import get_close_matches
from pyvis.network import Network

#* run with 'python -m artist_connections'

def search(edges_json: EdgesJSON, query: str) -> str | None:
    if query in edges_json:
        return query
    
    matches = get_close_matches(query, edges_json.keys(), n=1, cutoff=0.8)
    if len(matches) > 0: 
        return matches[0] 
    
    return None
    

def create_singular_graph(edges_json: EdgesJSON, query: str) -> GraphNetworkX:
    graph: GraphNetworkX = {"nodes": [], "edges": []}

    graph["nodes"].append(query)
    for key in edges_json[query].keys():
        graph["nodes"].append(key.encode("ascii", "ignore").decode())

    for node in graph["nodes"]:
        node = node.encode("ascii", "ignore").decode()
        if node not in edges_json:
            # node exists but not in edges_json
            # means that this is a feature artist but they dont have a song of their own with a feature
            # * node should salways still exist in nodes_json if generated using edges_json in other script
            continue
            
        for key, value in edges_json[node].items():
            if key in graph["nodes"]:
                #new_edge: Edge = {"source": key, "target": node, "weight": value }
                new_edge = (key, node, value)
                graph["edges"].append(new_edge)

    return graph

def show_graph(graph: GraphNetworkX):
    G = nx.DiGraph()
    G.add_weighted_edges_from(graph["edges"])
    pos = nx.spring_layout(G, k=2)

    node_degrees = {}
    if not isinstance(G.degree, int):
        node_degrees = dict(G.degree)
    nx.draw_networkx(G, with_labels=True, node_color="skyblue", pos=pos)
    nx.set_node_attributes(G, node_degrees, "size")

    net = Network(width="100%", height="800px", bgcolor="black", directed=True, font_color="white", neighborhood_highlight=True) # type: ignore
    net.from_nx(G)
    net.show("graph.html", notebook=False)
    
def main():
    query: str = "Isaiah Rashad"
    edges_data = load_edges_json("data/edges.json")

    if edges_data is None:
        raise ValueError("Data is None")

    validated_query = search(edges_data, query)
    if validated_query is None:
        raise ValueError("Search query invalid, check your spelling")
    graph = create_singular_graph(edges_data, validated_query)
    show_graph(graph)


if __name__ == "__main__":
    main()