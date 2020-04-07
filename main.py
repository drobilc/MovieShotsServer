from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

from downloader import SubtitleDownloader
from generator import WordFinder, IntoxicationLevel

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Global variables that are available for all requests
downloader = SubtitleDownloader()
word_finder = WordFinder()

@app.route('/<movie>/<intoxication>/<int:number_of_players>')
@cross_origin()
def hello_world(movie, intoxication, number_of_players):
    # Convert the received intoxication level to enum
    intoxication_level = IntoxicationLevel[intoxication.upper()]
    next_intoxication_level = intoxication_level.next_level()

    # Get current intoxication level number of shots and next level number of shots
    minimum_number_of_shots = intoxication_level.value
    maximum_number_of_shots = next_intoxication_level.value

    # Download subtitles from podnapisi.net with movie name
    subtitles, subtitle_generator = downloader.get_subtitles(movie)
    possible_words = word_finder.get_words(subtitle_generator, minimum_number_of_shots, maximum_number_of_shots)

    selected_words = possible_words[:number_of_players]

    return jsonify({
        "movie": subtitles['name'],
        "words": [{"word": keyword, "occurrences": occurrences} for keyword, occurrences in selected_words]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)