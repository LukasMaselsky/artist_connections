from artist_connections.datatypes.datatypes import Artists
from artist_connections.helpers.helpers import int_input, load_json, scatter_plot, sort_artists_by_song_count, timing
import matplotlib.pyplot as plt
import polars as pl

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

    scatter_plot(df, "solo songs", "feat songs", "genre", 
                f"Solo vs feature songs for top {limit} artists with most songs", 
                font_colour, bg_colour, label_limit)

    plt.show()

def main():
    edges_data = load_json("data/artists.json", Artists)
    if edges_data is None: return
    

    sorted_edges = sort_artists_by_song_count(edges_data)

    print(f"\nHow many entries would you like in the scatter plot? (max {len(sorted_edges)})")
    scatter = int_input("Entries: ", len(sorted_edges))

    print("\nHow many labels shown would you like for the scatter plot?")
    scatter_labels = int_input("Labels: ", scatter)

    show_scatter_plot(sorted_edges, limit=scatter, label_limit=scatter_labels)
    
    
if __name__ == "__main__":
    main()