#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset


echo "Initializing database schema..."
python imdb/init_db.py



echo "Starting aiohttp server..."
gunicorn imdb.main:init_app --bind 0.0.0.0:8000 --worker-class aiohttp.GunicornWebWorker