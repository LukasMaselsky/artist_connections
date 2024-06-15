from typing import List, TypedDict

type EdgesJSON = dict[str, dict[str, int]]

class Edge(TypedDict):
    source: str
    target: str
    weight: int

class Graph(TypedDict):
    nodes: List[str]
    edges: List[Edge]


