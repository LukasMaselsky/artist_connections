import polars as pl
import time
from artist_connections.datatypes.datatypes import EdgesJSON
from artist_connections.helpers.helpers import write_to_json
from difflib import get_close_matches, SequenceMatcher
from collections import defaultdict



# v1: 146 seconds, 77 to load df (whole data)
# v2: < 1 sec (2 cols (modified))
# v3: 41 sec with fuzzy matching
# v4: extra cols, 107 sec
#* run with 'python -m artist_connections.tools.generate_edges_json' from top


def parse_features(s: str) -> list[str]:
    if len(s) == 2:
        # no features
        return []

    strings = []
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]
        for item in s.split(","):
            decoded_s = item
            if decoded_s.startswith('"') and decoded_s.endswith('"'):
                decoded_s = decoded_s[1:-1]    
            decoded_s = decoded_s.replace("\\\\'", "'")
            decoded_s = decoded_s.replace('\\\\\\"', '"')
            decoded_s = decoded_s.replace("\\\\$", "$")
            decoded_s = decoded_s.replace("\\\\`", "`")
            strings.append(decoded_s)
        return strings
    return []

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

    #* artist,features,tag,year,language_cld3

    for row in df.iter_rows():
        features: list[str] = parse_features(row[1])
        artist, was_updated = process_non_english(row[0], features, custom_list)

        if artist not in data:
            data[artist] = {
                "features": defaultdict(int),
                "genres": defaultdict(int),
                "feat_songs": 0,
                "solo_songs": 0
            }

        if len(features) == 0 or (was_updated and len(features) == 1):
            data[artist]["solo_songs"] += 1
        else:
            # prevents artist being "featured" on their own song recorded as an actual feature
            # e.g. Cam'ron, {"Cam\\'ron"} gets processed to Cam'ron, [Cam'ron], so this should count as solo
            if len(features) == 1 and artist == features[0]:
                data[artist]["solo_songs"] += 1
            else:
                data[artist]["feat_songs"] += 1
        

        data[artist]["genres"][row[2]] += 1

        for feature in features:
            # prevents artist being "featured" on their own song recorded as an actual feature
            if SequenceMatcher(None, feature, artist).ratio() > 0.9: 
                continue

            data[artist]["features"][feature] += 1
            
            
    
    write_to_json(data, "data/edges.json")
        



if __name__ == "__main__":
    start_time = time.time()
    main(start_time)
    print("--- %s seconds ---" % (time.time() - start_time))