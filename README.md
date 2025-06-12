


imdb API

GET /movies
GET /movies/id
POST /movies



The data files were downloaded from https://datasets.imdbws.com/. 
Their description is here: https://www.imdb.com/interfaces/


specifically the following files were used to create the database


obtaining the data to build the database:
1.title.basics.tsv.gz
2.title.ratings.tsv.gz


url -O https://datasets.imdbws.com/title.basics.tsv.gz #(size 197M)  June 2025
   

curl -O https://datasets.imdbws.com/title.ratings.tsv.gz   #(size 7750k) June 2025


unpack the datasets into tsv files, i.e.  '7z e  title.basics.tsv.gz'




Edge cases in table title.basics.tsv:
multiole titles:
tt0000049	short	Boxing Match; or, Glove Contest	Boxing Match; or, Glove Contest	0	1896	\N	\N	Short,Sport

some movies have no genre: (might substitute unknown -otherwise might not show when searching for genre=any)
"tt0000502"	"movie"	"Bohemios"	"Bohemios"	false	1905		100	 [null]


There are many movies without a rating - so we should return null for the rating if it is not present:
there are 386K movie records without a rating
SELECT count(m.*)
FROM public.movie m
LEFT JOIN public.rating r ON m.tconst = r.tconst
WHERE r."averageRating" IS NULL;
>>386544