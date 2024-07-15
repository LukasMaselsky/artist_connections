from artist_connections.datatypes.datatypes import Edges, Artists
from artist_connections.helpers.helpers import load_json, rgba_to_hex, timing, search
import matplotlib.pyplot as plt
import igraph as ig
import matplotlib as mpl


#* run with 'python -m artist_connections.extras.network'


@timing(show_arg_vals=False)
def create_singular_graph(edges_json: Artists, query: str, extended=True) -> Edges:
    '''
        if extended is false, connections between artists who are connected to {query} are not calculated
    '''

    nodes: set[str] = set()
    edges: Edges = []

    nodes.add(query)
    # all incoming nodes to {query}
    for key in edges_json[query]["features"].keys():
        nodes.add(key)

    # all outgoing nodes to {query}
    for artist, data in edges_json.items():
        if query in data["features"]:
            nodes.add(artist)
    
    if not extended:
        # ingoing
        for key, value in edges_json[query]["features"].items():
            edges.append((key, query, value)) 
        nodes.remove(query)

        #outgoing
        for node in nodes:
            if node not in edges_json: continue
            if query in edges_json[node]["features"]:
                edges.append((query, node, edges_json[node]["features"][query]))

        return edges
        
                
    for node in nodes:
        if node not in edges_json:
            # node exists but not in edges_json
            # means that this is a feature artist but they dont have a song of their own with a feature
            # * node should always still exist in nodes_json if generated using edges_json in other script
            continue
         
        for key, value in edges_json[node]["features"].items():
            if key in nodes:
                new_edge = (key, node, value)
                edges.append(new_edge)
                    
    return edges

@timing(show_arg_vals=False)
def create_full_graph(edges_json: Artists) -> Edges:
    edges: Edges = []
    for artist, data in edges_json.items():
        features = data["features"]
        for key, value in features.items():
            edges.append((key, artist, value))
    return edges

def create_sizes(degrees: list[int], limit) -> list[int]:
    biggest = max(degrees)
    multiplier = limit // biggest
    return [degree * multiplier for degree in degrees]

@timing(show_arg_vals=False)
def show_igraph(edges: Edges, full_graph=False, show_labels=True):
    G = ig.Graph()
    G = G.TupleList(edges, directed=True, weights=True)
    fig, ax = plt.subplots()
    
    fig.patch.set_facecolor((0, 0, 0))
    ax.set_facecolor((0, 0, 0))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0) # fractions of figure w/h

    visual_style = {}
    if show_labels:
        visual_style["vertex_label"] = G.vs["name"]
        visual_style["vertex_label_color"] = "white"
    visual_style["vertex_color"] = "skyblue"
    #sizes = [degree * 10 for degree in G.vs.degree()]

    sizes = create_sizes(G.vs.degree(), 300)
    
    visual_style["vertex_size"] = sizes
    visual_style["vertex_label_size"] = 8

    dists = []
    for size in sizes:
        if size > 50:
            dists.append(0) # place label INSIDE circle if it fits
        elif size < 20:
            dists.append(1) # if really small, move further
        else:
            dists.append(0.6)

    visual_style["vertex_label_dist"] = dists

    edge_colors = []
    base_alpha = 0.3
    for weight in G.es["weight"]:
        alpha = base_alpha + (0.05 * (weight - 1))
        alpha = alpha if alpha <= 1 else 1

        edge_colors.append(rgba_to_hex(58, 201, 255, alpha))

    visual_style["edge_color"] = edge_colors
    visual_style["edge_width"] = G.es["weight"]
    arrow_size = [weight * 3 for weight in G.es["weight"]]
    visual_style["edge_arrow_size"], visual_style["edge_arrow_width"] = arrow_size, arrow_size

    layout = G.layout("kamada_kawai" if not full_graph else "lgl")
    bbox = (500, 500) #? doesnt work
    layout.fit_into(bbox=bbox)
    ig.plot(G, layout=layout, target=ax, bbox=bbox, **visual_style)
    plt.show()

    
def main():
    mpl.rcParams['font.sans-serif'] = "Arial Unicode MS"
    artists = load_json("data/artists.json", Artists)

    if artists is None:
        raise ValueError("Artist JSON is None")

    query = search(artists, "Artist name: ")
    
    graph = create_singular_graph(artists, query)
    #graph = create_full_graph(artists)
   
    show_igraph(graph)
    
if __name__ == "__main__":
    main()