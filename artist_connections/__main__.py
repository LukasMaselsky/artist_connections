from artist_connections.datatypes.datatypes import Edges, EdgesJSON
from artist_connections.helpers.helpers import load_edges_json
import networkx as nx
import matplotlib.pyplot as plt
from difflib import get_close_matches
from pyvis.network import Network
import time
import sys
import igraph as ig

#* run with 'python -m artist_connections'

def search(edges_json: EdgesJSON, query: str) -> str | None:
    if query in edges_json:
        return query
    
    matches = get_close_matches(query, edges_json.keys(), n=1, cutoff=0.6)
    if len(matches) > 0: 
        return matches[0] 
    
    return None
    

def create_singular_graph(edges_json: EdgesJSON, query: str) -> Edges:
    nodes = set()
    edges: Edges = []

    nodes.add(query)
    # all incoming nodes to {query}
    for key in edges_json[query].keys():
        nodes.add(key.encode("ascii", "ignore").decode())

    # all outgoing nodes to {query}
    for artist, features in edges_json.items():
        if query in features:
            nodes.add(artist.encode("ascii", "ignore").decode())
       
                
    for node in nodes:
        if node not in edges_json:
            # node exists but not in edges_json
            # means that this is a feature artist but they dont have a song of their own with a feature
            # * node should salways still exist in nodes_json if generated using edges_json in other script
            continue
            
        for key, value in edges_json[node].items():
            if key in nodes:
                new_edge = (key, node, value)
                edges.append(new_edge)

    return edges

def create_full_graph(edges_json: EdgesJSON) -> Edges:
    edges: Edges = []
    for artist, features in edges_json.items():
        artist = artist.encode("ascii", "ignore").decode()
        for key, value in features.items():
            key = key.encode("ascii", "ignore").decode()
            edges.append((key, artist, value))
    return edges

def show_igraph(edges: Edges):
    G = ig.Graph()
    G = G.TupleList(edges, directed=True, weights=True)
    
    fig, ax = plt.subplots()
    
    layout = G.layout("kamada_kawai")
    ig.plot(G, layout=layout, target=ax)
    plt.show()
   


def show_graph(edges: Edges):
    G = nx.DiGraph()
    G.add_weighted_edges_from(edges)
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
    start_time = time.time()
    
    query: str = "JMSN"
    edges_data = load_edges_json("data/edges.json")
    print("--- %s seconds --- to load df" % (time.time() - start_time))
    point = time.time()
    if edges_data is None:
        raise ValueError("Data is None")

    validated_query = search(edges_data, query)
    print("--- %s seconds --- to search" % (time.time() - point))
    point2 = time.time()
    if validated_query is None:
        raise ValueError("Search query invalid, check your spelling")
    graph = create_singular_graph(edges_data, validated_query)
    #graph = create_full_graph(edges_data)
    print("--- %s seconds --- to create graph" % (time.time() - point2))
    point3 = time.time()
    #show_graph(graph)
    show_igraph(graph)
    print("--- %s seconds --- to show graph" % (time.time() - point3))
    

if __name__ == "__main__":
    main()