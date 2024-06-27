import polars as pl

#* run from base directory with "python -m artist_connections.tools.generate_modified_csv"

def main():
    df = pl.scan_csv(r"data/song_lyrics.csv").select(pl.col("title", "artist", "features", "tag", "year", "language_cld3"))
    
    df.collect().write_csv(r"data/song_lyrics_modified_2.csv", separator=",")

if __name__ == "__main__":
    main()