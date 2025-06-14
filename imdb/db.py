from sqlalchemy import Table, Column, String, Integer,  ForeignKey, Numeric, MetaData

#SQLAlchemy Core
meta = MetaData()

movie = Table(
    'movie', meta,
    Column('tconst', String(50), primary_key=True, nullable=False),
    #Column('titletype', String(20)),  #not required for
    Column('title', String(1000)),
    Column('originaltitle', String(1000)),
    #Column('isadult', Boolean),
    Column('startyear', Integer),
    Column('rating', Numeric(3, 1)), #allow for 10.0
    Column('runtimeminutes', Integer),
    schema='public'
)

genre = Table(
    'genre', meta,
    Column('tconst', String(50), ForeignKey('public.movie.tconst', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('genre', String(100), primary_key=True, nullable=False),
    schema='public'
)


# not needed we put the rating field into
# rating = Table(
#     'rating',
#     meta,
#     Column('tconst', String(50), primary_key=True),
#     Column('averageRating', Float, nullable=False),
#     Column('numVotes', Integer, nullable=False),
#     schema='public'
# )

