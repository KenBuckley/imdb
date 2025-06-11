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
    """ limit the return of all movies to the first 1000
        otherwise we risk overloading the client
    """
    pool = request.app['db']
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM public.movie")
        # Convert to list of dicts
        movies = [dict(row) for row in rows]
        return web.json_response(movies)



async def get_movie_by_id(request):
    movie_id = request.match_info['id']
    pool = request.app['db']

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'SELECT * FROM public.movie WHERE tconst = $1', movie_id
        )
        if row:
            return web.json_response(dict(row))
        else:
            return web.Response(status=404, text='Movie not found')