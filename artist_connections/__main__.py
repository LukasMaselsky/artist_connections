from datatypes.datatypes import EdgesJSON
from helpers.helpers import load_edges_json
import polars as pl


def main():

    query: str = "Tyler, The Creator"
    data = load_edges_json("data/edges.json")
    print(data)
    '''
    data = load_json()
    if data is None:
        raise ValueError("Data is None")
    
    print(data[query])
    '''

if __name__ == "__main__":
    main()