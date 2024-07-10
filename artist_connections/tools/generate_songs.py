import polars as pl
from artist_connections.datatypes.datatypes import SongData, Songs
from artist_connections.helpers.helpers import timing, write_json, load_json
from difflib import SequenceMatcher
import ast

#v1: 216 sec
#* run with 'python -m artist_connections.tools.generate_songs' from top

@timing 
def main() -> None:
    df = pl.read_csv(r"data/song_lyrics_modified.csv")
    data: Songs = {}
   
    #* title,artist,features,tag,year,language_cld3

    for row in df.iter_rows():
        song = str(row[0])
        song_data: SongData = {
            "artist": row[1],
            "features": ast.literal_eval(row[2]),
            "genre": row[3],
            "year": row[4]
        }
        if song not in data:
            data[song] = [song_data]
        else:
            data[song].append(song_data)
    
    write_json(data, "data/songs_2.json")
        



if __name__ == "__main__":
    main()