import csv
import os

from datetime import date
from typing import List

from sqlalchemy import desc, asc
from sqlalchemy.engine import Engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from werkzeug.security import generate_password_hash

from sqlalchemy.orm import scoped_session
from flask import _app_ctx_stack

from movie.domain.model import User, Review, Director, Actor, Genre, Movie
from movie.adapters.repository import AbstractRepository

tags = None


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def get_user(self, username) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter_by(_username=username).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return user

    def add_movie(self, movie: Movie):
        with self._session_cm as scm:
            scm.session.add(movie)
            scm.commit()

    def get_movie(self, id: int) -> Movie:
        movie = None
        try:
            movie = self._session_cm.session.query(Movie).filter(Movie._id == id).one()
        except NoResultFound:
            pass
        return movie

    def get_number_of_movies(self):
        number_of_movies = self._session_cm.session.query(Movie).count()
        return number_of_movies

    def get_movies_by_id(self, id_list):
        movies = self._session_cm.session.query(Movie).filter(Movie._id.in_(id_list)).all()
        return movies

    def get_movie_ids_all(self):
        movie_ids =[]
        ids = self._session_cm.session.execute(
            'SELECT id FROM movies').fetchall()
        for item in ids:
            i = item[0]
            movie_ids.append(i)

        return movie_ids

    def get_movie_ids_for_genre(self, genre_name: str):
        movies_ids = []

        # Use native SQL to retrieve article ids, since there is no mapped class for the article_tags table.
        row = self._session_cm.session.execute('SELECT id FROM genres WHERE name = :genre_name',
                                               {'genre_name': genre_name}).fetchone()

        if row is None:
            # No tag with the name tag_name - create an empty list.
            movies_ids = list()
        else:
            genre_id = row[0]

            # Retrieve article ids of articles associated with the tag.
            movies_ids = self._session_cm.session.execute(
                'SELECT movie_id FROM movies_genres WHERE genres_id = :genres_id ORDER BY movie_id ASC',
                {'genres_id': genre_id}
            ).fetchall()
            movies_ids = [id[0] for id in movies_ids]

        return movies_ids

    # [(10,),(2,),(4,)]
    # for item in movie_ids:
    #     id = item[0] [10,2,4]

    def get_movie_ids_for_actor(self, actor_name: str):
        movies_ids = []

        # Use native SQL to retrieve article ids, since there is no mapped class for the article_tags table.
        row = self._session_cm.session.execute('SELECT id FROM actors WHERE name = :actor_name',
                                               {'actor_name': actor_name}).fetchone()

        if row is None:
            # No tag with the name tag_name - create an empty list.
            movies_ids = list()
        else:
            actor_id = row[0]

            # Retrieve article ids of articles associated with the tag.
            movies_ids = self._session_cm.session.execute(
                'SELECT movie_id FROM movies_actors WHERE actors_id = :actors_id ORDER BY movie_id ASC',
                {'actors_id': actor_id}
            ).fetchall()
            movies_ids = [id[0] for id in movies_ids]

        return movies_ids

    def get_movie_ids_for_director(self, director_name: str):
        movies_ids = []

        # Use native SQL to retrieve article ids, since there is no mapped class for the article_tags table.
        row = self._session_cm.session.execute('SELECT id FROM directors WHERE name = :director_name',
                                               {'director_name': director_name}).fetchone()

        if row is None:
            # No tag with the name tag_name - create an empty list.
            movies_ids = list()
        else:
            director_id = row[0]

            # Retrieve article ids of articles associated with the tag.
            movies_ids = self._session_cm.session.execute(
                'SELECT movie_id FROM movies_directors WHERE directors_id = :directors_id ORDER BY movie_id ASC',
                {'directors_id': director_id}
            ).fetchall()
            movies_ids = [id[0] for id in movies_ids]

        return movies_ids

    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.add(genre)
            scm.commit()

    def get_genres(self) -> List[Genre]:
        genres = self._session_cm.session.query(Genre).all()
        return genres

    def add_actor(self, actor: Actor):
        with self._session_cm as scm:
            scm.session.add(actor)
            scm.commit()

    def get_actors(self) -> List[Actor]:
        actors = self._session_cm.session.query(Actor).all()
        return actors

    def add_director(self, director: Director):
        with self._session_cm as scm:
            scm.session.add(director)
            scm.commit()

    def get_directors(self) -> List[Director]:
        directors = self._session_cm.session.query(Director).all()
        return directors

    def add_review(self, comment: Review):
        super().add_review(comment)
        with self._session_cm as scm:
            scm.session.add(comment)
            scm.commit()

    def get_reviews(self):
        reviews = self._session_cm.session.query(Review).all()
        return reviews


