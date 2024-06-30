from collections import deque
from artist_connections.datatypes.datatypes import Graph
from artist_connections.helpers.helpers import load_json


def flatten_gen(l: list[str] | str):
    for i in l:
        if isinstance(i, (list,tuple)):
            for j in flatten_gen(i):
                yield j
        else:
            yield i

def flatten(l: list[str]):
    return list(flatten_gen(l))

def print_path(l: list[str]):
    '''Takes flattened list and prints in nice format'''
    print(" -> ".join(l))

def find_shortest_path(graph: Graph, start: str, end: str) -> list[str] | None:
    dist = {start: [start]}
    q = deque([start])
    while len(q):
        at = q.popleft()
        for next in graph[at]:
            if next not in dist:
                dist[next] = [dist[at], next] # type: ignore
                q.append(next)
    return dist.get(end)


def main():
    links = load_json("data/links.json", Graph)
    if links is None: return

    artist1 = input("Artist 1: ")
    artist2 = input("Artist 2: ")

    if artist1 not in links:
        print("Artist 1 does not exist")
        return
    
    if artist2 not in links:
        print("Artist 2 does not exist")
        return

    path = find_shortest_path(links, artist1, artist2)
    if path is None: 
        print("No path found")
        return
    path = flatten(path)
    print()
    print_path(path)
    print(f"The artists have {len(path)} degrees of separation")


    return

if __name__ == "__main__":
    main()