from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from podnapisi import PodnapisiNet
from downloader import SubtitleDownloader
from generator import DrinkingGame
from exceptions import *

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Global variables that are available for all requests
downloader = SubtitleDownloader()
subtitles_service = PodnapisiNet()

@app.errorhandler(ApiException)
def handle_api_exception(error):
    response = jsonify(error.to_dict())
    return response

@app.route('/game')
@cross_origin()
def game_generation():
    # Get the url GET parameters for movie title, intoxication and number of
    # players. Default values for intocixation is 8 shots, default number of
    # players is 4
    movie_title = request.args.get('movie', default=None, type=str)    
    intoxication_level = request.args.get('intoxication', default=8, type=int)
    number_of_players = request.args.get('players', default=4, type=int)

    if not movie_title:
        raise InvalidParametersException('movie')

    # Download subtitles from subtitles provider with movie_title
    subtitles, subtitle_generator = downloader.get_subtitles(movie_title)

    # Generate a new drinking game
    game = DrinkingGame(subtitles, subtitle_generator, number_of_players, intoxication_level)

    return jsonify(game.to_dict())

@app.route('/suggestions')
def movie_suggestions():
    keywords = request.args.get('keywords', None)

    if not keywords:
        raise InvalidParametersException('keywords')

    suggestions = subtitles_service.get_suggestions(keywords)
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)