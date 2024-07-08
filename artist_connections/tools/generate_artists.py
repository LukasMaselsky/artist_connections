import polars as pl
from artist_connections.datatypes.datatypes import Artists
from artist_connections.helpers.helpers import timing, write_to_json, load_json, parse_features, process, should_filter
from difflib import SequenceMatcher
from collections import defaultdict

# v1: 146 seconds, 77 to load df (whole data)
# v2: < 1 sec (2 cols (modified))
# v3: 41 sec with fuzzy matching
# v4: extra cols, 107 sec
#* run with 'python -m artist_connections.tools.generate_artists' from top

@timing 
def main() -> None:
    df = pl.read_csv(r"data/song_lyrics_modified.csv")
    data: Artists = {}

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
        else:
            # prevents artist being "featured" on their own song recorded as an actual feature
            # e.g. Cam'ron, {"Cam\\'ron"} gets processed to Cam'ron, [Cam'ron], so this should count as solo
            if len(features) == 1 and artist == features[0]:
                data[artist]["solo_songs"] += 1
                continue

        
        added = 0
        for feature in features:
            # prevents artist being "featured" on their own song recorded as an actual feature
            if SequenceMatcher(None, feature, artist).ratio() > 0.7: 
                continue
            if should_filter(feature, filter_list):
                continue

            added += 1
            data[artist]["features"][feature] += 1
        
        if added != 0:
            data[artist]["feat_songs"] += 1
        else:
            data[artist]["solo_songs"] += 1
            
            
    write_to_json(data, "data/artists.json")
        



if __name__ == "__main__":
    main()