from collections import deque
from re import L
from artist_connections.datatypes.datatypes import Graph
from artist_connections.helpers.helpers import load_json, search, styled, timing


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
    print(" <-> ".join(l))

def bbfs(graph: Graph, start: str, end: str) -> list[str] | None:
    if start == end:
        return [start]

    # Initialize distances and queues for both directions
    dist_start = {start: [start]}
    dist_end = {end: [end]}
    q_start = deque([start])
    q_end = deque([end])

    def bfs(graph: Graph, q: deque[str], dist_this_side: dict[str, list[str]], dist_other_side: dict[str, list[str]]):
        current = q.popleft()
        for neighbor in graph[current]:
            if neighbor not in dist_this_side:
                # Add neighbor to current path and queue
                dist_this_side[neighbor] = dist_this_side[current] + [neighbor] #* this creates a "link" between current node and the neighbor
                
                q.append(neighbor)
                # Check if the other side has reached this neighbor
                if neighbor in dist_other_side:
                    return neighbor  # Return the meeting point
        return None

    def reconstruct_path(dist_start: dict[str, list[str]], dist_end: dict[str, list[str]], meet_point: str):
        # Combine the paths from both directions
        path_start = dist_start[meet_point]
        path_end = dist_end[meet_point][::-1]  # Reverse the end path to start from the meet point
        return path_start + path_end[1:]  # Exclude the meet point from the end path to avoid duplication

    while q_start and q_end:
        # Extend BFS alternately
        if len(q_start) <= len(q_end):
            meet_point = bfs(graph, q_start, dist_start, dist_end)
        else:
            meet_point = bfs(graph, q_end, dist_end, dist_start)

        if meet_point:
            return reconstruct_path(dist_start, dist_end, meet_point)

    return None  # If no path is found

def bfs(graph: Graph, start: str, end: str) -> list[str] | None:

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
    '''In between O(n^2) and O(n^3) depending on density of graph USING BFS'''
    '''Approximately: 0.000002x^{3.05}, over a minute for top 300'''
    '''A lot faster with bbfs'''
    longest_path = []
    
    for a in graph.keys():
        for b in graph.keys():
            if a == b: continue
            path = bbfs(graph, a, b)
            if path is None: continue
            
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
    graph: Graph = {artist: l for artist, l in links.items() if len(l) != 0}
    return graph

def separation_game(links: Graph):

    print("See how many degrees of separation 2 artist have\n")

    while True:
        artist1 = search(links, "Artist 1: ")
        artist2 = search(links, "Artist 1: ")

        path = bbfs(links, artist1, artist2)
        if path is None: 
            print("No path found")
        else:
            print()
            print_path(path)
            print(f"The artists have {len(path) - 1} degrees of separation")
        answer = input("Play again? [y/n]: ")
        if answer.lower() != "y":
            break
        print()

def main():
    links = load_json("data/links.json", Graph)
    if links is None: return
    links = filter_isolated(links) #* this gets it down from ~840 000 -> ~457 000

    separation_game(links)
    return
    subgraph = get_subgraph(links, 1000)
    print_path(longest_ever_path(subgraph))

if __name__ == "__main__":
    main()