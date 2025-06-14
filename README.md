


imdb API

Quick start
To run the application in docker,type
docker compose up -d --build 

In your browser you can see the documentation for the api at 
http://localhost:8080/api/doc#/IMDB



GET /movies
GET /movies/id
POST /movies


Running the server locally using python:
The packge manager used here is uv, so it will need to be installed on the local machine.

cd to the project directory imdb.
from the directory containing docker-compose.yml enter the following commands:
uv venv 
uv sync
python -m imdb.main



specifically the following files were used to create the database


obtaining the data to build the database:
1.title.basics.tsv.gz
2.title.ratings.tsv.gz





Edge cases in table title.basics.tsv:
multiole titles:
tt0000049	short	Boxing Match; or, Glove Contest	Boxing Match; or, Glove Contest	0	1896	\N	\N	Short,Sport

some movies have no genre: (might substitute unknown -otherwise might not show when searching for genre=any)
"tt0000502"	"movie"	"Bohemios"	"Bohemios"	false	1905		100	 [null]

table design: 
we keep the field original title as that might also be used in the search for the title (more information needed).

Do not apply indexes before bulk data loading, or else this will slow down the loading. Apply indexes after data loading.

the program should take into account that when creating a movie, that movie/genre are keys on table genre, 
hence we should remove duplicate genes from the creation of a new movie (many different methods available to do this).

There are many movies without a rating - so we should return null for the rating if it is not present:
there are 386K movie records without a rating
SELECT count(m.*)
FROM public.movie m
LEFT JOIN public.rating r ON m.tconst = r.tconst
WHERE r."averageRating" IS NULL;
>>386544


> 
> json example of a record with no rating:
>http://localhost:8080/movie/tt0000846
> 

>
 

