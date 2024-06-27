import polars as pl
from artist_connections.datatypes.datatypes import SongData, Songs
from artist_connections.helpers.helpers import timing, write_to_json, load_json, parse_features, should_filter, process
from difflib import SequenceMatcher

#v1: 216 sec
#* run with 'python -m artist_connections.tools.generate_songs' from top

@timing 
def main() -> None:
    df = pl.read_csv(r"data/song_lyrics_modified.csv")
    data: Songs = {}

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

        for feature in features:
            # prevents artist being "featured" on their own song recorded as an actual feature
            if SequenceMatcher(None, feature, artist).ratio() > 0.7 or should_filter(feature, filter_list):
                features.remove(feature)
                continue

        song = row[0]
        song_data: SongData = {
            "artist": artist,
            "features": features,
            "genre": row[3],
            "year": row[4]
        }
        if song not in data:
            data[song] = [song_data]
        else:
            data[song].append(song_data)

            
    write_to_json(data, "data/songs.json")
        



if __name__ == "__main__":
    main()