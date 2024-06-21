from artist_connections.datatypes.datatypes import Edges, EdgesJSON, Connections, Array
from artist_connections.helpers.helpers import load_edges_json, load_filter_list_json, rgba_to_hex, should_filter
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
from difflib import get_close_matches
from pyvis.network import Network
import time
import igraph as ig
from collections import defaultdict
import seaborn as sns
import polars as pl
import itertools

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
    

def create_singular_graph(edges_json: EdgesJSON, query: str) -> Edges:
    nodes = set()
    edges: Edges = []

    nodes.add(query)
    # all incoming nodes to {query}
    for key in edges_json[query].keys():
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
            
        for key, value in edges_json[node].items():
            if key in nodes:
                new_edge = (key, node, value)
                edges.append(new_edge)

    return edges

def create_full_graph(edges_json: EdgesJSON) -> Edges:
    edges: Edges = []
    for artist, features in edges_json.items():
        for key, value in features.items():
            edges.append((key, artist, value))
    return edges

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
   
def create_connections(edges_json: EdgesJSON) -> Connections:
    filter_list = load_filter_list_json("data/filter_list.json")
    if filter_list is None:
        raise ValueError("Filter list is None")
    

    connections: Connections = defaultdict(lambda: Array(2)) # "artist": (in, out)
    for artist, features in edges_json.items():
        if not should_filter(artist, filter_list):
            connections[artist][0] += sum(features.values())

        for key, value in features.items():
            if not should_filter(key, filter_list):
                connections[key][1] += value
    
    # sort by total of in + out
    return dict(sorted(connections.items(), key=lambda x: x[1][0] + x[1][1], reverse=True))

def set_font_color(ax, color):
    ax.set_xlabel(ax.get_xlabel(), color=color)  # X-axis label
    ax.set_ylabel(ax.get_ylabel(), color=color)  # Y-axis label
    ax.tick_params(axis='x', colors=color)  # X-axis tick labels
    ax.tick_params(axis='y', colors=color)  # Y-axis tick labels
   
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(color)  # Tick labels

def show_connections_graph(connections: Connections, limit: int):
    tuples = list(connections.items())[:limit]
    data = [[(x, "Features received", y[0]), (x, "Features given", y[1])] for x, y in tuples]
    data = list(itertools.chain.from_iterable(data))
    
    df = pl.DataFrame(data=data, schema=["artist", "direction", "connections"])

    colour1 = rgba_to_hex(58, 201, 255)
    colour2 = rgba_to_hex(252, 73, 100)
    font_colour = "white"
    bg_colour = "black"

    g = sns.catplot(
        data=df, kind="bar",
        x="connections", y="artist", hue="direction",
        errorbar="sd", palette=[colour1, colour2], height=6
    )
    g.set_axis_labels("Number of connections", "Artist")
    g.figure.suptitle("Artists with the most feature connections", fontsize=16, color=font_colour)
    g.tick_params(axis='x', colors=font_colour)
    g.tick_params(axis='y', colors=font_colour)
    g.set(facecolor=bg_colour)
    g.figure.patch.set_facecolor(bg_colour)

    for ax in g.axes.flat:
        set_font_color(ax, font_colour)
    
    if g.legend is not None:
        for text in g.legend.texts:
            text.set_color(font_colour)
    plt.subplots_adjust(top=0.85)
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

    show_igraph(graph)
    print("--- %s seconds --- to show graph" % (time.time() - point3))
    
def test():
    start_time = time.time()
    mpl.rc('font', family="Arial")

    edges_data = load_edges_json("data/edges.json")
    print("--- %s seconds --- to load df" % (time.time() - start_time))
    point = time.time()
    if edges_data is None:
        raise ValueError("Data is None")
   
    connections = create_connections(edges_data)
    print("--- %s seconds --- to create connections" % (time.time() - point))
    
    show_connections_graph(connections, 30)
    '''
    counter = 0
    for k, v in connections.items():
        if "(" in k and ")" in k:
            print(k, v)
            counter += 1
        if counter > 5:
            break
    '''
        


if __name__ == "__main__":
    test()