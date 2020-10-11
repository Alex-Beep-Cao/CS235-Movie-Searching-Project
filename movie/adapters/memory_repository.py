import csv
import os
from datetime import date, datetime
from typing import List

from bisect import bisect, bisect_left, insort_left

from werkzeug.security import generate_password_hash

from movie.adapters.repository import AbstractRepository, RepositoryException
from movie.domain.model import User
from movie.domain.model import Movie, Genre, Actor, Director, Review
from movie.domain.model import make_genre_association, make_actor_association, make_director_association, make_review


class MemoryRepository(AbstractRepository):

    def __init__(self):
        # self._articles = list()
        # self._articles_index = dict()
        self._tags = list()
        self._users = list()
        self._comments = list()

        self._movies = list()
        self._movies_index = dict()
        self._genres = list()
        self._actors = list()
        self._directors = list()
        self._reviews = list()

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.username == username), None)

    def add_movie(self, movie: Movie):
        insort_left(self._movies, movie)
        self._movies_index[movie.id] = movie

    def get_movie(self, id: int) -> Movie:
        movie = None

        try:
            movie = self._movies_index[id]
        except KeyError:
            pass

        return movie

    def get_number_of_movies(self):
        return len(self._movies)

    def get_movies_by_id(self, id_list):
        # Strip out any ids in id_list that don't represent Movie ids in the repository.
        existing_ids = [id for id in id_list if id in self._movies_index]

        # Fetch the Movies.
        movies = [self._movies_index[id] for id in existing_ids]
        return movies

    def get_movie_ids_all(self):
        movie_ids = [movie.id for movie in self._movies]

        return movie_ids

    def get_movie_ids_for_genre(self, genre_name: str):
        # Linear search, to find the first occurrence of a Genre with the name genre_name.
        genre = next((genre for genre in self._genres if genre.genre_name == genre_name), None)

        # Retrieve the ids of movies associated with the Genre.
        if genre is not None:
            movie_ids = [movie.id for movie in genre.genre_movies]
        else:
            # No Genre with name genre_name, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_movie_ids_for_actor(self, actor_name: str):
        # Linear search, to find the first occurrence of a Actor with the name actor_name.
        actor = next((actor for actor in self._actors if actor.actor_name == actor_name), None)

        # Retrieve the ids of movies associated with the Actor.
        if actor is not None:
            movie_ids = [movie.id for movie in actor.actor_movies]
        else:
            # No Actor with name actor_name, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_movie_ids_for_director(self, director_name: str):
        # Linear search, to find the first occurrence of a Director with the name director_name .
        director = next((director for director in self._directors if director.director_name == director_name), None)

        # Retrieve the ids of movies associated with the Director.
        if director is not None:
            movie_ids = [movie.id for movie in director.director_movies]
        else:
            # No Director with name director_name , so return an empty list.
            movie_ids = list()

        return movie_ids

    def add_genre(self, genre: Genre):
        self._genres.append(genre)

    def get_genres(self) -> List[Genre]:
        return self._genres

    def add_actor(self, actor: Actor):
        self._actors.append(actor)

    def get_actors(self) -> List[Actor]:
        return self._actors

    def add_director(self, director: Director):
        self._directors.append(director)

    def get_directors(self) -> List[Director]:
        return self._directors

    def add_review(self, comment: Review):
        super().add_review(comment)
        self._reviews.append(comment)

    def get_reviews(self):
        return self._reviews


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_users(data_path: str, repo: MemoryRepository):
    users = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'users.csv')):
        user = User(
            username=data_row[1],
            password=generate_password_hash(data_row[2])
        )
        repo.add_user(user)
        users[data_row[0]] = user
    return users


def load_comments(data_path: str, repo: MemoryRepository, users):
    for data_row in read_csv_file(os.path.join(data_path, 'comments.csv')):
        comment = make_review(
            comment_text=data_row[3],
            user=users[data_row[1]],
            movie=repo.get_movie(int(data_row[2])),
            timestamp=datetime.fromisoformat(data_row[4])
        )
        repo.add_review(comment)


def load_movies_and_genres(data_path: str, repo: MemoryRepository):
    genres = dict()
    actors = dict()
    directors = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'Data1000Movies.csv')):

        movie_key = int(data_row[0])
        # no need to substring, the double quotes already auto trimmed by csv read function
        # movie_genres = data_row[2][1:-1].split(',')
        movie_genres = data_row[2].split(',')
        movie_actors = data_row[5].split(',')
        movie_director = data_row[4].strip()

        # Add any new genres; associate the current movie with genres.
        for genre in movie_genres:
            genre = genre.strip()
            if genre not in genres.keys():
                genres[genre] = list()
            genres[genre].append(movie_key)

        for actor in movie_actors:
            actor = actor.strip()
            if actor not in actors.keys():
                actors[actor] = list()
            actors[actor].append(movie_key)

        if movie_director not in directors.keys():
            directors[movie_director] = list()
        directors[movie_director].append(movie_key)

        # Create Movie object.
        movie = Movie(
            title=data_row[1],
            description=data_row[3],
            year=data_row[6],
            runtime_minutes=data_row[7],
            rating=data_row[8],
            votes=data_row[9],
            revenue_millions=data_row[10],
            meta_score=data_row[11],

            id=movie_key
        )

        # Add the Movie to the repository.
        repo.add_movie(movie)

    # Create Genre objects, associate them with Movies and add them to the repository.
    for genre_name in genres.keys():
        genre = Genre(genre_name)
        for movie_id in genres[genre_name]:
            movie = repo.get_movie(movie_id)
            make_genre_association(movie, genre)
        repo.add_genre(genre)

    for actor_name in actors.keys():
        actor = Actor(actor_name)
        for movie_id in actors[actor_name]:
            movie = repo.get_movie(movie_id)
            make_actor_association(movie, actor)
        repo.add_actor(actor)

    for director_name in directors.keys():
        director = Director(director_name)
        for movie_id in directors[director_name]:
            movie = repo.get_movie(movie_id)
            make_director_association(movie, director)
        repo.add_director(director)


def populate(data_path: str, repo: MemoryRepository):
    # Load movies and genres into the repository.
    load_movies_and_genres(data_path, repo)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # Load comments into the repository.
    load_comments(data_path, repo, users)
