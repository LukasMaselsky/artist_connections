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

def should_filter(s: str, filter_list: list[str]) -> bool:
    if s in filter_list:
        return True
    return False


def parse_features(s: str) -> list[str]:
    if len(s) == 2:
        # no features
        return []

    strings = []
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]
        for item in s.split(","):
            decoded_s = item
            if decoded_s.startswith('"') and decoded_s.endswith('"'):
                decoded_s = decoded_s[1:-1]    
            decoded_s = decoded_s.replace("\\\\'", "'")
            decoded_s = decoded_s.replace('\\\\\\"', '"')
            decoded_s = decoded_s.replace("\\\\$", "$")
            decoded_s = decoded_s.replace("\\\\`", "`")
            strings.append(decoded_s)
        return strings
    return []

def load_edges_json(path: str) -> EdgesJSON | None:
    try:
        with open(path, encoding="utf-8") as f:
            data: EdgesJSON = json.load(f)
        return data
    except Exception as e:
        return None
    
def load_nodes_json(path: str) -> list[str] | None:
    try:
        with open(path) as f:
            data: NodesJSON = json.load(f)
        return data
    except Exception as e:
        return None
    
def load_filter_list_json(path: str) -> list[str] | None:
    try:
        with open(path, encoding="utf-8") as f:
            data: list[str] = json.load(f)
        return data
    except Exception as e:
        return None
    
def write_to_json(data, path: str) -> None:
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False)

