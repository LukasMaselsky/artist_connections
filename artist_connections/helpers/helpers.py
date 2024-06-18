from typing import List
from artist_connections.datatypes.datatypes import EdgesJSON, NodesJSON
import json

def rgba_to_hex(r: int, g: int, b: int, a: float):
    if r < 0 or r > 255:
        raise ValueError("r value must be in between 0 and 255")
    if g < 0 or g > 255:
        raise ValueError("g value must be in between 0 and 255")
    if b < 0 or b > 255:
        raise ValueError("b value must be in between 0 and 255")
    if a < 0.0 or a > 1.0:
        raise ValueError("a value must be in between 0 and 1")

    return '#{:02x}{:02x}{:02x}{:02x}'.format(r, g, b, int(255 * a))

def parse_features(s: str) -> List[str]:
    if len(s) == 2:
        # no features
        return []
    
    strings = []
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]
        for item in s.split(","):
            decoded_s: str = item.encode().decode('unicode_escape')
            decoded_s = decoded_s.replace("\\'", "'")
            if decoded_s.startswith('"') and decoded_s.endswith('"'):
                decoded_s = decoded_s[1:-1]    
            strings.append(decoded_s)
        return strings
    return []

def load_edges_json(path: str) -> EdgesJSON | None:
    try:
        with open(path) as f:
            data: EdgesJSON = json.load(f)
        return data
    except Exception as e:
        return None
    
def load_nodes_json(path: str) -> List[str] | None:
    try:
        with open(path) as f:
            data: NodesJSON = json.load(f)
        return data
    except Exception as e:
        return None