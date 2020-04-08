from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

from downloader import SubtitleDownloader
from generator import WordFinder

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Global variables that are available for all requests
downloader = SubtitleDownloader()
word_finder = WordFinder()

@app.route('/<movie>/<int:intoxication_level>/<int:number_of_players>')
@cross_origin()
def hello_world(movie, intoxication_level, number_of_players):
    # Download subtitles from podnapisi.net with movie name
    subtitles, subtitle_generator = downloader.get_subtitles(movie)
    possible_words = word_finder.get_words(subtitle_generator, intoxication_level, intoxication_level + 1)

    selected_words = possible_words[:number_of_players]

    return jsonify({
        "movie": subtitles['name'],
        "words": [{"word": keyword, "occurrences": occurrences} for keyword, occurrences in selected_words]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)