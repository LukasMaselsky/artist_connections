from artist_connections.datatypes.datatypes import Graph
from artist_connections.helpers.helpers import load_json

def filter_non_cycles(links: Graph) -> Graph:
    graph: Graph = {}
    for artist, l in links.items():
        if len(l) == 2: # if potentially part of cycle, only has 2 connections
            graph[artist] = l
    return graph

def get_cycle(start: str, cons: set[str], graph: Graph) -> None | list[str]:
    cycle = []
    cycle.append(start)

    prev = start
    lcons = list(cons)
    nxt = lcons[0]
    end = lcons[1]

    #check if end artist also exists in filtered graph
    if end not in graph or nxt not in graph:
        return None

    while True:
        cur = nxt
        if cur not in graph:
            # next node was one that was filtered out
            cycle = None
            break

        new_cons = list(graph[cur])
        con1, con2 = new_cons[0], new_cons[1]
        nxt = con1 if con1 != prev else con2 
        prev = cur

        if nxt in cycle:
            # cycle failed, becomes a web
            cycle = None
            break

        cycle.append(cur)
        if nxt == end:
            cycle.append(end)
            break


    return cycle

        
def get_longest_cycles(graph: Graph):
    '''Input of filtered graph'''

    longest = [[]]

    done = set()

    for a, b in graph.items():
        if a in done: continue # skip duplicates

        cycle = get_cycle(a, b, graph)

        if cycle is None: continue
        if len(cycle) > len(longest[0]):
            longest = [cycle]
            done.update(cycle)
        elif len(cycle) == len(longest[0]):
            longest.append(cycle)
            done.update(cycle)


    return longest





def main():
    links = load_json("data/links.json", Graph)
    if links is None: return
    graph = filter_non_cycles(links)
    cycles = get_longest_cycles(graph)
    for cycle in cycles:
        print(cycle, f"Length: {len(cycle)}")

    return


if __name__ == "__main__":
    main()


