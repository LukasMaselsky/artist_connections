from typing import TypedDict
from collections import defaultdict

type EdgesJSON = dict[str, ArtistData]
type NodesJSON = list[str]

type Edges = list[tuple[str, str, int]]
type Connections = dict[str, Array]

class ArtistData(TypedDict):
    features: defaultdict[str, int]
    genres: defaultdict[str, int]
    feat_songs: int
    solo_songs: int

class Array():
    def __init__(self, size: int, default_val: int = 0):
        self.size = size
        self.data = [default_val] * size

    def __getitem__(self, index: int) -> int:
        return self.data[index]

    def __setitem__(self, index: int, value: int):
        self.data[index] = value

    def __repr__(self):
        return repr(self.data)

class GraphNetworkX(TypedDict):
    nodes: list[str]
    edges: Edges
