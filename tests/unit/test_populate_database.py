from sqlalchemy import select, inspect

from movie.adapters.orm import metadata


def test_database_populate_inspect_table_names(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    assert inspector.get_table_names() == ['actors', 'directors', 'genres', 'movies', 'movies_actors',
                                           'movies_directors', 'movies_genres', 'reviews', 'users']


def test_database_populate_select_all_genres(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_genres_table = inspector.get_table_names()[2]

    #
    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_genres_table]])
        result = connection.execute(select_statement)
        #
        all_genre_names = []
        for row in result:
            all_genre_names.append(row['name'])
        #
        assert all_genre_names[0] == 'Action'
        assert all_genre_names[5] == 'Thriller'
        assert len(all_genre_names) == 10


def test_database_populate_select_all_users(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_users_table = inspector.get_table_names()[8]

    with database_engine.connect() as connection:
        # query for records in table users
        select_statement = select([metadata.tables[name_of_users_table]])
        result = connection.execute(select_statement)

        all_users = []
        for row in result:
            all_users.append(row['username'])

        assert all_users == ['thorke', 'fmercury']


def test_database_populate_select_all_reviews(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_reviews_table = inspector.get_table_names()[7]

    with database_engine.connect() as connection:
        # query for records in table comments
        select_statement = select([metadata.tables[name_of_reviews_table]])
        result = connection.execute(select_statement)

        all_comments = []
        for row in result:
            all_comments.append((row['id'], row['user_id'], row['movie_id'], row['comment']))

        assert all_comments == [(1, 2, 1, "good movie"),
                                (2, 1, 1, "Yeah great"),
                                (3, 2, 1, "awesome!")]


def test_database_populate_select_all_director(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_directors_table = inspector.get_table_names()[1]

    #
    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_directors_table]])
        result = connection.execute(select_statement)
        #
        all_directors_names = []
        for row in result:
            all_directors_names.append(row['name'])
        #
        assert all_directors_names[1] == 'Ridley Scott'
        assert len(all_directors_names) == 5


def test_database_populate_select_all_actor(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_actors_table = inspector.get_table_names()[0]

    #
    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_actors_table]])
        result = connection.execute(select_statement)
        #
        all_actors_names = []
        for row in result:
            all_actors_names.append(row['name'])
        #
        assert all_actors_names[1] == 'Vin Diesel'
        assert len(all_actors_names) == 20


def test_database_populate_select_all_movie(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_movies_table = inspector.get_table_names()[3]

    #
    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_movies_table]])
        result = connection.execute(select_statement)
        #
        all_movies_names = []
        for row in result:
            all_movies_names.append(row['id'])
        #
        assert len(all_movies_names) == 5

def test_database_populate_select_all_movie_actor(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_movies_actor_table = inspector.get_table_names()[4]

    #
    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_movies_actor_table]])
        result = connection.execute(select_statement)
        #
        all_movies_actor_ids = []
        for row in result:
            all_movies_actor_ids.append(row['id'])
        #
        assert len(all_movies_actor_ids) == 20



def test_database_populate_select_all_movie_dir(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_movies_dir_table = inspector.get_table_names()[5]

    #
    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_movies_dir_table]])
        result = connection.execute(select_statement)
        #
        all_movies_dir_ids = []
        for row in result:
            all_movies_dir_ids.append(row['id'])
        #
        assert len(all_movies_dir_ids) == 5

def test_database_populate_select_all_movie_genre(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_movies_genre_table = inspector.get_table_names()[6]

    #
    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_movies_genre_table]])
        result = connection.execute(select_statement)
        #
        all_movies_genre_ids = []
        for row in result:
            all_movies_genre_ids.append(row['id'])
        #
        assert len(all_movies_genre_ids) == 10