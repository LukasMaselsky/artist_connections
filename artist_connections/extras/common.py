from artist_connections.datatypes.datatypes import Songs
from artist_connections.helpers.helpers import load_json, rgba_to_hex, timing
import matplotlib.pyplot as plt
from collections import defaultdict
import seaborn as sns
import polars as pl
import itertools
import matplotlib as mpl

@timing(show_arg_vals=False)
def sort_songs_by_feature_count(songs: Songs):
    return dict(sorted(songs.items(), key=lambda x: len(x[1]), reverse=True))

@timing(show_arg_vals=False)
def get_top_songs(songs: Songs, limit: int) -> Songs:
    if limit > len(songs) or limit < 0:
        raise ValueError("Limit out of bounds") 
    return {k: songs[k] for k in list(songs)[:limit]}

@timing
def main():
    mpl.rcParams['font.sans-serif'] = "Arial Unicode MS"
    songs = load_json("data/songs.json", Songs)
    if songs is None: return
   
    sorted_songs = sort_songs_by_feature_count(songs)
    subset_songs = get_top_songs(sorted_songs, 30)
    for k, v in subset_songs.items():
        print(k, len(v))

if __name__ == "__main__":
    main()
   