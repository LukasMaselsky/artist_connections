from helpers.helpers import do_thing
import polars as pl
from typing import List


def parse_features(s: str) -> List[str]:
    if len(s) == 2:
        # no features
        return []
    
    strings = []
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]
        for item in s.split(","):
            decoded_s = item.encode().decode('unicode_escape')
            decoded_s = decoded_s.replace("\\'", "'")
            if decoded_s.startswith('"') and decoded_s.endswith('"'):
                decoded_s = decoded_s[1:-1]    
            strings.append(decoded_s)
    return strings
        
    

def main() -> None:
    #* run with 'python artist_connections/__main__.py'
    df = pl.read_csv(r"data/song_lyrics_1000.csv")
    print(df)
    
    for row in df.iter_rows():
        features = parse_features(row[1])
        print(f"Song artist: {row[0]}, Features: {features}")



if __name__ == "__main__":
    main()