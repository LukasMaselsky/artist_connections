from artist_connections.datatypes.datatypes import Artists
from artist_connections.helpers.helpers import load_json, scatter_plot, timing, write_to_json
import matplotlib.pyplot as plt
import time
from collections import defaultdict
import seaborn as sns
import polars as pl
import itertools

@timing
def sort_by_song_count(edges_json: Artists) -> Artists:
    return dict(sorted(edges_json.items(), key=lambda x: x[1]["solo_songs"] + x[1]["feat_songs"], reverse=True))

def show_scatter_plot(edges_json: Artists, limit: int, label_limit: int, dark: bool = False):
    if limit > len(edges_json) or limit < 0:
        raise ValueError("Limit out of bounds")
    if label_limit > limit:
        raise ValueError("Label limit out of bounds")
    
    tuples = list(edges_json.items())[:limit]
    #* genre of an artist is approximated by the most common genre of their songs
    data = [(x, y["solo_songs"], y["feat_songs"], max(y["genres"], key=lambda k:y["genres"].get(k, 0))) for x, y in tuples]
    
    df = pl.DataFrame(data=data, schema=["artist", "solo songs", "feat songs", "genre"])
    
    font_colour = "white" if dark else "black"
    bg_colour = "black" if dark else "white"

    #scatter_plot(df, "solo songs", "feat songs", "genre", 
    #            f"Solo vs feature songs for top {limit} artists with most songs", 
    #            font_colour, bg_colour, label_limit)

    m = []
    for row in df.iter_rows():
        if row[3] == "misc":
            m.append(row[0])
    write_to_json(m, "data/l.json")

    plt.show()

def main():
    edges_data = load_json("data/artists.json", Artists)
    if edges_data is None: return
    
    sorted_edges = sort_by_song_count(edges_data)
    show_scatter_plot(sorted_edges, limit=len(sorted_edges), label_limit=10)
    
    '''
    count = 0
    for k, v in sorted_edges.items():
        if v["solo_songs"] < 1 and v["feat_songs"] > 10:
            count += 1
            print(k, v["feat_songs"], v["solo_songs"])
        if count > 50:
            break
    print(count)
    '''
    
if __name__ == "__main__":
    main()