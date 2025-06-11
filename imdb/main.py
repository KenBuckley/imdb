#aiohttp core
from aiohttp import web

#3rd party imports
from aiohttp_swagger import *

#local imports
from routes import setup_routes
from settings import load_config,load_connection_pool



async def init_app():
    async def on_cleanup(app):
        await app['db'].close()

    app = web.Application()
    app['config'] = load_config()
    # Create DB connection pool
    app['db'] = await load_connection_pool()
    app.on_cleanup.append(on_cleanup)

    setup_routes(app)
    setup_swagger(app)


    return app


# Run the app
if __name__ == '__main__':
    web.run_app(init_app())