from collections import deque
from re import L
from artist_connections.datatypes.datatypes import Graph
from artist_connections.helpers.helpers import load_json, timing


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

    if len(graph[start]) == 0 or len(graph[end]) == 0:
        return None

    dist = {start: [start]}
    q = deque([start])
    while len(q):
        at = q.popleft()
        for next in graph[at]:
            if next not in dist:
                dist[next] = [dist[at], next] # type: ignore
                q.append(next)
    return dist.get(end)

@timing(show_arg_vals=False)
def longest_ever_path(graph: Graph) -> list[str]:
    '''Longest shortest path of all shortest paths'''
    '''In between O(n^2) and O(n^3) depending on density of graph'''
    '''Approximately: 0.000002x^{3.05}, over a minute for top 300'''
    longest_path = []
    
    for a in graph.keys():
        for b in graph.keys():
            if a == b: continue
            path = find_shortest_path(graph, a, b)
            if path is None: continue
            path = flatten(path)
            
            if len(path) > len(longest_path):
                longest_path = path


    return longest_path

def sort_by_edge_count(links: Graph) -> Graph:
    return dict(sorted(links.items(), key=lambda x: len(x[1]), reverse=True))

def get_first_n(links: Graph, limit: int) -> Graph:
    return {k: v for i, (k, v) in enumerate(links.items()) if i < limit}

def get_subgraph(links: Graph, limit: int) -> Graph:
    links = sort_by_edge_count(links)
    sublist = get_first_n(links, limit)

    sublist_cleaned: Graph = {}
    for artist, arr in sublist.items():
        new_links = set()
        for item in arr:
            if item in sublist:
                new_links.add(item)

        if len(new_links) != 0: # don't add nodes that only have connections outside of the top {limit}
            sublist_cleaned[artist] = new_links

    return sublist_cleaned


@timing(show_arg_vals=False)
def filter_isolated(links: Graph) -> Graph:
    graph: Graph = {}
    for artist, l in links.items():
        if len(l) != 0:
            graph[artist] = l
    return graph

def separation_game(links: Graph):
    while True:
        artist1 = input("Artist 1: ")
        while artist1 not in links:
            print("Artist 1 could not be found")
            artist1 = input("Artist 1: ")
        
        artist2 = input("Artist 2: ")
        while artist2 not in links:
            print("Artist 2 could not be found")
            artist2 = input("Artist 2: ")

        path = find_shortest_path(links, artist1, artist2)
        if path is None: 
            print("No path found")
        else:
            path = flatten(path)

            print()
            print_path(path)
            print(f"The artists have {len(path) - 1} degrees of separation")
        answer = input("Play again? [Y] = Yes, [N] = No: ")
        if answer.lower() != "y":
            break

def main():
    links = load_json("data/links.json", Graph)
    if links is None: return
    links = filter_isolated(links) #* this gets it down from ~840 000 -> ~457 000
    
    links = get_subgraph(links, 200)
    print_path(longest_ever_path(links))

    return

    separation_game(links)

    return

if __name__ == "__main__":
    main()