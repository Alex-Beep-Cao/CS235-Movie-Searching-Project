from datetime import date, datetime

import pytest

from movie.adapters.database_repository import SqlAlchemyRepository
from movie.domain.model import User, Movie, Review, Actor, Genre, Director, make_review
from movie.adapters.repository import RepositoryException

def test_repository_can_add_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('Dave', '123456789')
    repo.add_user(user)

    repo.add_user(User('Martin', '123456789'))

    user2 = repo.get_user('Dave')


def test_repository_can_retrieve_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_movie_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_movies = repo.get_number_of_movies()

    # Check that the query returned 5 Movie.
    assert number_of_movies == 5


def test_repository_can_add_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_movies = repo.get_number_of_movies()

    new_movie_id = number_of_movies + 1

    movie = Movie(
        "Morning Alex",
        "very cool ",
        2020,
        1000,
        5.0,
        199,
        100.5,
        11,
        new_movie_id
    )
    repo.add_movie(movie)

    assert repo.get_movie(new_movie_id) == movie  # revenue _ failed
    assert repo.get_number_of_movies() == 6


def test_repository_can_retrieve_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(1)

    # Check that the Article has the expected title.
    assert movie.title == 'Guardians of the Galaxy'

    # Check that the Article is commented as expected.
    comment_one = [comment for comment in movie.comments if comment.comment == 'good movie'][
        0]
    comment_two = [comment for comment in movie.comments if comment.comment == 'Yeah great'][0]

    assert comment_one.user.username == 'fmercury'
    assert comment_two.user.username == "thorke"

    # Check that the Article is tagged as expected.
    assert movie.is_genre_by(Genre('Action'))
    assert movie.is_genre_by(Genre('Adventure'))


def test_repository_does_not_retrieve_a_non_existent_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(100000)
    assert movie is None


def test_repository_can_get_movies_by_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_id([2, 1])

    assert len(movies) == 2
    assert movies[
               0].title == 'Guardians of the Galaxy'
    assert movies[1].title == "Prometheus"


def test_repository_does_not_retrieve_movie_for_non_existent_id(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_id([2, 209])

    assert len(movies) == 1
    assert movies[
               0].title == "Prometheus"


def test_repository_returns_an_empty_list_for_non_existent_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_id([0, 199])

    assert len(movies) == 0


def test_movie_load(session_factory):
    repo = SqlAlchemyRepository(session_factory)
    movie_ids = repo.get_movie_ids_all()

    assert len(movie_ids) == 5


def test_repository_returns_movie_ids_for_existing_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie_ids = repo.get_movie_ids_for_genre('Action')

    assert movie_ids == [1, 5]


def test_repository_returns_movie_ids_for_existing_actor(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie_ids = repo.get_movie_ids_for_actor('Michael Fassbender')

    assert movie_ids == [2]

def test_repository_returns_movie_ids_for_existing_director(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie_ids = repo.get_movie_ids_for_director('M. Night Shyamalan')

    assert movie_ids == [3]


def test_repository_returns_none_when_there_are_no_subsequent_movies(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(177)


    assert movie is None

def test_repository_can_add_a_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genre = Genre('Motoring')
    repo.add_genre(genre)

    assert genre in repo.get_genres()

def test_repository_can_add_a_director(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    director = Director('Motoring')
    repo.add_director(director)

    assert director in repo.get_directors()

def test_repository_can_add_a_actor(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    actor = Actor('Motoring')
    repo.add_actor(actor)

    assert actor in repo.get_actors()

def test_repository_can_add_a_comment(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    movie = repo.get_movie(2)
    comment = make_review("Trump's onto it!", user, movie)

    repo.add_review(comment)

    assert comment in repo.get_reviews()


def test_repository_does_not_add_a_comment_without_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(2)
    comment = Review(None, movie, "Trump's onto it!", datetime.today())

    with pytest.raises(RepositoryException):
        repo.add_review(comment)


def test_repository_can_retrieve_reviews(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    assert len(repo.get_reviews()) == 3


