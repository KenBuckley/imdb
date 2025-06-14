#!/bin/bash

# if any of the commands in your code fails for any reason, the entire script fails
set -o errexit
# fail exit if one of your pipe command fails
set -o pipefail
# exits if any of your variables is not set
set -o nounset


# download the imdb data files if they are not present
# github (free tier) only allows individual file sizes of max 100MB , which forces us to download the files
# on first run. They will not be downloaded again if they are found to exist in /app/data.
#
# The imdb files may change at any time so this introduces
# an element of risk to the project (because the imdb files may have breaking changes in
# the future). So we would prefer to self host the tsv files if possible.
# File to check (uncompressed)
FILE="/app/data/title.ratings.tsv"
# Download URL
URL="https://datasets.imdbws.com/title.ratings.tsv.gz"

# If file does not exist, download and unzip
if [ ! -f "$FILE" ]; then
    echo "File $FILE not found. Downloading and extracting..."
    cd /app/data
    curl -O "$URL"
    gunzip -f title.ratings.tsv.gz
else
    echo "File $FILE already exists. Skipping download."
fi

# File to check (uncompressed)
FILE_B="/app/data/title.basics.tsv"

# Download URL_B
URL_B="https://datasets.imdbws.com/title.basics.tsv.gz"

# If file does not exist, download and unzip
if [ ! -f "$FILE_B" ]; then
    echo "File $FILE_B not found. Downloading and extracting..."
    cd /app/data
    curl -O "$URL_B"
    gunzip -f title.basics.tsv.gz
else
    echo "File $FILE_B already exists. Skipping download."
fi

#important move back to the /app directory after the cd to data.
cd /app  #reset to root directory after downloads

#hopefully at this stage postgres is ready
# you can use nc to check for postgres if you prefer:
#while ! nc -z $SQL_HOST $SQL_PORT; do
#    sleep 0.2
#    >&2 echo 'Waiting for PostgreSQL to become available...'
#done
#>&2 echo 'postgres OK.'

#Check to see if postgress is available, wait until  it is ready
postgres_ready() {
python << END
import sys

import psycopg

try:
    psycopg.connect(
        dbname="${SQL_DB}",
        user="${SQL_USER}",
        password="${SQL_PASSWORD}",
        host="${SQL_HOST}",
        port="${SQL_PORT}",
    )
except psycopg.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  #>&2 set #debugging assistance. use to check evn settings on terminal
  sleep 2
  >&2 echo 'sleeping 2...'
done
>&2 echo 'PostgreSQL ok'

#pwd #debugging assistance

#If you have an image with an entrypoint pointing to entrypoint.sh, and you run your container as
#docker run my_image server start,
#that will translate to running entrypoint.sh server start in the container. At the exec line entrypoint.sh, the shell
#running as pid 1 will replace itself with the command server start.
exec "$@"