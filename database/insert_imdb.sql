--MOVIE
INSERT INTO public.movie (
    tconst,
    titletype,
    primarytitle,
    originaltitle,
    isadult,
    startyear,
    runtimeminutes
)
SELECT
    tconst,
    titletype,
    primarytitle,
    originaltitle,
    isadult,
    startyear,
    runtimeminutes
FROM public.title_basics
where titletype = 'movie';

--GENRE
insert into public.genre(
tconst,
genre
)
select tconst,
unnest(string_to_array(genres, ',')) AS genre
from public.title_basics
where titletype='movie'
and genres is not null