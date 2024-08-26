from artist_connections.datatypes.datatypes import Artists, Connections, connection_factory
from artist_connections.helpers.helpers import int_input, load_json, rgba_to_hex, scatter_plot, styled, timing
import matplotlib.pyplot as plt
from collections import defaultdict
import seaborn as sns
import polars as pl
import itertools
import matplotlib as mpl

@timing(show_arg_vals=False)
def create_connections(edges_json: Artists) -> Connections:
    connections: Connections = defaultdict(connection_factory) # "artist": (in, out)
    for artist, data in edges_json.items():
        features = data["features"]
        
        connections[artist]["received"] += sum(features.values())

        if connections[artist]["genre"] is not None:
            connections[artist]["genre"] = max(data["genres"], key=lambda k:data["genres"].get(k, ""))


        for key, value in features.items():     
            connections[key]["given"] += value

            if connections[key]["genre"] is not None:
                connections[key]["genre"] = max(data["genres"], key=lambda k:data["genres"].get(k, ""))
    
    # sort by total of in + out
    return dict(sorted(connections.items(), key=lambda x: x[1]["received"] + x[1]["given"], reverse=True))

def set_font_color(ax, color):
    ax.set_xlabel(ax.get_xlabel(), color=color)  # X-axis label
    ax.set_ylabel(ax.get_ylabel(), color=color)  # Y-axis label
    ax.tick_params(axis='x', colors=color)  # X-axis tick labels
    ax.tick_params(axis='y', colors=color)  # Y-axis tick labels
   
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(color)  # Tick labels

@timing(show_arg_vals=False)
def show_connections_graph(connections: Connections, limit: int, dark: bool = False):
    if limit > len(connections) or limit < 0:
        raise ValueError("Limit out of bounds") 
    
    tuples = list(connections.items())[:limit]
    data = [[(x, "Features received", y["received"]), (x, "Features given", y["given"])] for x, y in tuples]
    data = list(itertools.chain.from_iterable(data))
    
    df = pl.DataFrame(data=data, schema=["artist", "direction", "connections"])

    colour1 = rgba_to_hex(58, 201, 255)
    colour2 = rgba_to_hex(252, 73, 100)
    font_colour = "white" if dark else "black"
    bg_colour = "black" if dark else "white"

    g = sns.catplot(
        data=df, kind="bar",
        x="connections", y="artist", hue="direction",
        errorbar="sd", palette=[colour1, colour2], height=6
    )
    g.set_axis_labels("Number of connections", "Artist", fontsize=14)
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

@timing(show_arg_vals=False)
def show_connections_scatter_plot(connections: Connections, limit: int, label_limit: int, dark: bool = False):
    if limit > len(connections) or limit < 0:
        raise ValueError("Limit out of bounds")
    if label_limit > limit:
        raise ValueError("Label limit out of bounds")
    
    tuples = list(connections.items())[:limit]
    data = [(x, y["received"], y["given"], y["genre"]) for x, y in tuples] # received, given

    df = pl.DataFrame(data=data, schema=["artist", "features received", "features given", "genre"])

    font_colour = "white" if dark else "black"
    bg_colour = "black" if dark else "white"

    scatter_plot(df, "features received", "features given", "genre", 
                f"Features received vs features given for top {limit} artists",
                font_colour, bg_colour, label_limit)
    plt.show()


def main():
    mpl.rcParams['font.sans-serif'] = "Arial Unicode MS"
    edges_data = load_json("data/artists.json", Artists)
    if edges_data is None: return
   
    connections = create_connections(edges_data)

    print("How many entries would you like in the bar plot?")
    print(styled("WARNING: ANYTHING ABOVE 40 WILL MAKE THE LABELS UNREADABLE", "red", "bold"))
    bar = int_input("Entries: ", len(connections))
    
    print(f"\nHow many entries would you like in the scatter plot? (max {len(connections)})")
    scatter = int_input("Entries: ", len(connections))

    print("\nHow many labels shown would you like for the scatter plot?")
    scatter_labels = int_input("Labels: ", scatter)

    show_connections_graph(connections, bar)
    #show_connections_scatter_plot(connections, limit=scatter, label_limit=scatter_labels)
    
    

if __name__ == "__main__":
    main()