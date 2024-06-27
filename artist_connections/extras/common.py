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

def main():
    mpl.rcParams['font.sans-serif'] = "Arial Unicode MS"
    songs = load_json("data/songs.json", Songs)
    if songs is None: return
   
    sorted_songs = sort_songs_by_feature_count(songs)
    counter = 0
    for k, v in sorted_songs.items():
        print(k, len(v))

        if counter + 1 >= 10:
            break
        counter += 1

if __name__ == "__main__":
    main()
   