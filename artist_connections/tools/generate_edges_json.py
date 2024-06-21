import polars as pl
import time
from artist_connections.datatypes.datatypes import EdgesJSON
from artist_connections.helpers.helpers import parse_features, write_to_json
from difflib import get_close_matches, SequenceMatcher



# v1: 146 seconds, 77 to load df (whole data)
# v2: < 1 sec (2 cols (modified))
# v3: 41 sec with fuzzy matching
#* run with 'python -m artist_connections.tools.generate_edges_json' from top

def process_non_english(artist: str, features: list[str], custom_list: list[str]) -> tuple[str, bool]:
    '''
    Format of types of string to be processed:  (dima bamberg),"{""дима бамберг (dima bamberg)""}"
    Unicode version will always be in features (I think, haven't checked)
    If this format found, always store feature as the artist name, ascii version should be discarded
    '''
    if artist in custom_list:
        return features[0], True

    if "(" in artist and ")" in artist:
        for feature in features:
            if "(" not in feature or ")" not in feature: # check so artist_inside doesnt fail
                continue

            feature_inside = (feature.split("("))[1].split(")")[0]
            artist_inside = (artist.split("("))[1].split(")")[0]

            if artist_inside == "" or artist_inside.isspace(): # handle: "artist name ... ()" format
                return feature, True

            if SequenceMatcher(None, feature_inside, artist_inside).ratio() > 0.7:
                return feature, True

    return artist, False
        
def main(start_time: float) -> None:
    df = pl.read_csv(r"data/song_lyrics_modified.csv")
    data: EdgesJSON = {}
    print("--- %s seconds --- to load DF" % (time.time() - start_time))

    # too lazy to filter this stuff any other way
    custom_list = ["Meng Jia & Jackson Wang ( / )","Oblivion (U)","7 Princess (7)","Josielle Gomes (J)","LUCIA (P)","Serenity Flores (s)","Yoohyeon & Dami (&)","Rumble-G (-G)","Kenza Mechiche Alami(Me)","D9 (9)","(`) (Emotional Trauma)","Dimitri Romanee (CV. )"]

    for row in df.iter_rows():
        features: list[str] = parse_features(row[1])
        
        if len(features) == 0: 
            continue
        
        artist, was_updated = process_non_english(row[0], features, custom_list)

        if artist not in data:
            if was_updated and len(features) == 1:
                continue
            data[artist] = {}

        for feature in features:
            # prevents artist being "featured" on their own song recorded as an actual feature
            if SequenceMatcher(None, feature, artist).ratio() > 0.9: 
                continue

            if feature in data[artist]:
                data[artist][feature] += 1
            else:
                data[artist][feature] = 1
    
    write_to_json(data, "data/edges_2.json")
        



if __name__ == "__main__":
    start_time = time.time()
    main(start_time)
    print("--- %s seconds ---" % (time.time() - start_time))