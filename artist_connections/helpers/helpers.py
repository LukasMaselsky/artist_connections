from polars import DataFrame
from artist_connections.datatypes.datatypes import EdgesJSON
from typing import Any, TypeVar, Type
import json
from functools import wraps
import time
import os
import matplotlib.pyplot as plt
import seaborn as sns

def scatter_plot(df: DataFrame, x: str, y:str, hue: str, title: str, font_colour: str, bg_colour: str, label_limit: int):
    fig, ax = plt.subplots()
    fig.patch.set_facecolor(bg_colour)
    fig.suptitle(title, fontsize=16, color=font_colour)
    g = sns.scatterplot(data=df, x="solo songs", y="feat songs", hue="genre", ax=ax, edgecolor=None)
    g.set(facecolor=bg_colour)
    ax.set_facecolor(bg_colour)
    ax.set_xlabel('Solo songs', color=font_colour)
    ax.set_ylabel('Songs with features', color=font_colour)
    ax.tick_params(axis='x', colors=font_colour)
    ax.tick_params(axis='y', colors=font_colour)
    for spine in ax.spines.values():
        spine.set_edgecolor(font_colour)

    # add point labels
    for i, row in enumerate(df.iter_rows()):
        g.text(row[1], row[2] + 7, row[0], horizontalalignment='center', size='small', color='black', weight='medium')
        if i >= label_limit - 1:
            break

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print(f'Function {f.__name__} took {te-ts:2.4f} seconds\n')
        return result
    return wrap

def rgba_to_hex(r: int, g: int, b: int, a: float = 1):
    if r < 0 or r > 255:
        raise ValueError("r value must be in between 0 and 255")
    if g < 0 or g > 255:
        raise ValueError("g value must be in between 0 and 255")
    if b < 0 or b > 255:
        raise ValueError("b value must be in between 0 and 255")
    if a < 0.0 or a > 1.0:
        raise ValueError("a value must be in between 0 and 1")

    return '#{:02x}{:02x}{:02x}{:02x}'.format(r, g, b, int(255 * a))

T = TypeVar("T")

@timing
def load_json(path: str, type: Type[T]) -> T | None:

    if not os.path.exists(path):
        print("File not found, check that you have the correct path")

    try:
        with open(path, encoding="utf-8") as f:
            data: T = json.load(f)
        return data
    except FileNotFoundError:
        print("File not found")
    except json.JSONDecodeError:
        print("Invalid JSON format")
    except Exception as e:
        print(f"Unnexpected error: {e}")


@timing
def write_to_json(data: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False)
