from typing import List, Tuple, TypedDict

type EdgesJSON = dict[str, dict[str, int]]
type NodesJSON = List[str]

class Edge(TypedDict):
    source: str
    target: str
    weight: int

class Graph(TypedDict):
    nodes: List[str]
    edges: List[Edge]

class GraphNetworkX(TypedDict):
    nodes: List[str]
    edges: List[Tuple[str, str, int]]
