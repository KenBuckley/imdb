from sqlalchemy import Table, Column, String, Integer, Boolean, ForeignKey, Float, MetaData

#SQLAlchemy Core
meta = MetaData()

movie = Table(
    'movie', meta,
    Column('tconst', String(50), primary_key=True, nullable=False),
    Column('titletype', String(20)),
    Column('primarytitle', String(1000)),
    Column('originaltitle', String(1000)),
    Column('isadult', Boolean),
    Column('startyear', Integer),
    Column('runtimeminutes', Integer),
    schema='public'
)

genre = Table(
    'genre', meta,
    Column('tconst', String(50), ForeignKey('public.movie.tconst', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('genre', String(100), primary_key=True, nullable=False),
    schema='public'
)

rating = Table(
    'rating',
    meta,
    Column('tconst', String(50), primary_key=True),
    Column('averageRating', Float, nullable=False),
    Column('numVotes', Integer, nullable=False),
    schema='public'
)

