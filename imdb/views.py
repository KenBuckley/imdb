#aiohttp core
from aiohttp import web
#import asyncpg
#import json

# Valid genres -move to utility to share with create movie below
    # we got the
valid_genres = {
    'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama',
    'Family', 'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror',
    'Music', 'Musical', 'Mystery', 'News', 'Reality-TV', 'Romance',
    'Sci-Fi', 'Short', 'Sport', 'Talk-Show', 'Thriller', 'War', 'Western'
}
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


async def generate_unique_tconst(conn):
    """Generate a new tconst  in IMDB format (tt + 7 digits) by finding max + 1"""
    try:
        # approach: Find the highest numeric value from existing tconst IDs
        # Extract digits after 'tt' prefix and convert to integer
        # get the max number after the tt
        # could just do max tconst and this will also work.
        max_tconst = await conn.fetchval("""
                                         SELECT max(tconst)
                                         FROM public.movie
                                         """)
        max_tconst= max_tconst.strip()
        max_number = int(max_tconst[2:])

        # Increment by 1 for new ID
        new_number = max_number + 1

        if new_number <= 9_999_999:  #7x9
            tconst = f"tt{new_number:07d}"
        elif new_number > 9_999_999 and new_number <= 99_999_999: #8x9
            tconst = f"tt{new_number:08d}"
        else:
            raise Exception(f"we have reached the limit of the current key size")

        return tconst

    except Exception as e:
        raise Exception(f"Could not generate a tconst: {str(e)}")



async def create_movie(request):
    """
    ---
    description: Create a new movie with optional genres
    tags:
      - IMDB
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - title
            properties:
              title:
                type: string
                description: Primary title of the movie
                maxLength: 1000
              originaltitle:
                type: string
                description: Original title of the movie
                maxLength: 1000
              startyear:
                type: integer
                description: Year the movie was released
                minimum: 1800
                maximum:
              rating:
                type: number
                description: Movie rating (0.0 - 10.0)
                minimum: 0
                maximum: 10
              runtimeminutes:
                type: integer
                description: Runtime in minutes
                minimum: 1
              genres:
                type: array
                description: List of genres for the movie
                items:
                  type: string
                  enum: [Animation, Biography, Comedy, Crime, Documentary, Drama, Family, Fantasy, Film-Noir, Game-Show, History, Horror, Music, Musical, Mystery, News, Reality-TV, Romance, Sci-Fi, Short, Sport, Talk-Show, Thriller, War, Western]
    responses:
      "201":
        description: Movie created successfully
      "400":
        description: Invalid input data
      "500":
        description: Database error
    """
    pool = request.app['db']



    try:
        # Parse JSON request body
        data = await request.json()
    except Exception:
        return web.json_response(
            {'error': 'Invalid JSON in request body'},
            status=400
        )

    # Validate required fields
    if 'title' not in data or not data['title'].strip():
        return web.json_response(
            {'error': 'Title is required and cannot be empty'},
            status=400
        )

    # Extract and validate data
    # todo: keep the field lengths in one location and apply to sqlalchemy definitions
    #
    title = data['title'].strip()[:1000]  # Truncate to max length
    originaltitle = data.get('originaltitle', '').strip()[:1000] if data.get('originaltitle') else None
    startyear = data.get('startyear')
    rating = data.get('rating')
    runtimeminutes = data.get('runtimeminutes')
    genres = data.get('genres', [])

    # Validate data types and ranges manually - this is a
    # guess as to what is really required, I would need more info.
    # Also we could also use pydantic,and get the bonus of the type checking as well
    # (great to find type bugs) but I havnt used pydantic with aiohttp before
    # so I will keep the checking simple.
    try:
        if startyear is not None:
            startyear = int(startyear)
            if startyear < 1800:
                #todo we need to limit the size to prevent errors if number is too big
                raise ValueError("startyear must be > 1800.")

        if rating is not None:
            rating = float(rating)
            if rating < 0 or rating > 10:
                #todo force to xx.y for number (3,1) in database.
                raise ValueError("rating must be between 0.0 and 10.0")

        if runtimeminutes is not None:
            runtimeminutes = int(runtimeminutes)
            if runtimeminutes < 1:
                raise ValueError("runtimeminutes must be greater than 0")

        if not isinstance(genres, list):
            raise ValueError("genres must be a list")

        # Validate genres
        for genre in genres:
            if genre not in valid_genres:
                raise ValueError(f"Invalid genre '{genre}'. Valid genres: {sorted(valid_genres)}")

        # Remove duplicates from genres
        genres = list(set(genres))

    except (ValueError, TypeError) as e:
        return web.json_response(
            {'error': f'Invalid data: {str(e)}'},
            status=400
        )

    try:
        async with pool.acquire() as conn:
            # Start transaction
            async with conn.transaction():
                # Generate unique tconst
                tconst = await generate_unique_tconst(conn)

                # Insert movie
                await conn.execute("""
                                   INSERT INTO public.movie (tconst, title, originaltitle, startyear, rating, runtimeminutes)
                                   VALUES ($1, $2, $3, $4, $5, $6)
                                   """, tconst, title, originaltitle, startyear, rating, runtimeminutes)

                # Insert genres (if there are any)
                if genres:
                    genre_values = [(tconst, genre) for genre in genres]
                    await conn.executemany("""
                                           INSERT INTO public.genre (tconst, genre)
                                           VALUES ($1, $2)
                                           """, genre_values)

                # Fetch the created movie with genres for response
                movie_data = await conn.fetchrow("""
                                                 SELECT m.tconst,
                                                        COALESCE(array_agg(g.genre ORDER BY g.genre)
                                                                 FILTER(WHERE g.genre IS NOT NULL), ARRAY[]
                                                                 ::varchar[])                     AS genres,
                                                        m.title,
                                                        m.originaltitle,
                                                        m.startyear,
                                                        m.rating::float, m.runtimeminutes,
                                                        'https://www.imdb.com/title/' || m.tconst AS url
                                                 FROM public.movie m
                                                          LEFT JOIN public.genre g ON m.tconst = g.tconst
                                                 WHERE m.tconst = $1
                                                 GROUP BY m.tconst, m.title, m.originaltitle, m.startyear, m.rating,
                                                          m.runtimeminutes
                                                 """, tconst)

        return web.json_response(
            {
                'message': 'Movie created successfully',
                'movie': dict(movie_data)
            },
            status=201
        )

    except Exception as e:
        return web.json_response(
            {'error': f'Database error: {str(e)}'},
            status=500
        )
