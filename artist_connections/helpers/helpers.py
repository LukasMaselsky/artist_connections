from polars import DataFrame
from typing import Any, TypeVar, Type
import json
from functools import wraps
import time
import os
import matplotlib.pyplot as plt
import seaborn as sns
from difflib import SequenceMatcher

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)

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


def timing(func=None, show_arg_vals=True):
    #? if used with @timing, then func is a callable and it calls the _decorator with func as arg
    #? if used with @timing(show_arg_vals=False) it just return _decorator since its already calling it with ()
    assert callable(func) or func is None
    def _decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            ts = time.time()
            result = f(*args, **kwargs)
            te = time.time()
           
            args_dict = dict(zip(f.__code__.co_varnames, args)) if show_arg_vals else f.__code__.co_varnames
            print(f'Function {f.__name__}, args: {args_dict}, kwargs: {kwargs} took {te-ts:2.4f} seconds\n')
            return result
        return wrap
    return _decorator(func) if callable(func) else _decorator

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


@timing(show_arg_vals=False)
def write_to_json(data: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False)

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

def process(artist: str, features: list[str], custom_list: list[str]) -> str:
    '''
    Format of types of string to be processed:  (dima bamberg),"{""дима бамберг (dima bamberg)""}"
    Unicode version will always be in features (I think, haven't checked)
    If this format found, always store feature as the artist name, ascii version should be discarded
    Also things like "Earth, Wind & Fire": {"Earth / Wind & Fire"}
    '''
    if artist in custom_list:
        return features[0]
    
    if len(features) == 1:
        feature = features[0]
        if feature == artist:
            features.remove(feature)
            return feature

    for feature in features:
        if artist == feature.encode("ascii", "ignore").decode():
            features.remove(feature)
            return feature
        if " /" in feature:
            if artist == feature.replace(" /", ",").replace(u"\u200b", ""):
                features.remove(feature)
                return artist
        if " / " in feature:
            if artist == feature.replace(" / ", ",").replace(u"\u200b", ""):
                features.remove(feature)
                return artist
        if u"\u00a0" in feature:
            if artist == feature.replace(u"\u00a0", " "):
                features.remove(feature)
                return artist
        if artist == feature.replace(u"\u200b", ""):
            features.remove(feature)
            return artist
        
        

    if "(" in artist and ")" in artist:
        for feature in features:
            if "(" not in feature or ")" not in feature: # check so artist_inside doesnt fail
                continue

            feature_inside = (feature.split("("))[1].split(")")[0]
            artist_inside = (artist.split("("))[1].split(")")[0]

            if artist_inside == "" or artist_inside.isspace(): # handle: "artist name ... ()" format
                features.remove(feature)
                return feature

            if SequenceMatcher(None, feature_inside, artist_inside).ratio() > 0.7:
                features.remove(feature)
                return feature

    return artist

def should_filter(s: str, filter_list: list[str]) -> bool:
    if s in filter_list:
        return True
    return False