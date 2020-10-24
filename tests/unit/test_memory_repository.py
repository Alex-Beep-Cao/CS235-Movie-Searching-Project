from datetime import date, datetime
from typing import List

import pytest

from movie.domain.model import User, Movie, Review, Actor, Genre, make_review
from movie.adapters.repository import RepositoryException


def test_repository_can_add_a_user(in_memory_repo):
    user = User('Dave', '123456789')
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('Dave') is user


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = in_memory_repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_movie_count(in_memory_repo):
    number_of_articles = in_memory_repo.get_number_of_movies()

    # Check that the query returned 5 Articles.
    assert number_of_articles == 5


def test_repository_does_not_retrieve_a_non_existent_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(101)
    assert movie is None


def test_repository_can_get_first_movie(in_memory_repo):
    movie = in_memory_repo.get_movies_by_id([1])
    assert movie[0].title == 'Guardians of the Galaxy'


def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    movies = in_memory_repo.get_movies_by_id([0, 9])

    assert len(movies) == 0


def test_repository_returns_movie_ids_for_existing_genre(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_for_genre('Horror')

    assert movie_ids == [3]


def test_repository_returns_an_empty_list_for_non_existent_tag(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_for_director('James Gunn')

    assert len(movie_ids) == 1


def test_repository_can_add_a_genre(in_memory_repo):
    genre = Genre('Motoring')
    in_memory_repo.add_genre(genre)

    assert genre in in_memory_repo.get_genres()


def test_repository_can_add_a_comment(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    movie = in_memory_repo.get_movie(2)
    comment = make_review("nice nice nice", user, movie)

    in_memory_repo.add_review(comment)

    assert comment in in_memory_repo.get_reviews()


def test_repository_does_not_add_a_comment_without_a_user(in_memory_repo):
    article = in_memory_repo.get_movie(2)
    comment = Review(None, article, "Trump's onto it!", datetime.today())

    with pytest.raises(RepositoryException):
        in_memory_repo.add_review(comment)


def test_repository_does_not_add_a_comment_without_an_movie_properly_attached(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    movie = in_memory_repo.get_movie(2)
    comment = Review(None, movie, "Trump's onto it!", datetime.today())

    user.add_review(comment)

    with pytest.raises(RepositoryException):
        # Exception expected because the Article doesn't refer to the Comment.
        in_memory_repo.add_review(comment)


def test_repository_can_retrieve_comments(in_memory_repo):
    assert len(in_memory_repo.get_reviews()) == 3


