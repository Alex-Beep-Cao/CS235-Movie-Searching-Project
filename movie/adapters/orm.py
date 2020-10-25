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
    Column('year', Integer, nullable=False),
    Column('title', String(1024), nullable=False),
    Column('description', String(1024), nullable=False),
    Column('runtime_minutes', Float, nullable=False),
    Column('meta_score', Integer, nullable=False),
    Column('rating', Float, nullable=False),
    Column('votes', Integer, nullable=False),
    Column('revenue_millions', Float, nullable=False)

)

genres = Table(
    'genres', metadata,
    Column('name', String(64), primary_key=True, nullable=False),
)

directors = Table(
    'directors', metadata,
    Column('name', String(64), primary_key=True, nullable=False),
)

actors = Table(
    'actors', metadata,
    Column('name', String(64), primary_key=True, nullable=False),
)

movie_genres = Table(
    'movies_genres', metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('genres_name', String(64), ForeignKey('genres.name')),
    Column('movies_id', Integer, ForeignKey('movies.id'))
)


movies_directors = Table(
    'movies_directors', metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('directors_name', String(64), ForeignKey('directors.name')),
    Column('movies_id', Integer, ForeignKey('movies.id'))
)

movies_actors = Table(
    'movies_actors', metadata,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('actors_name', String(64), ForeignKey('actors.name')),
    Column('movies_id', Integer, ForeignKey('movies.id'))
)


def map_model_to_tables():
    mapper(model.User, users, properties={
        '_username': users.c.username,
        '_password': users.c.password,
        '_reviews': relationship(model.Review, backref='_user')
    })
    mapper(model.Review, reviews, properties={
        '_comment': reviews.c.comment,
        '_timestamp': reviews.c.timestamp
    })

    movies_mapper = mapper(model.Movie, movies, properties={
        '_id': movies.c.id,
        '_year': movies.c.year,
        '_title': movies.c.title,
        '_description': movies.c.description,
        '_runtime_minutes': movies.c.runtime_minutes,
        '_rating': movies.c.rating,
        '_votes': movies.c.votes,
        '_revenue_millions': movies.c.revenue_millions,
        '_meta_score': movies.c.meta_score,
        '_comments': relationship(model.Review, backref='_movie'),

        
    })








