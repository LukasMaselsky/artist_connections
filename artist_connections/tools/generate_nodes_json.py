import polars as pl
import time
import json
from typing import Set, List
from difflib import get_close_matches, SequenceMatcher
from artist_connections.helpers.helpers import parse_features, load_edges_json

# ~40 sec with fuzzy matching
# ~3 sec with faster method

def faster_main(start_time: float) -> None:
    '''
    Uses already generated edges.json instead of full csv
    No need to fuzzy check, already handled by creating edges.json
    '''
    edges_json = load_edges_json("data/edges.json")
    if edges_json is None:
        raise ValueError("Data is None")
    data: Set[str] = set()
    print("--- %s seconds --- to load DF" % (time.time() - start_time))

    for artist, features in edges_json.items():
        data.add(artist)

        # skip songs without features
        if len(features) == 0: 
            continue
        
        for feature in features.keys():
            data.add(feature)
    
    with open("data/alternate_nodes.json", "w") as outfile:
        json.dump(list(data), outfile)
  
def main(start_time: float) -> None:
    df = pl.read_csv(r"data/song_lyrics_modified.csv")
    data: Set[str] = set()
    print("--- %s seconds --- to load DF" % (time.time() - start_time))

    for row in df.iter_rows():
        artist: str = row[0]
        features = parse_features(row[1])
        
        data.add(artist)

        # skip songs without features
        if len(features) == 0: 
            continue
        
        for feature in features:
            if SequenceMatcher(None, feature, artist).ratio() > 0.9: # needed cause edges does this implementation
                continue
            
            data.add(feature)
    
    with open("data/nodes.json", "w") as outfile:
        json.dump(list(data), outfile)
        



if __name__ == "__main__":
    start_time = time.time()
    faster_main(start_time)
    print("--- %s seconds ---" % (time.time() - start_time))