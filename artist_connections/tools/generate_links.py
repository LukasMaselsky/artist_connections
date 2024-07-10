import polars as pl
from artist_connections.datatypes.datatypes import Graph
from artist_connections.helpers.helpers import timing, encoder, should_filter, write_json
import ast

#* run with 'python -m artist_connections.tools.generate_links' from top

def add_node(graph: Graph, node: str) -> None:
    if node not in graph:
        graph[node] = set()

@timing 
def main() -> None:
    df = pl.read_csv(r"data/song_lyrics_modified.csv")
    links: Graph = {}

    #* title,artist,features,tag,year,language_cld3

    for row in df.iter_rows():
        artist: str = row[1]
        features: list[str] = ast.literal_eval(row[2])

        add_node(links, artist)
       
        for feature in features:
            # add feature as a node and add feature and artist to eachothers links list
            add_node(links, feature)
            links[artist].add(feature)
            links[feature].add(artist)

    write_json(links, 'data/links_2.json', encoder)
    

        

if __name__ == "__main__":
    main()