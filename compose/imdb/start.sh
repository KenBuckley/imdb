#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

#could put this env DATABASE_URL in the docker-compose.yml too.
export DATABASE_URL="postgresql://${SQL_USER}:${SQL_PASSWORD}@${SQL_HOST}:${SQL_PORT}/${SQL_DB}"

#create the temporary tables to load data from the tsv files
#we can delete these tables later if we wish, after we have inserted into table movie and table genre.
echo "load datasets from tsv files..."
psql "$DATABASE_URL" <<'EOF'
-- Create the tables if they do not exist,
CREATE TABLE IF NOT EXISTS title_basics (
    tconst TEXT PRIMARY KEY,
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
    averageRating NUMERIC(3,1),
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
#create tables movie and genre as per SqlAlchemy defs., if tables exist they
# 1. will not be created
# 2. will not be populated
python /app/imdb/init_db.py

#usually move these commands to a .sql file to run but this is another way to run
psql "$DATABASE_URL" <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.movie LIMIT 1) THEN
        RAISE NOTICE 'Loading movie data...';
        INSERT INTO public.movie (
            tconst,
            --titletype,
            title,
            originaltitle,
            --isadult,
            startyear,
            runtimeminutes
        )
        SELECT
            tconst,
            --titletype,
            primarytitle,
            originaltitle,
            --isadult,
            startyear,
            runtimeminutes
        FROM public.title_basics
        where titletype = 'movie';
        RAISE NOTICE 'Loading movie data (including ratings)...';
        UPDATE movie m
        set rating =  averagerating
        FROM public.title_ratings r
        where m.tconst = r.tconst;
    ELSE
        RAISE NOTICE 'Table movie: data already exists. Skipping.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM public.genre LIMIT 1) THEN
        RAISE NOTICE 'Loading genre data...';
        insert into public.genre(
        tconst,
        genre
        )
        select tconst,
        unnest(string_to_array(genres, ',')) AS genre
        from public.title_basics
        where titletype='movie'
        and genres is not null;
    ELSE
        RAISE NOTICE 'Table genre: data already exists. Skipping.';
    END IF;

END
\$\$;
EOF





echo "Starting aiohttp server..."
gunicorn imdb.main:init_app --bind 0.0.0.0:8000 --worker-class aiohttp.GunicornWebWorker