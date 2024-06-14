from helpers.helpers import do_thing
import polars as pl
from typing import List
import time

# v1: 146 seconds

def parse_features(s: str) -> List[str]:
    if len(s) == 2:
        # no features
        return []
    
    strings = []
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]
        for item in s.split(","):
            decoded_s: str = item.encode().decode('unicode_escape')
            decoded_s = decoded_s.replace("\\'", "'")
            if decoded_s.startswith('"') and decoded_s.endswith('"'):
                decoded_s = decoded_s[1:-1]    
            strings.append(decoded_s)
        return strings
    return []
        
def main() -> None:
    #* run with 'python artist_connections/__main__.py'
    df = pl.read_csv(r"data/song_lyrics.csv")
    data: dict[str, dict[str, int]] = {}
    
    for row in df.iter_rows():
        artist: str = row[0]
        features = parse_features(row[1])

        # skip songs without features
        if len(features) == 0: 
            continue
        
        if artist not in data:
            data[artist] = {}
        
        for feature in features:
            if feature == artist:
                continue

            if feature in data[artist]:
                data[artist][feature] += 1
            else:
                data[artist][feature] = 1
            

        #print(f"Song artist: {artist}, Features: {features}")



if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))