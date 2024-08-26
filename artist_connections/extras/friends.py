from artist_connections.datatypes.datatypes import Artists
from artist_connections.helpers.helpers import load_json
from typing import FrozenSet

def main():
    artists = load_json("data/artists.json", Artists)
    if not artists: return

    data: dict[FrozenSet, int] = {}

    for artist, artist_data in artists.items():
        for feature, count in artist_data["features"].items():
            key = frozenset([artist, feature])
            data[key] = data.get(key, 0) + count

    data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
    for i, (k, v) in enumerate(data.items()):
        print(k, v)
        if i == 20:
            break



   
    
    
if __name__ == "__main__":
    main()