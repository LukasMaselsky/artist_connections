from artist_connections.datatypes.datatypes import EdgesJSON
from artist_connections.helpers.helpers import load_json, timing
import matplotlib.pyplot as plt
import time
from collections import defaultdict
import seaborn as sns
import polars as pl
import itertools

@timing
def sort_by_song_count(edges_json: EdgesJSON) -> EdgesJSON:
    return dict(sorted(edges_json.items(), key=lambda x: x[1]["solo_songs"] + x[1]["feat_songs"], reverse=True))

def show_scatter_plot(edges_json: EdgesJSON, limit: int, dark: bool = False):
    if limit > len(edges_json) or limit < 0:
        raise ValueError("Limit out of bounds") 
    
    tuples = list(edges_json.items())[:limit]
    #* genre of an artist is approximated by the most common genre of their songs
    data = [(x, y["solo_songs"], y["feat_songs"], max(y["genres"], key=lambda k:y["genres"].get(k, 0))) for x, y in tuples]
    
    df = pl.DataFrame(data=data, schema=["artist", "solo songs", "feat songs", "genre"])
    
    font_colour = "white" if dark else "black"
    bg_colour = "black" if dark else "white"

    fig, ax = plt.subplots()
    fig.patch.set_facecolor(bg_colour)
    fig.suptitle(f"Solo vs feature songs for top {limit} artist with most songs", fontsize=16, color=font_colour)
    g = sns.scatterplot(data=df, x="solo songs", y="feat songs", hue="genre", ax=ax, edgecolor=None)
    g.set(facecolor=bg_colour)
    ax.set_facecolor(bg_colour)
    ax.set_xlabel('Solo songs', color=font_colour)
    ax.set_ylabel('Songs with features', color=font_colour)
    ax.tick_params(axis='x', colors=font_colour)
    ax.tick_params(axis='y', colors=font_colour)
    for spine in ax.spines.values():
        spine.set_edgecolor(font_colour)

    plt.show()

def main():
    edges_data = load_json("data/edges.json", EdgesJSON)
    if edges_data is None:
        raise ValueError("Data is None")
    
    sorted_edges = sort_by_song_count(edges_data)
    
    count = 0
    for k, v in sorted_edges.items():
        if v["solo_songs"] < 1 and v["feat_songs"] > 10:
            count += 1
            print(k, v["feat_songs"], v["solo_songs"])
        if count > 50:
            break
    print(count)
    
    #show_scatter_plot(sorted_edges, 1000)

    

if __name__ == "__main__":
    main()