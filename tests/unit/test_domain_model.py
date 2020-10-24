from datetime import date

from movie.domain.model import User, Movie, Genre, Review, ModelException, make_genre_association, \
    make_actor_association, make_director_association, Actor, Director

import pytest


@pytest.fixture()
def movie():
    return Movie(
        "Guardians of the Galaxy",
        "A group of intergalactic criminals are forced to work together to stop a fanatical warrior from taking control of the universe.",
        2014,
        121,
        8.1,
        757074,
        333.13,
        76

    )


@pytest.fixture()
def user():
    return User('dbowie', '1234567890')


@pytest.fixture()
def genre():
    return Genre('New Zealand')


@pytest.fixture()
def actor():
    return Actor('Emma Stone')


@pytest.fixture()
def director():
    return Director('Alex')


def test_user_construction(user):
    assert user.username == 'dbowie'
    assert user.password == '1234567890'
    assert repr(user) == '<User dbowie 1234567890>'


def test_movie_construction(movie):
    assert movie.id is None
    assert movie.title == "Guardians of the Galaxy"
    assert movie.description == "A group of intergalactic criminals are forced to work together to stop a fanatical warrior from taking control of the universe."
    assert movie.year == 2014
    assert movie.runtime_minutes == 121

    assert movie.number_of_comments == 0

    assert repr(movie) == '<Movie 2014 Guardians of the Galaxy>'


def test_genre_construction(genre):
    assert genre.genre_name == 'New Zealand'
    for movie in genre.genre_movies:
        assert False


def test_make_genre_association(movie, genre):
    make_genre_association(movie, genre)

    assert genre.is_applied_to(movie)
    assert movie in genre.genre_movies


def test_make_actor_association(movie, actor):
    make_actor_association(movie, actor)

    assert actor.is_applied_to(movie)
    assert movie in actor._actor_movies


def test_make_director_association(movie, director):
    make_director_association(movie, director)

    assert director.is_applied_to(movie)
    assert movie in director._director_movies




