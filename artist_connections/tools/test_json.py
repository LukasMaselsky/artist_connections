from artist_connections.helpers.helpers import load_edges_json
import json
from typing import List

def main():
    original = load_edges_json("data/nodes.json")
    with open("data/alternate_nodes.json") as f:
        alternate: List[str] = json.load(f)
    
    if original is None:
        return
    
    print(f"Original: {len(original)}, Alternate: {len(alternate)}")


if __name__ == "__main__":
    main()