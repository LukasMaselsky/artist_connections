import polars as pl
from artist_connections.datatypes.datatypes import Artists
from artist_connections.helpers.helpers import timing, write_json, load_json
from collections import defaultdict
import ast

# v1: 146 seconds, 77 to load df (whole data)
# v2: < 1 sec (2 cols (modified))
# v3: 41 sec with fuzzy matching
# v4: extra cols, 107 sec
#* run with 'python -m artist_connections.tools.generate_artists' from top

@timing 
def main() -> None:
    df = pl.read_csv(r"data/song_lyrics_modified.csv")
    data: Artists = {}

    #* title,artist,features,tag,year,language_cld3
    
    for row in df.iter_rows():
        artist: str = row[1]
        features: list[str] = ast.literal_eval(row[2])

        if artist not in data:
            data[artist] = {
                "features": defaultdict(int),
                "genres": defaultdict(int),
                "feat_songs": 0,
                "solo_songs": 0
            }
        
        data[artist]["genres"][row[3]] += 1

        if len(features) == 0:
            data[artist]["solo_songs"] += 1
            continue
        
        added = 0
        for feature in features:
            added += 1
            data[artist]["features"][feature] += 1
        
        if added != 0:
            data[artist]["feat_songs"] += 1
        else:
            data[artist]["solo_songs"] += 1

    write_json(data, "data/artists.json")
        



if __name__ == "__main__":
    main()