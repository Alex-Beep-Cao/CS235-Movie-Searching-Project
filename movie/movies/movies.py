from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

import movie.adapters.repository as repo
import movie.utilities.utilities as utilities
import movie.movies.services as services

from movie.authentication.authentication import login_required

# Configure Blueprint.
movies_blueprint = Blueprint(
    'movies_bp', __name__)


@movies_blueprint.route('/movies_by_genre', methods=['GET'])
def movies_by_genre():
    movies_per_page = 3

    # Read query parameters.
    genre_name = request.args.get('genre')
    actor_name = request.args.get('actor')
    director_name = request.args.get('director')
    # pagination cursor
    cursor = request.args.get('cursor')
    # comment
    movie_to_show_comments = request.args.get('view_comments_for')

    if movie_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent movie id.
        movie_to_show_comments = -1
    else:
        # Convert movie_to_show_comments  from string to int.
        movie_to_show_comments = int(movie_to_show_comments)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # print(genre_name)
    # print(actor_name)
    # print(director_name)
    if genre_name:
        genre_name = genre_name.strip()
    else:
        genre_name = ''
    if actor_name:
        actor_name = actor_name.strip()
    else:
        actor_name = ''
    if director_name:
        director_name = director_name.strip()
    else:
        director_name = ''

    movie_ids_all = services.get_movie_ids_all(repo.repo_instance)
    movie_ids = movie_ids_all

    # https://www.kite.com/python/answers/how-to-find-the-intersection-of-two-lists-in-python
    # list1 = [1, 2, 3]
    # list2 = [1, 3, 5]
    # intersection_set = set.intersection(set(list1), set(list2))
    # find intersection of list1 and list2
    # intersection_list = list(intersection_set)
    # print(intersection_list)
    #     OUTPUT
    #     [1, 3]

    # Retrieve movie ids for movies that are genre with genre_name.
    if genre_name:
        genre_movie_ids = services.get_movie_ids_for_genre(genre_name, repo.repo_instance)
        movie_ids = list(set.intersection(set(movie_ids), set(genre_movie_ids)))

    # Retrieve movie ids for movies that are acted with actor_name.
    if actor_name:
        actor_movie_ids = services.get_movie_ids_for_actor(actor_name, repo.repo_instance)
        movie_ids = list(set.intersection(set(movie_ids), set(actor_movie_ids)))

    # Retrieve movie ids for movies that are directed with director_name.
    if director_name:
        director_movie_ids = services.get_movie_ids_for_director(director_name, repo.repo_instance)
        movie_ids = list(set.intersection(set(movie_ids), set(director_movie_ids)))

    movie_ids.sort()
    # print(movie_ids)

    # Retrieve the batch of movies to display on the Web page.
    movies = services.get_movies_by_id(movie_ids[cursor:cursor + movies_per_page], repo.repo_instance)

    first_article_url = None
    last_article_url = None
    next_article_url = None
    prev_article_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_article_url = url_for('movies_bp.movies_by_genre', genre=genre_name, actor=actor_name,
                                   director=director_name, cursor=cursor - movies_per_page)
        first_article_url = url_for('movies_bp.movies_by_genre', genre=genre_name, actor=actor_name,
                                    director=director_name)

    if cursor + movies_per_page < len(movie_ids):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_article_url = url_for('movies_bp.movies_by_genre', genre=genre_name, actor=actor_name,
                                   director=director_name, cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movie_ids) / movies_per_page)
        if len(movie_ids) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_article_url = url_for('movies_bp.movies_by_genre', genre=genre_name, actor=actor_name,
                                   director=director_name, cursor=last_cursor)

    # Construct urls for viewing movie comments and adding comments.
    for movie in movies:
        movie['view_comment_url'] = url_for('movies_bp.movies_by_genre', genre=genre_name,
                                            actor=actor_name, director=director_name,
                                            cursor=cursor,
                                            view_comments_for=movie['id'])
        movie['add_comment_url'] = url_for('movies_bp.comment_on_movie', movie=movie['id'])

    # Generate the webpage to display the articles.
    return render_template(
        'movies/movies.html',

        movies=movies,

        genre_name=genre_name,
        actor_name=actor_name,
        director_name=director_name,

        genre_urls=utilities.get_genres_and_urls(),
        actor_urls=utilities.get_actors_and_urls(),
        director_urls=utilities.get_directors_and_urls(),

        first_article_url=first_article_url,
        last_article_url=last_article_url,
        prev_article_url=prev_article_url,
        next_article_url=next_article_url,

        show_comments_for_movie=movie_to_show_comments
    )


@movies_blueprint.route('/comment_on_movie', methods=['GET', 'POST'])
@login_required
def comment_on_movie():
    # Obtain the username of the currently logged in user.
    username = session['username']

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an movie id, when subsequently called with a HTTP POST request, the movie id remains in the
    # form.
    form = CommentForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the comment text has passed data validation.
        # Extract the movie id, representing the commented movie, from the form.
        movie_id = int(form.movie_id.data)

        # Use the service layer to store the new comment.
        services.add_comment(movie_id, form.comment.data, username, repo.repo_instance)

        # Retrieve the movie in dict form.
        movie = services.get_movie(movie_id, repo.repo_instance)

        # refresh this webpage
        # to show all the comments of this movie, include the newly created one.
        return redirect(url_for('movies_bp.comment_on_movie', movie=movie_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the movie id, representing the movie to comment, from a query parameter of the GET request.
        movie_id = int(request.args.get('movie'))

        # Store the movie id in the form.
        form.movie_id.data = movie_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the movie id of the movie being commented from the form.
        movie_id = int(form.movie_id.data)

    # For a GET or an unsuccessful POST, retrieve the movie to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    movie = services.get_movie(movie_id, repo.repo_instance)
    return render_template(
        'movies/comment_on_movie.html',
        title='Comment movie',
        movie=movie,
        form=form,
        handler_url=url_for('movies_bp.comment_on_movie'),

        # selected_articles=utilities.get_selected_articles(),
        selected_articles=list(),
        # tag_urls=utilities.get_tags_and_urls()
        tag_urls=list(),

        genre_urls=utilities.get_genres_and_urls(),
        actor_urls=utilities.get_actors_and_urls(),
        director_urls=utilities.get_directors_and_urls(),
    )


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', [
        DataRequired(),
        Length(min=4, message='Your comment is too short'),
        ProfanityFree(message='Your comment must not contain profanity')])
    movie_id = HiddenField("Movie id")
    submit = SubmitField('Submit')
