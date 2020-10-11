from typing import Iterable

from movie.adapters.repository import AbstractRepository
from movie.domain.model import Movie, Genre, Actor, Director, Review
from movie.domain.model import make_review


class NonExistentMovieException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_comment(movie_id: int, comment_text: str, username: str, repo: AbstractRepository):
    # Check that the movie exists.
    movie = repo.get_movie(movie_id)
    if movie is None:
        raise NonExistentMovieException

    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    # Create comment.
    comment = make_review(comment_text, user, movie)

    # Update the repository.
    repo.add_review(comment)


def get_movie(movie_id: int, repo: AbstractRepository):
    movie = repo.get_movie(movie_id)

    if movie is None:
        raise NonExistentMovieException

    return movie_to_dict(movie)


def get_movie_ids_all(repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_all()

    return movie_ids


def get_movie_ids_for_genre(genre_name, repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_for_genre(genre_name)

    return movie_ids


def get_movie_ids_for_actor(actor_name, repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_for_actor(actor_name)

    return movie_ids


def get_movie_ids_for_director(director_name, repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_for_director(director_name)

    return movie_ids


def get_movies_by_id(id_list, repo: AbstractRepository):
    movies = repo.get_movies_by_id(id_list)

    # Convert Movies to dictionary form.
    movies_as_dict = movies_to_dict(movies)

    return movies_as_dict


def get_comments_for_movie(movie_id, repo: AbstractRepository):
    movie = repo.get_movie(movie_id)

    if movie is None:
        raise NonExistentMovieException

    return comments_to_dict(movie.comments)


# ============================================
# Functions to convert model entities to dicts
# ============================================

def movie_to_dict(movie: Movie):

    movie_dict = {
        'id': movie.id,

        'title': movie.title,
        'description': movie.description,
        'year': movie.year,
        'runtime_minutes': movie.runtime_minutes,
        'rating': movie.rating,
        'votes': movie.votes,
        'revenue_millions': movie.revenue_millions,
        'meta_score': movie.meta_score,

        # TODO:
        'comments': comments_to_dict(movie.comments),

        'genres': genres_to_dict(movie.genres),
        'actors': actors_to_dict(movie.actors),
        'directors': directors_to_dict(movie.directors)
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie]):
    return [movie_to_dict(movie) for movie in movies]


def comment_to_dict(comment: Review):
    comment_dict = {
        'username': comment.user.username,
        'movie_id': comment.movie.id,
        'comment_text': comment.comment,
        'timestamp': comment.timestamp
    }
    return comment_dict


def comments_to_dict(comments: Iterable[Review]):
    return [comment_to_dict(comment) for comment in comments]


def genre_to_dict(genre: Genre):
    genre_dict = {
        'name': genre.genre_name,
        'genre_movies': [movie.id for movie in genre.genre_movies]
    }
    return genre_dict


def genres_to_dict(genres: Iterable[Genre]):
    return [genre_to_dict(genre) for genre in genres]


def actor_to_dict(actor: Actor):
    actor_dict = {
        'name': actor.actor_name,
        'actor_movies': [movie.id for movie in actor.actor_movies]
    }
    return actor_dict


def actors_to_dict(actors: Iterable[Actor]):
    return [actor_to_dict(actor) for actor in actors]


def director_to_dict(director: Director):
    director_dict = {
        'name': director.director_name,
        'director_movies': [movie.id for movie in director.director_movies]
    }
    return director_dict


def directors_to_dict(directors: Iterable[Director]):
    return [director_to_dict(director) for director in directors]


# ============================================
# Functions to convert dicts to model entities
# ============================================

# def dict_to_movie(dict):
#     movie = Movie(dict.id,
#                   dict.title,
#                   dict.description,
#                   )
#     # Note there's no comments or genres.
#     return movie
