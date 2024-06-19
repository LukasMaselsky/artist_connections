from typing import Tuple, TypedDict

type EdgesJSON = dict[str, dict[str, int]]
type NodesJSON = list[str]

type Edges = list[Tuple[str, str, int]]
type Connections = dict[str, int]

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
