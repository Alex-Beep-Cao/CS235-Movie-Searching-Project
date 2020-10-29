import pytest

import datetime

from sqlalchemy.exc import IntegrityError

from movie.domain.model import User, Movie, Review, Actor, Director, make_review, make_genre_association, \
    make_actor_association, \
    make_director_association


def insert_user(empty_session, values=None):
    new_name = "Andrew"
    new_password = "1234"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                          {'username': new_name, 'password': new_password})
    row = empty_session.execute('SELECT id from users where username = :username',
                                {'username': new_name}).fetchone()
    return row[0]


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                              {'username': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT id from users'))
    keys = tuple(row[0] for row in rows)
    return keys


def make_user():
    user = User("Andrew", "111")
    return user


def insert_movie(empty_session):
    empty_session.execute(
        'INSERT INTO movies ( title, genre, description, director, actor, year, runtime_minutes,rating, votes, revenue,'
        'metascore ) VALUES '
        '( "Morning Alex",'
        '"Music",'
        '"very cool ",'
        '"Alex",'
        '"Alexxx",'
        '"2020",'
        '"1000.00",'
        '"5.0",'
        '"199.9",'
        '"100.000",'
        '"11.10")'
    )
    row = empty_session.execute('SELECT id from movies').fetchone()
    return row[0]


def make_movie():
    movie = Movie(
        "Morning Alex",
        "Music",
        "very cool ",
        "Alex",
        "Alexxx",
        "2020",
        "1000.00",
        "5.0",
        "199.9",
        "100.000",
        "11.10"

    )
    return movie


#
#
# def insert_genres(empty_session):
#     empty_session.execute(
#         'INSERT INTO genres (name) VALUES ("News"), ("New Zealand")'
#     )
#     rows = list(empty_session.execute('SELECT id from tags'))
#     keys = tuple(row[0] for row in rows)
#     return keys


def test_loading_of_users(empty_session):
    users = list()
    users.append(("Andrew", "1234"))
    users.append(("Cindy", "1111"))
    insert_users(empty_session, users)

    expected = [
        User("Andrew", "1234"),
        User("Cindy", "999")
    ]
    assert empty_session.query(User).all() == expected


def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT username, password FROM users'))
    assert rows == [("Andrew", "111")]


def test_saving_of_users_with_common_username(empty_session):
    insert_user(empty_session, ("Andrew", "1234"))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("Andrew", "111")
        empty_session.add(user)
        empty_session.commit()


def test_loading_of_article(empty_session):
    movie_key = insert_movie(empty_session)
    expected_movie = make_movie()
    fetched_movie = empty_session.query(Movie).one()

    assert expected_movie == fetched_movie
    assert movie_key == fetched_movie.id