def movie_record_generator(filename):
    with open(filename, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        headers = next(reader)

        for data_row in reader:
            movie_key = int(data_row[0])
            # no need to substring, the double quotes already auto trimmed by csv read function
            # movie_genres = data_row[2][1:-1].split(',')
            movie_title = str(data_row[1])
            movie_genres_list = data_row[2].split((','))
            # movie_genres = ', '.join(data_row[2].split(','))
            movie_description = str(data_row[3])
            movie_director = str(data_row[4].strip())

            movie_actors_list = data_row[5].split((','))
            # movie_actors = ', '.join(data_row[5].split(','))
            movie_year = int(data_row[6])
            runtime_minutes = int(data_row[7])
            movie_rating = float(data_row[8])
            movie_votes = int(data_row[9])

            movie_genres = movie_genres_list
            for i in movie_genres:
                i.strip()
                if i not in genre.keys():
                    genre[i] = list()
                genre[i].append(movie_key)

            movie_actors = movie_actors_list
            for i in movie_actors:
                i = i.strip()
                if i not in actor.keys():
                    actor[i] = list()
                actor[i].append(movie_key)

            movie_directors = movie_director
            if movie_directors not in director.keys():
                director[movie_directors] = list()
            director[movie_directors].append(movie_key)

            movie_revenue = str(data_row[10])
            if movie_revenue != "N/A":
                movie_revenue = float(movie_revenue)
            else:
                movie_revenue = "N/A"
            movie_metascore = str(data_row[11])
            if movie_metascore != "N/A":
                movie_metascore = float(movie_metascore)
            else:
                movie_metascore = "N/A"

            yield movie_key, movie_title, movie_description, movie_year, \
                  runtime_minutes, movie_rating, movie_votes, movie_revenue, movie_metascore


def movie_director_generator():
    movie_director_key = 0
    director_key = 0

    for d in director.keys():
        director_key += 1
        for movie_key in director[d]:
            movie_director_key += 1
            yield movie_director_key, director_key, movie_key


def movie_genre_generator():
    movie_genre_key = 0
    genre_key = 0

    for g in genre.keys():
        genre_key += 1
        for movie_key in genre[g]:
            movie_genre_key += 1
            yield movie_genre_key, genre_key, movie_key


def movie_actor_generator():
    movie_actor_key = 0
    actor_key = 0

    for a in actor.keys():
        actor_key += 1
        for movie_key in actor[a]:
            movie_actor_key += 1
            yield movie_actor_key, actor_key, movie_key


def get_genre_records():
    genre_records = []
    genre_key = 0

    for g in genre:
        genre_key += 1
        genre_records.append((genre_key, g))

    return genre_records


def get_director_records():
    director_records = []
    director_key = 0

    for d in director:
        director_key += 1
        director_records.append((director_key, d))

    return director_records


def get_actors_records():
    actor_records = []
    actor_key = 0

    for a in actor:
        actor_key += 1
        actor_records.append((actor_key, a))

    return actor_records


def generic_generator(filename, post_process=None):
    with open(filename) as infile:
        reader = csv.reader(infile)

        # Read first line of the CSV file.
        next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]

            if post_process is not None:
                row = post_process(row)
            yield row


def process_user(user_row):
    user_row[2] = generate_password_hash(user_row[2])
    return user_row


# year, runtime_minutes, rating, votes,revenue, metascore )
def populate(engine: Engine, data_path: str):
    conn = engine.raw_connection()
    cursor = conn.cursor()

    global director, actor, genre
    director = dict()
    genre = dict()
    actor = dict()

    insert_movies = """
               INSERT INTO movies (
               id, title, description,  year, runtime_minutes, rating, votes, revenue_millions, meta_score)
               VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.executemany(insert_movies, movie_record_generator(os.path.join(data_path, 'Data1000Movies.csv')))
    # a = cursor.fetchall()
    # print(a)

    insert_users = """
        INSERT INTO users (
        id, username, password)
        VALUES (?, ?, ?)"""
    cursor.executemany(insert_users, generic_generator(os.path.join(data_path, 'users.csv'), process_user))

    insert_genres = """
        INSERT INTO genres (
        id, name)
        VALUES(?, ?)"""
    cursor.executemany(insert_genres, get_genre_records())

    insert_directors = """
        INSERT INTO directors (
        id, name )
        VALUES(?, ?)"""
    cursor.executemany(insert_directors, get_director_records())

    insert_directors = """
            INSERT INTO actors (
            id, name )
            VALUES(?, ?)"""
    cursor.executemany(insert_directors, get_actors_records())

    insert_movie_director = """
        INSERT INTO movies_directors (
        id, directors_id, movie_id)
        VALUES(?,?,?)"""
    cursor.executemany(insert_movie_director, movie_director_generator())

    insert_movie_genre = """
            INSERT INTO movies_genres (
            id, genres_id, movie_id)
            VALUES(?,?,?)"""
    cursor.executemany(insert_movie_genre, movie_genre_generator())

    insert_movie_actor = """
            INSERT INTO movies_actors (
            id, actors_id, movie_id)
            VALUES(?,?,?)"""
    cursor.executemany(insert_movie_actor, movie_actor_generator())

    insert_reviews = """
           INSERT INTO reviews (
           id,user_id, movie_id, comment, timestamp)
           VALUES (?,?,?,?,?)"""
    cursor.executemany(insert_reviews, generic_generator(os.path.join(data_path, 'comments.csv')))

    conn.commit()
    conn.close()
