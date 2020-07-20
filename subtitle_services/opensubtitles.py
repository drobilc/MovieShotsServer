import tmdbsimple as tmdb
from .movie import Movie
from datetime import datetime
from pythonopensubtitles.opensubtitles import OpenSubtitles

import chardet

import urllib.request
import srt
import gzip
import io

class OpenSubtitlesService(object):
    
    def __init__(self, tmdb_api_key='', opensubtitles_username='', opensubtitles_password=''):
        # Configure the movie database client with our api key
        tmdb.API_KEY = tmdb_api_key

        # To get images, we must construct the URL from the configuration
        self.configuration = tmdb.Configuration().info()

        # Import the open subtitles client and login to get the token
        self.opensubtitles = OpenSubtitles()
        self.token = self.opensubtitles.login(opensubtitles_username, opensubtitles_password)
        assert self.token is not None
    
    def get_imdb_id(self, tmdb_id):
        movie = tmdb.Movies(tmdb_id)
        response = movie.info()
        
        if response['imdb_id']:
            return int(response['imdb_id'].replace('tt', ''))
    
    def construct_cover_url(self, poster_path):
        return '{}{}{}'.format(self.configuration['images']['secure_base_url'], self.configuration['images']['poster_sizes'][0], poster_path)
    
    def parse_movie_suggestion(self, movie):
        # Extract release year from movie (the movie might not have a release date)
        movie_year = 0
        try:
            release_date = datetime.strptime(movie['release_date'], '%Y-%m-%d')
            movie_year = release_date.year
        except Exception:
            pass

        # If movie has a poster, generate its full url movie['poster_path']
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
        
        # After data has been downloaded a list of Movie object should be constructed
        suggestions = []
        for movie in search.results:
            try:
                # Try to extract the needed information from each result
                suggestions.append(self.parse_movie_suggestion(movie))
            except Exception as e:
                pass
        
        # Both, the suggestions and tbdb response should be returned,
        # so that the response can be saved in local database 
        return suggestions, response
    
    def find_subtitles(self, imdb_id, language='eng'):
        data = self.opensubtitles.search_subtitles([{'sublanguageid': language, 'imdbid': imdb_id}])
        
        if data is None:
            return None, None
        
        subtitles = list(filter(lambda subtitle: subtitle['SubFormat'] == 'srt', data))
        subtitles = sorted(subtitles, key=lambda subtitle: subtitle['SubDownloadsCnt'], reverse=True)

        if len(subtitles) > 0:
            return subtitles[0]['SubDownloadLink'], subtitles
        
        return None, None

    def download_subtitles(self, url):
        download_url = url.replace('filead', 'subencoding-utf8/filead')
        response = urllib.request.urlopen(download_url)
        compressed_file = io.BytesIO(response.read())
        decompressed_file = gzip.GzipFile(fileobj=compressed_file)
        
        file_content = decompressed_file.read().decode('utf-8')
        subtitle_generator = srt.parse(file_content)
        return subtitle_generator

    def get_subtitles(self, movie, language='eng'):
        imdb_id = self.get_imdb_id(movie.id)
        download_link, subtitle_data = self.find_subtitles(imdb_id, language)
        if download_link is not None:
            return self.download_subtitles(download_link)