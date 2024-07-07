#!/bin/sh
python -m artist_connections.tools.generate_modified_csv
python -m artist_connections.tools.generate_artists
python -m artist_connections.tools.generate_links
python -m artist_connections.tools.generate_songs
