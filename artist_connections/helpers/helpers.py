from polars import DataFrame
from typing import Any, TypeVar, Type
import json
from functools import wraps
import time
import os
import matplotlib.pyplot as plt
import seaborn as sns
from difflib import SequenceMatcher, get_close_matches
from typing import Literal
from artist_connections.datatypes.datatypes import Artists



colors = {"black": 30, "red": 31, "green": 32, "yellow": 33, "blue": 34, "purple": 35, "cyan": 36, "white": 37}
styles = {"none": 0, "bold": 1, "underline": 2}
Colors = Literal["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]
Styles = Literal["none", "bold", "underline"]

def styled(text: str, color: Colors = "white", style: Styles = "none") -> str: 
    return f"\033[{styles[style]};{colors[color]};40m{text}\033[0;37;40m"
class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)

def scatter_plot(df: DataFrame, x: str, y:str, hue: str, title: str, font_colour: str, bg_colour: str, label_limit: int):
    fig, ax = plt.subplots()
    fig.patch.set_facecolor(bg_colour)
    fig.suptitle(title, fontsize=16, color=font_colour)
    g = sns.scatterplot(data=df, x=x, y=y, hue=hue, ax=ax, edgecolor=None)
    g.set(facecolor=bg_colour)
    ax.set_facecolor(bg_colour)
    ax.set_xlabel(x, color=font_colour)
    ax.set_ylabel(y, color=font_colour)
    ax.tick_params(axis='x', colors=font_colour)
    ax.tick_params(axis='y', colors=font_colour)
    for spine in ax.spines.values():
        spine.set_edgecolor(font_colour)

    # add point labels
    for i, row in enumerate(df.iter_rows()):
        g.text(row[1], row[2] + 15, row[0], horizontalalignment='center', size='small', color='black', weight='medium')
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
            print(f'Function {styled(f.__name__, style="bold")}, args: {args_dict}, kwargs: {kwargs} took {te-ts:2.4f} seconds\n')
            return result
        return wrap
    return _decorator(func) if callable(func) else _decorator

def rgba_to_hex(r: int, g: int, b: int, a: float = 1) -> str:  
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
        print(f"Unexpected error: {e}")

@timing(show_arg_vals=False)
def write_to_json(data: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False)

@timing(show_arg_vals=False)
def sort_artists_by_song_count(artists: Artists) -> Artists:
    return dict(sorted(artists.items(), key=lambda x: x[1]["solo_songs"] + x[1]["feat_songs"], reverse=True))

def custom_filter(s: str) -> bool:
    '''For all the bullshit ones, casts of tv shows/musicals etc that can't be detected by program rules'''    

    #* get rid of broadway/musical/tv show casts
    if "cast of" in s.lower():
        return True
    
    return False

def parse_features(s: str) -> list[str]:
    '''Convert list of features from a strint to a list, processing each one according to rules

    Args:
        s (str): list of features as unprocessed string e.g. "{""Cam\\'ron"",""Opera Steve""}"

    Returns:
        list[str]: list of processed features
    '''    
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
    Unicode version will always be in features (I think, haven't checked all)
    If this format found, always store feature as the artist name, ascii version should be discarded
    Also things like "Earth, Wind & Fire": {"Earth / Wind & Fire"}, the feature is discarded
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
    if custom_filter(s):
        return True
    return False

def print_options(options: list[str]):
    for i, option in enumerate(options):
        print(f"[{i}] {option}")

def int_input(message: str, maximum: int, minimum: int = 0) -> int:
    while True:
        try:
            a = int(input(message))
            if a > maximum or a < minimum:
                print(f"Please enter a valid number ({minimum} to {maximum})")
            else:
                break
        except ValueError:
            print("Please enter a number")
    return a

def search(data: dict[str, T], message: str) -> str:
    '''
    Takes user input and searches data for the artist name. 
    If no match found, gives fuzzy found matches as options
    '''    

    def search_for(data: dict[str, T], query: str) -> str | None:    
        if query in data:
            return query
        
        matches = get_close_matches(query, data.keys(), n=3, cutoff=0.6)
        if len(matches) == 0: return None 
        
        print("An exact match couldn't be found, did you mean: ")

        print_options(matches)

        choose = int_input("Choose an option: ", len(matches) - 1)

        return matches[choose]
   
    query: str = input(message)
    searched_for = search_for(data, query)
    
    while searched_for is None:
        print("Search query invalid, no matches found")
        query: str = input(message)
        searched_for = search_for(data, query)

    return searched_for
