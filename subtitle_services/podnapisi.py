import requests
from bs4 import BeautifulSoup
import uuid, os.path, re
from io import BytesIO
import glob
import zipfile
import srt
import shutil
from exceptions import *
from subtitle_services.movie import Movie

class PodnapisiNet(object):

    def __init__(self):
        self.MAIN_URL = "https://www.podnapisi.net"
        self.ADVANCED_SEARCH_URL = self.MAIN_URL + "/subtitles/search/advanced"
        self.SUGGESTIONS_URL = self.MAIN_URL + "/en/moviedb/suggestions"

        self.session = requests.Session()
    
    def parse_subtitles(self, response):
        subtitles = []
        html = BeautifulSoup(response, 'html.parser')
        rows = html.find_all('tr', {'class': 'subtitle-entry'})
        
        for row in rows:
            first_column = row.find('td')
            subtitle_name = first_column.find('a', recursive=False)
            subtitles.append({
                "title": subtitle_name.text.strip(),
                "url": self.MAIN_URL + subtitle_name['href'],
                "download_url": self.MAIN_URL + subtitle_name['href'] + "/download"
            })

        return subtitles
    
    def search(self, keywords, language="en"):
        search_parameters = {
            "keywords": keywords, 
            "year": "",
            "seasons": "",
            "episodes": "",
            "language": language
        }
        response = self.session.get(self.ADVANCED_SEARCH_URL, params=search_parameters)
        
        subtitles = self.parse_subtitles(response.text)
        if len(subtitles) <= 0:
            raise SubtitlesNotFoundException(keyword)

        movie = Movie(id=0, name=subtitles[0]['title'])
        return movie, subtitles
    
    def get_suggestions(self, keywords):
        search_parameters = {
            "keywords": keywords,
        }
        response = self.session.get(self.SUGGESTIONS_URL, params=search_parameters)

        suggestions = []
        for suggestion in response.json()[1]:
            suggestions.append(Movie(id=0, name=suggestion))
        return suggestions
    
    def download(self, subtitle, temporary_path='./subtitles'):
        # Download zip file from the server
        response = self.session.get(subtitle['download_url'])

        # Convert received response bytes to file-like object
        zip_object = BytesIO(response.content)

        # Extract files to a temporary path
        extract_folder_name = str(uuid.uuid4().hex)
        extract_folder_path = os.path.join(temporary_path, extract_folder_name)
        with zipfile.ZipFile(zip_object, 'r') as zip_file:
            zip_file.extractall(extract_folder_path)
        
        # Get srt file and read it as a file object
        subtitle_file_glob = os.path.join(extract_folder_path, "*.srt")
        subtitle_files = glob.glob(subtitle_file_glob)

        if len(subtitle_files) <= 0:
            raise SubtitlesNotFoundException(subtitle['title'])

        subtitle_file = subtitle_files[0]

        # Read first found subtitle file
        subtitle_generator = None

        with open(subtitle_file, 'r', encoding='utf-8') as subtitle_file:
            file_content = subtitle_file.read()
            subtitle_generator = srt.parse(file_content)

        # Finally, remove zip folder
        shutil.rmtree(extract_folder_path)

        return subtitle_generator