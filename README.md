


imdb API

Quick start
To run the application in docker,type
docker compose up -d --build 

In your browser you can see the documentation for the api at 
http://localhost:8080/api/doc#/IMDB  
  


GET /movies  
GET /movies/id  
POST /movies  

To create a new movie entry, post a json dataset to the server as follows:
```
bash 
  curl -X POST http://localhost:8080/movie \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Adventure Movie",
    "originaltitle": "mijn avonturenfilm",
    "startyear": 2024,
    "rating": 8.5,
    "runtimeminutes": 120,
    "genres": ["Comedy", "Drama"]
  }'
```

Optional api question: pagination techniques.
If the api is going to be used for a web interface then the web interface would ask for
the standard paging below, but if the api is focused on providing data for processing then I would 
prefer to have seek pagination -here we have id's and timestamps in the data so easy to implement..

```
#paging for a web site:  
async def get_all_movies(request):  
    # Get query parameters  
    page = int(request.query.get('page', 1))  
    limit = int(request.query.get('limit', 50))  
    offset = (page - 1) * limit  
    
    # Add to the query
    rows = await conn.fetch("""
        SELECT ... 
        FROM public.movie m 
        LEFT JOIN public.genre g ON m.tconst = g.tconst 
        GROUP BY m.tconst
        ORDER BY tconst ASC
        LIMIT $1 OFFSET $2
    """, limit, offset)
```  

Running the server locally using python:
The packge manager used here is uv, so it will need to be installed on the local machine.

cd to the project directory imdb.
Make sure the database is running.
From the directory containing docker-compose.yml enter the following commands (linux machine), 

uv venv  
uv sync  
source .venv/bin/activate    
python -m imdb.main   

now in your browser go to localhost:8080/api/doc .
Note: if you run the server locally using python, you will download the imdb
files (unzipped) to you local directory at the location install_dir/data. These will be downloaded
only once, and will also be used if you build the container again. 


### Edge cases in table title.basics.tsv:
1. There are some movies with multiple titles:
tt0000049	short	Boxing Match; or, Glove Contest	Boxing Match; or, Glove Contest	0	1896	\N	\N	Short,Sport

2. some movies have no genre: (might substitute unknown -otherwise might not show when searching for genre=any)
"tt0000502"	"movie"	"Bohemios"	"Bohemios"	false	1905		100	 [null]

### table design: 
it might also be good to keep the field originalTitle as that might also be used in the search for the title 
especially for titles that are not in english. We could also add unaccent or og_trgm to assist with searching titles and
originalTitle.
(more information needed to make this decision).

Do not apply indexes before bulk data loading, or else this will slow down the loading. Apply indexes after data loading.

the program should take into account that when creating a movie, that movie/genre are keys on table genre, 
hence we should remove duplicate genes from the creation of a new movie (many different methods available to do this).

Note: there are many movies without a rating - so we return null for the rating if it is not present:
there are 386K movie records without a rating



 

