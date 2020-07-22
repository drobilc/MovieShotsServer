from flask import Flask, request, jsonify

from subtitle_services.opensubtitles import OpenSubtitlesService
from subtitle_services.movie import Movie
import settings

from generator import DrinkingGame
from exceptions import *
import re

app = Flask(__name__)

# Global variables that are available for all requests
subtitle_service = OpenSubtitlesService(
    app,    # Flask application used for logging
    tmdb_api_key=settings.TMDB_API_KEY,
    opensubtitles_username=settings.OPENSUBTITLES_USERNAME,
    opensubtitles_password=settings.OPENSUBTITLES_PASSWORD
)

@app.errorhandler(ApiException)
def handle_api_exception(error):
    response = jsonify(error.to_dict())
    return response

@app.route('/game')
def game_generation():
    # Get the url GET parameters for movie title, intoxication and number of
    # players. Default values for intocixation is 8 shots, default number of
    # players is 4
    movie_title = request.args.get('movie', default=None, type=str)
    intoxication_level = request.args.get('intoxication', default=8, type=int)
    number_of_players = request.args.get('players', default=4, type=int)

    # If user taps on a suggestion in app, movie_id is forwarded to the server
    # alongside movie_title. In this case, we should only try to get subtitles
    # from know TMDB id.
    movie_id = request.args.get('movie_id', default=None, type=str)
    if movie_id is not None:
        # Construct a movie from received id (with empty title for now, it will
        # be updated once additional movie information is received)
        movie = Movie(movie_id, "")
        subtitle_generator = subtitle_service.get_subtitles(movie)
        game = DrinkingGame(movie, subtitle_generator, number_of_players, intoxication_level)
        return jsonify(game.to_dict())

    # If movie_id is not provided, movie_title is used to generate game. If it
    # is not provided, we should return an expcetion. If movie_title is
    # provided, we should first find suggestions and use the first suggestion
    # (the most probable one) to download subtitles.

    if not movie_title:
        raise InvalidParametersException('movie')

    suggestions, _ = subtitle_service.get_suggestions(movie_title)
    if suggestions is None or len(suggestions) <= 0:
        raise MovieNotFoundException(movie_title)

    movie = suggestions[0]
    try:
        subtitle_generator = subtitle_service.get_subtitles(movie)
    except Exception as e:
        print(e)
        raise SubtitlesNotFoundException(movie_title)

    if subtitle_generator is None:
        raise SubtitlesNotFoundException(movie_title)

    # Generate a new drinking game
    game = DrinkingGame(movie, subtitle_generator, number_of_players, intoxication_level)

    return jsonify(game.to_dict())

@app.route('/game/rate')
def game_rating():
    game_id = request.args.get('game', default=None, type=str)
    rating = request.args.get('rating', default=None, type=float)
    
    if not game_id:
        raise InvalidParametersException('game')

    if not rating:
        raise InvalidParametersException('rating')

    # TODO: Add rating to database

    return jsonify({
        'game': game_id,
        'rating': rating
    })

@app.route('/movie/trending')
def trending_movies():
    page = request.args.get('page', default=1, type=int)
    return jsonify(subtitle_service.get_popular(page))

@app.route('/suggestions')
def movie_suggestions():
    keywords = request.args.get('keywords', None)

    if not keywords:
        raise InvalidParametersException('keywords')

    suggestions, response = subtitle_service.get_suggestions(keywords)
    return jsonify([suggestion.to_dict() for suggestion in suggestions])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4567, debug=True)