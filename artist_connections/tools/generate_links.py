import polars as pl
from artist_connections.datatypes.datatypes import Graph
from artist_connections.helpers.helpers import timing, Encoder, load_json, parse_features, process, should_filter
from difflib import SequenceMatcher
import json

#* run with 'python -m artist_connections.tools.generate_links' from top

def add_node(graph: Graph, node: str) -> None:
    if node not in graph:
        graph[node] = set()

@timing 
def main() -> None:
    df = pl.read_csv(r"data/song_lyrics_modified.csv")
    data: Graph = {}

    filter_list = load_json("data/filter_list.json", list[str])
    if filter_list is None: return

    # too lazy to filter this stuff any other way
    custom_list = ["Meng Jia & Jackson Wang ( / )","Oblivion (U)","7 Princess (7)","Josielle Gomes (J)","LUCIA (P)","Serenity Flores (s)","Yoohyeon & Dami (&)","Rumble-G (-G)","Kenza Mechiche Alami(Me)","D9 (9)","(`) (Emotional Trauma)","Dimitri Romanee (CV. )"]

    #* title,artist,features,tag,year,language_cld3

    for row in df.iter_rows():
        features: list[str] = parse_features(row[2])
        artist = process(row[1], features, custom_list)

        if should_filter(artist, filter_list):
            continue

        add_node(data, artist)
        if artist not in data:
            data[artist] = set()
       
        if len(features) == 1 and artist == features[0]:
            continue

        for feature in features:
            # prevents artist being "featured" on their own song recorded as an actual feature
            if SequenceMatcher(None, feature, artist).ratio() > 0.7: 
                continue
            if should_filter(feature, filter_list):
                continue

            # add feature as a node and add feature and artist to eachothers links list
            add_node(data, feature)
            data[artist].add(feature)
            data[feature].add(artist)

    json_string = json.dumps(data, cls=Encoder, indent=4)
    with open('data/links.json', 'w') as json_file:
        json_file.write(json_string)   
        

if __name__ == "__main__":
    main()