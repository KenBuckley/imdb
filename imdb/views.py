#aiohttp core
from aiohttp import web
import asyncpg
import json


async def index(request):
    db = request.app['config']['postgres']['database']
    host = request.app['config']['postgres']['host']
    return web.Response(text=f"imdb server active.\nselected database:{db}\ndb host:{host}")


# Get all movies from DB
async def get_all_movies(request):
    """
    ---
    description: All movies with sorting support
    tags:
      - IMDB
    parameters:
      - name: sort
        in: query
        description: Sort by field with direction (e.g., year_asc, rating_desc, title_asc)
        required: false
        type: string
        enum: [year_asc, year_desc, rating_asc, rating_desc, title_asc, title_desc]
    responses:
      "200":
        description: Successful response
      "400":
        description: Invalid sort parameter
    """
    pool = request.app['db']

    # Get sort parameter from query string
    sort_param = request.query.get('sort', 'tconst_asc')  # default sort

    # Define valid sort options and their SQL equivalents
    valid_sorts = {
        'year_asc': 'm.startyear ASC NULLS LAST',
        'year_desc': 'm.startyear DESC NULLS LAST',
        'rating_asc': 'm.rating ASC NULLS LAST',
        'rating_desc': 'm.rating DESC NULLS LAST',
        'title_asc': 'm.primarytitle ASC',
        'title_desc': 'm.primarytitle DESC',
        'tconst_asc': 'm.tconst ASC'  # default fallback
    }

    # Validate sort parameter
    if sort_param not in valid_sorts:
        return web.json_response(
            {'error': f'Invalid sort parameter. Valid options: {list(valid_sorts.keys())}'},
            status=400
        )

    order_clause = valid_sorts[sort_param]

    try:
        async with pool.acquire() as conn:

            query = f"""
                SELECT m.tconst,
                       COALESCE(array_agg(g.genre ORDER BY g.genre) 
                                FILTER (WHERE g.genre IS NOT NULL), ARRAY[]::varchar[]) AS genre,
                       m.primarytitle,
                       m.startyear,
                       m.rating::float,
                       m.runtimeminutes,
                       'https://www.imdb.com/title/' || m.tconst AS url
                FROM public.movie m 
                LEFT JOIN public.genre g ON m.tconst = g.tconst 
                GROUP BY m.tconst
                ORDER BY {order_clause}
                
            """
            rows = await conn.fetch(query)
            return web.json_response([dict(row) for row in rows])
    except Exception as e:
        #can log error or hand error back with 500 -or sentry error.
        return web.json_response ({'error': 'There was a database error.'}, status=500 )



async def get_movie_by_id(request):
    """
    ---
    description: All movies with sorting support
    tags:
      - IMDB
    parameters:
      - name: sort
        in: query
        description: Sort by field with direction (e.g., year_asc, rating_desc, title_asc)
        required: false
        type: string
        enum: [year_asc, year_desc, rating_asc, rating_desc, title_asc, title_desc]
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
                     --titletype,
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
              order by m.tconst asc
              order by {order_clause}
              """, movie_id)
            if row:
                return web.json_response(dict(row))
            else:
                return web.Response(status=404, text='Movie not found')
        except Exception as e:
            return web.json_response ({'error': 'There was a database error.'}, status=500 )