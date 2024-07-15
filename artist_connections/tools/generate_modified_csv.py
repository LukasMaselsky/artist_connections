import orjson
import polars as pl
from artist_connections.helpers.helpers import parse_features, timing, process, should_filter, load_json
import numpy as np
import numpy.typing as npt

#* run from base directory with "python -m artist_connections.tools.generate_modified_csv"

#! decided to get rid of all "misc" entries, some may be actual songs but majority are books, poems etc
#! tradeoff between over including and getting rid of some actual songs, choosing option 2


@timing
def main():
    df = pl.scan_csv(r"data/song_lyrics.csv")
    df = df.select(pl.col("title", "artist", "features", "tag", "year", "language_cld3")).collect()

    # too lazy to filter this stuff any other way
    custom_list = set(["Meng Jia & Jackson Wang ( / )","Oblivion (U)","7 Princess (7)","Josielle Gomes (J)","LUCIA (P)","Serenity Flores (s)","Yoohyeon & Dami (&)","Rumble-G (-G)","Kenza Mechiche Alami(Me)","D9 (9)","(`) (Emotional Trauma)","Dimitri Romanee (CV. )"])
   
    original_filter_list = load_json("data/filter_list.json", list[str])
    if original_filter_list is None: return
    filter_list: set[str] = set(original_filter_list)

    #* title,artist,features,tag,year,language_cld3

    artist_col: list[str | None] = []
    features_col: list[str | None] = []
    
    col = df['artist']
    all_artists: set[str] = set(col.filter(col.str.contains(",")).unique()) # all artists wtih commas e.g. "Tyler, The Creator"
    
    for i, row in enumerate(df.iter_rows()):
        art, feats = row[1], row[2]

        features = parse_features(feats)
        artist = process(art, features, custom_list, filter_list, all_artists)

        if should_filter(artist, filter_list):
            artist_col.append(None)
            features_col.append(None)
            continue

        artist_col.append(artist)
        str_features: str = orjson.dumps(features).decode("utf-8")
        features_col.append(str_features)

   
    modified = df.with_columns([pl.Series(artist_col).alias("artist"), pl.Series(features_col).alias("features")])
    filtered = modified.drop_nulls(["artist", "features"]).filter(pl.col("tag") != "misc")
   
    filtered.write_csv(r"data/song_lyrics_modified.csv", separator=",")

if __name__ == "__main__":
    main()