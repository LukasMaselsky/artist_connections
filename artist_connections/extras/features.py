from artist_connections.datatypes.datatypes import Songs
from artist_connections.helpers.helpers import load_json



def main():
    songs_data = load_json("data/songs.json", Songs)
    if not songs_data: return

    genres = {"rap": [0, 0], "rb": [0, 0], "rock": [0, 0], "pop": [0, 0], "country": [0, 0]}

    for song_name, songs in songs_data.items():
        for song in songs:
            if len(song["features"]) > 0:
                genres[song["genre"]][1] += 1
            else:
                genres[song["genre"]][0] += 1

    genres_sorted = {}
    for genre, (s, f) in genres.items():
        genres_sorted[genre] = round((f / (s + f)) * 100, 2)
    
    genres_sorted = dict(sorted(genres_sorted.items(), key=lambda x: x[1], reverse=True))
   
    print("Genre : Percentage of songs that have features")
    for genre, percentage in genres_sorted.items():
        print(f"{genre} : {percentage}%")



if __name__ == "__main__":
    main()