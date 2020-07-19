from flask import Flask, request, jsonify

from subtitle_services.podnapisi import PodnapisiNet
from subtitle_services.opensubtitles import OpenSubtitles

from generator import DrinkingGame
from exceptions import *
import re

app = Flask(__name__)

# Global variables that are available for all requests
# subtitle_service = PodnapisiNet()
subtitle_service = OpenSubtitles()

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

    if not movie_title:
        raise InvalidParametersException('movie')

    # Find all possible subtitles for requested movie title
    movie, possible_subtitles = subtitle_service.search(movie_title)

    # Perform filtering, in our case simply select the first subtitles
    selected_subtitles = possible_subtitles[0]

    # Download the selected subtitles
    subtitle = subtitle_service.download(selected_subtitles)

    # Generate a new drinking game
    game = DrinkingGame(movie, subtitle, number_of_players, intoxication_level)

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

@app.route('/suggestions')
def movie_suggestions():
    keywords = request.args.get('keywords', None)

    if not keywords:
        raise InvalidParametersException('keywords')

    suggestions = subtitle_service.get_suggestions(keywords)
    return jsonify([suggestion.to_dict() for suggestion in suggestions])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)