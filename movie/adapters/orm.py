from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey, Float
)
from sqlalchemy.orm import mapper, relationship

from movie.domain import model

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False)
)

reviews = Table(
    'reviews', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.id')),
    Column('movie_id', ForeignKey('movies.id')),
    Column('comment', String(1024), nullable='False'),
    Column('timestamp', DateTime, nullable=False)

)

movies = Table(
    'movies', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(1024), nullable=False),
    # Column('genre', String(1024), nullable=False),
    Column('description', String(1024), nullable=False),
    # Column('director', String(1024), nullable=False),
    # Column('actor', String(1024), nullable=False),
    Column('year', Integer, nullable=False),
    Column('runtime_minutes', Float, nullable=False),
    Column('rating', Float, nullable=False),
    Column('votes', Integer, nullable=False),
    Column('revenue', Float, nullable=False),
    Column('metascore', Integer, nullable=False)

)
# Rank,Title,Genre,Description,Director,Actors,Year,Runtime (Minutes),Rating,Votes,Revenue (Millions),Metascore
genres = Table(
    'genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(64), nullable=False)
)

directors = Table(
    'directors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(64), nullable=False),
)

actors = Table(
    'actors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(64), nullable=False),
)

movie_genres = Table(
    'movies_genres', metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('genres_name', String(64), ForeignKey('genres.name')),
    Column('movie_id', Integer, ForeignKey('movies.id'))
)

movies_directors = Table(
    'movies_directors', metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('directors_name', String(64), ForeignKey('directors.name')),
    Column('movie_id', Integer, ForeignKey('movies.id'))
)

movies_actors = Table(
    'movies_actors', metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('actors_name', String(64), ForeignKey('actors.name')),
    Column('movie_id', Integer, ForeignKey('movies.id'))
)


def map_model_to_tables():
    mapper(model.User, users, properties={
        '_username': users.c.username,
        '_password': users.c.password,
        '_reviews': relationship(model.Review, backref='_user')
    })
    #     mapper(model.Review, reviews, properties={
    #         '_comment': reviews.c.comment,
    #         '_timestamp': reviews.c.timestamp
    #     })
    #
    mapper(model.Movie, movies, properties={
        '_id': movies.c.id,
        '_year': movies.c.year,
        '_title': movies.c.title,
        '_description': movies.c.description,
        '_runtime_minutes': movies.c.runtime_minutes,
        '_rating': movies.c.rating,
        '_votes': movies.c.votes,
        '_revenue': movies.c.revenue,
        '_metascore': movies.c.metascore,
        '_comments': relationship(model.Review, backref='_movie'),

    })
#
