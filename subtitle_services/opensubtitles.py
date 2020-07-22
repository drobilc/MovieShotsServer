import tmdbsimple as tmdb
from .movie import Movie
from datetime import datetime
from pythonopensubtitles.opensubtitles import OpenSubtitles

import urllib.request
import srt
import gzip
import io

from exceptions import *

class OpenSubtitlesService(object):
    
    def __init__(self, flask_app, tmdb_api_key='', opensubtitles_username='', opensubtitles_password=''):
        self.flask_app = flask_app

        # Configure the movie database client with our api key
        tmdb.API_KEY = tmdb_api_key

        # To get images, we must construct the URL from the configuration
        self.configuration = tmdb.Configuration().info()

        # Import the open subtitles client and login to get the token
        self.opensubtitles = OpenSubtitles()
        self.token = self.opensubtitles.login(opensubtitles_username, opensubtitles_password)
        assert self.token is not None
    
    def get_imdb_id(self, movie):
        """Get movie IMDB id from Movie object by TMDB id"""
        tmbd_movie = tmdb.Movies(movie.id)
        response = tmbd_movie.info()

        # After additional movie information is received, add it to the Movie
        # object.
        movie.update_information(response)
        
        # If the response contains IMDB id, return both, the ID (as an integer)
        # and the TMDB database movie information
        if response['imdb_id']:
            return int(response['imdb_id'].replace('tt', ''))
    
    def construct_cover_url(self, poster_path):
        # The TMDB image URLs must be constructed from three parts as described
        # at https://developers.themoviedb.org/3/getting-started/images
        return '{}{}{}'.format(
            self.configuration['images']['secure_base_url'],
            self.configuration['images']['poster_sizes'][0],
            poster_path
        )
    
    def parse_movie_suggestion(self, movie):
        # Extract release year from movie (the movie might not have a release
        # date). The application will not display movie year if it is set to 0.
        movie_year = 0
        try:
            # The release date from TMDB is in format YYYY-MM-DD, only extract
            # year. The release date can also be empty so wrap it in try-except
            # block to ensure this doesn't crash.
            release_date = datetime.strptime(movie['release_date'], '%Y-%m-%d')
            movie_year = release_date.year
        except Exception:
            pass

        # If movie has a poster, generate its full url from movie['poster_path']
        cover_url = ''
        if movie['poster_path'] is not None:
            cover_url = self.construct_cover_url(movie['poster_path'])

        # Construct a new Movie object that contains all the data which will be
        # displayed in our application
        return Movie(movie['id'], movie['title'], year=movie_year, cover=cover_url)
    
    def get_suggestions(self, query):
        # Create a new search object and use it to find movies matching query
        search = tmdb.Search()
        response = search.movie(query=query)
        
        # After data has been downloaded a list of Movie objects should be
        # constructed.
        suggestions = []
        for movie in search.results:
            try:
                # Try to extract the needed information from each result
                suggestions.append(self.parse_movie_suggestion(movie))
            except Exception as e:
                self.flask_app.logger.error('Suggestion for query "{}" could not be parsed: {}'.format(query, e))
        
        # Both, the suggestions and TMDB response should be returned,
        # so that the response can be saved in local database 
        return suggestions, response
    
    def find_subtitles(self, imdb_id, language='eng'):
        # Use OpenSubtitles database to find subtitles for specific movie using
        # IMDB id.
        data = self.opensubtitles.search_subtitles([{
            'sublanguageid': language,
            'imdbid': imdb_id
        }])
        
        if data is None:
            return None
        
        # Filter subtitles by file format (currently, we only support .srt file
        # format) and order them by number of downloads.
        subtitles = list(filter(lambda subtitle: subtitle['SubFormat'] == 'srt', data))
        subtitles = sorted(subtitles, key=lambda subtitle: subtitle['SubDownloadsCnt'], reverse=True)

        if len(subtitles) > 0:
            return subtitles

    def download_subtitles(self, url):
        """Download gzipped subtitles from URL, extracts them in memory and returns srt object"""
        # OpenSubtitles service can automatically convert subtitles from their
        # encoding to "utf-8" (experimentally).
        download_url = url.replace('filead', 'subencoding-utf8/filead')
        
        # Download subtitles from OpenSubtitles and decompress gzip in memory
        response = urllib.request.urlopen(download_url)
        compressed_file = io.BytesIO(response.read())
        decompressed_file = gzip.GzipFile(fileobj=compressed_file)
        
        # Read contents of the decompressed file (.srt filetype), ASSUME it is
        # "utf-8" encoded and use the srt parser to parse subtitles file
        file_content = decompressed_file.read().decode('utf-8')
        subtitle_generator = srt.parse(file_content)

        return subtitle_generator

    def get_subtitles(self, movie, language='eng'):
        """Search subtitles by Movie object and return srt object"""
        # Get movie IMDB id from its TMDB id
        imdb_id = self.get_imdb_id(movie)

        # Get a list of possible subtitles from OpenSubtitles database
        found_subtitles = self.find_subtitles(imdb_id, language)
        if found_subtitles is None:
            raise SubtitlesNotFoundException(movie.title)

        for found_subtitle in found_subtitles:
            try:
                # Get subtitle download link and try to download subtitles. If
                # subtitles are successfully downloaded, end the loop, otherwise
                # try to download the next ones.
                download_link = found_subtitle['SubDownloadLink']
                if download_link is not None:
                    subtitle_generator = self.download_subtitles(download_link)
                    if subtitle_generator is not None:
                        return subtitle_generator
            except Exception as e:
                self.flask_app.logger.error('Subtitles for {} could not be parsed: {}'.format(movie, e))