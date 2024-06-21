from typing import TypedDict

type EdgesJSON = dict[str, dict[str, int]]
type NodesJSON = list[str]

type Edges = list[tuple[str, str, int]]
type Connections = dict[str, Array]

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

class Edge(TypedDict):
    source: str
    target: str
    weight: int

class Graph(TypedDict):
    nodes: list[str]
    edges: list[Edge]

class GraphNetworkX(TypedDict):
    nodes: list[str]
    edges: Edges
