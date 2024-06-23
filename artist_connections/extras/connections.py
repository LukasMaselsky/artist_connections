from artist_connections.datatypes.datatypes import EdgesJSON, Connections, Array
from artist_connections.helpers.helpers import load_edges_json, load_filter_list_json, rgba_to_hex, should_filter, timing
import matplotlib.pyplot as plt
import time
from collections import defaultdict
import seaborn as sns
import polars as pl
import itertools

@timing
def create_connections(edges_json: EdgesJSON) -> Connections:
    filter_list = load_filter_list_json("data/filter_list.json")
    if filter_list is None:
        raise ValueError("Filter list is None")
    

    connections: Connections = defaultdict(lambda: Array(2)) # "artist": (in, out)
    for artist, data in edges_json.items():
        features = data["features"]
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

@timing
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

def main():
    edges_data = load_edges_json("data/edges.json")
    if edges_data is None:
        raise ValueError("Data is None")
   
    connections = create_connections(edges_data)

    show_connections_graph(connections, 30)
    counter = 0
    for k, v in connections.items():
        print(k, v)
        counter += 1
        if counter > 20:
            break
    

if __name__ == "__main__":
    main()