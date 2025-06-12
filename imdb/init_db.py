from sqlalchemy import create_engine, MetaData
from db import movie,genre,rating
from settings import load_config

"""
create and populate the tables 
movie
genre
in the database.
Tables will not be created if they already exist.
"""
def create_tables(engine):
    meta = MetaData()
    #create all the tables defined in the MetaData()
    meta.create_all(bind=engine,checkfirst=True, tables=[movie,genre,rating])


config=load_config()
DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)
    create_tables(engine)
