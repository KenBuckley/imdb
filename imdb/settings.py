import os
from dotenv import load_dotenv
import asyncpg


# Load variables from .env into os.environ
load_dotenv()

database=os.getenv("SQL_DB", "imdb")
user=os.getenv("SQL_USER", "imdb")
password=os.getenv("SQL_PASSWORD","password")
host=os.getenv("SQL_HOST", "127.0.0.1")
port=int(os.getenv("SQL_PORT", 5432))

# Function to create a config dictionary
def load_config():
    return {
        "postgres":{
            "database": database,
            "user": user,
            "password": password,
            "host": host,
            "port": port,
        }
    }

async def load_connection_pool():
    pool = await asyncpg.create_pool(
        user=user,
        password=password,
        database=database,
        host=host,
        port=port
    )
    return pool
