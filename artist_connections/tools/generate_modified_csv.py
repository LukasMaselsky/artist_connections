import polars as pl
from artist_connections.helpers.helpers import timing

#* run from base directory with "python -m artist_connections.tools.generate_modified_csv"

#! decided to get rid of all "misc" entries, some may be actual songs but majority are books, poems etc
#! tradeoff between over including and getting rid of some actual songs, choosing option 2

@timing
def main():
    df = pl.scan_csv(r"data/song_lyrics.csv")
    df = df.select(pl.col("title", "artist", "features", "tag", "year", "language_cld3"))
    df = df.filter(pl.col("tag") != "misc")

    df.collect().write_csv(r"data/song_lyrics_modified.csv", separator=",")

if __name__ == "__main__":
    main()