from artist_connections.datatypes.datatypes import Edges, EdgesJSON
from artist_connections.helpers.helpers import load_edges_json, rgba_to_hex, timing
import networkx as nx
import matplotlib.pyplot as plt
from difflib import get_close_matches
from pyvis.network import Network
import igraph as ig


#* run with 'python -m artist_connections'

def normalise(str: str):
    return str.encode("ascii", "ignore").decode()

def search(edges_json: EdgesJSON, query: str) -> str | None:
    if query in edges_json:
        return query
    
    matches = get_close_matches(query, edges_json.keys(), n=1, cutoff=0.6)
    if len(matches) > 0: 
        return matches[0] 
    
    return None
    
@timing
def create_singular_graph(edges_json: EdgesJSON, query: str) -> Edges:
    nodes: set[str] = set()
    edges: Edges = []

    nodes.add(query)
    # all incoming nodes to {query}
    for key in edges_json[query]["features"].keys():
        nodes.add(key)

    # all outgoing nodes to {query}
    for artist, features in edges_json.items():
        if query in features:
            nodes.add(artist)
       
                
    for node in nodes:
        if node not in edges_json:
            # node exists but not in edges_json
            # means that this is a feature artist but they dont have a song of their own with a feature
            # * node should salways still exist in nodes_json if generated using edges_json in other script
            continue
            
        for key, value in edges_json[node]["features"].items():
            if key in nodes:
                new_edge = (key, node, value)
                edges.append(new_edge)

    return edges

@timing
def create_full_graph(edges_json: EdgesJSON) -> Edges:
    edges: Edges = []
    for artist, data in edges_json.items():
        features = data["features"]
        for key, value in features.items():
            edges.append((key, artist, value))
    return edges

@timing
def show_igraph(edges: Edges, full_graph=False):
    G = ig.Graph()
    G = G.TupleList(edges, directed=True, weights=True)
    fig, ax = plt.subplots()
    
    fig.patch.set_facecolor((0, 0, 0))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor((0, 0, 0))

    visual_style = {}
    visual_style["vertex_label"] = G.vs["name"]
    visual_style["vertex_label_color"] = "white"
    visual_style["vertex_color"] = "skyblue"
    visual_style["vertex_size"] = [degree * 10 for degree in G.vs.degree()]
    visual_style["vertex_label_size"] = 8
    visual_style["vertex_label_dist"] = 0.6
    visual_style["edge_color"] = rgba_to_hex(58, 201, 255, 0.3)
    visual_style["edge_width"] = G.es["weight"]
    arrow_size = [weight * 3 for weight in G.es["weight"]]
    visual_style["edge_arrow_size"], visual_style["edge_arrow_width"] = arrow_size, arrow_size

    layout = G.layout("kamada_kawai" if not full_graph else "lgl")
    ig.plot(G, layout=layout, target=ax, **visual_style)
    plt.show()

'''
def show_graph(edges: Edges) -> None:
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
'''
    
def main():
  
    query: str = "JMSN"
    edges_data = load_edges_json("data/edges.json")

    if edges_data is None:
        raise ValueError("Data is None")

    validated_query = search(edges_data, query)
    
    if validated_query is None:
        raise ValueError("Search query invalid, check your spelling")
    graph = create_singular_graph(edges_data, validated_query)
    #graph = create_full_graph(edges_data)
   
    show_igraph(graph)
    
        


if __name__ == "__main__":
    main()