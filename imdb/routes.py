from .views import index, get_all_movies, get_movie_by_id

def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/movie', get_all_movies)
    app.router.add_get('/movie/{id}', get_movie_by_id)