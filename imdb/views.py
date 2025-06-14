#aiohttp core
from aiohttp import web
#import asyncpg
#import json


async def index(request):
    db = request.app['config']['postgres']['database']
    host = request.app['config']['postgres']['host']
    return web.Response(text=f"imdb server active.\nselected database:{db}\ndb host:{host}")


# Get all movies from DB
async def get_all_movies(request):
    """
    ---
    description: All movies with sorting and filtering support
    tags:
      - IMDB
    parameters:
      - name: sort
        in: query
        description: Sort by field with direction (e.g., year_asc, rating_desc, title_asc)
        required: false
        type: string
        enum: [year_asc, year_desc, rating_asc, rating_desc, title_asc, title_desc]
      - name: genre
        in: query
        description: Filter by genre
        required: false
        type: string
        enum: [Animation, Biography, Comedy, Crime, Documentary, Drama, Family, Fantasy, Film-Noir, Game-Show, History, Horror, Music, Musical, Mystery, News, Reality-TV, Romance, Sci-Fi, Short, Sport, Talk-Show, Thriller, War, Western]
      - name: rating_from
        in: query
        description: Minimum rating (inclusive)
        required: false
        type: number
        minimum: 0
        maximum: 10
      - name: rating_to
        in: query
        description: Maximum rating (inclusive)
        required: false
        type: number
        minimum: 0
        maximum: 10
    responses:
      "200":
        description: Successful response
      "400":
        description: Invalid parameters
    """
    pool = request.app['db']

    # Get parameters from query string
    sort_param = request.query.get('sort', 'tconst_asc')
    genre_filter = request.query.get('genre')
    rating_from = request.query.get('rating_from')
    rating_to = request.query.get('rating_to')

    # Define valid sort options and their SQL equivalents
    valid_sorts = {
        'year_asc': 'm.startyear ASC NULLS LAST',
        'year_desc': 'm.startyear DESC NULLS LAST',
        'rating_asc': 'm.rating ASC NULLS LAST',
        'rating_desc': 'm.rating DESC NULLS LAST',
        'title_asc': 'm.title ASC',
        'title_desc': 'm.title DESC',
        'tconst_asc': 'm.tconst ASC'
    }

    # Valid genres
    valid_genres = {
        'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama',
        'Family', 'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror',
        'Music', 'Musical', 'Mystery', 'News', 'Reality-TV', 'Romance',
        'Sci-Fi', 'Short', 'Sport', 'Talk-Show', 'Thriller', 'War', 'Western'
    }

    # Validation
    if sort_param not in valid_sorts:
        return web.json_response(
            {'error': f'Invalid sort parameter. Valid options: {list(valid_sorts.keys())}'},
            status=400
        )

    if genre_filter and genre_filter not in valid_genres:
        return web.json_response(
            {'error': f'Invalid genre. Valid options: {sorted(valid_genres)}'},
            status=400
        )

    # Validate rating parameters
    try:
        if rating_from is not None:
            rating_from = float(rating_from)
            if rating_from < 0 or rating_from > 10:
                raise ValueError("rating_from must be between 0 and 10")

        if rating_to is not None:
            rating_to = float(rating_to)
            if rating_to < 0 or rating_to > 10:
                raise ValueError("rating_to must be between 0 and 10")

        if rating_from is not None and rating_to is not None and rating_from > rating_to:
            raise ValueError("rating_from cannot be greater than rating_to")

    except (ValueError, TypeError) as e:

        return web.json_response(
            {'error': f'Invalid rating parameter: {str(e)}'},
            status=400
        )

    # Build WHERE clauses and parameters
    where_clauses = []
    params = []
    param_count = 0

    # Genre filter
    if genre_filter:
        param_count += 1
        where_clauses.append(
            f"EXISTS (SELECT 1 FROM public.genre g2 WHERE g2.tconst = m.tconst AND g2.genre = ${param_count})")
        params.append(genre_filter)

    # Rating filters
    if rating_from is not None:
        param_count += 1
        where_clauses.append(f"m.rating >= ${param_count}")
        params.append(rating_from)

    if rating_to is not None:
        param_count += 1
        where_clauses.append(f"m.rating <= ${param_count}")
        params.append(rating_to)

    # Construct WHERE clause
    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    order_clause = valid_sorts[sort_param]

    try:
        async with pool.acquire() as conn:
            query = f"""
                SELECT m.tconst,
                       COALESCE(array_agg(g.genre ORDER BY g.genre) 
                                FILTER (WHERE g.genre IS NOT NULL), ARRAY[]::varchar[]) AS genre,
                       m.title,
                       m.startyear,
                       m.rating::float,
                       m.runtimeminutes,
                       'https://www.imdb.com/title/' || m.tconst AS url
                FROM public.movie m 
                LEFT JOIN public.genre g ON m.tconst = g.tconst 
                {where_sql}
                GROUP BY m.tconst
                ORDER BY {order_clause}
            """
            rows = await conn.fetch(query, *params)
            return web.json_response([dict(row) for row in rows])

    except Exception as e:
        return web.json_response({'error': 'Database error occurred'}, status=500 )


async def get_movie_by_id(request):
    """
    ---
    description: All movies with sorting support
    tags:
      - IMDB
    parameters:

    responses:
      "200":
        description: Successful response
      "400":
        description: Invalid sort parameter
    """
    movie_id = request.match_info['id']
    pool = request.app['db']


    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow("""
              SELECT m.tconst,
                     COALESCE(array_agg(g.genre ORDER BY g.genre) 
                              FILTER (WHERE g.genre IS NOT NULL), ARRAY[]::varchar[]) AS genre,
                     m.title,
                     --m.originaltitle,
                     --m.isadult,
                     m.startyear,
                     m.rating::float,
                     m.runtimeminutes,
                     'https://www.imdb.com/title/' || m.tconst AS url
              FROM public.movie m 
              left join public.genre g on m.tconst = g.tconst
              WHERE m.tconst = $1 
              group by m.tconst
              """, movie_id)
            if row:
                return web.json_response(dict(row))
            else:
                return web.Response(status=404, text='Movie not found')
        except Exception as e:
            return web.json_response ({'error': 'There was a database error.'}, status=500 )