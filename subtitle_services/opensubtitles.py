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

class OpenSubtitles(object):
    
    def __init__(self):
        self.MAIN_URL = "https://www.opensubtitles.org"
        self.SUGGESTIONS_URL = self.MAIN_URL + "/libs/suggest.php"
        self.session = requests.Session()
    
    def parse_subtitles(self, response):
        subtitles = []

        html = BeautifulSoup(response, 'html.parser')
        print(html)

        results_table = html.find('table', {'id': 'search_results'})
        result_rows = results_table.find_all('tr')
        for row in result_rows[1:]:
            columns = row.find_all('td')
            if len(columns) < 1:
                continue
            link_column = columns[0]
            link = link_column.find('a')

            if link is None or 'href' not in link.attrs:
                continue

            # Get the subtitle id from received link href
            id_matches = re.search('\/(\d+)\/', link['href'])
            if not id_matches:
                continue

            subtitle_id = id_matches.group(1)
            download_url = "https://www.opensubtitles.org/en/subtitleserve/sub/{}".format(subtitle_id)

            subtitles.append({
                "title": link.text.replace('\n', ' '),
                "url": self.MAIN_URL + link['href'],
                "download_url": download_url
            })
            
        return subtitles

    def search(self, keyword, language="en"):
        # First, create a request to suggestions url to get movie id
        suggestions = self.get_suggestions(keyword)
        if len(suggestions) <= 0:
            raise MovieNotFoundException(keyword)

        movie_id = suggestions[0].id

        url = f'https://www.opensubtitles.org/en/search/sublanguageid-eng/idmovie-{movie_id}/sort-7/asc-0'
        response = self.session.get(url)

        subtitles = self.parse_subtitles(response.text)
        if len(subtitles) <= 0:
            raise SubtitlesNotFoundException(keyword)

        return suggestions[0], subtitles
    
    def get_suggestions(self, keyword):
        search_parameters = {
            "format": "json3",
            "MovieName": keyword,
            "SubLanguageID": "eng"
        }
        response = self.session.get(self.SUGGESTIONS_URL, params=search_parameters)
        suggestions = []
        for suggestion in response.json():
            suggestions.append(Movie(**suggestion))
        return suggestions
    
    def download(self, subtitle, temporary_path='./subtitles'):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,sl;q=0.8,la;q=0.7,da;q=0.6",
            "cache-control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "referer": subtitle['url'],
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
        }

        # Download zip file from the server
        response = self.session.get(subtitle['download_url'], headers=headers)

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

        with open(subtitle_file, 'r') as subtitle_file:
            file_content = subtitle_file.read()
            subtitle_generator = srt.parse(file_content)

        # Finally, remove zip folder
        shutil.rmtree(extract_folder_path)

        return subtitle_generator