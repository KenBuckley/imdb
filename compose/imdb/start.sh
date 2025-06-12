#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

#could put this env DATABASE_URL in the docker-compose.yml too.
export DATABASE_URL="postgresql://${SQL_USER}:${SQL_PASSWORD}@${SQL_HOST}:${SQL_PORT}/${SQL_DB}"

echo "load datasets from tsv files..."
psql "$DATABASE_URL" <<'EOF'
-- Create the tables if they do not exist
CREATE TABLE IF NOT EXISTS title_basics (
    tconst TEXT,
    titleType TEXT,
    primaryTitle TEXT,
    originalTitle TEXT,
    isAdult BOOLEAN,
    startYear INTEGER,
    endYear INTEGER,
    runtimeMinutes INTEGER,
    genres TEXT
);

CREATE TABLE IF NOT EXISTS title_ratings (
    tconst TEXT PRIMARY KEY,
    averageRating REAL,
    numVotes INTEGER
);

EOF

row_count=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM title_basics;" | xargs)

if [ "$row_count" -eq 0 ]; then
    echo "Table title_basics is empty. Loading data..."
    psql "$DATABASE_URL" -c "\COPY title_basics FROM '/app/data/title.basics.tsv' WITH (FORMAT text, DELIMITER E'\t', NULL '\N', HEADER);"
else
    echo "Table title_basics already has data. Skipping COPY."
fi


row_count=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM title_ratings;" | xargs)

if [ "$row_count" -eq 0 ]; then
    echo "Table title_ratings is empty. Loading data..."
    psql "$DATABASE_URL" -c "\COPY title_ratings FROM '/app/data/title.ratings.tsv' WITH (FORMAT text, DELIMITER E'\t', NULL '\N', HEADER);"
else
    echo "Table title_ratings already has data. Skipping COPY."
fi





echo "Initializing database schema..."
#create tables movie and genre as per SqlAlchemy defs., if tables exist they will not be created
python imdb/init_db.py

#echo "Loading table movie"
#psql "$DATABASE_URL" <<EOF
#DO \$\$
#BEGIN
#    IF NOT EXISTS (SELECT 1 FROM public.movie LIMIT 1) THEN
#        RAISE NOTICE 'Loading data...';
#
#
#    ELSE
#        RAISE NOTICE 'Data already exists. Skipping.';
#    END IF;
#END
#\$\$;
#EOF



echo "Starting aiohttp server..."
gunicorn imdb.main:init_app --bind 0.0.0.0:8000 --worker-class aiohttp.GunicornWebWorker