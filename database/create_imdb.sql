#used to quickly view database

CREATE TABLE TABLE IF NOT EXISTS title_basics (
    tconst TEXT PRIMARY KEY,
    titleType TEXT,
    primaryTitle TEXT,
    originalTitle TEXT,
    isAdult BOOLEAN,
    startYear INT,
    endYear INT,
    runtimeMinutes INT,
    genres TEXT
);

CREATE TABLE TABLE IF NOT EXISTS title_ratings (
    tconst TEXT PRIMARY KEY,
    averageRating REAL,
    numVotes INT
);


CREATE TABLE TABLE IF NOT EXISTS movie (
    tconst TEXT PRIMARY KEY,             -- Unique identifier like 'tt0000591'
    titleType TEXT,                      -- e.g., 'movie'
    primaryTitle TEXT,                   -- e.g., 'The Prodigal Son'
    originalTitle TEXT,                  -- e.g., 'L'enfant prodigue'
    isAdult BOOLEAN,                     -- 0 or 1 (use BOOLEAN in PostgreSQL)
    startYear INTEGER,                   -- e.g., 1907
    runtimeMinutes INTEGER               -- e.g., 90
);
-- CREATE TYPE genre_enum AS ENUM ('Documentary', 'Short', 'Sport', 'Comedy');
--
-- CREATE TABLE genre (
--     tconst TEXT PRIMARY KEY,
--     genre genre_enum
-- );
CREATE TABLE TABLE IF NOT EXISTS genre (
    tconst TEXT NOT NULL,
    genre TEXT NOT NULL,
    PRIMARY KEY (tconst,genre)
);



