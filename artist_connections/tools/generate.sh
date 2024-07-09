#!/bin/sh

fast=false
while getopts "f" flag; do
    case $flag in
        f) fast=true;;
    esac
done

if [ "$fast" == false ]; then
    python -m artist_connections.tools.generate_modified_csv
fi

python -m artist_connections.tools.generate_artists
python -m artist_connections.tools.generate_links
python -m artist_connections.tools.generate_songs
