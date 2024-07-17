# Artist Connections

> An analysis of the connections between artists from over 5 million songs

## Developing

### Built With

-   Python 3.12.0

### Prerequisites

For the display of any of the graphs, the **Arial Unicode MS** font needs to be installed. Otherwise, Unicode characters for the Matplotlib graphs will not be displayed correctly

The dataset used for the analysis is the [Genius Song Lyrics](https://www.kaggle.com/datasets/carlosgdcj/genius-song-lyrics-with-language-information) dataset from Kaggle. To move the dataset to correct directory and rename it:

```shell
mv <path of dataset> path-of-project/data
mv <name of dataset> song_lyrics.csv # rename file
```

### Setting up Dev

To clone he repo to local:

```shell
git clone https://github.com/LukasMaselsky/artist_connections.git
cd artist_connections
pip install -r requirements.txt
```

### Generating

To generate the cleaned dataset and additional JSON files, run:

```shell
./artist_connections/tools/generate.sh
```

This runs `generate_modified_cs.py` to clean the dataset, and then runs `generate.py` to create the JSON files used in the analysis.

Alternatively, if you don't have BASH installed you can run

```python
python -m artist_connections.tools.generate_modified_csv
python -m artist_connections.tools.generate
```

to achieve the same result.

### Using

Running the main script using

```python
python -m artist_connections
```

gives a choice to see any of the graphs/analysis patterns. You can also run each script individually.

## Tests

Describe and show how to run the tests with code examples.
Explain what these tests test and why.

```shell
Give an example
```

## Licensing

State what the license is and how to find the text version of the license.
