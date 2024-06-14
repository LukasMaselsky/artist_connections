import polars as pl
from pathlib import Path



def main():
    rows = 1000
    parent_dir = Path(__file__).parent
    output_data_path = parent_dir / ".." / "data" / f"song_lyrics_{rows}.csv"

    df = pl.read_csv(r"../data/song_lyrics.csv").select(pl.col("artist", "features")).limit(rows)
    df.write_csv(output_data_path, separator=",")

if __name__ == "__main__":
    main()