import polars as pl
import time
from artist_connections.datatypes.datatypes import EdgesJSON
from artist_connections.helpers.helpers import parse_features, write_to_json, process_non_english
from difflib import get_close_matches, SequenceMatcher



# v1: 146 seconds, 77 to load df (whole data)
# v2: < 1 sec (2 cols (modified))
# v3: 41 sec with fuzzy matching
#* run with 'python -m artist_connections.tools.generate_edges_json' from top
        
def main(start_time: float) -> None:
    df = pl.read_csv(r"data/song_lyrics_modified.csv")
    data: EdgesJSON = {}
    print("--- %s seconds --- to load DF" % (time.time() - start_time))

    for row in df.iter_rows():
        artist: str = row[0]
        features = parse_features(row[1])
        
        if artist not in data:
            data[artist] = {}

        # skip songs without features
        if len(features) == 0: 
            continue
        
        for feature in features:
            # prevents artist being featured on their own song recorded as an actual feature
            if SequenceMatcher(None, feature, artist).ratio() > 0.9: 
                continue

            if feature in data[artist]:
                data[artist][feature] += 1
            else:
                data[artist][feature] = 1
    
    write_to_json(data, "data/edges_3.json")
        



if __name__ == "__main__":
    start_time = time.time()
    main(start_time)
    print("--- %s seconds ---" % (time.time() - start_time))