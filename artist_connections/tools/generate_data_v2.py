import polars as pl
from typing import List
import time
import json
from difflib import get_close_matches, SequenceMatcher
from artist_connections.helpers.helpers import parse_features
from artist_connections.datatypes.datatypes import Graph
        
def main(start_time: float) -> None:
    #* run with 'python artist_connections/tools/generate_data_v2.py'
    df = pl.read_json(r"data/edges.json")
    data: Graph = {"nodes": [], "edges": []}
    print("--- %s seconds --- to load DF" % (time.time() - start_time))

    for row in df.iter_rows():
        artist: str = row[0]
        features = parse_features(row[1])

        if artist not in data["nodes"]:
            data["nodes"].append(artist)
        
        # skip songs without features
        if len(features) == 0: 
            continue
        
        for feature in features:
            if SequenceMatcher(None, feature, artist).ratio() > 0.9:
                continue
        
            if feature not in data["nodes"]:
                data["nodes"].append(feature) # all features should also be guaranteed to be a node


            if feature in data[artist]:
                data[artist][feature] += 1
            else:
                data[artist][feature] = 1
    
    with open("data/datav2.json", "w") as outfile:
        json.dump(data, outfile)
        



if __name__ == "__main__":
    start_time = time.time()
    main(start_time)
    print("--- %s seconds ---" % (time.time() - start_time))