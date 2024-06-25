from typing import TypedDict
from collections import defaultdict
class ArtistData(TypedDict):
    features: defaultdict[str, int]
    genres: defaultdict[str, int]
    feat_songs: int
    solo_songs: int

class Connection(TypedDict):
    received: int
    given: int
    genre: str

DEFAULT_CONNECTION = {
    "received": 0,
    "given": 0,
    "genre": "",
}

def connection_factory() -> Connection:
    return Connection(**DEFAULT_CONNECTION)

EdgesJSON = dict[str, ArtistData]

Edges = list[tuple[str, str, int]]
Connections = dict[str, Connection]
class GraphNetworkX(TypedDict):
    nodes: list[str]
    edges: Edges
