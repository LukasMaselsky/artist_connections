import polars as pl
from artist_connections.datatypes.datatypes import Artists, Graph, Songs, SongData
from artist_connections.helpers.helpers import timing, write_json, encoder
from collections import defaultdict
import orjson

# v1: 146 seconds, 77 to load df (whole artists)
# v2: < 1 sec (2 cols (modified))
# v3: 41 sec with fuzzy matching
# v4: extra cols, 107 sec
# v5: combined all, now 90 sec
# v6: with orjson.loads, now 45 sec
#* run with 'python -m artist_connections.tools.generate_artists' from top


@timing 
def main() -> None:
    df = pl.read_csv(r"data/song_lyrics_modified.csv")
    artists: Artists = {}
    songs: Songs = {}
    links: Graph = {}

    #* title,artist,features,tag,year,language_cld3
    
    for row in df.iter_rows():
        song: str = str(row[0])
        artist: str = row[1]
        features = orjson.loads(row[2])
        tag: str = row[3]
        year: int = row[4]

        if artist not in artists:
            artists[artist] = {
                "features": defaultdict(int),
                "genres": defaultdict(int),
                "feat_songs": 0,
                "solo_songs": 0
            }
        artists[artist]["genres"][row[3]] += 1
        
        # links
        if artist not in links:
            links[artist] = set()

        # use feature loop for both artists and links
        added = 0
        for feature in features:
            added += 1
            artists[artist]["features"][feature] += 1

            # add feature as a node and add feature and artist to eachothers links list
            if feature not in links:
                links[feature] = set()
            links[artist].add(feature)
            links[feature].add(artist)
        
        
        if added != 0:
            artists[artist]["feat_songs"] += 1
        else:
            artists[artist]["solo_songs"] += 1

        # songs
        song_songs: SongData = {
            "artist": artist,
            "features": features,
            "genre": tag,
            "year": year
        }
        if song not in songs:
            songs[song] = [song_songs]
        else:
            songs[song].append(song_songs)

    write_json(artists, "data/artists_2.json")
    write_json(songs, "data/songs_2.json")
    write_json(links, 'data/links_2.json', encoder)
        



if __name__ == "__main__":
    main()